"""Pytest configuration and fixtures."""
import os
import pytest
from unittest.mock import AsyncMock, Mock

from docs_mcp_server import DocsConfig, DocsAPIClient, DocsServer
from docs_mcp_server.models import User, Document


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = DocsConfig()
    config.base_url = "https://test.docs.example.com"
    config.token = "test-token-123"
    config.timeout = 30
    config.max_retries = 3
    return config


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id="user-123",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        date_joined="2024-01-01T00:00:00Z"
    )


@pytest.fixture
def mock_document():
    """Create a mock document for testing."""
    return Document(
        id="doc-123",
        title="Test Document",
        content="This is test content",
        creator_id="user-123",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        is_favorite=False,
        accesses=[]
    )


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.patch = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
async def mock_api_client(mock_config, mock_http_client):
    """Create a mock API client for testing."""
    client = DocsAPIClient(config=mock_config)
    client._http_client = mock_http_client
    return client


@pytest.fixture
def mock_server(mock_config):
    """Create a mock server for testing."""
    return DocsServer(config=mock_config, server_name="test-server")


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    env_vars = [
        "DOCS_BASE_URL",
        "DOCS_API_TOKEN", 
        "DOCS_TIMEOUT",
        "DOCS_MAX_RETRIES"
    ]
    
    # Store original values
    original_values = {}
    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]
