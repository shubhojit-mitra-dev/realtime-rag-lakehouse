# ADR-003: Terraform over Serverless Framework

**Date**: 2026-11-19
**Status**: Accepted

---

## Context

All AWS infrastructure needs to be defined as code, version-controlled, and deployable
reproducibly. Two primary tools were considered: the Serverless Framework and Terraform.

---

## Decision

Use **Terraform** as the infrastructure-as-code tool for all AWS resources.

---

## Consequences

**Positive:**
- **Universal skill**: Terraform is the most widely recognized IaC tool across the industry.
  It appears in job descriptions for cloud engineering, DevOps, platform engineering, and
  data engineering roles. Serverless Framework is primarily known in the serverless niche.
- **Full AWS resource coverage**: Terraform can provision any AWS resource — VPCs, RDS,
  EKS, IAM, Step Functions, S3 Vectors — not just Lambda and API Gateway.
- **State management**: Terraform tracks resource state explicitly, making drift detection
  and incremental changes safe and predictable.
- **Plan before apply**: `terraform plan` shows exactly what will change before anything
  is modified. No surprises.
- **Modular design**: Terraform modules allow clean separation of concerns (one module per
  AWS service group) that maps directly to the system architecture.
- **Multi-cloud transferability**: the mental model and HCL syntax transfers to GCP, Azure,
  and Kubernetes (via Terraform providers).

**Negative:**
- More verbose than Serverless Framework for Lambda-specific resources
- Requires explicit IAM policy writing (Serverless Framework auto-generates basic policies)
- Learning curve for HCL syntax (mitigated by good module structure)

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| Serverless Framework | Primarily a Lambda deploy tool. Limited resource coverage. Niche skill in job market. Abstracts away IAM which is a learning gap. |
| AWS CDK (Python) | Python-based IaC is appealing, but CDK synthesizes to CloudFormation which is slower and harder to debug than Terraform's direct API calls. CDK is also primarily an AWS-only skill. |
| AWS SAM | Transform layer on CloudFormation. Limited to serverless resources. Same issues as Serverless Framework. |
| CloudFormation | Verbose YAML/JSON, slow deployments, poor developer experience compared to Terraform. |
| Pulumi | Compelling but smaller ecosystem and community than Terraform. Less likely to appear on job descriptions. |
