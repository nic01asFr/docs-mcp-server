"""Tests for configuration management."""
import os
import pytest

from docs_mcp_server.config import DocsConfig
from docs_mcp_server.exceptions import DocsError


def test_config_from_env():
    """Test configuration loading from environment variables."""
    os.environ["DOCS_BASE_URL"] = "https://docs.example.com"
    os.environ["DOCS_API_TOKEN"] = "test-token"
    os.environ["DOCS_TIMEOUT"] = "60"
    os.environ["DOCS_MAX_RETRIES"] = "5"
    
    config = DocsConfig()
    
    assert config.base_url == "https://docs.example.com"
    assert config.token == "test-token"
    assert config.timeout == 60
    assert config.max_retries == 5


def test_config_missing_required():
    """Test configuration with missing required variables."""
    with pytest.raises(DocsError, match="DOCS_BASE_URL environment variable is required"):
        DocsConfig()


def test_config_invalid_timeout():
    """Test configuration with invalid timeout."""
    os.environ["DOCS_BASE_URL"] = "https://docs.example.com"
    os.environ["DOCS_API_TOKEN"] = "test-token"
    os.environ["DOCS_TIMEOUT"] = "invalid"
    
    with pytest.raises(DocsError, match="Invalid DOCS_TIMEOUT value"):
        DocsConfig()


def test_config_default_values():
    """Test configuration with default values."""
    os.environ["DOCS_BASE_URL"] = "https://docs.example.com"
    os.environ["DOCS_API_TOKEN"] = "test-token"
    
    config = DocsConfig()
    
    assert config.timeout == 30  # default
    assert config.max_retries == 3  # default


def test_config_url_normalization():
    """Test URL normalization in configuration."""
    os.environ["DOCS_BASE_URL"] = "https://docs.example.com/"
    os.environ["DOCS_API_TOKEN"] = "test-token"
    
    config = DocsConfig()
    
    assert config.base_url == "https://docs.example.com"  # trailing slash removed
