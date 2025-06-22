"""Custom exceptions for the Docs MCP Server."""

from typing import Any, Dict, Optional


class DocsError(Exception):
    """Base exception class for all Docs MCP Server errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DocsAPIError(DocsError):
    """Exception raised when the Docs API returns an error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, {"status_code": status_code, "response": response_data})
        self.status_code = status_code
        self.response_data = response_data or {}


class DocsAuthError(DocsError):
    """Exception raised when authentication with the Docs API fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)


class DocsConnectionError(DocsError):
    """Exception raised when connection to the Docs API fails."""

    def __init__(self, message: str = "Failed to connect to Docs API") -> None:
        super().__init__(message)


class DocsTimeoutError(DocsError):
    """Exception raised when a request to the Docs API times out."""

    def __init__(self, message: str = "Request to Docs API timed out") -> None:
        super().__init__(message)


class DocsValidationError(DocsError):
    """Exception raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message, {"field": field} if field else {})
        self.field = field


class DocsNotFoundError(DocsAPIError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, status_code=404)
        self.resource_type = resource_type
        self.resource_id = resource_id


class DocsPermissionError(DocsAPIError):
    """Exception raised when the user doesn't have permission for an operation."""

    def __init__(self, operation: str, resource: Optional[str] = None) -> None:
        message = f"Permission denied for operation: {operation}"
        if resource:
            message += f" on {resource}"
        super().__init__(message, status_code=403)
        self.operation = operation
        self.resource = resource


class DocsRateLimitError(DocsAPIError):
    """Exception raised when the API rate limit is exceeded."""

    def __init__(self, retry_after: Optional[int] = None) -> None:
        message = "API rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
