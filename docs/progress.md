# Progress Tracker

> This document is updated continuously throughout development.
> Every agent working on this project updates this file at the start and end of every subphase.

---

## Current Status

| | |
|---|---|
| **Current Phase** | Phase 1 — Terraform Infrastructure |
| **Current Subphase** | Not started — read `docs/phases/phase-1/phase-1-overview.md` |
| **Branch** | `main` |
| **Last updated** | 2026-11-19 |

---

## Phase Overview

| Phase | Title | Status |
|---|---|---|
| **Phase 0** | Project Foundation | ✅ Complete |
| Phase 1 | Terraform Infrastructure | ⬜ Not Started |
| Phase 2 | Medallion Pipeline (Bronze → Silver → Gold) | ⬜ Not Started |
| Phase 3 | Self-Indexing RAG Engine | ⬜ Not Started |
| Phase 4 | Ingestion Control + Backfill | ⬜ Not Started |
| Phase 5 | Next.js Frontend + CI/CD + Polish | ⬜ Not Started |

---

## Phase 0 — Project Foundation

**Goal**: Repository is fully bootstrapped. Any agent can clone this repo and immediately
understand what to build, how to work, and where everything lives.

**Subphases:**

| Subphase | Title | Branch | Status | PR |
|---|---|---|---|---|
| 0.1 | Repository bootstrap and documentation | `main` | 🔄 In Progress | — |

### 0.1 Checklist

- [x] `AGENTS.md` created (agent operating manual)
- [x] `CLAUDE.md` created (redirect to AGENTS.md)
- [x] `README.md` written (project overview)
- [x] `docs/architecture.md` written (full system design)
- [x] `docs/progress.md` created (this file)
- [x] Directory structure scaffolded
- [x] `docs/adr/` — all 5 ADRs written
- [x] `backend/pyproject.toml` initialized with uv
- [x] `pre-commit` config written
- [x] `.gitignore` written
- [x] `.env.example` written
- [x] Phase 1 overview doc written
- [x] Initial commits pushed

---

## Phase 1 — Terraform Infrastructure

**Goal**: All AWS infrastructure defined as Terraform code and deployable with `terraform apply`.

> Phase 1 overview doc will be created when Phase 0 is complete.

---

## Blockers / Notes

| Date | Note |
|---|---|
| 2026-11-19 | Project initialized. GitHub remote: `shubhojit-mitra-dev/realtime-rag-lakehouse` |

---

## Milestones

| Milestone | Target | Achieved |
|---|---|---|
| Repo bootstrapped | Phase 0 | — |
| First terraform deploy | Phase 1 | — |
| First data in Bronze | Phase 1 | — |
| Full Bronze → Silver → Gold pipeline | Phase 2 | — |
| First vector in S3 Vectors | Phase 3 | — |
| RAG answers first question | Phase 3 | — |
| Backfill closes a 24h gap | Phase 4 | — |
| Frontend live on Vercel | Phase 5 | — |
| CI/CD green | Phase 5 | — |
