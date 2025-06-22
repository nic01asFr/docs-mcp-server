# Installation Guide

## Quick Start

```bash
pip install docs-mcp-server
```

## Development Installation

```bash
git clone https://github.com/nic01asFr/docs-mcp-server.git
cd docs-mcp-server
pip install -e ".[dev]"
```

## Requirements

- Python 3.8+
- Access to a DINUM Docs instance
- API token for authentication

## Configuration

### Environment Variables

Set the following environment variables:

```bash
export DOCS_BASE_URL="https://your-docs-instance.com"
export DOCS_API_TOKEN="your-api-token"
export DOCS_TIMEOUT=30  # Optional: request timeout in seconds
export DOCS_MAX_RETRIES=3  # Optional: maximum retry attempts
```

### Configuration File

Alternatively, you can configure via code:

```python
from docs_mcp_server import DocsConfig, DocsServer

config = DocsConfig(
    base_url="https://your-docs-instance.com",
    token="your-api-token",
    timeout=30,
    max_retries=3
)

server = DocsServer(config=config)
```

## Verification

Test your configuration:

```bash
docs-mcp-server --config-check
```

This will verify:
- Environment variables are set correctly
- API connection is working
- Authentication is valid

## Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

ENV DOCS_BASE_URL="https://your-docs-instance.com"
ENV DOCS_API_TOKEN="your-api-token"

CMD ["docs-mcp-server"]
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Increase `DOCS_TIMEOUT` value
   - Check network connectivity

2. **Authentication Failed**
   - Verify `DOCS_API_TOKEN` is correct
   - Check token permissions

3. **SSL Certificate Issues**
   - Ensure your Docs instance has valid SSL certificates
   - For self-signed certificates, you may need additional configuration

### Debug Mode

```bash
docs-mcp-server --verbose
```

This enables detailed logging for troubleshooting.
