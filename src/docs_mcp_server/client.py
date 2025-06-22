"""Professional HTTP client for the Docs API."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .config import DocsConfig
from .exceptions import (
    DocsAPIError,
    DocsAuthError,
    DocsConnectionError,
    DocsNotFoundError,
    DocsPermissionError,
    DocsRateLimitError,
    DocsTimeoutError,
    DocsValidationError,
)
from .models import (
    Document,
    DocumentAccess,
    DocumentAccessCreateRequest,
    DocumentAccessUpdateRequest,
    DocumentCreateRequest,
    DocumentDuplicateRequest,
    DocumentListResponse,
    DocumentMoveRequest,
    DocumentUpdateRequest,
    DocumentVersionList,
    Invitation,
    InvitationCreateRequest,
    LinkConfigurationRequest,
    ListDocument,
    User,
    UserListResponse,
    AITransformRequest,
    AITranslateRequest,
    AITransformResponse,
    AITranslateResponse,
)

logger = logging.getLogger(__name__)


class DocsAPIClient:
    """Professional async HTTP client for the Docs API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        config: Optional[DocsConfig] = None,
    ) -> None:
        """Initialize the Docs API client.
        
        Args:
            base_url: Base URL of the Docs instance
            token: Authentication token
            config: Configuration object (overrides base_url and token)
        """
        if config:
            self.config = config
        else:
            if not base_url or not token:
                raise ValueError("Either config or both base_url and token must be provided")
            # Create a minimal config
            import os
            os.environ["DOCS_BASE_URL"] = base_url
            os.environ["DOCS_API_TOKEN"] = token
            self.config = DocsConfig()

        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = asyncio.Semaphore(int(self.config.rate_limit))

    async def __aenter__(self) -> "DocsAPIClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure the HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.config.auth_headers,
                follow_redirects=True,
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((DocsConnectionError, DocsTimeoutError)),
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make an HTTP request with error handling and retries."""
        await self._ensure_client()
        assert self._client is not None

        url = f"{self.config.api_base_url}/{endpoint.lstrip('/')}"
        
        # Rate limiting
        async with self._rate_limiter:
            try:
                logger.debug(f"Making {method} request to {url}")
                
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    **kwargs,
                )
                
                # Handle different response types
                if response.status_code == 204:  # No Content
                    return {"success": True}
                
                if response.status_code == 401:
                    raise DocsAuthError("Authentication failed - invalid or expired token")
                
                if response.status_code == 403:
                    raise DocsPermissionError("Permission denied")
                
                if response.status_code == 404:
                    raise DocsNotFoundError("Resource", "unknown")
                
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_seconds = int(retry_after) if retry_after else None
                    raise DocsRateLimitError(retry_seconds)
                
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"detail": response.text}
                    
                    raise DocsAPIError(
                        message=error_data.get("detail", f"HTTP {response.status_code}"),
                        status_code=response.status_code,
                        response_data=error_data,
                    )
                
                response.raise_for_status()
                
                try:
                    return response.json()
                except Exception:
                    # Some endpoints might return non-JSON responses
                    return {"data": response.text}
                    
            except httpx.TimeoutException as e:
                raise DocsTimeoutError(f"Request timed out: {e}") from e
            except httpx.ConnectError as e:
                raise DocsConnectionError(f"Failed to connect: {e}") from e
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 422:
                    # Validation error
                    try:
                        error_data = e.response.json()
                        raise DocsValidationError(
                            message=error_data.get("detail", "Validation error"),
                        )
                    except Exception:
                        raise DocsValidationError("Validation error") from e
                raise

    # Document CRUD operations

    async def list_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
    ) -> DocumentListResponse:
        """List documents with optional filters."""
        params = filters or {}
        data = await self._request("GET", "documents/", params=params)
        return DocumentListResponse.parse_obj(data)

    async def get_document(self, document_id: Union[str, UUID]) -> Document:
        """Get a document by ID."""
        data = await self._request("GET", f"documents/{document_id}/")
        return Document.parse_obj(data)

    async def create_document(
        self,
        title: str,
        content: Optional[str] = None,
        parent_id: Optional[Union[str, UUID]] = None,
    ) -> Document:
        """Create a new document."""
        request_data = DocumentCreateRequest(
            title=title,
            content=content,
        )
        
        if parent_id:
            # Create as child
            data = await self._request(
                "POST",
                f"documents/{parent_id}/children/",
                json_data=request_data.dict(exclude_none=True),
            )
        else:
            # Create as root document
            data = await self._request(
                "POST",
                "documents/",
                json_data=request_data.dict(exclude_none=True),
            )
        
        return Document.parse_obj(data)

    async def update_document(
        self,
        document_id: Union[str, UUID],
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Document:
        """Update a document."""
        request_data = DocumentUpdateRequest(title=title, content=content)
        data = await self._request(
            "PATCH",
            f"documents/{document_id}/",
            json_data=request_data.dict(exclude_none=True),
        )
        return Document.parse_obj(data)

    async def delete_document(self, document_id: Union[str, UUID]) -> Dict[str, Any]:
        """Delete a document (soft delete)."""
        return await self._request("DELETE", f"documents/{document_id}/")

    async def restore_document(self, document_id: Union[str, UUID]) -> Dict[str, Any]:
        """Restore a soft-deleted document."""
        return await self._request("POST", f"documents/{document_id}/restore/")

    async def move_document(
        self,
        document_id: Union[str, UUID],
        target_id: Union[str, UUID],
        position: str = "last-child",
    ) -> Dict[str, Any]:
        """Move a document in the tree structure."""
        request_data = DocumentMoveRequest(
            target_document_id=UUID(str(target_id)),
            position=position,  # type: ignore
        )
        return await self._request(
            "POST",
            f"documents/{document_id}/move/",
            json_data=request_data.dict(),
        )

    async def duplicate_document(
        self,
        document_id: Union[str, UUID],
        with_accesses: bool = False,
    ) -> Dict[str, Any]:
        """Duplicate a document."""
        request_data = DocumentDuplicateRequest(with_accesses=with_accesses)
        return await self._request(
            "POST",
            f"documents/{document_id}/duplicate/",
            json_data=request_data.dict(),
        )

    # Document access management

    async def list_accesses(self, document_id: Union[str, UUID]) -> List[DocumentAccess]:
        """List document access permissions."""
        data = await self._request("GET", f"documents/{document_id}/accesses/")
        
        if "results" in data:
            return [DocumentAccess.parse_obj(item) for item in data["results"]]
        return [DocumentAccess.parse_obj(item) for item in data]

    async def grant_access(
        self,
        document_id: Union[str, UUID],
        user_id: Optional[Union[str, UUID]] = None,
        user_email: Optional[str] = None,
        role: str = "reader",
    ) -> DocumentAccess:
        """Grant access to a document."""
        if not user_id and not user_email:
            raise ValueError("Either user_id or user_email must be provided")
        
        # If email provided, search for user first
        if user_email and not user_id:
            users = await self.search_users(user_email)
            if not users.results:
                raise DocsNotFoundError("User", user_email)
            user_id = users.results[0].id

        request_data = DocumentAccessCreateRequest(
            user_id=UUID(str(user_id)) if user_id else None,
            role=role,  # type: ignore
        )
        data = await self._request(
            "POST",
            f"documents/{document_id}/accesses/",
            json_data=request_data.dict(exclude_none=True),
        )
        return DocumentAccess.parse_obj(data)

    async def update_access(
        self,
        document_id: Union[str, UUID],
        access_id: Union[str, UUID],
        role: str,
    ) -> DocumentAccess:
        """Update document access permissions."""
        request_data = DocumentAccessUpdateRequest(role=role)  # type: ignore
        data = await self._request(
            "PATCH",
            f"documents/{document_id}/accesses/{access_id}/",
            json_data=request_data.dict(),
        )
        return DocumentAccess.parse_obj(data)

    async def revoke_access(
        self,
        document_id: Union[str, UUID],
        access_id: Union[str, UUID],
    ) -> Dict[str, Any]:
        """Revoke document access."""
        return await self._request(
            "DELETE", f"documents/{document_id}/accesses/{access_id}/"
        )

    # Invitations

    async def create_invitation(
        self,
        document_id: Union[str, UUID],
        email: str,
        role: str = "reader",
    ) -> Invitation:
        """Create an invitation to a document."""
        request_data = InvitationCreateRequest(email=email, role=role)  # type: ignore
        data = await self._request(
            "POST",
            f"documents/{document_id}/invitations/",
            json_data=request_data.dict(),
        )
        return Invitation.parse_obj(data)

    async def list_invitations(self, document_id: Union[str, UUID]) -> List[Invitation]:
        """List invitations for a document."""
        data = await self._request("GET", f"documents/{document_id}/invitations/")
        
        if "results" in data:
            return [Invitation.parse_obj(item) for item in data["results"]]
        return [Invitation.parse_obj(item) for item in data]

    async def delete_invitation(
        self,
        document_id: Union[str, UUID],
        invitation_id: Union[str, UUID],
    ) -> Dict[str, Any]:
        """Delete an invitation."""
        return await self._request(
            "DELETE", f"documents/{document_id}/invitations/{invitation_id}/"
        )

    # User search

    async def search_users(self, query: str, document_id: Optional[Union[str, UUID]] = None) -> UserListResponse:
        """Search users by email."""
        params = {"q": query}
        if document_id:
            params["document_id"] = str(document_id)
        
        data = await self._request("GET", "users/", params=params)
        return UserListResponse.parse_obj(data)

    async def get_current_user(self) -> User:
        """Get current user information."""
        data = await self._request("GET", "users/me/")
        return User.parse_obj(data)

    # Favorites

    async def add_favorite(self, document_id: Union[str, UUID]) -> Dict[str, Any]:
        """Add document to favorites."""
        return await self._request("POST", f"documents/{document_id}/favorite/")

    async def remove_favorite(self, document_id: Union[str, UUID]) -> Dict[str, Any]:
        """Remove document from favorites."""
        return await self._request("DELETE", f"documents/{document_id}/favorite/")

    async def list_favorites(self) -> DocumentListResponse:
        """List favorite documents."""
        data = await self._request("GET", "documents/favorite/")
        return DocumentListResponse.parse_obj(data)

    # Tree operations

    async def get_children(self, document_id: Union[str, UUID]) -> List[ListDocument]:
        """Get child documents."""
        data = await self._request("GET", f"documents/{document_id}/children/")
        
        if "results" in data:
            return [ListDocument.parse_obj(item) for item in data["results"]]
        return [ListDocument.parse_obj(item) for item in data]

    async def get_descendants(self, document_id: Union[str, UUID]) -> List[ListDocument]:
        """Get all descendant documents."""
        data = await self._request("GET", f"documents/{document_id}/descendants/")
        
        if "results" in data:
            return [ListDocument.parse_obj(item) for item in data["results"]]
        return [ListDocument.parse_obj(item) for item in data]

    async def get_tree(self, document_id: Union[str, UUID]) -> List[ListDocument]:
        """Get document tree structure."""
        data = await self._request("GET", f"documents/{document_id}/tree/")
        return [ListDocument.parse_obj(item) for item in data]

    # Versions

    async def list_versions(
        self,
        document_id: Union[str, UUID],
        from_version_id: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> DocumentVersionList:
        """List document versions."""
        params = {}
        if from_version_id:
            params["version_id"] = from_version_id
        if page_size:
            params["page_size"] = page_size
        
        data = await self._request(
            "GET", f"documents/{document_id}/versions/", params=params
        )
        return DocumentVersionList.parse_obj(data)

    async def get_version(
        self,
        document_id: Union[str, UUID],
        version_id: str,
    ) -> Dict[str, Any]:
        """Get a specific document version."""
        return await self._request(
            "GET", f"documents/{document_id}/versions/{version_id}/"
        )

    async def delete_version(
        self,
        document_id: Union[str, UUID],
        version_id: str,
    ) -> Dict[str, Any]:
        """Delete a document version."""
        return await self._request(
            "DELETE", f"documents/{document_id}/versions/{version_id}/"
        )

    # Trashbin

    async def list_trashbin(self) -> DocumentListResponse:
        """List documents in trashbin."""
        data = await self._request("GET", "documents/trashbin/")
        return DocumentListResponse.parse_obj(data)

    # Link configuration

    async def update_link_configuration(
        self,
        document_id: Union[str, UUID],
        link_reach: str,
        link_role: str,
    ) -> Document:
        """Update document link configuration."""
        request_data = LinkConfigurationRequest(
            link_reach=link_reach,  # type: ignore
            link_role=link_role,  # type: ignore
        )
        data = await self._request(
            "PUT",
            f"documents/{document_id}/link-configuration/",
            json_data=request_data.dict(),
        )
        return Document.parse_obj(data)

    # AI features (if enabled)

    async def ai_transform(
        self,
        document_id: Union[str, UUID],
        text: str,
        action: str,
    ) -> AITransformResponse:
        """Transform text using AI."""
        request_data = AITransformRequest(text=text, action=action)
        data = await self._request(
            "POST",
            f"documents/{document_id}/ai-transform/",
            json_data=request_data.dict(),
        )
        return AITransformResponse.parse_obj(data)

    async def ai_translate(
        self,
        document_id: Union[str, UUID],
        text: str,
        language: str,
    ) -> AITranslateResponse:
        """Translate text using AI."""
        request_data = AITranslateRequest(text=text, language=language)
        data = await self._request(
            "POST",
            f"documents/{document_id}/ai-translate/",
            json_data=request_data.dict(),
        )
        return AITranslateResponse.parse_obj(data)

    # Configuration

    async def get_config(self) -> Dict[str, Any]:
        """Get public configuration."""
        return await self._request("GET", "config/")
