# ADR-002: Step Functions Express over S3 Event Chains

**Date**: 2026-11-19
**Status**: Accepted

---

## Context

The medallion pipeline has four sequential steps:
1. Collect from APIs → Bronze S3
2. Bronze → Silver (validation, cleaning)
3. Silver → Gold (aggregation, enrichment)
4. Gold → S3 Vectors (embedding)

These steps need to be orchestrated: each step must complete before the next starts,
failures must be retried, and execution history must be observable.

Two options were considered: S3 event chains and AWS Step Functions.

---

## Decision

Use **AWS Step Functions Express Workflows** as the pipeline orchestrator.

---

## Consequences

**Positive:**
- **Visual execution graph** in the AWS Console — every step shows ✅ or ❌ in real time.
  This is a demo superpower: open the console during a presentation and walk through a live execution.
- **Declarative retries**: each step can have independent retry configuration (max attempts,
  backoff rate, interval). No retry logic scattered across individual Lambda functions.
- **Single observability surface**: one execution history entry shows all four steps, their
  inputs, outputs, and durations. With S3 events you'd chase four separate CloudWatch log streams.
- **Conditional branching**: can add quality gates (skip embedding if Silver validation failure
  rate exceeds threshold) without restructuring Lambda code.
- **Cost**: ~$0.009/month at every-5-minute ingestion frequency. Effectively free.
- **Strong resume keyword**: "AWS Step Functions" is a recognized enterprise orchestration tool.

**Negative:**
- Slight added latency per state transition (~10–50ms overhead)
- State machine definition (Amazon States Language JSON) has a learning curve
- Express Workflows have a 5-minute execution limit (more than sufficient for our pipeline)

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| S3 event notifications chaining | No central failure visibility; debugging requires chasing 4+ separate CloudWatch streams; retry logic duplicated in each Lambda; no visual execution graph |
| AWS SQS between each step | Adds message queue management; no built-in execution history; more infrastructure to define and monitor |
| Airflow (MWAA) | Always-on compute (minimum $50/month); overkill for a 4-step pipeline; violates cost constraint |
| Step Functions Standard | Charges per state transition ($0.025/1000); Express is better for high-frequency short-duration workflows |
