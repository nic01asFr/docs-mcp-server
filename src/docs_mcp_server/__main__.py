"""Entry point for running docs-mcp-server as a module.

This allows the package to be executed as:
    python -m docs_mcp_server [arguments]
"""

import asyncio
import sys


def main():
    """Main entry point - starts MCP server directly if no args, otherwise CLI."""
    # If launched without arguments (by Cursor/Claude Desktop), start MCP server directly
    if len(sys.argv) == 1:
        import os

        from .config import DocsConfig
        from .server import DocsServer

        # Read environment variables
        base_url = os.environ.get('DOCS_BASE_URL')
        api_token = os.environ.get('DOCS_API_TOKEN')

        print(f"DEBUG: DOCS_BASE_URL = {base_url or 'NOT SET'}", file=sys.stderr)
        print(f"DEBUG: DOCS_API_TOKEN = {'SET' if api_token else 'NOT SET'}", file=sys.stderr)

        if not base_url or not api_token:
            print("ERROR: DOCS_BASE_URL and DOCS_API_TOKEN environment variables are required", file=sys.stderr)
            sys.exit(1)

        # Create config explicitly from environment variables
        try:
            config = DocsConfig(
                base_url=base_url,
                api_token=api_token
            )
            print("DEBUG: Config created successfully", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Failed to create config: {e}", file=sys.stderr)
            sys.exit(1)

        # Start the MCP server in stdio mode
        server = DocsServer(config=config)
        asyncio.run(server.run())
    else:
        # If launched with arguments, use CLI
        from .cli import cli_main
        cli_main()

if __name__ == "__main__":
    main()
