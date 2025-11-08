"""Docs MCP Server - Professional integration for collaborative documentation."""

__version__ = "0.2.0"
__author__ = "Nicolas LAVAL"
__description__ = "Professional MCP Server for Docs - Complete API integration with 31 tools"

from .client import DocsAPIClient
from .config import DocsConfig, get_global_config
from .exceptions import DocsAPIError, DocsAuthError, DocsError, DocsNotFoundError
from .models import (
    AITransformResponse,
    AITranslateResponse,
    Document,
    DocumentAccess,
    DocumentListResponse,
    DocumentVersion,
    Invitation,
    User,
)
from .server import DocsServer

__all__ = [
    # Core classes
    "DocsServer",
    "DocsAPIClient",
    "DocsConfig",

    # Configuration
    "get_global_config",

    # Exceptions
    "DocsError",
    "DocsAPIError",
    "DocsAuthError",
    "DocsNotFoundError",

    # Models
    "Document",
    "DocumentListResponse",
    "User",
    "DocumentAccess",
    "Invitation",
    "DocumentVersion",
    "AITransformResponse",
    "AITranslateResponse",

    # Package info
    "__version__",
    "__author__",
    "__description__",
]


def create_server(
    base_url: str = None,
    token: str = None,
    server_name: str = "docs-mcp-server"
) -> DocsServer:
    """Create a DocsServer instance with simplified configuration.
    
    Args:
        base_url: Base URL of the Docs instance (optional if set in env)
        token: Authentication token (optional if set in env)
        server_name: Name of the MCP server
        
    Returns:
        Configured DocsServer instance
        
    Example:
        >>> server = create_server("https://docs.example.com", "your-token")
        >>> await server.run()
    """
    return DocsServer(
        base_url=base_url,
        token=token,
        server_name=server_name
    )


def create_client(
    base_url: str = None,
    token: str = None
) -> DocsAPIClient:
    """Create a DocsAPIClient instance with simplified configuration.
    
    Args:
        base_url: Base URL of the Docs instance (optional if set in env)
        token: Authentication token (optional if set in env)
        
    Returns:
        Configured DocsAPIClient instance
        
    Example:
        >>> async with create_client("https://docs.example.com", "your-token") as client:
        ...     documents = await client.list_documents()
    """
    config = None
    if base_url or token:
        import os
        if base_url:
            os.environ["DOCS_BASE_URL"] = base_url
        if token:
            os.environ["DOCS_API_TOKEN"] = token
        config = DocsConfig()

    return DocsAPIClient(config=config)
