# ADR-005: Data-Type-Aware Chunking Strategy

**Date**: 2026-11-19
**Status**: Accepted

---

## Context

The Gold layer contains heterogeneous data: hourly price summaries, daily summaries, news
articles, and market signals. Each has different information density, structure, and the
kinds of questions users will ask about it.

A naive chunking approach (fixed character-count splitting) produces poor retrieval quality:
- A 500-character chunk of a Parquet row produces fragments with no semantic meaning
- A news headline plus its body in separate chunks retrieves only half the context
- Mixing price data with sentiment data in one chunk makes it less retrievable for either type

Chunking strategy directly determines RAG answer quality. This is not a cosmetic decision.

---

## Decision

Implement a **ChunkingStrategyFactory** that selects a data-type-specific chunking function
based on the Gold-layer file's prefix/metadata tag.

### Chunking strategies by data type

| Data Type | S3 Gold Prefix | Strategy | Example output chunk |
|---|---|---|---|
| Hourly market summary | `gold/hourly_summary/` | One chunk per ticker per hour | `"BTC 2026-11-18 14:00 UTC: open $43200 close $43580 high $43650 low $43100 vol 1.4B change +0.88% RSI 61 trend bullish"` |
| Daily market summary | `gold/daily_summary/` | One chunk per ticker per day | `"ETH 2026-11-18 daily: open $2340 close $2290 high $2380 low $2270 vol 8.2B change -2.14% sentiment 0.52 neutral"` |
| Enriched news | `gold/enriched_news/` | Headline + summary as one chunk | `"Reuters 2026-11-18 14:23 UTC: Bitcoin ETF inflows reach $500M this week — institutional demand accelerating. Sentiment: positive (0.81). Tickers: BTC"` |
| Market signals | `gold/market_signals/` | Group all signals per ticker per time window | `"AAPL signals 2026-11-18 15:00 UTC: SMA20=$191.4 SMA50=$188.2 SMA20>SMA50 bullish crossover. RSI=54 neutral. Volume: below 20-day avg. MACD: positive histogram"` |

### Implementation

```
ChunkingStrategyFactory
  ├── HourlySummaryChunker   (implements BaseChunker)
  ├── DailySummaryChunker    (implements BaseChunker)
  ├── EnrichedNewsChunker    (implements BaseChunker)
  └── MarketSignalsChunker   (implements BaseChunker)
```

Each chunker:
1. Accepts a Pandas DataFrame (one Gold Parquet file)
2. Returns `List[Chunk]` where `Chunk` is a Pydantic model with `text`, `metadata`, `ticker`, `timestamp`, `source`, `data_type`
3. The `text` field is what gets embedded
4. The `metadata` dict is stored in DynamoDB for structured retrieval

---

## Consequences

**Positive:**
- Each chunk is semantically complete and self-contained for its data type
- Retrieval quality is higher — a question about BTC price gets a price chunk, not a fragments mix
- Adding a new data type requires only adding a new Chunker class (Open/Closed principle)
- Chunk metadata enables DynamoDB-based temporal filtering for time-sensitive queries

**Negative:**
- More code than a single generic chunker (justified by significantly better retrieval quality)
- Chunking logic must be updated when new Gold data types are added

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| Fixed character-count splitting | Splits mid-sentence, destroys data relationships, poor retrieval for structured tabular data |
| LangChain `RecursiveCharacterTextSplitter` | Designed for unstructured text documents. Our data is semi-structured tabular data where row boundaries matter more than character counts. |
| One chunk per Parquet file | A file can contain hundreds of rows and thousands of characters — vastly exceeds embedding model context window and returns irrelevant results on retrieval |
| LLM-based chunking | Adds latency and cost to every ingestion run. Overkill for structured financial data with predictable shapes. |
