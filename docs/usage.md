# Usage Guide

## Starting the Server

### Command Line

```bash
# Start with environment variables
docs-mcp-server

# Start with explicit configuration
docs-mcp-server --base-url https://docs.example.com --token your-token

# Start with custom server name
docs-mcp-server --name my-docs-server

# Start with verbose logging
docs-mcp-server --verbose
```

### Python Module

```bash
python -m docs_mcp_server
```

### Programmatic Usage

```python
import asyncio
from docs_mcp_server import DocsServer

async def main():
    server = DocsServer(
        base_url="https://docs.example.com",
        token="your-token",
        server_name="my-docs-server"
    )
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Tools

The server provides 25+ tools organized by functionality:

### Document Management

- `docs_list_documents` - List documents with filters
- `docs_get_document` - Get specific document by ID
- `docs_create_document` - Create new document
- `docs_update_document` - Update existing document
- `docs_delete_document` - Delete document (soft delete)
- `docs_restore_document` - Restore deleted document

### Document Tree Operations

- `docs_move_document` - Move document in tree structure
- `docs_duplicate_document` - Create document copy
- `docs_get_children` - Get child documents
- `docs_get_tree` - Get complete tree structure

### Access Management

- `docs_list_accesses` - List document permissions
- `docs_grant_access` - Grant user access to document
- `docs_update_access` - Update access permissions
- `docs_revoke_access` - Remove user access

### User Operations

- `docs_search_users` - Search users by email
- `docs_get_current_user` - Get current user info
- `docs_invite_user` - Invite user to document
- `docs_list_invitations` - List pending invitations
- `docs_cancel_invitation` - Cancel invitation

### Favorites

- `docs_add_favorite` - Add document to favorites
- `docs_remove_favorite` - Remove from favorites
- `docs_list_favorites` - List favorite documents

### Version History

- `docs_list_versions` - List document versions
- `docs_get_version` - Get specific version content

### AI Features

- `docs_ai_transform` - Transform text (correct, rephrase, summarize)
- `docs_ai_translate` - Translate text to another language

### Utility

- `docs_list_trashbin` - List deleted documents

## Available Resources

The server exposes 4 MCP resources:

- `docs://documents` - All accessible documents
- `docs://favorites` - User's favorite documents
- `docs://trashbin` - Deleted documents
- `docs://user` - Current user information

## Using the API Client

```python
from docs_mcp_server import DocsAPIClient

async def example():
    async with DocsAPIClient() as client:
        # List documents
        documents = await client.list_documents()
        print(f"Found {documents.count} documents")
        
        # Get specific document
        doc = await client.get_document("doc-id-123")
        print(f"Document title: {doc.title}")
        
        # Create new document
        new_doc = await client.create_document(
            title="My New Document",
            content="This is the content"
        )
        print(f"Created document: {new_doc.id}")
        
        # Update document
        updated_doc = await client.update_document(
            document_id=new_doc.id,
            title="Updated Title",
            content="Updated content"
        )
        
        # Grant access to another user
        access = await client.grant_access(
            document_id=new_doc.id,
            user_email="colleague@example.com",
            role="editor"
        )
```

## Error Handling

```python
from docs_mcp_server import DocsAPIClient, DocsError, DocsNotFoundError

async def robust_example():
    try:
        async with DocsAPIClient() as client:
            doc = await client.get_document("non-existent-id")
    except DocsNotFoundError:
        print("Document not found")
    except DocsError as e:
        print(f"API error: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Configuration Examples

### Multiple Environments

```python
from docs_mcp_server import DocsConfig, DocsServer

# Development environment
dev_config = DocsConfig(
    base_url="https://docs-dev.example.com",
    token="dev-token",
    timeout=60  # Longer timeout for dev
)

# Production environment
prod_config = DocsConfig(
    base_url="https://docs.example.com",
    token="prod-token",
    timeout=30,
    max_retries=5  # More retries for prod
)

# Create servers
dev_server = DocsServer(config=dev_config, server_name="docs-dev")
prod_server = DocsServer(config=prod_config, server_name="docs-prod")
```
