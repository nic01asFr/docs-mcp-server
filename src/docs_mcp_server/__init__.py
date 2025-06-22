"""
Docs MCP Server

Professional MCP server for DINUM Docs collaborative document platform.
Provides complete CRUD operations and advanced document management features.
"""

__version__ = "0.1.0"
__author__ = "Nicolas François"
__email__ = "nicolas.francois@example.com"

from .client import DocsAPIClient
from .config import DocsConfig
from .exceptions import DocsError, DocsAPIError, DocsAuthError
from .server import DocsServer

__all__ = [
    "DocsAPIClient",
    "DocsConfig", 
    "DocsError",
    "DocsAPIError", 
    "DocsAuthError",
    "DocsServer",
]
