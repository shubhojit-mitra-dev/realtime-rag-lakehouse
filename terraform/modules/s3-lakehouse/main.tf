# ==============================================================================
# S3 Lakehouse Module — Bronze, Silver, Gold Storage Layers
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Bronze Bucket (Raw Landing Zone)
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
# 2. Silver Bucket (Cleansed & Conformed Layer)
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "silver" {
  bucket        = "${var.project_name}-silver-${var.environment}"
  force_destroy = var.environment == "dev" || var.environment == "test"

  tags = {
    Name  = "${var.project_name}-silver-${var.environment}"
    Layer = "silver"
  }
}

resource "aws_s3_bucket_public_access_block" "silver" {
  bucket = aws_s3_bucket.silver.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver" {
  bucket = aws_s3_bucket.silver.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "silver" {
  bucket = aws_s3_bucket.silver.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "silver" {
  depends_on = [aws_s3_bucket_versioning.silver]
  bucket     = aws_s3_bucket.silver.id

  rule {
    id     = "silver-versioning-lifecycle"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# ------------------------------------------------------------------------------
# 3. Gold Bucket (Business-Ready & RAG-Ready Layer)
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "gold" {
  bucket        = "${var.project_name}-gold-${var.environment}"
  force_destroy = var.environment == "dev" || var.environment == "test"

  tags = {
    Name  = "${var.project_name}-gold-${var.environment}"
    Layer = "gold"
  }
}

resource "aws_s3_bucket_public_access_block" "gold" {
  bucket = aws_s3_bucket.gold.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "gold" {
  bucket = aws_s3_bucket.gold.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "gold" {
  bucket = aws_s3_bucket.gold.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "gold" {
  depends_on = [aws_s3_bucket_versioning.gold]
  bucket     = aws_s3_bucket.gold.id

  rule {
    id     = "gold-versioning-lifecycle"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

