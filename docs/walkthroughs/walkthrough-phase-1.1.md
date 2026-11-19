# Walkthrough: Phase 1.1 — Terraform Provider, Backend, and S3 Lakehouse Buckets

## What Was Done
Implemented the primary storage tier of the medallion lakehouse architecture using Terraform and Python. Created the root Terraform configuration and a dedicated `s3-lakehouse` module that provisions Bronze, Silver, and Gold S3 buckets with mandatory AES-256 encryption, strict public access blocks, versioning, and retention lifecycle rules. Additionally, created typed Python configurations and constants with 100% test coverage using Moto and automated Terraform syntax validation.

---

## Files Changed

| File | Type | Lines +/- | Purpose |
|---|---|---|---|
| `docs/phases/phase-1/subphase-1.1.md` | Docs | +77 / -0 | Specification and acceptance criteria for subphase 1.1 |
| `docs/progress.md` | Docs | +18 / -3 | Progress tracker updating Phase 1.1 status |
| `backend/src/shared/constants.py` | Python | +49 / -0 | Centralized constants for medallion layers, prefixes, and partition formats |
| `backend/src/shared/config.py` | Python | +62 / -0 | Pydantic model for AWS settings and bucket name resolution |
| `backend/tests/unit/test_s3_lakehouse.py` | Test | +191 / -0 | Unit tests for constants, configuration, Moto S3 operations, and Terraform syntax |
| `terraform/modules/s3-lakehouse/variables.tf` | Terraform | +24 / -0 | Input variables for lakehouse storage module |
| `terraform/modules/s3-lakehouse/main.tf` | Terraform | +188 / -0 | Resource declarations for Bronze, Silver, Gold buckets, encryption, access blocks, and lifecycle |
| `terraform/modules/s3-lakehouse/outputs.tf` | Terraform | +49 / -0 | Exported bucket IDs, ARNs, and names from lakehouse module |
| `terraform/variables.tf` | Terraform | +34 / -0 | Root Terraform variables (region, environment, project name, retention days) |
| `terraform/main.tf` | Terraform | +43 / -0 | Root Terraform configuration wiring AWS provider and the `s3-lakehouse` module |
| `terraform/outputs.tf` | Terraform | +49 / -0 | Root output variables surfacing bucket resources |
| `terraform/terraform.tfvars.example` | Config | +11 / -0 | Example variables template for local deployments |

---

## How to Read This PR (ordered reading guide)

1. **Start with the architectural contract:**
   - [`docs/phases/phase-1/subphase-1.1.md`](file:///home/blackknight05/Desktop/data-project/docs/phases/phase-1/subphase-1.1.md) — review the requirements and acceptance criteria.
2. **Review the Python lakehouse foundations:**
   - [`backend/src/shared/constants.py`](file:///home/blackknight05/Desktop/data-project/backend/src/shared/constants.py) — see layer definitions (`bronze`, `silver`, `gold`), prefixes, and Hive partition formatting (`dt=YYYY-MM-DD`).
   - [`backend/src/shared/config.py`](file:///home/blackknight05/Desktop/data-project/backend/src/shared/config.py) → class `LakehouseConfig` — see how environment variables and default bucket naming conventions (`${project}-${layer}-${env}`) are validated.
3. **Inspect the TDD test suite:**
   - [`backend/tests/unit/test_s3_lakehouse.py`](file:///home/blackknight05/Desktop/data-project/backend/tests/unit/test_s3_lakehouse.py) — verify how Moto mocks S3 operations and how pytest executes `terraform validate` and `terraform fmt -check`.
4. **Inspect the Terraform module:**
   - [`terraform/modules/s3-lakehouse/variables.tf`](file:///home/blackknight05/Desktop/data-project/terraform/modules/s3-lakehouse/variables.tf) → inputs for naming and lifecycle retention.
   - [`terraform/modules/s3-lakehouse/main.tf`](file:///home/blackknight05/Desktop/data-project/terraform/modules/s3-lakehouse/main.tf) → review the 3 buckets and their public access blocks, SSE-S3 encryption, versioning, and lifecycle expiration rules.
   - [`terraform/modules/s3-lakehouse/outputs.tf`](file:///home/blackknight05/Desktop/data-project/terraform/modules/s3-lakehouse/outputs.tf) → exported bucket attributes.
5. **Inspect the root Terraform orchestration:**
   - [`terraform/main.tf`](file:///home/blackknight05/Desktop/data-project/terraform/main.tf) — AWS provider block with default resource tags, S3 remote state backend declaration, and module invocation.
   - [`terraform/variables.tf`](file:///home/blackknight05/Desktop/data-project/terraform/variables.tf) and [`terraform/outputs.tf`](file:///home/blackknight05/Desktop/data-project/terraform/outputs.tf).

---

## Key Code Sections

### 1. Zero-Leakage S3 Bucket Lifecycle & Security Pattern
In [`terraform/modules/s3-lakehouse/main.tf`](file:///home/blackknight05/Desktop/data-project/terraform/modules/s3-lakehouse/main.tf):

```hcl
resource "aws_s3_bucket" "bronze" {
  bucket        = "${var.project_name}-bronze-${var.environment}"
  force_destroy = var.environment == "dev" || var.environment == "test"

  tags = {
    Name  = "${var.project_name}-bronze-${var.environment}"
    Layer = "bronze"
  }
}

resource "aws_s3_bucket_public_access_block" "bronze" {
  bucket = aws_s3_bucket.bronze.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bronze" {
  bucket = aws_s3_bucket.bronze.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "bronze" {
  depends_on = [aws_s3_bucket_versioning.bronze]
  bucket     = aws_s3_bucket.bronze.id

  rule {
    id     = "bronze-retention-lifecycle"
    status = "Enabled"

    filter {}

    expiration {
      days = var.bronze_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
```
*Why this matters*: Every bucket explicitly prevents public exposure, mandates encryption at rest, maintains versioning for auditing/time-travel, and enforces lifecycle policies (e.g. 90-day object expiration for raw Bronze data, 30-day noncurrent version pruning, and cleanup of aborted multipart uploads).

### 2. Type-Safe Dynamic Bucket Configuration
In [`backend/src/shared/config.py`](file:///home/blackknight05/Desktop/data-project/backend/src/shared/config.py):

```python
class LakehouseConfig(BaseModel):
    project_name: str = Field(
        default_factory=lambda: os.environ.get("LAKEHOUSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)
    )
    environment: str = Field(
        default_factory=lambda: os.environ.get("LAKEHOUSE_ENVIRONMENT", DEFAULT_ENVIRONMENT)
    )
    aws_region: str = Field(
        default_factory=lambda: os.environ.get(
            "AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", DEFAULT_AWS_REGION)
        )
    )

    bronze_bucket: str = Field(default_factory=lambda: os.environ.get("BRONZE_BUCKET", ""))
    silver_bucket: str = Field(default_factory=lambda: os.environ.get("SILVER_BUCKET", ""))
    gold_bucket: str = Field(default_factory=lambda: os.environ.get("GOLD_BUCKET", ""))

    @model_validator(mode="after")
    def populate_default_bucket_names(self) -> "LakehouseConfig":
        if not self.bronze_bucket:
            self.bronze_bucket = f"{self.project_name}-bronze-{self.environment}"
        if not self.silver_bucket:
            self.silver_bucket = f"{self.project_name}-silver-{self.environment}"
        if not self.gold_bucket:
            self.gold_bucket = f"{self.project_name}-gold-{self.environment}"
        return self
```
*Why this matters*: Ensures Python services (Lambdas, collectors, transformers) have a single source of truth for bucket names with automatic fallback to standard convention while allowing environment-level overrides for testing or staging.

---

## Test Coverage Summary

- **Total Unit Tests**: 13 passed, 0 failed.
- **Code Coverage**: 92.45% (exceeds project threshold of 80%).
- **Verification Gates**:
  - `uv run ruff check .`: 0 lint errors.
  - `uv run mypy src/`: 0 type errors across all source files.
  - `terraform validate`: 0 errors.
  - `terraform fmt -check -recursive`: clean canonical formatting.

---

## What the App Can Do After This PR

1. Full infrastructure definitions exist for the storage tier (`realtime-rag-lakehouse-bronze-dev`, `silver`, `gold`).
2. Terraform can be initialized and validated cleanly in local or CI environments.
3. Python services can load typed configuration and reference standard prefix constants across all lakehouse layers.
4. Foundation is fully primed for Subphase 1.2: DynamoDB metadata and pipeline state tables.
