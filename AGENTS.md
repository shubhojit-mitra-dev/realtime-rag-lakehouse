# AGENTS.md — Coding Agent Operating Manual

> **This file is mandatory reading for every AI coding agent before touching a single line of code.**
> This applies to all agents: Claude, Gemini, Copilot, Cursor, or any other.
> Read this file completely. No exceptions.

---

## 0. What Is This Project?

`realtime-rag-lakehouse` is a production-grade serverless data platform on AWS.

It ingests live financial data (crypto prices, stock prices, news headlines) through a
**medallion architecture** (Bronze → Silver → Gold) orchestrated by **AWS Step Functions**.
Every Gold-layer write auto-triggers embedding into **Amazon S3 Vectors** (self-indexing).
Users query the live data in plain English through a **LangChain RAG chatbot** and a
**Next.js** frontend.

**Key constraint**: True `$0` idle cost. When nobody uses the app, nothing runs.
Ingestion is toggle-based with automatic historical backfill on activation.

Full architecture and design decisions live in `docs/`. Start there.

---

## 1. Project Phase Structure

The project is divided into **numbered phases**. Each phase has **3–10 subphases**.

```
Phase 1 → Subphase 1.1, 1.2, 1.3 …
Phase 2 → Subphase 2.1, 2.2, 2.3 …
…
```

**Before starting a phase:**
- Read the phase documentation in `docs/phases/phase-N/phase-N-overview.md`
- Understand all deliverables
- Understand the "done when" condition

**Before starting a subphase:**
- Read the subphase doc: `docs/phases/phase-N/subphase-N.M.md`
- Create the git branch: `git checkout -b phase-N.M-short-description`
- Do NOT create all subphase docs at once — only create the doc for the current subphase before starting it

---

## 2. Git Discipline

### Branch naming
```
phase-1.1-terraform-s3-buckets
phase-1.2-iam-roles
phase-2.1-pydantic-schemas
```

### Atomic commits — STRICT

**One file per commit. No exceptions. No batching.**

```bash
# CORRECT
git add terraform/modules/s3-lakehouse/main.tf
git commit -m "feat(terraform): add S3 Bronze bucket with lifecycle policy"

# WRONG — never do this
git add terraform/modules/s3-lakehouse/main.tf terraform/modules/s3-lakehouse/variables.tf
git commit -m "add terraform files"
```

### Commit message format (Conventional Commits)

```
<type>(<scope>): <short description>

Types: feat | fix | test | docs | refactor | chore | ci
Scope: terraform | lambda | pipeline | indexer | chat | frontend | docs | tests

Examples:
feat(pipeline): implement silver transformer with pydantic validation
test(pipeline): add unit tests for silver transformer deduplication
fix(indexer): handle empty Gold parquet file in embedder lambda
docs(adr): add ADR-002 step functions over s3 event chains
chore(deps): add boto3 and pydantic to pyproject.toml
```

### Pull Requests

After every completed subphase:
1. Push branch to origin
2. Open a PR against `main`
3. Write a walkthrough document (see Section 7)
4. PR title: `[Phase N.M] Short description of what was done`
5. Wait for PR to be merged before starting the next subphase
6. Never force-push to `main`

---

## 3. Test-Driven Development (TDD) — Mandatory

**Tests are written BEFORE any implementation code. Always.**

### The TDD cycle for every subphase

```
1. Read subphase doc → understand required behaviour
2. Write all tests (unit + integration stubs)
3. Run tests → confirm they ALL fail (red)
4. Write minimum implementation to make tests pass
5. Refactor — keep tests green
6. All tests must pass before opening a PR
```

### Test file location

```
backend/tests/unit/test_<module>.py         ← Unit tests (mocked AWS with moto)
backend/tests/integration/test_<module>.py  ← Integration tests (against real or localstack)
```

### Test completeness checklist (before writing any implementation)

For every function being tested, write tests covering:
- [ ] Happy path (valid input → expected output)
- [ ] Edge cases (empty input, boundary values, None values)
- [ ] Error cases (invalid input, API failures, malformed data)
- [ ] Idempotency (running twice gives same result where expected)
- [ ] Data shape (output schema matches Pydantic model)

### Mock data

All mock data lives in `backend/tests/fixtures/`. Use realistic data — not `"test_string"`.

```python
# WRONG
ticker = "test"
price = 0

# CORRECT — realistic fixture
ticker = "BTC"
price = 43_250.75
timestamp = "2026-11-18T14:00:00Z"
```

### Failing tests

**Never modify a test to make it pass unless the test itself has a provable bug.**

If a test keeps failing:
1. Read the error message in full
2. Identify: which file → which function → which line → what is the actual vs expected value
3. Trace the call stack upward
4. Fix the implementation, not the test
5. If after thorough investigation the test is genuinely wrong (incorrect expectation, wrong mock setup), document why before changing it

---

## 4. Error Tracing Protocol

When any error occurs during development or testing:

```
Step 1: Read the FULL error output — do not skim
Step 2: Identify the error type (ImportError, ValidationError, ClientError, etc.)
Step 3: Find the exact file, function, and line number
Step 4: Understand the root cause — not just the symptom
Step 5: Check if related tests cover this code path
Step 6: Fix at the root cause, not with a workaround
Step 7: Run all tests again after fix
```

Do not suppress exceptions with bare `except: pass`. Every exception must be caught
specifically and either handled or re-raised with context:

```python
# WRONG
try:
    result = s3.get_object(...)
except:
    pass

# CORRECT
try:
    result = s3.get_object(Bucket=bucket, Key=key)
except s3.exceptions.NoSuchKey as e:
    raise DataNotFoundError(f"Object {key} not found in {bucket}") from e
```

---

## 5. Documentation Standards

### Phase overview doc
Created ONCE at the start of each phase.
Path: `docs/phases/phase-N/phase-N-overview.md`
Contains: goals, deliverables, all subphase list, done-when condition, tech decisions.

### Subphase doc
Created ONE AT A TIME, immediately before starting that subphase.
Path: `docs/phases/phase-N/subphase-N.M.md`
Contains: specific tasks, expected behaviour, test cases to write, done-when condition.
Do NOT pre-create all subphase docs — only the current one.

### Progress log
Running document updated continuously.
Path: `docs/progress.md`
Contains: checklist of phases/subphases, current status, blockers, notes.
Update it at: start of subphase, after tests written, after implementation, after PR merged.

### ADRs (Architecture Decision Records)
Path: `docs/adr/ADR-NNN-title.md`
Created when a significant technical decision is made or revisited.
Format: Context → Decision → Consequences → Alternatives considered.

### All docs are Markdown. No Word docs, no Notion, no notion exports.

---

## 6. Code Quality Standards

### SOLID Principles

- **Single Responsibility**: One Lambda handler does one thing. One module = one concern.
- **Open/Closed**: Use abstract base classes for data sources — add new sources without modifying existing ones.
- **Liskov Substitution**: Any data source implementation is interchangeable.
- **Interface Segregation**: Don't force modules to depend on interfaces they don't use.
- **Dependency Inversion**: Inject clients (S3, DynamoDB) — never instantiate them inside business logic.

### Pythonic practices

- Type hints on every function signature — no exceptions
- Pydantic models for all data shapes that cross a boundary (API response, Lambda event, S3 object)
- Dataclasses for internal value objects
- No global mutable state
- Use `pathlib.Path` not string concatenation for paths
- Use `logging` not `print` — structured JSON logs via `python-json-logger`
- Constants in `src/shared/constants.py` — never hardcode strings in business logic

### Design patterns in use

| Pattern | Where |
|---|---|
| Strategy | Data source collectors (CoinGecko, AlphaVantage, NewsAPI share an interface) |
| Repository | S3 and DynamoDB access abstracted behind repository classes |
| Factory | Chunker selects chunking strategy based on data type |
| Template Method | Bronze/Silver/Gold transformers share a base pipeline step |

### Code quality gates (must pass before every commit)

```bash
uv run ruff check .          # zero lint errors
uv run mypy src/             # zero type errors
uv run pytest                # all tests pass
```

Pre-commit hooks enforce this automatically. Never bypass them with `--no-verify`.

---

## 7. PR Walkthrough Document

After every subphase, before opening the PR, create:
Path: `docs/walkthroughs/walkthrough-phase-N.M.md`

### Required sections

```markdown
# Walkthrough: Phase N.M — Short Title

## What Was Done (2–3 sentences)
## Files Changed
| File | Type | Lines +/- | Purpose |
## How to Read This PR (ordered reading guide)
  - Start with: `path/to/file.py` → function `name()` — why this first
  - Then: `path/to/other.py` → class `ClassName` — what to look for
  - ...
## Key Code Sections (with actual code blocks and explanations)
  - Explain non-obvious patterns, AWS SDK usage, design decisions
  - Assume reader knows Python basics and FastAPI; explain anything deeper
## Test Coverage Summary
## What the App Can Do After This PR
```

The walkthrough must be thorough enough that someone can read the entire PR just by
following its reading guide — without needing to randomly browse files.

---

## 8. Security Rules

- **No secrets in code or committed files** — ever. Use SSM Parameter Store.
- **No hardcoded AWS account IDs, region names, or ARNs** — use Terraform variables and outputs.
- **IAM least privilege** — every Lambda role has only the permissions it needs. No `*` actions.
- **Input validation at every boundary** — Pydantic models validate all external input before it touches business logic.
- **Dependency pinning** — `uv.lock` is committed. No floating versions.
- **`.env` files are gitignored** — always. Use `.env.example` with placeholder values.

---

## 9. Project Tooling

| Tool | Purpose | Command |
|---|---|---|
| `uv` | Python package + env management | `uv sync`, `uv add <pkg>` |
| `ruff` | Linter + formatter | `uv run ruff check .` / `uv run ruff format .` |
| `mypy` | Static type checker | `uv run mypy src/` |
| `pytest` | Test runner | `uv run pytest` |
| `moto` | AWS service mocking for tests | Used in `conftest.py` fixtures |
| `terraform` | Infrastructure as code | `terraform plan`, `terraform apply` |
| `pre-commit` | Git hooks for quality gates | `pre-commit install`, runs on every commit |

### UV — the only package manager for this project

```bash
# Add a dependency
uv add boto3

# Add a dev dependency
uv add --dev pytest moto

# Run a command in the venv
uv run pytest

# Never use pip directly in this project
```

---

## 10. What "Done" Means

A subphase is done when ALL of the following are true:

- [ ] All tests pass (`uv run pytest`)
- [ ] Zero lint errors (`uv run ruff check .`)
- [ ] Zero type errors (`uv run mypy src/`)
- [ ] The "done when" condition in the subphase doc is demonstrably met
- [ ] Walkthrough doc is written
- [ ] PR is open with correct title format
- [ ] `docs/progress.md` is updated

A phase is done when ALL subphases are merged into `main`.

---

## 11. File to Read After This One

After reading `AGENTS.md`, proceed in this order:
1. `docs/architecture.md` — full system architecture
2. `docs/progress.md` — where are we right now?
3. `docs/phases/phase-N/phase-N-overview.md` — the current phase
4. `docs/phases/phase-N/subphase-N.M.md` — the current subphase
5. Start the TDD cycle

Do not start coding before reading all four documents above.
