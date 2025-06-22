"""Entry point for running docs-mcp-server as a module.

This allows the package to be executed as:
    python -m docs_mcp_server [arguments]
"""

from .cli import cli_main

if __name__ == "__main__":
    cli_main()
