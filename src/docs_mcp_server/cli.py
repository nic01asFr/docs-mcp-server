"""Command Line Interface for Docs MCP Server."""
import argparse
import asyncio
import logging
import sys

from . import DocsConfig, DocsServer, __description__, __version__
from .exceptions import DocsError


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Reduce noise from external libraries
    if not verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="docs-mcp-server",
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server with environment variables
  docs-mcp-server

  # Start server with explicit configuration
  docs-mcp-server --base-url https://docs.example.com --token your-api-token

  # Start server with custom name and verbose logging
  docs-mcp-server --name my-docs-server --verbose

Environment Variables:
  DOCS_BASE_URL     Base URL of the Docs instance
  DOCS_API_TOKEN    Authentication token for the API
  DOCS_TIMEOUT      Request timeout in seconds (default: 30)
  DOCS_MAX_RETRIES  Maximum number of retries (default: 3)

For more information, visit: https://github.com/nic01asFr/docs-mcp-server
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--base-url",
        type=str,
        help="Base URL of the Docs instance (default: from DOCS_BASE_URL env var)"
    )

    parser.add_argument(
        "--token",
        type=str,
        help="Authentication token (default: from DOCS_API_TOKEN env var)"
    )

    parser.add_argument(
        "--name",
        type=str,
        default="docs-mcp-server",
        help="Name of the MCP server (default: docs-mcp-server)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Check configuration and exit"
    )

    return parser


async def check_configuration(
    base_url: str | None = None,
    token: str | None = None
) -> bool:
    """Check if the configuration is valid.
    
    Args:
        base_url: Base URL override
        token: Token override
        
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        # Set environment variables if provided
        if base_url or token:
            import os
            if base_url:
                os.environ["DOCS_BASE_URL"] = base_url
            if token:
                os.environ["DOCS_API_TOKEN"] = token

        # Try to create config
        config = DocsConfig()
        print("OK Configuration loaded successfully")
        print(f"  Base URL: {config.base_url}")
        print(f"  Token: {'*' * (len(config.api_token) - 4) + config.api_token[-4:] if len(config.api_token) > 4 else '****'}")
        print(f"  Timeout: {config.timeout}s")
        print(f"  Max retries: {config.max_retries}")

        # Try to test the API connection
        from .client import DocsAPIClient
        async with DocsAPIClient(config=config) as client:
            user = await client.get_current_user()
            print("OK API connection successful")
            print(f"  Authenticated as: {user.email}")
            print(f"  User ID: {user.id}")

        return True

    except DocsError as e:
        print(f"ERROR Configuration error: {e.message}")
        return False
    except Exception as e:
        print(f"ERROR Unexpected error: {e!s}")
        return False


async def run_server(
    base_url: str | None = None,
    token: str | None = None,
    server_name: str = "docs-mcp-server"
) -> None:
    """Run the MCP server.
    
    Args:
        base_url: Base URL override
        token: Token override 
        server_name: Name of the MCP server
    """
    try:
        server = DocsServer(
            base_url=base_url,
            token=token,
            server_name=server_name
        )

        print(f"Starting {server_name}...")
        print(f"Base URL: {server.config.base_url}")
        print("Press Ctrl+C to stop the server")

        await server.run()

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except DocsError as e:
        print(f"Docs error: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e!s}")
        sys.exit(1)


async def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Handle config check
    if args.config_check:
        success = await check_configuration(args.base_url, args.token)
        sys.exit(0 if success else 1)

    # Run the server
    await run_server(
        base_url=args.base_url,
        token=args.token,
        server_name=args.name
    )


def cli_main() -> None:
    """Synchronous entry point for the CLI."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)  # 128 + SIGINT


if __name__ == "__main__":
    cli_main()
