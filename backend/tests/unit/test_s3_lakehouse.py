"""Unit tests for S3 Lakehouse configuration, constants, and bucket structure."""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import boto3
import pytest
from moto import mock_aws

from src.shared.config import LakehouseConfig
from src.shared.constants import (
    BRONZE_PREFIXES,
    DATE_PARTITION_FORMAT,
    GOLD_PREFIXES,
    LAKEHOUSE_LAYERS,
    SILVER_PREFIXES,
)


class TestLakehouseConstants:
    """Verify system constants defining the medallion lakehouse architecture."""

    def test_layer_definitions(self) -> None:
        """Verify the three medallion layers are defined in correct order."""
        assert LAKEHOUSE_LAYERS == ("bronze", "silver", "gold")

    def test_bronze_prefixes(self) -> None:
        """Verify Bronze layer prefixes for raw data sources."""
        assert "crypto" in BRONZE_PREFIXES
        assert "stocks" in BRONZE_PREFIXES
        assert "news" in BRONZE_PREFIXES

    def test_silver_prefixes(self) -> None:
        """Verify Silver layer prefixes for cleansed/conformed data and quarantine."""
        assert "market_ticks" in SILVER_PREFIXES
        assert "news_articles" in SILVER_PREFIXES
        assert "quarantine" in SILVER_PREFIXES

    def test_gold_prefixes(self) -> None:
        """Verify Gold layer prefixes for business-ready tables."""
        assert "hourly_summary" in GOLD_PREFIXES
        assert "daily_summary" in GOLD_PREFIXES
        assert "enriched_news" in GOLD_PREFIXES
        assert "market_signals" in GOLD_PREFIXES

    def test_date_partition_format(self) -> None:
        """Verify the standard Hive-style date partitioning format."""
        assert DATE_PARTITION_FORMAT == "dt=%Y-%m-%d"


class TestLakehouseConfig:
    """Verify configuration loading and bucket name resolution."""

    def test_default_config(self) -> None:
        """Test default config generates standard bucket names."""
        with patch.dict(os.environ, {}, clear=True):
            config = LakehouseConfig()
            assert config.project_name == "realtime-rag-lakehouse"
            assert config.environment == "dev"
            assert config.aws_region == "us-east-1"
            assert config.bronze_bucket == "realtime-rag-lakehouse-bronze-dev"
            assert config.silver_bucket == "realtime-rag-lakehouse-silver-dev"
            assert config.gold_bucket == "realtime-rag-lakehouse-gold-dev"

    def test_custom_environment_and_project(self) -> None:
        """Test config with custom project and environment names."""
        with patch.dict(
            os.environ,
            {
                "LAKEHOUSE_PROJECT_NAME": "custom-lakehouse",
                "LAKEHOUSE_ENVIRONMENT": "prod",
                "AWS_REGION": "us-west-2",
            },
            clear=True,
        ):
            config = LakehouseConfig()
            assert config.project_name == "custom-lakehouse"
            assert config.environment == "prod"
            assert config.aws_region == "us-west-2"
            assert config.bronze_bucket == "custom-lakehouse-bronze-prod"
            assert config.silver_bucket == "custom-lakehouse-silver-prod"
            assert config.gold_bucket == "custom-lakehouse-gold-prod"

    def test_explicit_bucket_override(self) -> None:
        """Test explicit override of individual bucket names."""
        with patch.dict(
            os.environ,
            {
                "BRONZE_BUCKET": "my-custom-bronze-bucket",
                "SILVER_BUCKET": "my-custom-silver-bucket",
                "GOLD_BUCKET": "my-custom-gold-bucket",
            },
            clear=True,
        ):
            config = LakehouseConfig()
            assert config.bronze_bucket == "my-custom-bronze-bucket"
            assert config.silver_bucket == "my-custom-silver-bucket"
            assert config.gold_bucket == "my-custom-gold-bucket"

    def test_invalid_environment_raises(self) -> None:
        """Test that invalid environment value fails validation."""
        with pytest.raises(ValueError):
            LakehouseConfig(environment="invalid_env")


class TestMotoS3Lakehouse:
    """Verify S3 operations against Moto mocked AWS environment."""

    @mock_aws
    def test_lakehouse_bucket_lifecycle(self) -> None:
        """Test creating lakehouse buckets and writing/reading objects."""
        s3 = boto3.client("s3", region_name="us-east-1")
        config = LakehouseConfig()

        # Create all three buckets
        for bucket_name in (config.bronze_bucket, config.silver_bucket, config.gold_bucket):
            s3.create_bucket(Bucket=bucket_name)

        # Verify buckets exist
        response = s3.list_buckets()
        bucket_names = [b["Name"] for b in response["Buckets"]]
        assert config.bronze_bucket in bucket_names
        assert config.silver_bucket in bucket_names
        assert config.gold_bucket in bucket_names

        # Write test Bronze payload
        test_key = "crypto/dt=2026-11-19/test_tick.json"
        test_payload = b'{"ticker": "BTC", "price": 43250.75}'
        s3.put_object(Bucket=config.bronze_bucket, Key=test_key, Body=test_payload)

        # Read back and verify
        obj = s3.get_object(Bucket=config.bronze_bucket, Key=test_key)
        assert obj["Body"].read() == test_payload


class TestTerraformLakehouseSyntax:
    """Verify Terraform configuration files are syntactically valid."""

    def test_terraform_files_exist(self) -> None:
        """Verify all expected Terraform files and modules exist."""
        project_root = Path(__file__).resolve().parents[3]
        tf_root = project_root / "terraform"
        s3_module = tf_root / "modules" / "s3-lakehouse"

        assert (tf_root / "main.tf").exists(), "terraform/main.tf must exist"
        assert (tf_root / "variables.tf").exists(), "terraform/variables.tf must exist"
        assert (tf_root / "outputs.tf").exists(), "terraform/outputs.tf must exist"
        assert (s3_module / "main.tf").exists(), "s3-lakehouse/main.tf must exist"
        assert (s3_module / "variables.tf").exists(), "s3-lakehouse/variables.tf must exist"
        assert (s3_module / "outputs.tf").exists(), "s3-lakehouse/outputs.tf must exist"

    def test_terraform_validate(self) -> None:
        """Verify terraform validate passes with zero errors."""
        project_root = Path(__file__).resolve().parents[3]
        tf_root = project_root / "terraform"

        # Initialize without remote backend
        init_cmd = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=tf_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert init_cmd.returncode == 0, f"terraform init failed: {init_cmd.stderr}"

        # Validate
        validate_cmd = subprocess.run(
            ["terraform", "validate"],
            cwd=tf_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert validate_cmd.returncode == 0, f"terraform validate failed: {validate_cmd.stderr}"

    def test_terraform_fmt_check(self) -> None:
        """Verify terraform files follow canonical formatting."""
        project_root = Path(__file__).resolve().parents[3]
        tf_root = project_root / "terraform"

        fmt_cmd = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive"],
            cwd=tf_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert fmt_cmd.returncode == 0, f"terraform fmt check failed: {fmt_cmd.stdout}"
