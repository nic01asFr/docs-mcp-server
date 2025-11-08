"""Pytest configuration and fixtures."""
import os
import pytest
from unittest.mock import AsyncMock, Mock

from docs_mcp_server import DocsConfig, DocsAPIClient, DocsServer
from docs_mcp_server.models import User, Document


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables for all tests."""
    # Store original values
    original_base_url = os.environ.get("DOCS_BASE_URL")
    original_token = os.environ.get("DOCS_API_TOKEN")

    # Set test values
    os.environ["DOCS_BASE_URL"] = "https://test.docs.example.com"
    os.environ["DOCS_API_TOKEN"] = "test-token-123456"

    yield

    # Restore original values
    if original_base_url:
        os.environ["DOCS_BASE_URL"] = original_base_url
    else:
        os.environ.pop("DOCS_BASE_URL", None)

    if original_token:
        os.environ["DOCS_API_TOKEN"] = original_token
    else:
        os.environ.pop("DOCS_API_TOKEN", None)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    # Create config with explicit values to avoid env file issues
    config = DocsConfig(
        base_url="https://test.docs.example.com",
        api_token="test-token-123456",
        _env_file=None  # Disable env file loading for tests
    )
    return config


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="test@example.com",
        full_name="Test User",
        short_name="TU"
    )


@pytest.fixture
def mock_document():
    """Create a mock document for testing."""
    return Document(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Test Document",
        content="This is test content",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T01:00:00Z",
        depth=0,
        path="/test-document",
        is_favorite=False,
        nb_accesses_ancestors=0,
        nb_accesses_direct=1,
        numchild=0,
        user_roles=["owner"]
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
