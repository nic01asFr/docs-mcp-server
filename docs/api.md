# API Reference

## Core Classes

### DocsServer

Main MCP server class that handles tool and resource requests.

```python
class DocsServer:
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None, 
        config: Optional[DocsConfig] = None,
        server_name: str = "docs-mcp-server"
    )
```

**Parameters:**
- `base_url`: Base URL of the Docs instance
- `token`: API authentication token
- `config`: Configuration object (alternative to base_url/token)
- `server_name`: Name identifier for the MCP server

**Methods:**
- `async run()`: Start the MCP server
- `async list_tools(request)`: List available tools
- `async call_tool(request)`: Execute a tool
- `async list_resources(request)`: List available resources
- `async read_resource(request)`: Read a resource

### DocsAPIClient

HTTP client for interacting with the Docs API.

```python
class DocsAPIClient:
    def __init__(
        self,
        config: Optional[DocsConfig] = None,
        http_client: Optional[httpx.AsyncClient] = None
    )
```

**Parameters:**
- `config`: Configuration object
- `http_client`: Custom HTTP client (optional)

### DocsConfig

Configuration management class.

```python
class DocsConfig:
    def __init__(self)
```

Loads configuration from environment variables:
- `DOCS_BASE_URL`: Base URL (required)
- `DOCS_API_TOKEN`: API token (required)
- `DOCS_TIMEOUT`: Request timeout in seconds (default: 30)
- `DOCS_MAX_RETRIES`: Maximum retry attempts (default: 3)

## Document Operations

### list_documents

List documents with optional filtering and pagination.

```python
async def list_documents(
    self,
    filters: Optional[Dict[str, Any]] = None
) -> DocumentList
```

**Filter Parameters:**
- `is_creator_me`: Filter by documents created by current user
- `is_favorite`: Filter by favorite documents
- `title`: Search by title
- `ordering`: Sort order (e.g., '-updated_at', 'title')
- `page`: Page number
- `page_size`: Documents per page

### get_document

Get a specific document by ID.

```python
async def get_document(self, document_id: str) -> Document
```

### create_document

Create a new document.

```python
async def create_document(
    self,
    title: str,
    content: Optional[str] = None,
    parent_id: Optional[str] = None
) -> Document
```

### update_document

Update an existing document.

```python
async def update_document(
    self,
    document_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> Document
```

### delete_document

Soft delete a document.

```python
async def delete_document(self, document_id: str) -> Dict[str, Any]
```

### restore_document

Restore a deleted document.

```python
async def restore_document(self, document_id: str) -> Document
```

## Tree Operations

### move_document

Move a document in the tree structure.

```python
async def move_document(
    self,
    document_id: str,
    target_id: str,
    position: str = "last-child"
) -> Dict[str, Any]
```

**Position Options:**
- `first-child`: As first child of target
- `last-child`: As last child of target
- `left`: As sibling before target
- `right`: As sibling after target

### duplicate_document

Create a copy of a document.

```python
async def duplicate_document(
    self,
    document_id: str,
    with_accesses: bool = False
) -> Document
```

### get_children

Get immediate child documents.

```python
async def get_children(self, document_id: str) -> List[Document]
```

### get_tree

Get complete tree structure around a document.

```python
async def get_tree(self, document_id: str) -> Dict[str, Any]
```

## Access Management

### list_accesses

List access permissions for a document.

```python
async def list_accesses(self, document_id: str) -> List[Access]
```

### grant_access

Grant access to a user.

```python
async def grant_access(
    self,
    document_id: str,
    user_email: str,
    role: str = "reader"
) -> Access
```

**Role Options:**
- `reader`: Read-only access
- `editor`: Read and edit access
- `administrator`: Full access except ownership transfer
- `owner`: Full ownership (use carefully)

### update_access

Update an existing access permission.

```python
async def update_access(
    self,
    document_id: str,
    access_id: str,
    role: str
) -> Access
```

### revoke_access

Remove user access.

```python
async def revoke_access(
    self,
    document_id: str,
    access_id: str
) -> Dict[str, Any]
```

## User Operations

### get_current_user

Get current authenticated user information.

```python
async def get_current_user(self) -> User
```

### search_users

Search for users by email.

```python
async def search_users(
    self,
    query: str,
    document_id: Optional[str] = None
) -> List[User]
```

## Invitation Management

### create_invitation

Invite a user to a document.

```python
async def create_invitation(
    self,
    document_id: str,
    email: str,
    role: str = "reader"
) -> Invitation
```

### list_invitations

List pending invitations for a document.

```python
async def list_invitations(self, document_id: str) -> List[Invitation]
```

### delete_invitation

Cancel a pending invitation.

```python
async def delete_invitation(
    self,
    document_id: str,
    invitation_id: str
) -> Dict[str, Any]
```

## Favorites

### add_favorite

Add document to favorites.

```python
async def add_favorite(self, document_id: str) -> Dict[str, Any]
```

### remove_favorite

Remove document from favorites.

```python
async def remove_favorite(self, document_id: str) -> Dict[str, Any]
```

### list_favorites

List favorite documents.

```python
async def list_favorites(self) -> DocumentList
```

## Version History

### list_versions

List document version history.

```python
async def list_versions(
    self,
    document_id: str,
    page_size: int = 20
) -> List[Version]
```

### get_version

Get specific version content.

```python
async def get_version(
    self,
    document_id: str,
    version_id: str
) -> Version
```

## AI Features

### ai_transform

Transform text using AI.

```python
async def ai_transform(
    self,
    document_id: str,
    text: str,
    action: str
) -> AITransformResponse
```

**Action Options:**
- `correct`: Grammar and spelling correction
- `rephrase`: Rephrase for clarity
- `summarize`: Create summary
- `prompt`: Custom transformation

### ai_translate

Translate text to another language.

```python
async def ai_translate(
    self,
    document_id: str,
    text: str,
    language: str
) -> AITranslateResponse
```

**Language Codes:**
- `fr`: French
- `en`: English
- `es`: Spanish
- `de`: German
- And more...

## Data Models

### Document

Represents a document in the system.

```python
class Document(BaseModel):
    id: str
    title: str
    content: str
    creator_id: str
    created_at: datetime
    updated_at: datetime
    is_favorite: bool
    accesses: List[Access]
```

### User

Represents a user in the system.

```python
class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    date_joined: datetime
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

### Access

Represents access permission to a document.

```python
class Access(BaseModel):
    id: str
    user_id: str
    role: str
    created_at: datetime
```

## Exception Handling

### DocsError

Base exception for all Docs-related errors.

```python
class DocsError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None)
```

### DocsAPIError

API-specific errors (4xx, 5xx responses).

### DocsAuthError

Authentication and authorization errors.

### DocsNotFoundError

404 Not Found errors.
