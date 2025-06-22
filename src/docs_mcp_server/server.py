"""Professional MCP Server for DINUM Docs."""

import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from mcp.server import Server, NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
)

from .client import DocsAPIClient
from .config import DocsConfig, get_global_config
from .exceptions import DocsError

logger = logging.getLogger(__name__)


class DocsServer:
    """Professional MCP Server for DINUM Docs."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        config: Optional[DocsConfig] = None,
        server_name: str = "docs-mcp-server",
    ) -> None:
        """Initialize the Docs MCP Server.
        
        Args:
            base_url: Base URL of the Docs instance
            token: Authentication token
            config: Configuration object
            server_name: Name of the MCP server
        """
        self.config = config or (
            DocsConfig() if not base_url and not token
            else self._create_config(base_url, token)
        )
        
        # Initialize MCP server
        self.server = Server(server_name)
        
        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
        self.server.list_resources = self.list_resources
        self.server.read_resource = self.read_resource

    def _create_config(self, base_url: Optional[str], token: Optional[str]) -> DocsConfig:
        """Create config from parameters."""
        if not base_url or not token:
            raise ValueError("Both base_url and token are required")
        
        import os
        os.environ["DOCS_BASE_URL"] = base_url
        os.environ["DOCS_API_TOKEN"] = token
        return DocsConfig()

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List all available MCP tools."""
        tools = [
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
        ]
        
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Execute a tool request."""
        try:
            async with DocsAPIClient(config=self.config) as client:
                tool_name = request.params.name
                args = request.params.arguments or {}
                
                logger.debug(f"Executing tool: {tool_name} with args: {args}")
                
                # Document CRUD operations
                if tool_name == "docs_list_documents":
                    result = await client.list_documents(args)
                    
                elif tool_name == "docs_get_document":
                    result = await client.get_document(args["document_id"])
                    
                elif tool_name == "docs_create_document":
                    result = await client.create_document(
                        title=args["title"],
                        content=args.get("content"),
                        parent_id=args.get("parent_id"),
                    )
                    
                elif tool_name == "docs_update_document":
                    result = await client.update_document(
                        document_id=args["document_id"],
                        title=args.get("title"),
                        content=args.get("content"),
                    )
                    
                elif tool_name == "docs_delete_document":
                    result = await client.delete_document(args["document_id"])
                    
                elif tool_name == "docs_restore_document":
                    result = await client.restore_document(args["document_id"])
                    
                # Tree operations
                elif tool_name == "docs_move_document":
                    result = await client.move_document(
                        document_id=args["document_id"],
                        target_id=args["target_id"],
                        position=args.get("position", "last-child"),
                    )
                    
                elif tool_name == "docs_duplicate_document":
                    result = await client.duplicate_document(
                        document_id=args["document_id"],
                        with_accesses=args.get("with_accesses", False),
                    )
                    
                elif tool_name == "docs_get_children":
                    result = await client.get_children(args["document_id"])
                    
                elif tool_name == "docs_get_tree":
                    result = await client.get_tree(args["document_id"])
                    
                # Access management
                elif tool_name == "docs_list_accesses":
                    result = await client.list_accesses(args["document_id"])
                    
                elif tool_name == "docs_grant_access":
                    result = await client.grant_access(
                        document_id=args["document_id"],
                        user_email=args["user_email"],
                        role=args.get("role", "reader"),
                    )
                    
                elif tool_name == "docs_update_access":
                    result = await client.update_access(
                        document_id=args["document_id"],
                        access_id=args["access_id"],
                        role=args["role"],
                    )
                    
                elif tool_name == "docs_revoke_access":
                    result = await client.revoke_access(
                        document_id=args["document_id"],
                        access_id=args["access_id"],
                    )
                    
                # Invitations
                elif tool_name == "docs_invite_user":
                    result = await client.create_invitation(
                        document_id=args["document_id"],
                        email=args["email"],
                        role=args.get("role", "reader"),
                    )
                    
                elif tool_name == "docs_list_invitations":
                    result = await client.list_invitations(args["document_id"])
                    
                elif tool_name == "docs_cancel_invitation":
                    result = await client.delete_invitation(
                        document_id=args["document_id"],
                        invitation_id=args["invitation_id"],
                    )
                    
                # User operations
                elif tool_name == "docs_search_users":
                    result = await client.search_users(
                        query=args["query"],
                        document_id=args.get("document_id"),
                    )
                    
                elif tool_name == "docs_get_current_user":
                    result = await client.get_current_user()
                    
                # Favorites
                elif tool_name == "docs_add_favorite":
                    result = await client.add_favorite(args["document_id"])
                    
                elif tool_name == "docs_remove_favorite":
                    result = await client.remove_favorite(args["document_id"])
                    
                elif tool_name == "docs_list_favorites":
                    result = await client.list_favorites()
                    
                # Trashbin
                elif tool_name == "docs_list_trashbin":
                    result = await client.list_trashbin()
                    
                # Versions
                elif tool_name == "docs_list_versions":
                    result = await client.list_versions(
                        document_id=args["document_id"],
                        page_size=args.get("page_size", 20),
                    )
                    
                elif tool_name == "docs_get_version":
                    result = await client.get_version(
                        document_id=args["document_id"],
                        version_id=args["version_id"],
                    )
                    
                # AI features
                elif tool_name == "docs_ai_transform":
                    result = await client.ai_transform(
                        document_id=args["document_id"],
                        text=args["text"],
                        action=args["action"],
                    )
                    
                elif tool_name == "docs_ai_translate":
                    result = await client.ai_translate(
                        document_id=args["document_id"],
                        text=args["text"],
                        language=args["language"],
                    )
                    
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Unknown tool: {tool_name}"
                        )]
                    )
                
                # Convert result to JSON for response
                if hasattr(result, 'dict'):
                    response_data = result.dict()
                elif hasattr(result, '__dict__'):
                    response_data = result.__dict__
                else:
                    response_data = result
                
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(response_data, indent=2, default=str, ensure_ascii=False)
                    )]
                )
                
        except DocsError as e:
            logger.error(f"Docs error in {tool_name}: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error: {e.message}"
                )]
            )
        except Exception as e:
            logger.error(f"Unexpected error in {tool_name}: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]
            )

    async def list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        """List available MCP resources."""
        resources = [
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
        
        return ListResourcesResult(resources=resources)

    async def read_resource(self, request: ReadResourceRequest) -> ReadResourceResult:
        """Read a specific MCP resource."""
        try:
            async with DocsAPIClient(config=self.config) as client:
                
                if request.uri == "docs://documents":
                    result = await client.list_documents()
                elif request.uri == "docs://favorites":
                    result = await client.list_favorites()
                elif request.uri == "docs://trashbin":
                    result = await client.list_trashbin()
                elif request.uri == "docs://user":
                    result = await client.get_current_user()
                else:
                    return ReadResourceResult(
                        contents=[TextContent(
                            type="text",
                            text=f"Unknown resource: {request.uri}"
                        )]
                    )
                
                # Convert result to JSON
                if hasattr(result, 'dict'):
                    response_data = result.dict()
                elif hasattr(result, '__dict__'):
                    response_data = result.__dict__
                else:
                    response_data = result
                
                return ReadResourceResult(
                    contents=[TextContent(
                        type="text",
                        text=json.dumps(response_data, indent=2, default=str, ensure_ascii=False)
                    )]
                )
                
        except DocsError as e:
            logger.error(f"Docs error reading resource {request.uri}: {e}")
            return ReadResourceResult(
                contents=[TextContent(
                    type="text",
                    text=f"Error: {e.message}"
                )]
            )
        except Exception as e:
            logger.error(f"Unexpected error reading resource {request.uri}: {e}")
            return ReadResourceResult(
                contents=[TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]
            )

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info(f"Starting Docs MCP Server for {self.config.base_url}")
        async with self.server:
            await self.server.run()
