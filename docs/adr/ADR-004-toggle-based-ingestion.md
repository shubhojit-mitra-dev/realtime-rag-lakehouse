# ADR-004: Toggle-Based Ingestion with Automatic Backfill

**Date**: 2026-11-19
**Status**: Accepted

---

## Context

The pipeline needs to ingest data from financial APIs on a schedule (every 5 minutes).
The naive implementation enables the EventBridge schedule permanently — data flows 24/7
whether or not anyone is using the application.

This creates a real cost and design problem:
- Lambda invocations, Gemini embedding API calls, and S3 writes accumulate continuously
- If the app is left dormant for weeks, the RAG knowledge base grows stale
- When the app is reactivated after dormancy, users asking about "this week" get stale answers
- Continuous ingestion defeats the serverless model: serverless should cost $0 at zero usage

Additionally, free API tiers have rate limits. CoinGecko (free) allows 30 calls/minute.
Running 24/7 at 5-minute intervals is well within limits, but there is no value in those
calls when no user is actively querying the system.

---

## Decision

Implement **toggle-based ingestion** with **automatic historical backfill on activation**.

### Design
- EventBridge rule is **DISABLED** by default in Terraform (a single `aws_cloudwatch_event_rule`
  attribute: `state = "DISABLED"`)
- A **Pipeline Controller Lambda** exposes two endpoints:
  - `POST /api/pipeline/start` — enables the rule AND triggers backfill
  - `POST /api/pipeline/stop` — disables the rule
- The **Backfill Lambda**:
  1. Reads `last_ingested_at` from DynamoDB (updated after every successful pipeline run)
  2. Computes gap: `gap = now - last_ingested_at`
  3. If gap > 10 minutes: fetches historical data from APIs for the gap period
  4. Runs historical data through the full Bronze → Silver → Gold → Embed pipeline
  5. Reports completion to Controller

### Result
- When dormant: cost is storage only (~$0.03/month)
- When activated: backfill closes any data gap in ~30 seconds before live ingestion starts
- User experience: seamless. No visible gap in the RAG knowledge base.

---

## Consequences

**Positive:**
- True $0 idle compute cost — nothing runs when no one is using the app
- No data gaps from the user's perspective — backfill makes the transition seamless
- APIs' rate limits respected — no wasted calls during dormancy
- Demonstrates production cost-awareness — a key interview talking point
- Simple mechanism: an EventBridge rule `state` toggle is a single API call

**Negative:**
- Activation has ~30-second delay (backfill completion time)
- If dormancy exceeds 30 days, NewsAPI historical limit is reached (30-day search window)
  Mitigation: for very long dormancy, the news gap is noted in the UI; market data still backfills fully.
- Backfill Lambda timeout risk for very long gaps (>90 days). Mitigation: cap backfill at 90 days.

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| Always-on ingestion | Runs continuously even with zero users. Accumulates Lambda + embedding API costs for no value. Defeats serverless model. |
| Manual data upload on demand | Requires user action to load data. Not "real-time". Loses the pipeline narrative. |
| Short TTL (expire old vectors) | Could purge vectors while user is mid-session. Complex to implement correctly. |
| Caching recent answers | Doesn't solve the stale data problem — LLM still generates answers from outdated knowledge base. |
