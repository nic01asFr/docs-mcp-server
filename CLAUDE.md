# CLAUDE.md

This file provides guidance for AI assistants when working with code in this repository.

## Project Overview

This is a professional MCP (Model Context Protocol) server that integrates Claude with Docs instances. It exposes **31 tools** and 4 resources for document management, access control, version history, AI-powered features, and **document content editing via Yjs (CRDT)**.

**Key Components:**
- `DocsAPIClient` ([client.py](src/docs_mcp_server/client.py)) - Async HTTP client with retry logic and rate limiting
- `DocsServer` ([server.py](src/docs_mcp_server/server.py)) - MCP server implementation with tool/resource handlers
- `DocsConfig` ([config.py](src/docs_mcp_server/config.py)) - Pydantic-based configuration from environment variables
- Pydantic models ([models.py](src/docs_mcp_server/models.py)) - Type-safe data models for all API entities
- `YjsDocumentUtils` ([yjs_utils.py](src/docs_mcp_server/yjs_utils.py)) - Utilities for Yjs document manipulation (v0.2.0+)

## Development Commands

### Setup
```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Install only test dependencies
pip install -e ".[test]"

# Setup pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=docs_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run tests in parallel
pytest -n auto
```

### Code Quality
```bash
# Lint and format with ruff (this project uses ruff, not black/flake8)
ruff check src/ tests/
ruff format src/ tests/

# Type checking with mypy (strict mode disabled, see pyproject.toml)
mypy src/docs_mcp_server

# Security scanning
bandit -r src/
safety check
```

### Running the Server
```bash
# Start MCP server (requires DOCS_BASE_URL and DOCS_API_TOKEN env vars)
docs-mcp-server

# Check configuration validity
docs-mcp-server --config-check

# Run with explicit config
docs-mcp-server --base-url https://docs.example.com --token your-token

# Run as Python module
python -m docs_mcp_server
```

## Architecture

### Request Flow
1. MCP client calls tool/resource via stdio transport
2. `DocsServer` receives request and routes to appropriate handler
3. Handler creates `DocsAPIClient` instance (async context manager)
4. Client makes HTTP request with retry logic (tenacity) and rate limiting (asyncio.Semaphore)
5. Response validated through Pydantic models and returned as JSON

### Key Architectural Patterns

**Async Context Manager Pattern**: `DocsAPIClient` uses `__aenter__`/`__aexit__` to manage httpx client lifecycle:
```python
async with DocsAPIClient(config=config) as client:
    result = await client.get_document(doc_id)
```

**Global Configuration**: Server uses module-level `_global_config` to share config across handlers (see [server.py:23](src/docs_mcp_server/server.py#L23)). This is set once at server startup.

**Error Hierarchy**: Custom exception hierarchy in [exceptions.py](src/docs_mcp_server/exceptions.py):
- `DocsError` (base)
  - `DocsAPIError` (API errors with status codes)
    - `DocsAuthError`, `DocsNotFoundError`, `DocsPermissionError`, `DocsRateLimitError`
  - `DocsConnectionError`, `DocsTimeoutError`, `DocsValidationError`

**Model Variants**: Models have different variants for different use cases:
- `User` vs `UserLight` - full vs minimal fields
- `Document` vs `ListDocument` vs `BaseDocument` - full content vs list view vs base fields
- Request models (e.g., `DocumentCreateRequest`) vs Response models (e.g., `Document`)

### MCP Tool Implementation

All tools follow this pattern in [server.py](src/docs_mcp_server/server.py):
1. Define tool schema in `list_tools()` (lines 69-567)
2. Implement handler logic in `call_tool()` (lines 570-749)
3. Convert result to JSON using `.dict()`, `.model_dump()`, or `__dict__`
4. Wrap in `TextContent` for MCP protocol

### Configuration Management

Configuration uses `pydantic-settings` with environment variables:
- **Required**: `DOCS_BASE_URL`, `DOCS_API_TOKEN`
- **Optional**: `DOCS_TIMEOUT`, `DOCS_MAX_RETRIES`, `DOCS_RATE_LIMIT`, etc.
- See [config.py:11-138](src/docs_mcp_server/config.py#L11-L138) for all fields

The `api_base_url` property automatically constructs the full API URL: `{base_url}/api/{api_version}`

## Yjs Document Content Editing (v0.2.0+)

### Overview

Docs uses **Yjs (CRDT)** for collaborative document editing. Documents are stored in a binary format encoded as base64. The MCP server can now read and write document content using the `pycrdt` library.

**Key Concepts:**
- **Yjs**: Conflict-free Replicated Data Type (CRDT) for real-time collaboration
- **BlockNote**: Rich text editor format used by Docs frontend (XML structure)
- **pycrdt**: Python implementation of Yjs CRDT (v0.12.0+)
- **Content Storage**: S3 object storage (not PostgreSQL database)
- **WebSocket Flag**: REST API requires `websocket: true` for content updates

### Document Structure

Documents use BlockNote XML structure within Yjs format:

```xml
<blockGroup>
  <blockContainer id="uuid">
    <paragraph textColor="default" textAlignment="left" backgroundColor="default">
      Text content here
    </paragraph>
  </blockContainer>
</blockGroup>
```

### Content Editing Workflow

**Read document content:**
```python
async with DocsAPIClient(config=config) as client:
    text = await client.get_content_text(document_id)
    print(f"Document content: {text}")
```

**Update document content:**
```python
# With plain text
await client.update_content(document_id, "New content here", format="text")

# With markdown
markdown_content = "# Title\n\nParagraph with **bold** text"
await client.update_content(document_id, markdown_content, format="markdown")
```

**Apply AI transformation:**
```python
# Correct grammar and save
await client.apply_ai_transform_to_content(document_id, "correct")

# Summarize content and save
await client.apply_ai_transform_to_content(document_id, "summarize")
```

**Translate content:**
```python
# Translate to English and save
await client.apply_ai_translate_to_content(document_id, "en")
```

### New MCP Tools (v0.2.0)

1. **`docs_get_content_text`** - Read document content as plain text
2. **`docs_update_content`** - Update document with text or markdown
3. **`docs_apply_ai_transform`** - Apply AI transformation and save to document
4. **`docs_apply_ai_translate`** - Translate and save document content

### Yjs Utilities

The `yjs_utils.py` module provides utilities for Yjs document manipulation:

```python
from docs_mcp_server.yjs_utils import YjsDocumentUtils

# Extract text from Yjs document
text = YjsDocumentUtils.extract_text(ydoc_base64)

# Create Yjs document from text
ydoc_base64 = YjsDocumentUtils.create_from_text("My content")

# Create Yjs document from markdown
ydoc_base64 = YjsDocumentUtils.create_from_markdown("# Title\n\nContent")

# Debug: Get document structure info
info = YjsDocumentUtils.get_structure_info(ydoc_base64)
```

### Important Implementation Notes

**XmlElement Construction**: pycrdt XmlElement requires all attributes and children in constructor:
```python
# ✓ CORRECT
paragraph = pycrdt.XmlElement(
    "paragraph",
    {"textColor": "default", "textAlignment": "left"},
    [pycrdt.XmlText("text content")]
)

# ✗ WRONG - attribute assignment not supported
paragraph["textColor"] = "default"  # TypeError
```

**XmlFragment Assignment**: Create fragment with children, then assign to document:
```python
# ✓ CORRECT
doc_store = pycrdt.XmlFragment([block_group])
ydoc["document-store"] = doc_store

# ✗ WRONG - push() method doesn't exist
doc_store.push([block_group])  # AttributeError
```

**WebSocket Flag Requirement**: Content updates require `websocket: true` flag in REST API:
```python
await client._request(
    "PATCH",
    f"documents/{doc_id}/",
    json_data={"content": ydoc_b64, "websocket": True}  # Required!
)
```

### Markdown Conversion API

The MCP server uses the official Docs API endpoint `/api/v1.0/convert/` for markdown conversion. This endpoint:
- Uses `@blocknote/server-util` library (official BlockNote implementation)
- Supports ALL BlockNote markdown features:
  - Headings (H1-H6)
  - Paragraphs with inline formatting (bold, italic, strikethrough, code)
  - Bullet lists and numbered lists
  - Checkboxes
  - Quotes
  - Code blocks with syntax highlighting
  - Tables
  - Links and images
  - Callouts

This ensures 100% compatibility with the Docs frontend editor.

### Limitations

- **Real-time Collaboration**: REST API only. WebSocket collaboration requires separate implementation.
- **Permissions**: Content editing requires `editor` or `owner` role on the document.

## Python Version Requirements

**Requires Python 3.10+** due to MCP package compatibility. The project originally supported 3.8-3.12, but MCP SDK requires ≥3.10.

CI tests run on Python 3.10, 3.11, and 3.12 only (see recent commits).

## Common Patterns

### Adding a New Tool

1. Add tool definition to `list_tools()` in [server.py](src/docs_mcp_server/server.py)
2. Add corresponding handler case in `call_tool()`
3. Implement the API method in `DocsAPIClient` if needed
4. Add Pydantic models for request/response if needed
5. Add tests in `tests/test_server.py`

### Adding a New API Endpoint

1. Define request/response models in [models.py](src/docs_mcp_server/models.py)
2. Implement method in `DocsAPIClient` using `_request()` helper
3. Add custom exception handling if needed
4. Export models from `__init__.py`

### Testing Conventions

- Use pytest fixtures defined in `conftest.py`
- Mock httpx responses, not the API client methods
- Use `pytest-asyncio` for async tests (auto mode enabled in pyproject.toml)
- Mark slow tests with `@pytest.mark.slow` (if configured)

## Type Checking Notes

- Project uses type hints but `mypy` strict mode is **disabled** (see [pyproject.toml:132](pyproject.toml#L132))
- Some type ignores are present for enum conversions (e.g., `role=role  # type: ignore`)
- Tests have relaxed type checking (`disallow_untyped_defs = false`)

## Pydantic Migration

This project uses **Pydantic v2**:
- Use `.model_dump()` instead of `.dict()` (though `.dict()` still works for now)
- Use `.parse_obj()` for deserialization (v1 compatibility)
- Field validators use `@field_validator` decorator with `mode="after"`

## MCP Server Specifics

**Stdio Transport**: Server communicates via stdin/stdout using `stdio_server()` context manager. Do not print to stdout in production code - use stderr or logging instead.

**Tool Arguments**: All tool arguments come as a dictionary. Extract with `.get()` for optional fields and direct access for required fields.

**Resource URIs**: Follow the pattern `docs://resource-name` (e.g., `docs://documents`, `docs://favorites`)

## Package Structure

```
src/docs_mcp_server/
├── __init__.py       # Public API exports and convenience functions
├── __main__.py       # Entry point for `python -m docs_mcp_server`
├── cli.py            # Click-based CLI implementation
├── client.py         # HTTP client with retry/rate limiting
├── config.py         # Pydantic settings and configuration
├── exceptions.py     # Custom exception hierarchy
├── models.py         # Pydantic models for all API entities
├── server.py         # MCP server implementation
└── yjs_utils.py      # Yjs document manipulation utilities (v0.2.0+)
```

## CI/CD

The project uses GitHub Actions with three workflows:
- **CI**: Tests on Python 3.10-3.12, linting, type checking
- **Security**: Bandit and safety checks
- **Release**: Automated PyPI publishing on tags

Pre-commit hooks run ruff formatting and linting before commits.
