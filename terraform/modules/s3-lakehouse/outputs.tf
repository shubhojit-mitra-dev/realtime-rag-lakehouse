# ==============================================================================
# S3 Lakehouse Module — Outputs
# ==============================================================================

output "bronze_bucket_id" {
  description = "The ID of the Bronze layer S3 bucket"
  value       = aws_s3_bucket.bronze.id
}

output "bronze_bucket_arn" {
  description = "The ARN of the Bronze layer S3 bucket"
  value       = aws_s3_bucket.bronze.arn
}

output "bronze_bucket_name" {
  description = "The name of the Bronze layer S3 bucket"
  value       = aws_s3_bucket.bronze.bucket
}

output "silver_bucket_id" {
  description = "The ID of the Silver layer S3 bucket"
  value       = aws_s3_bucket.silver.id
}

output "silver_bucket_arn" {
  description = "The ARN of the Silver layer S3 bucket"
  value       = aws_s3_bucket.silver.arn
}

output "silver_bucket_name" {
  description = "The name of the Silver layer S3 bucket"
  value       = aws_s3_bucket.silver.bucket
}

output "gold_bucket_id" {
  description = "The ID of the Gold layer S3 bucket"
  value       = aws_s3_bucket.gold.id
}

output "gold_bucket_arn" {
  description = "The ARN of the Gold layer S3 bucket"
  value       = aws_s3_bucket.gold.arn
}

output "gold_bucket_name" {
  description = "The name of the Gold layer S3 bucket"
  value       = aws_s3_bucket.gold.bucket
}

