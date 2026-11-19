# Subphase 1.1: Terraform Provider, Backend, and S3 Lakehouse Buckets

**Branch**: `phase-1.1-s3-buckets`  
**Parent Phase**: Phase 1 — Terraform Infrastructure  
**Status**: In Progress  

---

## 1. Goal & Specific Tasks

Provision the foundation of the AWS infrastructure and the core storage layer for the medallion lakehouse architecture.

### Specific Tasks:
1. **Root Terraform Configuration**:
   - `terraform/main.tf`: Define AWS provider with version constraints (`>= 5.0`), backend configuration, and default tags:
     - `Project = var.project_name`
     - `Environment = var.environment`
     - `ManagedBy = "terraform"`
   - `terraform/variables.tf`: Input variables (`aws_region`, `environment`, `project_name`).
   - `terraform/outputs.tf`: Re-export all bucket IDs, ARNs, and names.
   - `terraform/terraform.tfvars.example`: Example variable definitions.
2. **S3 Lakehouse Terraform Module (`terraform/modules/s3-lakehouse`)**:
   - Create 3 dedicated S3 buckets:
     - Bronze: `${var.project_name}-bronze-${var.environment}`
     - Silver: `${var.project_name}-silver-${var.environment}`
     - Gold: `${var.project_name}-gold-${var.environment}`
   - Attach mandatory security and lifecycle controls:
     - **Public Access Block**: Block all public ACLs, policies, and public access.
     - **Server-Side Encryption**: Enable AES256 (SSE-S3) encryption.
     - **Versioning**: Enable versioning to protect against accidental deletes and support time-travel.
     - **Lifecycle Management**:
       - Bronze: Expire current objects after 90 days; expire noncurrent versions after 30 days.
       - Silver: Expire noncurrent versions after 30 days.
       - Gold: Expire noncurrent versions after 30 days.
   - Outputs: Bucket IDs, ARNs, and names for Bronze, Silver, and Gold.
3. **Shared Python Constants & Configuration**:
   - `backend/src/shared/constants.py`: Define immutable constants for bucket tiers, key prefixes (`crypto/`, `stocks/`, `news/`, `quarantine/`), and date partitioning formats (`dt=YYYY-MM-DD`).
   - `backend/src/shared/config.py`: Pydantic settings model resolving bucket names and AWS configurations.
4. **Testing Suite (TDD)**:
   - `backend/tests/unit/test_s3_lakehouse.py`:
     - Test Python configuration and constants (validation, default values, prefix formats).
     - Test Moto-mocked S3 bucket operations enforcing bucket naming and tier behavior.
     - Test Terraform configuration validation (`terraform validate` and `terraform fmt`).

---

## 2. Expected Behaviour

- Root and module Terraform files adhere strictly to canonical formatting (`terraform fmt`).
- `terraform validate` executes cleanly without warnings or errors.
- All three buckets are fully private, encrypted, versioned, and have explicit lifecycle management.
- Python layer can import `constants.py` and `config.py` with full static type safety.
- Pytest suite runs green with code coverage >= 80%.

---

## 3. Test Cases to Write (TDD)

In `backend/tests/unit/test_s3_lakehouse.py`:
- `test_constants_prefixes_and_layers`: Verify layer names (`bronze`, `silver`, `gold`), prefixes, and formatting.
- `test_lakehouse_config_defaults`: Verify `LakehouseConfig` resolves default bucket names following the pattern `${project}-${layer}-${environment}`.
- `test_lakehouse_config_custom_override`: Verify custom environment variables correctly override bucket names.
- `test_moto_s3_bucket_structure`: Using `moto`, verify buckets can be created and queried, mimicking the Terraform layout.
- `test_terraform_syntax_and_validation`: Run `terraform fmt -check` and `terraform validate` within tests to catch syntax or configuration regressions.

---

## 4. Done When

- [ ] All unit tests in `backend/tests/unit/test_s3_lakehouse.py` pass.
- [ ] `uv run ruff check .` reports zero lint errors.
- [ ] `uv run mypy src/` reports zero type errors.
- [ ] `terraform -chdir=terraform init -backend=false` and `terraform -chdir=terraform validate` pass.
- [ ] Atomic commits executed per `AGENTS.md` (one file per commit).
- [ ] Subphase walkthrough doc written: `docs/walkthroughs/walkthrough-phase-1.1.md`.
- [ ] PR opened against `main` with title `[Phase 1.1] Terraform provider, backend, and S3 lakehouse buckets`.
- [ ] `docs/progress.md` updated.
