"""Centralized configuration management for realtime-rag-lakehouse."""

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from src.shared.constants import (
    DEFAULT_AWS_REGION,
    DEFAULT_ENVIRONMENT,
    DEFAULT_PROJECT_NAME,
)

EnvironmentType = Literal["dev", "staging", "prod", "test"]


class LakehouseConfig(BaseModel):
    """Configuration model for AWS Lakehouse resources and runtime settings."""

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

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Ensure environment matches allowed environments."""
        valid_envs = ("dev", "staging", "prod", "test")
        if v not in valid_envs:
            raise ValueError(f"Invalid environment '{v}'. Must be one of {valid_envs}")
        return v

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Ensure project name is non-empty and conforms to standard identifiers."""
        if not v or not v.strip():
            raise ValueError("project_name must not be empty")
        return v.strip().lower()

    @model_validator(mode="after")
    def populate_default_bucket_names(self) -> "LakehouseConfig":
        """Compute default bucket names if not explicitly supplied."""
        if not self.bronze_bucket:
            self.bronze_bucket = f"{self.project_name}-bronze-{self.environment}"
        if not self.silver_bucket:
            self.silver_bucket = f"{self.project_name}-silver-{self.environment}"
        if not self.gold_bucket:
            self.gold_bucket = f"{self.project_name}-gold-{self.environment}"
        return self
