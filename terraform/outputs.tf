# ==============================================================================
# Root Terraform Outputs — Lakehouse S3 Resources
# ==============================================================================

output "bronze_bucket_id" {
  description = "The ID of the Bronze layer S3 bucket"
  value       = module.s3_lakehouse.bronze_bucket_id
}

output "bronze_bucket_arn" {
  description = "The ARN of the Bronze layer S3 bucket"
  value       = module.s3_lakehouse.bronze_bucket_arn
}

output "bronze_bucket_name" {
  description = "The name of the Bronze layer S3 bucket"
  value       = module.s3_lakehouse.bronze_bucket_name
}

output "silver_bucket_id" {
  description = "The ID of the Silver layer S3 bucket"
  value       = module.s3_lakehouse.silver_bucket_id
}

output "silver_bucket_arn" {
  description = "The ARN of the Silver layer S3 bucket"
  value       = module.s3_lakehouse.silver_bucket_arn
}

output "silver_bucket_name" {
  description = "The name of the Silver layer S3 bucket"
  value       = module.s3_lakehouse.silver_bucket_name
}

output "gold_bucket_id" {
  description = "The ID of the Gold layer S3 bucket"
  value       = module.s3_lakehouse.gold_bucket_id
}

output "gold_bucket_arn" {
  description = "The ARN of the Gold layer S3 bucket"
  value       = module.s3_lakehouse.gold_bucket_arn
}

output "gold_bucket_name" {
  description = "The name of the Gold layer S3 bucket"
  value       = module.s3_lakehouse.gold_bucket_name
}

