# Phase 1 Overview — Terraform Infrastructure

**Status**: Not Started
**Prerequisites**: Phase 0 complete (this doc exists because Phase 0 is done)

---

## Goal

All AWS infrastructure required by the full project is defined as Terraform code and
deployable with a single `terraform apply`. No resource is created via the AWS console.
Every Lambda function exists as a deployed (but mostly empty) stub — ready for implementation
in Phase 2 onwards.

After Phase 1, the AWS account has:
- 3 S3 buckets (Bronze, Silver, Gold) with lifecycle policies
- 1 S3 Vectors index (for RAG embeddings)
- 2 DynamoDB tables (pipeline state, chunk metadata)
- 7 Lambda functions (stubbed, logging "not yet implemented")
- 1 Step Functions Express state machine (wired to Lambda stubs)
- 1 EventBridge scheduled rule (disabled by default)
- SSM Parameter Store entries for all API keys
- IAM roles with least-privilege policies for every Lambda
- CloudWatch log groups for all Lambdas and the state machine
- 1 S3 event notification on the Gold bucket → Embedder Lambda

---

## Subphases

| Subphase | Title | Branch |
|---|---|---|
| 1.1 | Terraform provider, backend, and S3 lakehouse buckets | `phase-1.1-s3-buckets` |
| 1.2 | DynamoDB tables | `phase-1.2-dynamodb` |
| 1.3 | IAM roles and policies | `phase-1.3-iam` |
| 1.4 | SSM Parameter Store entries | `phase-1.4-ssm` |
| 1.5 | Lambda function stubs | `phase-1.5-lambda-stubs` |
| 1.6 | Step Functions state machine | `phase-1.6-step-functions` |
| 1.7 | EventBridge scheduled rule | `phase-1.7-eventbridge` |
| 1.8 | S3 event notification (Gold → Embedder) | `phase-1.8-s3-events` |
| 1.9 | CloudWatch alarms and monitoring | `phase-1.9-monitoring` |

---

## Deliverables

- `terraform/` directory is complete and passes `terraform validate`
- `terraform plan` shows zero errors
- `terraform apply` completes successfully against a real AWS account
- All resources visible in AWS console
- Each Lambda logs "Phase N not yet implemented" when invoked manually
- `docs/walkthroughs/walkthrough-phase-1.N.md` exists for every subphase

---

## Technical Decisions for Phase 1

### Terraform structure
```
terraform/
  main.tf           ← Provider config, backend config
  variables.tf      ← Input variables (region, project name, env)
  outputs.tf        ← Exported values (bucket ARNs, table names, etc.)
  modules/
    s3-lakehouse/   ← Bronze, Silver, Gold buckets
    s3-vectors/     ← S3 Vectors index
    dynamodb/       ← Pipeline state + chunk metadata tables
    lambda/         ← All 7 Lambda functions + IAM
    step-functions/ ← State machine definition
    eventbridge/    ← Scheduled rule
    ssm/            ← Parameter Store entries
    monitoring/     ← CloudWatch alarms
```

### Remote state backend
Terraform state is stored in a dedicated S3 bucket (created manually before first apply).
This prevents state from being committed to git.

### Lambda stub pattern
Every Lambda deployed in Phase 1 returns a standard stub response:
```python
def handler(event, context):
    import logging
    logging.info("Lambda stub: %s — not yet implemented", context.function_name)
    return {"statusCode": 200, "body": "stub"}
```
This validates that all IAM permissions, event sources, and networking are correct before
any real logic is written.

### Environment tagging
Every resource tagged with:
```
Project = "realtime-rag-lakehouse"
Environment = var.environment  # "dev" or "prod"
ManagedBy = "terraform"
```

---

## Done When

- [ ] `terraform validate` passes with zero errors
- [ ] `terraform apply` completes against AWS with zero errors
- [ ] All 9 subphase PRs are merged into main
- [ ] Every resource visible in AWS console with correct tags
- [ ] `docs/progress.md` Phase 1 section is fully checked

---

## What the App Cannot Do Yet

After Phase 1, the application has infrastructure but no logic. No data flows.
No RAG answers. That comes in Phases 2–4.
