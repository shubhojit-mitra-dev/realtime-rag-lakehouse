# ==============================================================================
# Root Terraform Configuration — realtime-rag-lakehouse
# ==============================================================================

terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state configuration. When deploying in CI/CD, backend-config parameters
  # are supplied dynamically (see .github/workflows/deploy.yml).
  # For local development without remote state, comment this block or use local backend.
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# ------------------------------------------------------------------------------
# S3 Lakehouse Module (Bronze, Silver, Gold Layers)
# ------------------------------------------------------------------------------
module "s3_lakehouse" {
  source = "./modules/s3-lakehouse"

  project_name                       = var.project_name
  environment                        = var.environment
  bronze_retention_days              = var.bronze_retention_days
  noncurrent_version_expiration_days = var.noncurrent_version_expiration_days
}
