# System Architecture

> Last updated: 2026-11-19
> Status: Design finalized. Implementation begins Phase 1.

---

## Overview

`realtime-rag-lakehouse` is an event-driven, serverless data platform. It has two independently
operable concerns:

1. **The Data Pipeline** — ingestion, transformation, and storage through medallion layers
2. **The RAG Layer** — self-indexing, retrieval, and conversational query interface

Both are serverless, pay-per-use, and cost nothing when idle.

---

## Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION CONTROL                        │
│  Next.js "Go Live" → Pipeline Controller Lambda                 │
│  → Enable EventBridge Rule  +  Trigger Backfill Lambda          │
└───────────────────┬─────────────────────────────────────────────┘
                    │ (every 5 min when enabled)
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│               AWS STEP FUNCTIONS EXPRESS                        │
│  Step 1: Collect from APIs → write raw JSON to S3 Bronze        │
│  Step 2: Bronze → validate (Pydantic) → Parquet → S3 Silver     │
│  Step 3: Silver → aggregate + sentiment → Parquet → S3 Gold     │
│  Step 4: Gold → chunk → embed (Gemini) → S3 Vectors + DynamoDB  │
└─────────────────────────────────────────────────────────────────┘

S3 Bronze  →  S3 Silver  →  S3 Gold  ──S3 event──▶  Embedder Lambda
                                                          │
                                               ┌──────────┴──────────┐
                                               ▼                     ▼
                                          S3 Vectors            DynamoDB
                                        (vector index)      (chunk metadata)

User → Next.js Chat → RAG Lambda (LangChain)
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        Embed question  Query S3    Query DynamoDB
        (Gemini embed)  Vectors     (structured lookup)
                           │
                       Top-k chunks
                           │
                    ┌──────▼──────┐
                    │ Gemini Flash│ ← context + question
                    └──────┬──────┘
                           ▼
                    Natural language answer
                    with source citations
```

---

## Data Sources

| Source | Data | Endpoint type | Historical support |
|---|---|---|---|
| CoinGecko (free) | Crypto OHLCV, market cap | REST polling | Yes — `/coins/{id}/market_chart` |
| Alpha Vantage (free) | Stock OHLCV | REST polling | Yes — `TIME_SERIES_DAILY` |
| NewsAPI (free) | Financial headlines | REST polling | Yes — 30 days via `everything` |

---

## Medallion Architecture

### Bronze (Raw Landing Zone)
- Format: JSON (exactly as received from API)
- Transformation: None. Immutable.
- Partitioning: `dt=YYYY-MM-DD/`
- Purpose: Audit trail, replay source, schema-on-read

### Silver (Cleansed & Conformed)
- Format: Parquet (columnar, compressed)
- Transformation: Pydantic validation, type casting, timestamp normalization (UTC), deduplication
- Quarantine: Invalid records → `silver/quarantine/` (never dropped silently)
- Purpose: Reliable, schema-enforced data for downstream consumers

### Gold (Business-Ready + RAG-Ready)
- Format: Parquet
- Transformation: OHLCV aggregations (hourly/daily), sentiment scoring (TextBlob), market signals (SMA, momentum)
- Purpose: Pre-computed, RAG-ready data chunks that feed the self-indexing engine

---

## Self-Indexing Engine

The moment a Parquet file lands in the Gold S3 prefix, an S3 event notification triggers
the Embedder Lambda. This Lambda:

1. Reads the Parquet file into a Pandas DataFrame
2. Applies a data-type-aware chunking strategy (see `docs/adr/ADR-005-chunking-strategy.md`)
3. Calls `Gemini text-embedding-004` to generate 768-dim vectors for each chunk
4. Writes vectors to S3 Vectors via `PutVectors` (batched at 500 max per call)
5. Writes chunk metadata (ticker, timestamp, source, raw text) to DynamoDB

The result: the RAG knowledge base is always current. No human intervention required.

---

## Ingestion Control + Backfill

### Why toggle-based?
Scheduled 24/7 ingestion runs even when no one uses the app — this defeats the serverless
cost model. See `docs/adr/ADR-004-toggle-based-ingestion.md`.

### Activation sequence
1. User clicks "Go Live" in Next.js UI
2. `POST /api/pipeline/start` → Pipeline Controller Lambda
3. Controller queries DynamoDB for `last_ingested_at` timestamp
4. If gap detected: triggers Backfill Lambda with `{from: last_ts, to: now}`
5. Backfill fetches historical data from APIs → runs full pipeline → vectors updated
6. Controller enables EventBridge rule → real-time ingestion starts
7. UI polls `GET /api/pipeline/status` → shows "Live" with last ingestion timestamp

### Deactivation
`POST /api/pipeline/stop` → Controller disables EventBridge rule → cost drops to storage only.

---

## RAG Architecture

### Retrieval Strategy (Hybrid)
Not purely vector search. Two-stage retrieval:

1. **Semantic (S3 Vectors)**: embed user question → `QueryVectors` → top-k most similar chunks
2. **Structured (DynamoDB)**: if question contains temporal signal ("today", "this week", "yesterday"),
   query DynamoDB directly by timestamp range to ensure recency accuracy

LangChain custom retriever combines both results, deduplicates, and passes to Gemini Flash.

### Why not Bedrock Knowledge Bases?
Bedrock requires AWS-hosted embedding models (Titan), which incur per-token charges.
Using Google AI Studio's free `text-embedding-004` keeps embedding cost at $0.
See `docs/adr/ADR-001-s3-vectors-over-pinecone.md`.

---

## Infrastructure

All infrastructure defined in Terraform. Zero click-ops.

| Module | Resources |
|---|---|
| `s3-lakehouse` | 3 S3 buckets (bronze/silver/gold) + lifecycle policies |
| `s3-vectors` | S3 Vectors index |
| `dynamodb` | Pipeline state table + chunk metadata table |
| `lambda` | All Lambda functions + IAM roles (least privilege) |
| `step-functions` | Express workflow state machine |
| `eventbridge` | Scheduled rule (disabled by default) |
| `ssm` | Parameter Store entries for API keys |
| `monitoring` | CloudWatch log groups + alarms |

---

## Cost Model

| State | Monthly cost | Why |
|---|---|---|
| Dormant | ~$0.03 | S3 + S3 Vectors storage only. No compute. |
| Active | ~$0.05 | Lambda (free tier), Step Functions (<$0.01), Gemini (free tier) |

The platform never needs to be deprovisioned. It simply sits dormant between uses.
