# realtime-rag-lakehouse

**A Serverless Real-Time Data Lakehouse with Self-Indexing RAG on AWS**

> A production-grade serverless AWS data platform that ingests live financial data through
> medallion architecture (Bronze → Silver → Gold), auto-embeds new data into Amazon S3 Vectors
> on arrival, and lets users query it in plain English via a LangChain RAG chatbot.
> Provisioned end-to-end with Terraform. True `$0` idle cost.

---

## Architecture

```
EventBridge (togglable) → Step Functions → [Ingest → Bronze → Silver → Gold]
                                                                      ↓
                                                            S3 Event → Lambda (Embedder)
                                                                      ↓
                                                               S3 Vectors (auto-indexed)
                                                                      ↓
                                                         Next.js Chat → LangChain RAG → Gemini
```

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | AWS Step Functions Express |
| Compute | AWS Lambda (Python 3.11) |
| Storage | Amazon S3 (Bronze/Silver/Gold layers) |
| Vector Store | Amazon S3 Vectors |
| Metadata | Amazon DynamoDB |
| Embeddings | Gemini `text-embedding-004` |
| LLM | Gemini 2.0 Flash |
| RAG | LangChain |
| IaC | Terraform |
| Frontend | Next.js + TypeScript (Vercel) |
| Package Manager | uv |
| CI/CD | GitHub Actions |

## Project Status

See [`docs/progress.md`](docs/progress.md) for the current phase and subphase.

## Documentation

- [`AGENTS.md`](AGENTS.md) — mandatory reading for all coding agents
- [`docs/architecture.md`](docs/architecture.md) — full system architecture
- [`docs/progress.md`](docs/progress.md) — live progress tracker
- [`docs/adr/`](docs/adr/) — architecture decision records
- [`docs/phases/`](docs/phases/) — phase and subphase documentation

## Setup

> Detailed setup instructions added in Phase 1.

**Prerequisites**: AWS CLI, Terraform ≥ 1.9, uv, Node.js ≥ 20, Google AI Studio API key

```bash
# Install Python dependencies
cd backend && uv sync

# Deploy infrastructure
cd terraform && terraform init && terraform plan

# Start frontend
cd frontend && npm install && npm run dev
```

## Cost

- **Dormant** (default): ~$0.03/month (S3 storage only)
- **Active** (live ingestion + chat): ~$0.05/month (all AWS free tiers apply)
