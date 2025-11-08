"""Professional MCP Server for Docs."""
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

from .client import DocsAPIClient
from .config import DocsConfig
from .exceptions import DocsError

logger = logging.getLogger(__name__)


# Global config for use in handlers
_global_config: DocsConfig | None = None


def create_server(
    base_url: str | None = None,
    token: str | None = None,
    config: DocsConfig | None = None,
    server_name: str = "docs-mcp-server",
) -> Server:
    """Create and configure MCP server for Docs.
    
    Args:
        base_url: Base URL of the Docs instance
        token: Authentication token
        config: Configuration object
        server_name: Name of the MCP server
        
    Returns:
        Configured MCP Server instance
    """
    global _global_config

    # Setup configuration
    import sys
    try:
        if config:
            _global_config = config
        elif base_url or token:
            import os
            if base_url:
                os.environ["DOCS_BASE_URL"] = base_url
            if token:
                os.environ["DOCS_API_TOKEN"] = token
            _global_config = DocsConfig()
        else:
            _global_config = DocsConfig()
    except Exception as e:
        # Send error to stderr, not stdout (to avoid breaking MCP protocol)
        print(f"ERROR: Failed to load configuration: {e}", file=sys.stderr)
        print("Please set DOCS_BASE_URL and DOCS_API_TOKEN environment variables", file=sys.stderr)
        sys.exit(1)

    # Initialize MCP server
    server = Server(server_name)

    # Register tools handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available MCP tools."""
        return [
            # Document CRUD
            Tool(
                name="docs_list_documents",
                description="List documents with optional filters and pagination",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "is_creator_me": {
                            "type": "boolean",
                            "description": "Filter by documents created by current user"
                        },
                        "is_favorite": {
                            "type": "boolean",
                            "description": "Filter by favorite documents"
                        },
                        "title": {
                            "type": "string",
                            "description": "Search documents by title"
                        },
                        "ordering": {
                            "type": "string",
                            "description": "Sort order (e.g., '-updated_at', 'title', '-created_at')"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of documents per page"
                        }
                    }
                }
            ),
            Tool(
                name="docs_get_document",
                description="Get a specific document by ID with full content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to retrieve"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_create_document",
                description="Create a new document, optionally as child of another document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the new document"
                        },
                        "content": {
                            "type": "string",
                            "description": "Initial content of the document (optional)"
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "UUID of parent document (optional, creates root document if not provided)"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="docs_update_document",
                description="Update title and/or content of an existing document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the document"
                        },
                        "content": {
                            "type": "string",
                            "description": "New content for the document"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_delete_document",
                description="Delete a document (soft delete - can be restored)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to delete"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_restore_document",
                description="Restore a previously deleted document from trashbin",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to restore"
                        }
                    },
                    "required": ["document_id"]
                }
            ),

            # Document tree operations
            Tool(
                name="docs_move_document",
                description="Move a document to a different position in the tree structure",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to move"
                        },
                        "target_id": {
                            "type": "string",
                            "description": "UUID of the target document (where to move)"
                        },
                        "position": {
                            "type": "string",
                            "enum": ["first-child", "last-child", "left", "right"],
                            "description": "Position relative to target document",
                            "default": "last-child"
                        }
                    },
                    "required": ["document_id", "target_id"]
                }
            ),
            Tool(
                name="docs_duplicate_document",
                description="Create a copy of an existing document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to duplicate"
                        },
                        "with_accesses": {
                            "type": "boolean",
                            "description": "Whether to copy access permissions to the duplicate",
                            "default": False
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_get_children",
                description="Get immediate child documents of a document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the parent document"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_get_tree",
                description="Get the complete tree structure around a document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to get tree for"
                        }
                    },
                    "required": ["document_id"]
                }
            ),

            # Access management
            Tool(
                name="docs_list_accesses",
                description="List all access permissions for a document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_grant_access",
                description="Grant access to a document for a user by email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "user_email": {
                            "type": "string",
                            "description": "Email address of the user to grant access to"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["reader", "editor", "administrator", "owner"],
                            "description": "Role to assign to the user",
                            "default": "reader"
                        }
                    },
                    "required": ["document_id", "user_email"]
                }
            ),
            Tool(
                name="docs_update_access",
                description="Update the role of an existing access permission",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "access_id": {
                            "type": "string",
                            "description": "UUID of the access permission to update"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["reader", "editor", "administrator", "owner"],
                            "description": "New role for the access"
                        }
                    },
                    "required": ["document_id", "access_id", "role"]
                }
            ),
            Tool(
                name="docs_revoke_access",
                description="Remove access permission for a user on a document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "access_id": {
                            "type": "string",
                            "description": "UUID of the access permission to remove"
                        }
                    },
                    "required": ["document_id", "access_id"]
                }
            ),

            # Invitations
            Tool(
                name="docs_invite_user",
                description="Invite a user to a document via email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address to send invitation to"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["reader", "editor", "administrator", "owner"],
                            "description": "Role to assign when user accepts invitation",
                            "default": "reader"
                        }
                    },
                    "required": ["document_id", "email"]
                }
            ),
            Tool(
                name="docs_list_invitations",
                description="List all pending invitations for a document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_cancel_invitation",
                description="Cancel a pending invitation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "invitation_id": {
                            "type": "string",
                            "description": "UUID of the invitation to cancel"
                        }
                    },
                    "required": ["document_id", "invitation_id"]
                }
            ),

            # User search
            Tool(
                name="docs_search_users",
                description="Search for users by email address",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Email or partial email to search for"
                        },
                        "document_id": {
                            "type": "string",
                            "description": "Optional: exclude users who already have access to this document"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="docs_get_current_user",
                description="Get information about the currently authenticated user",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),

            # Favorites
            Tool(
                name="docs_add_favorite",
                description="Add a document to user's favorites",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to favorite"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_remove_favorite",
                description="Remove a document from user's favorites",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to unfavorite"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_list_favorites",
                description="List all documents marked as favorites by current user",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),

            # Trashbin
            Tool(
                name="docs_list_trashbin",
                description="List documents in trashbin (soft-deleted documents)",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),

            # Versions
            Tool(
                name="docs_list_versions",
                description="List version history of a document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of versions to retrieve",
                            "default": 20
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_get_version",
                description="Get content of a specific document version",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document"
                        },
                        "version_id": {
                            "type": "string",
                            "description": "ID of the version to retrieve"
                        }
                    },
                    "required": ["document_id", "version_id"]
                }
            ),

            # AI features (if enabled on the Docs instance)
            Tool(
                name="docs_ai_transform",
                description="Transform text using AI (correct, rephrase, summarize, or custom prompt)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document (required for AI access)"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to transform"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["correct", "rephrase", "summarize", "prompt"],
                            "description": "Type of transformation to apply"
                        }
                    },
                    "required": ["document_id", "text", "action"]
                }
            ),
            Tool(
                name="docs_ai_translate",
                description="Translate text using AI to specified language",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document (required for AI access)"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to translate"
                        },
                        "language": {
                            "type": "string",
                            "description": "Target language code (e.g., 'fr', 'en', 'es', 'de')"
                        }
                    },
                    "required": ["document_id", "text", "language"]
                }
            ),
            # Content editing with Yjs
            Tool(
                name="docs_get_content_text",
                description="Get document content as plain text. Extracts text from Yjs document format. Useful for reading documents before editing.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to read"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="docs_update_content",
                description="Update document content with text or markdown. Converts content to Yjs format and updates the document. This is the primary method for editing document content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to update"
                        },
                        "content": {
                            "type": "string",
                            "description": "New content for the document"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "markdown"],
                            "description": "Content format: 'text' for plain text or 'markdown' for markdown (default: 'text')",
                            "default": "text"
                        }
                    },
                    "required": ["document_id", "content"]
                }
            ),
            Tool(
                name="docs_apply_ai_transform",
                description="Apply AI transformation directly to document content and update it. Reads current content, applies AI transformation, and saves result. Actions: correct, rephrase, summarize, prompt, beautify, emojify.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to transform"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["correct", "rephrase", "summarize", "prompt", "beautify", "emojify"],
                            "description": "AI transformation action to apply"
                        },
                        "text": {
                            "type": "string",
                            "description": "Specific text to transform (optional, if not provided uses current document content)"
                        }
                    },
                    "required": ["document_id", "action"]
                }
            ),
            Tool(
                name="docs_apply_ai_translate",
                description="Apply AI translation directly to document content and update it. Reads current content, translates it, and saves result.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "UUID of the document to translate"
                        },
                        "language": {
                            "type": "string",
                            "description": "Target language code (e.g., 'fr', 'en', 'es', 'de', 'it', 'pt')"
                        },
                        "text": {
                            "type": "string",
                            "description": "Specific text to translate (optional, if not provided uses current document content)"
                        }
                    },
                    "required": ["document_id", "language"]
                }
            ),
        ]

    # Register call tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool request."""
        try:
            async with DocsAPIClient(config=_global_config) as client:
                logger.debug(f"Executing tool: {name} with args: {arguments}")

                # Document CRUD operations
                if name == "docs_list_documents":
                    result = await client.list_documents(arguments)

                elif name == "docs_get_document":
                    result = await client.get_document(arguments["document_id"])

                elif name == "docs_create_document":
                    result = await client.create_document(
                        title=arguments["title"],
                        content=arguments.get("content"),
                        parent_id=arguments.get("parent_id"),
                    )

                elif name == "docs_update_document":
                    result = await client.update_document(
                        document_id=arguments["document_id"],
                        title=arguments.get("title"),
                        content=arguments.get("content"),
                    )

                elif name == "docs_delete_document":
                    result = await client.delete_document(arguments["document_id"])

                elif name == "docs_restore_document":
                    result = await client.restore_document(arguments["document_id"])

                # Tree operations
                elif name == "docs_move_document":
                    result = await client.move_document(
                        document_id=arguments["document_id"],
                        target_id=arguments["target_id"],
                        position=arguments.get("position", "last-child"),
                    )

                elif name == "docs_duplicate_document":
                    result = await client.duplicate_document(
                        document_id=arguments["document_id"],
                        with_accesses=arguments.get("with_accesses", False),
                    )

                elif name == "docs_get_children":
                    result = await client.get_children(arguments["document_id"])

                elif name == "docs_get_tree":
                    result = await client.get_tree(arguments["document_id"])

                # Access management
                elif name == "docs_list_accesses":
                    result = await client.list_accesses(arguments["document_id"])

                elif name == "docs_grant_access":
                    result = await client.grant_access(
                        document_id=arguments["document_id"],
                        user_email=arguments["user_email"],
                        role=arguments.get("role", "reader"),
                    )

                elif name == "docs_update_access":
                    result = await client.update_access(
                        document_id=arguments["document_id"],
                        access_id=arguments["access_id"],
                        role=arguments["role"],
                    )

                elif name == "docs_revoke_access":
                    result = await client.revoke_access(
                        document_id=arguments["document_id"],
                        access_id=arguments["access_id"],
                    )

                # Invitations
                elif name == "docs_invite_user":
                    result = await client.create_invitation(
                        document_id=arguments["document_id"],
                        email=arguments["email"],
                        role=arguments.get("role", "reader"),
                    )

                elif name == "docs_list_invitations":
                    result = await client.list_invitations(arguments["document_id"])

                elif name == "docs_cancel_invitation":
                    result = await client.delete_invitation(
                        document_id=arguments["document_id"],
                        invitation_id=arguments["invitation_id"],
                    )

                # User operations
                elif name == "docs_search_users":
                    result = await client.search_users(
                        query=arguments["query"],
                        document_id=arguments.get("document_id"),
                    )

                elif name == "docs_get_current_user":
                    result = await client.get_current_user()

                # Favorites
                elif name == "docs_add_favorite":
                    result = await client.add_favorite(arguments["document_id"])

                elif name == "docs_remove_favorite":
                    result = await client.remove_favorite(arguments["document_id"])

                elif name == "docs_list_favorites":
                    result = await client.list_favorites()

                # Trashbin
                elif name == "docs_list_trashbin":
                    result = await client.list_trashbin()

                # Versions
                elif name == "docs_list_versions":
                    result = await client.list_versions(
                        document_id=arguments["document_id"],
                        page_size=arguments.get("page_size", 20),
                    )

                elif name == "docs_get_version":
                    result = await client.get_version(
                        document_id=arguments["document_id"],
                        version_id=arguments["version_id"],
                    )

                # AI features
                elif name == "docs_ai_transform":
                    result = await client.ai_transform(
                        document_id=arguments["document_id"],
                        text=arguments["text"],
                        action=arguments["action"],
                    )

                elif name == "docs_ai_translate":
                    result = await client.ai_translate(
                        document_id=arguments["document_id"],
                        text=arguments["text"],
                        language=arguments["language"],
                    )

                # Content editing with Yjs
                elif name == "docs_get_content_text":
                    result = await client.get_content_text(arguments["document_id"])
                    # Return plain text directly
                    return [TextContent(
                        type="text",
                        text=result
                    )]

                elif name == "docs_update_content":
                    result = await client.update_content(
                        document_id=arguments["document_id"],
                        content=arguments["content"],
                        format=arguments.get("format", "text"),
                    )

                elif name == "docs_apply_ai_transform":
                    result = await client.apply_ai_transform_to_content(
                        document_id=arguments["document_id"],
                        action=arguments["action"],
                        text=arguments.get("text"),
                    )

                elif name == "docs_apply_ai_translate":
                    result = await client.apply_ai_translate_to_content(
                        document_id=arguments["document_id"],
                        language=arguments["language"],
                        text=arguments.get("text"),
                    )

                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]

                # Convert result to JSON for response
                if hasattr(result, 'dict'):
                    response_data = result.dict()
                elif hasattr(result, 'model_dump'):
                    response_data = result.model_dump()
                elif hasattr(result, '__dict__'):
                    response_data = result.__dict__
                else:
                    response_data = result

                return [TextContent(
                    type="text",
                    text=json.dumps(response_data, indent=2, default=str, ensure_ascii=False)
                )]

        except DocsError as e:
            logger.error(f"Docs error in {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Error: {e.message}"
            )]
        except Exception as e:
            logger.error(f"Unexpected error in {name}: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Unexpected error: {e!s}"
            )]

    # Register resources handler
    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available MCP resources."""
        return [
            Resource(
                uri="docs://documents",
                name="All Documents",
                description="List of all accessible documents",
                mimeType="application/json"
            ),
            Resource(
                uri="docs://favorites",
                name="Favorite Documents",
                description="List of documents marked as favorites",
                mimeType="application/json"
            ),
            Resource(
                uri="docs://trashbin",
                name="Deleted Documents",
                description="List of soft-deleted documents in trashbin",
                mimeType="application/json"
            ),
            Resource(
                uri="docs://user",
                name="Current User",
                description="Information about the currently authenticated user",
                mimeType="application/json"
            ),
        ]

    # Register read resource handler
    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a specific MCP resource."""
        try:
            async with DocsAPIClient(config=_global_config) as client:

                if uri == "docs://documents":
                    result = await client.list_documents()
                elif uri == "docs://favorites":
                    result = await client.list_favorites()
                elif uri == "docs://trashbin":
                    result = await client.list_trashbin()
                elif uri == "docs://user":
                    result = await client.get_current_user()
                else:
                    return f"Unknown resource: {uri}"

                # Convert result to JSON
                if hasattr(result, 'dict'):
                    response_data = result.dict()
                elif hasattr(result, 'model_dump'):
                    response_data = result.model_dump()
                elif hasattr(result, '__dict__'):
                    response_data = result.__dict__
                else:
                    response_data = result

                return json.dumps(response_data, indent=2, default=str, ensure_ascii=False)

        except DocsError as e:
            logger.error(f"Docs error reading resource {uri}: {e}")
            return f"Error: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error reading resource {uri}: {e}", exc_info=True)
            return f"Unexpected error: {e!s}"

    return server


class DocsServer:
    """Professional MCP Server for Docs (wrapper class for compatibility)."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        config: DocsConfig | None = None,
        server_name: str = "docs-mcp-server",
    ) -> None:
        """Initialize the Docs MCP Server.
        
        Args:
            base_url: Base URL of the Docs instance
            token: Authentication token
            config: Configuration object
            server_name: Name of the MCP server
        """
        if config:
            self.config = config
        elif base_url or token:
            import os
            if base_url:
                os.environ["DOCS_BASE_URL"] = base_url
            if token:
                os.environ["DOCS_API_TOKEN"] = token
            self.config = DocsConfig()
        else:
            self.config = DocsConfig()

        self.server_name = server_name
        self.server = create_server(
            base_url=base_url,
            token=token,
            config=self.config,
            server_name=server_name
        )

    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        logger.info(f"Starting Docs MCP Server for {self.config.base_url}")

        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
