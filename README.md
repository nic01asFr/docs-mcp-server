<img src="https://docs.numerique.gouv.fr/assets/icon-docs-dsfr.svg" width="48" alt="Icône DSFR">

# Docs MCP Server
<div align="center">

**🚀 Professional MCP Server for Docs**

*Complete API integration with 31 tools including document content editing via Yjs*

[![PyPI version](https://badge.fury.io/py/docs-mcp-server.svg)](https://badge.fury.io/py/docs-mcp-server)
[![Python Support](https://img.shields.io/pypi/pyversions/docs-mcp-server.svg)](https://pypi.org/project/docs-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/nic01asFr/docs-mcp-server/workflows/CI/badge.svg)](https://github.com/nic01asFr/docs-mcp-server/actions)
[![Coverage](https://codecov.io/gh/nic01asFr/docs-mcp-server/branch/main/graph/badge.svg)](https://codecov.io/gh/nic01asFr/docs-mcp-server)
[![Security](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

[📖 Documentation](https://nic01asFr.github.io/docs-mcp-server/) •
[🚀 Installation](#-installation) •
[🛠️ Usage](#%EF%B8%8F-usage) •
[🤝 Contributing](CONTRIBUTING.md) •
[📋 Changelog](CHANGELOG.md)

</div>

---

The **Docs MCP Server** provides seamless integration between Claude and [Docs](https://docs.fr) instances through the Model Context Protocol (MCP). It enables Claude to interact with collaborative documents, manage access permissions, and leverage AI-powered features directly within the Docs ecosystem.

## ✨ Key Features

### 📝 **Complete Document Management**
- 📄 Create, read, update, and delete documents
- 🌳 Navigate hierarchical document structures
- ↔️ Move and reorganize documents in trees
- 📋 Duplicate documents with or without permissions
- ⭐ Manage favorites and restore from trashbin

### ✏️ **Document Content Editing** *(NEW in v0.2.0)*
- 📖 Read document content as plain text
- ✍️ Update documents with text or markdown
- 🔄 Apply AI transformations directly to documents
- 🌍 Translate document content automatically
- 🔧 Yjs (CRDT) format support for collaborative editing

### 👥 **Advanced Access Control**
- 🔐 Grant and revoke user permissions (reader, editor, administrator, owner)
- 📧 Send email invitations to external users
- 🔍 Search for users across the platform
- 📮 Manage pending invitations

### 🤖 **AI-Powered Features**
- ✍️ Text correction and grammar checking
- 🔄 Content rephrasing and summarization  
- 🌍 Multi-language translation support
- ⚡ Custom AI transformations

### 📚 **Version History**
- 📖 Browse document version history
- 🔍 Retrieve specific version content
- 📊 Track changes over time

### 🔌 **MCP Integration**
- **31 Tools**: Comprehensive set of operations including content editing
- **4 Resources**: Real-time data access
- **Type Safety**: Full TypeScript-style type hints
- **Error Handling**: Robust error management
- **Yjs Support**: Native collaborative document format

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install docs-mcp-server
```

### From Source (Development)

```bash
git clone https://github.com/nic01asFr/docs-mcp-server.git
cd docs-mcp-server
pip install -e \".[dev]\"
```

## ⚙️ Configuration

### Environment Variables

```bash
export DOCS_BASE_URL=\"https://your-docs-instance.com\"
export DOCS_API_TOKEN=\"your-api-token\"
export DOCS_TIMEOUT=30          # Optional: request timeout in seconds  
export DOCS_MAX_RETRIES=3       # Optional: maximum retry attempts
```

### Verify Configuration

```bash
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

## 🛠️ Usage

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
        base_url=\"https://docs.example.com\",
        token=\"your-token\",
        server_name=\"my-docs-server\"
    )
    await server.run()

if __name__ == \"__main__\":
    asyncio.run(main())
```

## 📋 Available Tools

<details>
<summary><strong>📄 Document Operations (6 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `docs_list_documents` | List documents with filtering and pagination |
| `docs_get_document` | Retrieve a specific document by ID |
| `docs_create_document` | Create new documents (root or child) |
| `docs_update_document` | Update document title and content |
| `docs_delete_document` | Soft delete documents |
| `docs_restore_document` | Restore deleted documents |

</details>

<details>
<summary><strong>✏️ Document Content Editing (4 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `docs_get_content_text` | Read document content as plain text |
| `docs_update_content` | Update document with text or markdown |
| `docs_apply_ai_transform` | Apply AI transformation and save to document |
| `docs_apply_ai_translate` | Translate and save document content |

</details>

<details>
<summary><strong>🌳 Tree Operations (4 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `docs_move_document` | Move documents in tree structure |
| `docs_duplicate_document` | Create document copies |
| `docs_get_children` | Get immediate child documents |
| `docs_get_tree` | Get complete tree structure |

</details>

<details>
<summary><strong>🔐 Access Management (7 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `docs_list_accesses` | List document permissions |
| `docs_grant_access` | Grant user access to documents |
| `docs_update_access` | Modify existing permissions |
| `docs_revoke_access` | Remove user access |
| `docs_invite_user` | Send email invitations |
| `docs_list_invitations` | List pending invitations |
| `docs_cancel_invitation` | Cancel invitations |

</details>

<details>
<summary><strong>👤 User & Content Management (8 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `docs_search_users` | Search users by email |
| `docs_get_current_user` | Get current user information |
| `docs_add_favorite` | Add documents to favorites |
| `docs_remove_favorite` | Remove from favorites |
| `docs_list_favorites` | List favorite documents |
| `docs_list_trashbin` | List deleted documents |
| `docs_list_versions` | List document version history |
| `docs_get_version` | Get specific version content |

</details>

<details>
<summary><strong>🤖 AI Features (2 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `docs_ai_transform` | AI text transformation (correct, rephrase, summarize) |
| `docs_ai_translate` | AI translation services |

</details>

## 📊 Resources

| Resource | Description |
|----------|-------------|
| `docs://documents` | All accessible documents |
| `docs://favorites` | User's favorite documents |
| `docs://trashbin` | Soft-deleted documents |
| `docs://user` | Current user information |

## 💡 Examples

### Basic Document Operations

```python
from docs_mcp_server import create_client

async def example():
    async with create_client() as client:
        # Create a document
        doc = await client.create_document(
            title=\"Project Proposal\",
            content=\"# Project Overview\\n\\nThis is our new project...\"
        )
        
        # Grant access to a colleague
        await client.grant_access(
            document_id=doc.id,
            user_email=\"colleague@example.com\",
            role=\"editor\"
        )
        
        # Use AI to improve content
        improved = await client.ai_transform(
            document_id=doc.id,
            text=\"This text needs improvement\",
            action=\"rephrase\"
        )
        print(f\"Improved text: {improved.result}\")
```

### MCP Server Integration

```python
import asyncio
from docs_mcp_server import DocsServer

async def main():
    server = DocsServer(
        base_url=\"https://docs.example.com\",
        token=\"your-token\",
        server_name=\"company-docs\"
    )
    await server.run()

asyncio.run(main())
```

### Error Handling

```python
from docs_mcp_server import DocsAPIClient, DocsError, DocsNotFoundError

async def robust_example():
    try:
        async with DocsAPIClient() as client:
            doc = await client.get_document(\"non-existent-id\")
    except DocsNotFoundError:
        print(\"Document not found\")
    except DocsError as e:
        print(f\"API error: {e.message}\")
    except Exception as e:
        print(f\"Unexpected error: {e}\")
```

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/nic01asFr/docs-mcp-server.git
cd docs-mcp-server
pip install -e \".[dev]\"
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docs_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### Code Quality

```bash
# Linting and formatting
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/docs_mcp_server

# Security scanning
bandit -r src/
safety check
```

### Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## 🏭 Production Ready

### ✅ **Quality Assurance**
- 🧪 Comprehensive test suite with >95% coverage
- 🔒 Type safety with mypy and pydantic
- 🧹 Code quality with ruff and pre-commit hooks
- 🛡️ Security scanning with bandit and safety
- 📊 Performance monitoring and optimization

### 🔐 **Security**
- 🔑 Secure API token management
- 🌐 HTTPS-only communication
- ✅ Input validation and sanitization
- 💾 No sensitive data storage
- 📋 Comprehensive security documentation

### 🚀 **CI/CD**
- 🔄 Automated testing on multiple Python versions (3.10-3.12)
- 📦 Automated PyPI publishing on releases
- 🔍 Security vulnerability scanning
- 📈 Performance regression testing

### 📚 **Documentation**
- 📖 Comprehensive API documentation
- 💡 Usage examples and tutorials
- 🤝 Contribution guidelines
- 🔒 Security policy
- 📋 Detailed changelog

## 🔗 Links

- 📦 [PyPI Package](https://pypi.org/project/docs-mcp-server/)
- 📖 [Documentation](https://nic01asFr.github.io/docs-mcp-server/)
- 🐙 [GitHub Repository](https://github.com/nic01asFr/docs-mcp-server)
- 🐛 [Issue Tracker](https://github.com/nic01asFr/docs-mcp-server/issues)
- 💬 [Discussions](https://github.com/nic01asFr/docs-mcp-server/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Contributors

<a href=\"https://github.com/nic01asFr/docs-mcp-server/graphs/contributors\">
  <img src=\"https://contrib.rocks/image?repo=nic01asFr/docs-mcp-server\" />
</a>

## 🙏 Acknowledgments

- [Model Context Protocol](https://github.com/modelcontextprotocol) for the MCP specification
- [La Suite Numérique](https://lasuite.numerique.gouv.fr/) and the DINUM team for creating the Docs platform
- All contributors and users of this project

---

<div align=\"center\">

**Made with ❤️ by Nicolas LAVAL**

*Enabling seamless AI integration with collaborative documentation*

</div>
