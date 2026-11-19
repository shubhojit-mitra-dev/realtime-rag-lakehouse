# ADR-001: S3 Vectors as the Vector Store

**Date**: 2026-11-19
**Status**: Accepted

---

## Context

The RAG layer requires a vector store to hold embeddings of Gold-layer data chunks and
support approximate nearest-neighbor search. Several options were evaluated.

The core constraint: **true $0 idle compute cost**. The vector store must not provision
any compute when no queries are being made.

---

## Decision

Use **Amazon S3 Vectors** as the vector store.

---

## Consequences

**Positive:**
- Zero provisioned compute — charges only on `PutVectors` and `QueryVectors` API calls
- Fully AWS-native — no third-party dependency, no additional credentials to manage
- Natively integrated with IAM — same role-based access as the rest of the stack
- Storage cost is ~$0.06/GB — at our scale (50K vectors, 768-dim) this is ~$0.009/month
- Query cost is $2.50/million queries — essentially $0 at demo/personal scale
- No index size limits on free tier (unlike Pinecone's 100K vector cap)
- Supports metadata filtering alongside vector similarity search

**Negative:**
- Newer service — less community documentation than Pinecone or pgvector
- No built-in full-text search (handled by DynamoDB structured lookup in our hybrid retrieval)
- Query latency slightly higher than dedicated vector DBs at massive scale (irrelevant at our scale)

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| Pinecone (free tier) | Third-party dependency, 100K vector limit on free tier, could change pricing |
| Supabase pgvector | Requires always-on Postgres compute, violates $0 idle constraint |
| OpenSearch Serverless | Charges hourly minimum OCU even with zero traffic — expensive idle |
| DynamoDB alone | No vector similarity search capability |
| ChromaDB (in Lambda) | Ephemeral — vectors lost between Lambda invocations (no persistence) |
