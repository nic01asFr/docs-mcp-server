"""Configuration management for the Docs MCP Server."""

from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DocsConfig(BaseSettings):
    """Configuration for the Docs MCP Server."""

    # API Configuration
    base_url: HttpUrl = Field(
        ...,
        env="DOCS_BASE_URL",
        description="Base URL of the Docs instance (e.g., https://docs.example.gouv.fr)",
    )

    api_token: str = Field(
        ...,
        env="DOCS_API_TOKEN",
        description="Authentication token for the Docs API",
    )

    api_version: str = Field(
        default="v1.0",
        env="DOCS_API_VERSION",
        description="API version to use",
    )

    # Request Configuration
    timeout: int = Field(
        default=30,
        env="DOCS_TIMEOUT",
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    max_retries: int = Field(
        default=3,
        env="DOCS_MAX_RETRIES",
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    rate_limit: float = Field(
        default=10.0,
        env="DOCS_RATE_LIMIT",
        ge=0.1,
        le=100.0,
        description="Maximum requests per second",
    )

    # MCP Configuration
    server_name: str = Field(
        default="docs-mcp-server",
        env="DOCS_MCP_SERVER_NAME",
        description="Name of the MCP server",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level",
    )

    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log message format",
    )

    # Development/Debug
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode",
    )

    # Cache Configuration
    cache_enabled: bool = Field(
        default=True,
        env="DOCS_CACHE_ENABLED",
        description="Enable response caching",
    )

    cache_ttl: int = Field(
        default=300,  # 5 minutes
        env="DOCS_CACHE_TTL",
        ge=0,
        description="Cache time-to-live in seconds",
    )

    @field_validator("base_url", mode="after")
    @classmethod
    def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure base_url doesn't end with a slash."""
        url_str = str(v)
        if url_str.endswith("/"):
            url_str = url_str.rstrip("/")
            return HttpUrl(url_str)
        return v

    @field_validator("api_token", mode="after")
    @classmethod
    def validate_api_token(cls, v: str) -> str:
        """Validate API token format."""
        if not v or len(v) < 10:
            raise ValueError("API token must be at least 10 characters long")
        return v.strip()

    @property
    def api_base_url(self) -> str:
        """Get the full API base URL."""
        # Remove trailing slash from base_url if present
        base = str(self.base_url).rstrip("/")
        return f"{base}/api/{self.api_version}"

    @property
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": f"{self.server_name}/0.1.0",
        }

    model_config = SettingsConfigDict(
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
        env_prefix="",  # No prefix for environment variables
    )


def get_config() -> DocsConfig:
    """Get the current configuration instance."""
    return DocsConfig()


def load_config_from_file(config_path: Path) -> DocsConfig:
    """Load configuration from a specific file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load configuration from the specified file
    from dotenv import load_dotenv

    # Load the dotenv file
    load_dotenv(config_path)

    config = DocsConfig()

    return config


def create_example_config(output_path: Path) -> None:
    """Create an example configuration file."""
    example_content = '''# Docs MCP Server Configuration
# Copy this file to .env and fill in your values

# Required: Docs instance configuration
DOCS_BASE_URL=https://your-docs-instance.gouv.fr
DOCS_API_TOKEN=your_api_token_here

# Optional: API settings
DOCS_API_VERSION=v1.0
DOCS_TIMEOUT=30
DOCS_MAX_RETRIES=3
DOCS_RATE_LIMIT=10.0

# Optional: MCP server settings
DOCS_MCP_SERVER_NAME=docs-mcp-server

# Optional: Logging
LOG_LEVEL=INFO
DEBUG=false

# Optional: Caching
DOCS_CACHE_ENABLED=true
DOCS_CACHE_TTL=300
'''

    output_path.write_text(example_content, encoding="utf-8")


# Global configuration instance
_config: DocsConfig | None = None


def get_global_config() -> DocsConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = get_config()
    return _config


def set_global_config(config: DocsConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
