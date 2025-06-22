# Contributing to DINUM Docs MCP Server

We welcome contributions to the DINUM Docs MCP Server! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Access to a DINUM Docs instance for testing

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/docs-mcp-server.git
   cd docs-mcp-server
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Environment Configuration

Create a `.env` file for testing:

```bash
DOCS_BASE_URL=https://your-test-docs-instance.com
DOCS_API_TOKEN=your-test-token
DOCS_TIMEOUT=30
DOCS_MAX_RETRIES=3
```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Ruff**: For linting and formatting
- **MyPy**: For type checking
- **Black**: For code formatting (via Ruff)
- **isort**: For import sorting (via Ruff)

Run all checks:

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/docs_mcp_server
```

### Testing

We maintain comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docs_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### Documentation

Update documentation when making changes:

```bash
# Build documentation locally
mkdocs serve

# Build for production
mkdocs build
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run the full test suite**:
   ```bash
   pytest
   ruff check src/ tests/
   mypy src/docs_mcp_server
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `ci:` CI/CD changes
- `chore:` Maintenance tasks

Examples:
```
feat: add support for document templates
fix: handle API timeout errors gracefully
docs: update installation guide
test: add integration tests for access management
```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Python version
- Package version
- DINUM Docs instance version (if known)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

### Feature Requests

For new features:

- Describe the use case
- Explain the expected behavior
- Consider backward compatibility
- Provide examples if possible

### Code Contributions

We welcome:

- Bug fixes
- New MCP tools
- Performance improvements
- Documentation improvements
- Test coverage improvements
- API client enhancements

## Architecture Guidelines

### Project Structure

```
src/docs_mcp_server/
├── __init__.py          # Package exports
├── server.py            # MCP server implementation
├── client.py            # API client
├── config.py            # Configuration management
├── models.py            # Data models
├── exceptions.py        # Custom exceptions
└── cli.py              # Command-line interface
```

### Design Principles

1. **Modularity**: Keep components loosely coupled
2. **Type Safety**: Use type hints throughout
3. **Error Handling**: Provide clear, actionable error messages
4. **Testing**: Maintain high test coverage
5. **Documentation**: Keep docs up-to-date with code
6. **Backward Compatibility**: Avoid breaking changes when possible

### Adding New Tools

When adding new MCP tools:

1. Add the API method to `DocsAPIClient`
2. Add the tool definition to `DocsServer.list_tools()`
3. Add the tool handler to `DocsServer.call_tool()`
4. Add comprehensive tests
5. Update documentation

Example:

```python
# In client.py
async def new_operation(self, param: str) -> SomeModel:
    """Perform a new operation."""
    response = await self._request("GET", f"/api/new-endpoint/{param}")
    return SomeModel(**response)

# In server.py (list_tools)
Tool(
    name="docs_new_operation",
    description="Perform a new operation",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param"]
    }
)

# In server.py (call_tool)
elif tool_name == "docs_new_operation":
    result = await client.new_operation(args["param"])
```

## Security

- Never commit API tokens or sensitive data
- Use environment variables for configuration
- Follow security best practices for HTTP clients
- Report security vulnerabilities privately

## Release Process

Releases are automated via GitHub Actions:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a GitHub release
4. GitHub Actions will build and publish to PyPI

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues and discussions first
- Join our community channels (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
