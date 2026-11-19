variable "project_name" {
  description = "Project name identifier used in resource naming and tags"
  type        = string
  default     = "realtime-rag-lakehouse"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "bronze_retention_days" {
  description = "Number of days before expiring raw data objects in the Bronze bucket"
  type        = number
  default     = 90
}

variable "noncurrent_version_expiration_days" {
  description = "Number of days before permanently deleting older noncurrent object versions"
  type        = number
  default     = 30
}

