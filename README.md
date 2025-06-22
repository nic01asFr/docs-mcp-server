# Docs MCP Server

[![PyPI version](https://badge.fury.io/py/docs-mcp-server.svg)](https://badge.fury.io/py/docs-mcp-server)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Professional MCP (Model Context Protocol) server for [DINUM Docs](https://github.com/suitenumerique/docs) - the French government's open-source collaborative document platform.

## 🚀 Quick Start

### Installation

```bash
pip install docs-mcp-server
```

### Basic Usage

```python
from docs_mcp_server import DocsServer
import asyncio

async def main():
    server = DocsServer(
        base_url="https://your-docs-instance.gouv.fr",
        token="your-auth-token"
    )
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Command Line

```bash
# Start the server
docs-mcp-server --base-url https://your-docs-instance.gouv.fr --token your-token

# Or use environment variables
export DOCS_BASE_URL="https://your-docs-instance.gouv.fr"
export DOCS_API_TOKEN="your-token"
docs-mcp-server
```

## 🎯 Features

### Document Operations (CRUD)

- ✅ **Create** documents with hierarchical structure
- ✅ **Read** documents with full content and metadata
- ✅ **Update** documents (title, content, properties)
- ✅ **Delete** documents (soft delete with restore capability)

### Advanced Document Management

- 🌳 **Tree Operations**: Move documents, manage parent-child relationships
- 👥 **Access Control**: Manage user permissions (Owner, Admin, Editor, Reader)
- 📧 **Invitations**: Invite users via email with specific roles
- ⭐ **Favorites**: Mark/unmark documents as favorites
- 📋 **Duplication**: Duplicate documents with/without access rights
- 🗑️ **Trash Management**: Restore soft-deleted documents

### Content & Collaboration

- 🔍 **Search**: Find documents and users
- 📁 **Attachments**: Upload and manage file attachments
- 🔄 **Versions**: Access document version history
- 🤖 **AI Integration**: Text transformation and translation (if enabled)

### Modern MCP Features

- 🛠️ **Tools**: Complete CRUD operations through MCP tools
- 📚 **Resources**: Expose documents as MCP resources
- 🔧 **Type Safety**: Full TypeScript-style type hints with Pydantic
- ⚡ **Async**: Fully asynchronous for performance
- 🎛️ **Configuration**: Flexible configuration through environment variables

## 📋 Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `docs_list_documents` | List documents with filtering | `is_creator_me`, `is_favorite`, `title`, `ordering` |
| `docs_get_document` | Get document by ID | `document_id` |
| `docs_create_document` | Create new document | `title`, `content?`, `parent_id?` |
| `docs_update_document` | Update existing document | `document_id`, `title?`, `content?` |
| `docs_delete_document` | Delete document (soft) | `document_id` |
| `docs_restore_document` | Restore deleted document | `document_id` |
| `docs_move_document` | Move document in tree | `document_id`, `target_id`, `position` |
| `docs_duplicate_document` | Duplicate document | `document_id`, `with_accesses?` |
| `docs_grant_access` | Grant user access | `document_id`, `user_email`, `role` |
| `docs_list_accesses` | List document permissions | `document_id` |
| `docs_revoke_access` | Remove user access | `document_id`, `access_id` |
| `docs_invite_user` | Invite user by email | `document_id`, `email`, `role` |
| `docs_search_users` | Search users by email | `query` |
| `docs_add_favorite` | Add to favorites | `document_id` |
| `docs_remove_favorite` | Remove from favorites | `document_id` |
| `docs_list_favorites` | List favorite documents | - |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DOCS_BASE_URL` | Base URL of your Docs instance | ✅ | - |
| `DOCS_API_TOKEN` | Authentication token | ✅ | - |
| `DOCS_API_VERSION` | API version to use | ❌ | `v1.0` |
| `DOCS_TIMEOUT` | Request timeout in seconds | ❌ | `30` |
| `DOCS_MAX_RETRIES` | Max retry attempts | ❌ | `3` |
| `DOCS_RATE_LIMIT` | Max requests per second | ❌ | `10` |
| `LOG_LEVEL` | Logging level | ❌ | `INFO` |

### Authentication

#### OIDC Token (Recommended)

```bash
# Get token from your OIDC provider
export DOCS_API_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Development Token

For development, you can extract a session token from your browser:

1. Log into your Docs instance
2. Open browser developer tools (F12)
3. Go to Network tab
4. Make any API request
5. Copy the `Authorization: Bearer ...` header value

## 🏗️ Architecture

```
docs-mcp-server/
├── src/docs_mcp_server/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # Main MCP server implementation
│   ├── client.py            # Docs API client
│   ├── models.py            # Pydantic data models
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   └── cli.py               # Command line interface
├── tests/                   # Comprehensive test suite
├── examples/                # Usage examples
└── docs/                    # Documentation
```

## 📚 Examples

### Basic Document Operations

```python
from docs_mcp_server import DocsAPIClient
import asyncio

async def example():
    async with DocsAPIClient("https://docs.example.fr", "token") as client:
        # Create a document
        doc = await client.create_document("My Document", "Initial content")
        print(f"Created document: {doc['id']}")
        
        # Update the document
        await client.update_document(doc['id'], title="Updated Title")
        
        # Grant access to a user
        await client.grant_access(doc['id'], "user@example.com", "editor")
        
        # List all documents
        docs = await client.list_documents({"is_creator_me": True})
        print(f"Found {docs['count']} documents")

asyncio.run(example())
```

### MCP Server Integration

```python
# server.py
from docs_mcp_server import DocsServer

server = DocsServer(
    base_url="https://docs.example.fr",
    token="your-token"
)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
```

### Claude Desktop Configuration

Add to your Claude Desktop `config.json`:

```json
{
  "mcpServers": {
    "docs": {
      "command": "docs-mcp-server",
      "env": {
        "DOCS_BASE_URL": "https://your-docs-instance.gouv.fr",
        "DOCS_API_TOKEN": "your-token"
      }
    }
  }
}
```

## 🧪 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/nic01asFr/docs-mcp-server.git
cd docs-mcp-server

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/docs_mcp_server --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Code Quality

```bash
# Format code
ruff format

# Lint code
ruff check --fix

# Type checking
pyright

# Run all quality checks
ruff check && ruff format --check && pyright
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Run quality checks (`ruff check && pyright`)
7. Commit your changes (`git commit -m 'feat: add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏛️ About DINUM Docs

[DINUM Docs](https://github.com/suitenumerique/docs) is an open-source collaborative document platform developed by:
- 🇫🇷 **DINUM** (Direction interministérielle du numérique) - France
- 🇩🇪 **ZenDiS** (Center for Digital Sovereignty) - Germany

It provides a secure, sovereign alternative to commercial document platforms for government and public sector use.

## 🔗 Related Projects

- [Docs (DINUM)](https://github.com/suitenumerique/docs) - The main Docs platform
- [MCP (Model Context Protocol)](https://github.com/modelcontextprotocol) - The protocol this server implements
- [Claude](https://claude.ai) - AI assistant that can use MCP servers

## 🐛 Issues & Support

- 🐛 [Report a bug](https://github.com/nic01asFr/docs-mcp-server/issues/new?labels=bug)
- 💡 [Request a feature](https://github.com/nic01asFr/docs-mcp-server/issues/new?labels=enhancement)
- 📖 [Documentation](https://github.com/nic01asFr/docs-mcp-server#readme)

## 📊 Status

- ✅ **Stable**: Core CRUD operations
- ✅ **Stable**: Access management
- ✅ **Stable**: Document tree operations
- 🧪 **Beta**: AI features (depends on Docs instance configuration)
- 🚧 **Planned**: Real-time collaboration features
- 🚧 **Planned**: Advanced search and filtering
- 🚧 **Planned**: Batch operations
