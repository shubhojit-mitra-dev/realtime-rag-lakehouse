"""
Root test configuration for realtime-rag-lakehouse.

This conftest.py sets up shared fixtures available to all tests.
AWS services are mocked with moto — no real AWS credentials required.

Fixture categories:
  - AWS resource setup (S3 buckets, DynamoDB tables)
  - Realistic sample data matching production schemas
  - Shared environment variable patching

Adding a new fixture: add it here if used across multiple test modules,
otherwise define it in the specific test file's local conftest.py.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def aws_credentials() -> None:
    """
    Patch AWS credentials for every test so moto intercepts all boto3 calls.

    moto works by intercepting boto3/botocore HTTP calls and returning mocked
    responses. It requires that the environment looks like it has credentials —
    the actual values are ignored, but their presence is checked by botocore.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
