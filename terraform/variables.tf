# ==============================================================================
# Root Terraform Variables
# ==============================================================================

variable "aws_region" {
  description = "AWS region for provisioning infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Target deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Base project name used in resource naming and default tags"
  type        = string
  default     = "realtime-rag-lakehouse"
}

variable "bronze_retention_days" {
  description = "Retention period in days for raw data in the Bronze bucket"
  type        = number
  default     = 90
}

variable "noncurrent_version_expiration_days" {
  description = "Retention period in days for noncurrent object versions in all lakehouse buckets"
  type        = number
  default     = 30
}

