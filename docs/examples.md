# Examples

## Basic Usage

### Starting the Server

```bash
# Set environment variables
export DOCS_BASE_URL="https://docs.example.com"
export DOCS_API_TOKEN="your-api-token"

# Start the server
docs-mcp-server
```

### Configuration Check

```bash
# Verify configuration
docs-mcp-server --config-check
```

Output:
```
✓ Configuration loaded successfully
  Base URL: https://docs.example.com
  Token: ****-token-****-1234
  Timeout: 30s
  Max retries: 3
✓ API connection successful
  Authenticated as: user@example.com
  User ID: user-123
```

## Document Management

### Creating and Managing Documents

```python
import asyncio
from docs_mcp_server import create_client

async def document_workflow():
    async with create_client() as client:
        # Create a new document
        doc = await client.create_document(
            title="Project Proposal",
            content="# Project Proposal\n\nThis is our new project..."
        )
        print(f"Created document: {doc.id}")
        
        # Update the document
        updated_doc = await client.update_document(
            document_id=doc.id,
            title="Updated Project Proposal",
            content="# Updated Project Proposal\n\nRevised content..."
        )
        
        # Create a child document
        child_doc = await client.create_document(
            title="Technical Specifications",
            content="## Technical Requirements\n\nDetailed specs...",
            parent_id=doc.id
        )
        
        # List all documents
        docs = await client.list_documents({
            "ordering": "-updated_at",
            "page_size": 10
        })
        print(f"Total documents: {docs.count}")
        
        return doc.id

asyncio.run(document_workflow())
```

### Document Tree Operations

```python
async def tree_operations():
    async with create_client() as client:
        # Get document tree
        tree = await client.get_tree("doc-123")
        print(f"Tree structure: {tree}")
        
        # Move document to different position
        await client.move_document(
            document_id="child-doc-id",
            target_id="new-parent-id",
            position="first-child"
        )
        
        # Duplicate a document
        duplicate = await client.duplicate_document(
            document_id="doc-123",
            with_accesses=True  # Copy permissions too
        )
        print(f"Duplicated as: {duplicate.id}")
```

## Access Management

### Sharing Documents

```python
async def sharing_workflow():
    async with create_client() as client:
        document_id = "doc-123"
        
        # Grant access to a colleague
        access = await client.grant_access(
            document_id=document_id,
            user_email="colleague@example.com",
            role="editor"
        )
        print(f"Granted access: {access.id}")
        
        # List all accesses
        accesses = await client.list_accesses(document_id)
        for access in accesses:
            print(f"User {access.user_id}: {access.role}")
        
        # Invite external user
        invitation = await client.create_invitation(
            document_id=document_id,
            email="external@partner.com",
            role="reader"
        )
        print(f"Invitation sent: {invitation.id}")
        
        # List pending invitations
        invitations = await client.list_invitations(document_id)
        for inv in invitations:
            print(f"Pending: {inv.email} as {inv.role}")
```

### User Search and Management

```python
async def user_management():
    async with create_client() as client:
        # Search for users
        users = await client.search_users(
            query="john",
            document_id="doc-123"  # Exclude users who already have access
        )
        
        for user in users:
            print(f"Found: {user.full_name} ({user.email})")
            
            # Grant access to found user
            await client.grant_access(
                document_id="doc-123",
                user_email=user.email,
                role="reader"
            )
        
        # Get current user info
        current_user = await client.get_current_user()
        print(f"Logged in as: {current_user.full_name}")
```

## Advanced Features

### Working with Favorites

```python
async def favorites_workflow():
    async with create_client() as client:
        # Add documents to favorites
        important_docs = ["doc-123", "doc-456", "doc-789"]
        
        for doc_id in important_docs:
            await client.add_favorite(doc_id)
            print(f"Added {doc_id} to favorites")
        
        # List favorite documents
        favorites = await client.list_favorites()
        print(f"You have {favorites.count} favorite documents:")
        
        for doc in favorites.results:
            print(f"- {doc.title} (ID: {doc.id})")
        
        # Remove from favorites
        await client.remove_favorite("doc-456")
```

### Version History

```python
async def version_workflow():
    async with create_client() as client:
        document_id = "doc-123"
        
        # List version history
        versions = await client.list_versions(
            document_id=document_id,
            page_size=10
        )
        
        print(f"Document has {len(versions)} versions:")
        for version in versions:
            print(f"- Version {version.version_number}: {version.created_at}")
        
        # Get specific version content
        if versions:
            old_version = await client.get_version(
                document_id=document_id,
                version_id=versions[1].id  # Get second-to-last version
            )
            print(f"Old content: {old_version.content[:100]}...")
```

### AI-Powered Text Processing

```python
async def ai_workflow():
    async with create_client() as client:
        document_id = "doc-123"  # Required for AI features
        text = "This is some text that needs improvement"
        
        # Correct grammar and spelling
        corrected = await client.ai_transform(
            document_id=document_id,
            text=text,
            action="correct"
        )
        print(f"Corrected: {corrected.result}")
        
        # Rephrase for clarity
        rephrased = await client.ai_transform(
            document_id=document_id,
            text=text,
            action="rephrase"
        )
        print(f"Rephrased: {rephrased.result}")
        
        # Create summary
        long_text = "Very long text content here..."
        summary = await client.ai_transform(
            document_id=document_id,
            text=long_text,
            action="summarize"
        )
        print(f"Summary: {summary.result}")
        
        # Translate to French
        translation = await client.ai_translate(
            document_id=document_id,
            text="Hello, how are you?",
            language="fr"
        )
        print(f"French: {translation.result}")
```

## Error Handling Examples

### Robust Error Handling

```python
from docs_mcp_server import (
    create_client, 
    DocsError, 
    DocsNotFoundError, 
    DocsAuthError
)

async def robust_workflow():
    try:
        async with create_client() as client:
            # Try to get a document that might not exist
            doc = await client.get_document("potentially-missing-id")
            print(f"Found document: {doc.title}")
            
    except DocsNotFoundError:
        print("Document was not found")
        # Maybe create it or use a different document
        
    except DocsAuthError:
        print("Authentication failed - check your token")
        # Maybe refresh token or re-authenticate
        
    except DocsError as e:
        print(f"API error occurred: {e.message}")
        if e.status_code:
            print(f"HTTP status: {e.status_code}")
        # Handle specific API errors
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle unexpected errors
```

### Retry Logic

```python
import asyncio
from docs_mcp_server import create_client, DocsAPIError

async def retry_operation(operation, max_retries=3):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except DocsAPIError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise the error
            
            if e.status_code and 500 <= e.status_code < 600:
                # Server error, worth retrying
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Server error, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                # Client error, don't retry
                raise

async def reliable_workflow():
    async with create_client() as client:
        # Define operation that might fail
        async def create_doc():
            return await client.create_document(
                title="Important Document",
                content="Critical content"
            )
        
        # Execute with retry logic
        doc = await retry_operation(create_doc)
        print(f"Successfully created: {doc.id}")
```

## MCP Server Integration

### Custom MCP Server Configuration

```python
import asyncio
from docs_mcp_server import DocsServer, DocsConfig

async def custom_server():
    # Create custom configuration
    config = DocsConfig()
    # Configuration loaded from environment
    
    # Create server with custom settings
    server = DocsServer(
        config=config,
        server_name="company-docs-server"
    )
    
    print("Starting custom MCP server...")
    await server.run()

if __name__ == "__main__":
    asyncio.run(custom_server())
```

### Multiple Environment Setup

```python
import os
from docs_mcp_server import DocsServer

def create_environment_server(env: str):
    """Create server for specific environment."""
    env_config = {
        "dev": {
            "base_url": "https://docs-dev.example.com",
            "token": os.getenv("DEV_DOCS_TOKEN"),
            "name": "docs-dev-server"
        },
        "staging": {
            "base_url": "https://docs-staging.example.com",
            "token": os.getenv("STAGING_DOCS_TOKEN"),
            "name": "docs-staging-server"
        },
        "prod": {
            "base_url": "https://docs.example.com",
            "token": os.getenv("PROD_DOCS_TOKEN"),
            "name": "docs-prod-server"
        }
    }
    
    if env not in env_config:
        raise ValueError(f"Unknown environment: {env}")
    
    config = env_config[env]
    return DocsServer(
        base_url=config["base_url"],
        token=config["token"],
        server_name=config["name"]
    )

async def run_environment_server():
    env = os.getenv("DEPLOY_ENV", "dev")
    server = create_environment_server(env)
    
    print(f"Starting {env} environment server...")
    await server.run()
```

## Performance Examples

### Batch Operations

```python
import asyncio
from docs_mcp_server import create_client

async def batch_document_creation():
    """Create multiple documents efficiently."""
    async with create_client() as client:
        # Create multiple documents concurrently
        document_data = [
            {"title": f"Document {i}", "content": f"Content for doc {i}"}
            for i in range(1, 11)
        ]
        
        # Create documents concurrently
        tasks = [
            client.create_document(title=data["title"], content=data["content"])
            for data in document_data
        ]
        
        documents = await asyncio.gather(*tasks)
        
        print(f"Created {len(documents)} documents:")
        for doc in documents:
            print(f"- {doc.title} (ID: {doc.id})")
        
        return [doc.id for doc in documents]

async def batch_access_management(document_ids, user_emails):
    """Grant access to multiple users on multiple documents."""
    async with create_client() as client:
        tasks = []
        
        for doc_id in document_ids:
            for email in user_emails:
                task = client.grant_access(
                    document_id=doc_id,
                    user_email=email,
                    role="reader"
                )
                tasks.append(task)
        
        # Execute all access grants concurrently
        accesses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = [a for a in accesses if not isinstance(a, Exception)]
        failed = [a for a in accesses if isinstance(a, Exception)]
        
        print(f"Granted {len(successful)} accesses, {len(failed)} failed")
```

These examples demonstrate the full range of capabilities provided by the Docs MCP Server, from basic document operations to advanced AI features and robust error handling.
