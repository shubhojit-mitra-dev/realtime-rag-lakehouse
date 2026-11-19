"""Shared constants across data pipeline, lakehouse storage, and RAG components."""

from typing import Final

# Medallion lakehouse layer identifiers
LAKEHOUSE_LAYERS: Final[tuple[str, ...]] = ("bronze", "silver", "gold")

# Bronze layer ingestion prefixes (raw data sources)
BRONZE_PREFIX_CRYPTO: Final[str] = "crypto"
BRONZE_PREFIX_STOCKS: Final[str] = "stocks"
BRONZE_PREFIX_NEWS: Final[str] = "news"

BRONZE_PREFIXES: Final[tuple[str, ...]] = (
    BRONZE_PREFIX_CRYPTO,
    BRONZE_PREFIX_STOCKS,
    BRONZE_PREFIX_NEWS,
)

# Silver layer cleansed and conformed prefixes
SILVER_PREFIX_MARKET_TICKS: Final[str] = "market_ticks"
SILVER_PREFIX_NEWS_ARTICLES: Final[str] = "news_articles"
SILVER_PREFIX_QUARANTINE: Final[str] = "quarantine"

SILVER_PREFIXES: Final[tuple[str, ...]] = (
    SILVER_PREFIX_MARKET_TICKS,
    SILVER_PREFIX_NEWS_ARTICLES,
    SILVER_PREFIX_QUARANTINE,
)

# Gold layer pre-aggregated and business-ready prefixes
GOLD_PREFIX_HOURLY_SUMMARY: Final[str] = "hourly_summary"
GOLD_PREFIX_DAILY_SUMMARY: Final[str] = "daily_summary"
GOLD_PREFIX_ENRICHED_NEWS: Final[str] = "enriched_news"
GOLD_PREFIX_MARKET_SIGNALS: Final[str] = "market_signals"

GOLD_PREFIXES: Final[tuple[str, ...]] = (
    GOLD_PREFIX_HOURLY_SUMMARY,
    GOLD_PREFIX_DAILY_SUMMARY,
    GOLD_PREFIX_ENRICHED_NEWS,
    GOLD_PREFIX_MARKET_SIGNALS,
)

# Standard Hive-style date partitioning format for S3 object keys
DATE_PARTITION_FORMAT: Final[str] = "dt=%Y-%m-%d"

# Default configuration identifiers
DEFAULT_PROJECT_NAME: Final[str] = "realtime-rag-lakehouse"
DEFAULT_ENVIRONMENT: Final[str] = "dev"
DEFAULT_AWS_REGION: Final[str] = "us-east-1"
