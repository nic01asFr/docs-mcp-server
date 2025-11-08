"""Professional HTTP client for the Docs API."""

import asyncio
import base64
import logging
from typing import Any
from uuid import UUID

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
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
    AITransformRequest,
    AITransformResponse,
    AITranslateRequest,
    AITranslateResponse,
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
)

logger = logging.getLogger(__name__)


class DocsAPIClient:
    """Professional async HTTP client for the Docs API."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        config: DocsConfig | None = None,
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

        self._client: httpx.AsyncClient | None = None
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
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
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
        filters: dict[str, Any] | None = None,
    ) -> DocumentListResponse:
        """List documents with optional filters."""
        params = filters or {}
        data = await self._request("GET", "documents/", params=params)
        return DocumentListResponse.parse_obj(data)

    async def get_document(self, document_id: str | UUID) -> Document:
        """Get a document by ID."""
        data = await self._request("GET", f"documents/{document_id}/")
        return Document.parse_obj(data)

    async def create_document(
        self,
        title: str,
        content: str | None = None,
        parent_id: str | UUID | None = None,
    ) -> Document:
        """Create a new document.

        Note: The API requires content to be base64-encoded.
        This method handles the encoding automatically.
        """
        # Encode content to base64 if provided
        encoded_content = None
        if content is not None:
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('ascii')

        request_data = DocumentCreateRequest(
            title=title,
            content=encoded_content,
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
        document_id: str | UUID,
        title: str | None = None,
        content: str | None = None,
    ) -> Document:
        """Update a document.

        Note: Currently, the API does not support updating document content.
        Only the title can be updated. Content parameter is kept for API
        compatibility but may not work.
        """
        request_data = DocumentUpdateRequest(title=title, content=content)
        data = await self._request(
            "PATCH",
            f"documents/{document_id}/",
            json_data=request_data.dict(exclude_none=True),
        )
        return Document.parse_obj(data)

    async def delete_document(self, document_id: str | UUID) -> dict[str, Any]:
        """Delete a document (soft delete)."""
        return await self._request("DELETE", f"documents/{document_id}/")

    async def restore_document(self, document_id: str | UUID) -> dict[str, Any]:
        """Restore a soft-deleted document."""
        return await self._request("POST", f"documents/{document_id}/restore/")

    async def move_document(
        self,
        document_id: str | UUID,
        target_id: str | UUID,
        position: str = "last-child",
    ) -> dict[str, Any]:
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
        document_id: str | UUID,
        with_accesses: bool = False,
    ) -> dict[str, Any]:
        """Duplicate a document."""
        request_data = DocumentDuplicateRequest(with_accesses=with_accesses)
        return await self._request(
            "POST",
            f"documents/{document_id}/duplicate/",
            json_data=request_data.dict(),
        )

    # Document content management with Yjs

    async def get_content_text(self, document_id: str | UUID) -> str:
        """Get document content as plain text.

        Extracts plain text from the Yjs document format.

        Args:
            document_id: ID of the document to read

        Returns:
            Plain text content extracted from the Yjs document

        Raises:
            DocsAPIError: If the document cannot be retrieved
            YjsDocumentError: If the content cannot be decoded
        """
        from .yjs_utils import extract_text

        doc = await self.get_document(document_id)
        return extract_text(doc.content)

    async def update_content(
        self,
        document_id: str | UUID,
        content: str,
        format: str = "text",
    ) -> Document:
        """Update document content with text or markdown.

        Converts the provided content to Yjs format and updates the document.

        Args:
            document_id: ID of the document to update
            content: New content as plain text or markdown
            format: Content format - "text" or "markdown" (default: "text")

        Returns:
            Updated document

        Raises:
            DocsAPIError: If the update fails
            YjsDocumentError: If the content cannot be encoded
            ValueError: If format is invalid

        Note:
            This method uses the Yjs document format internally.
            The API requires the websocket flag to be set for content updates.

        Example:
            >>> await client.update_content(
            ...     doc_id,
            ...     "Hello **World**!",
            ...     format="markdown"
            ... )
        """
        from .yjs_utils import create_from_markdown, create_from_text

        if format not in ("text", "markdown"):
            raise ValueError(f"Invalid format: {format}. Must be 'text' or 'markdown'")

        # Convert to Yjs format
        if format == "markdown":
            ydoc_b64 = create_from_markdown(content, self.config.base_url, self.config.api_token)
        else:
            ydoc_b64 = create_from_text(content)

        # Update via API with websocket flag
        data = await self._request(
            "PATCH",
            f"documents/{document_id}/",
            json_data={"content": ydoc_b64, "websocket": True},
        )

        return Document.parse_obj(data)

    async def apply_ai_transform_to_content(
        self,
        document_id: str | UUID,
        action: str,
        text: str | None = None,
    ) -> Document:
        """Apply AI transformation and update document content.

        Workflow:
        1. Get current content (if text not provided)
        2. Call AI transform
        3. Update document with AI result

        Args:
            document_id: ID of the document
            action: AI action - "correct", "rephrase", "summarize", "prompt",
                   "beautify", "emojify"
            text: Text to transform (if None, uses current document content)

        Returns:
            Updated document

        Raises:
            DocsAPIError: If AI transform or update fails
            YjsDocumentError: If content cannot be processed

        Example:
            >>> # Correct grammar in current document
            >>> await client.apply_ai_transform_to_content(doc_id, "correct")
            >>>
            >>> # Summarize specific text
            >>> await client.apply_ai_transform_to_content(
            ...     doc_id,
            ...     "summarize",
            ...     text="Long text to summarize..."
            ... )
        """
        # Get text to transform
        if text is None:
            text = await self.get_content_text(document_id)

        # Apply AI transformation
        result = await self.ai_transform(document_id, text, action)

        # Update document with AI result (assuming markdown format)
        return await self.update_content(document_id, result.answer, format="markdown")

    async def apply_ai_translate_to_content(
        self,
        document_id: str | UUID,
        language: str,
        text: str | None = None,
    ) -> Document:
        """Apply AI translation and update document content.

        Workflow:
        1. Get current content (if text not provided)
        2. Call AI translate
        3. Update document with translation

        Args:
            document_id: ID of the document
            language: Target language code (e.g., "en", "fr", "es")
            text: Text to translate (if None, uses current document content)

        Returns:
            Updated document

        Raises:
            DocsAPIError: If AI translate or update fails
            YjsDocumentError: If content cannot be processed

        Example:
            >>> # Translate current document to English
            >>> await client.apply_ai_translate_to_content(doc_id, "en")
            >>>
            >>> # Translate specific text to French
            >>> await client.apply_ai_translate_to_content(
            ...     doc_id,
            ...     "fr",
            ...     text="Hello world"
            ... )
        """
        # Get text to translate
        if text is None:
            text = await self.get_content_text(document_id)

        # Apply AI translation
        result = await self.ai_translate(document_id, text, language)

        # Update document with translation
        return await self.update_content(document_id, result.answer, format="markdown")

    # Document access management

    async def list_accesses(self, document_id: str | UUID) -> list[DocumentAccess]:
        """List document access permissions."""
        data = await self._request("GET", f"documents/{document_id}/accesses/")

        if "results" in data:
            return [DocumentAccess.parse_obj(item) for item in data["results"]]
        return [DocumentAccess.parse_obj(item) for item in data]

    async def grant_access(
        self,
        document_id: str | UUID,
        user_id: str | UUID | None = None,
        user_email: str | None = None,
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
        document_id: str | UUID,
        access_id: str | UUID,
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
        document_id: str | UUID,
        access_id: str | UUID,
    ) -> dict[str, Any]:
        """Revoke document access."""
        return await self._request(
            "DELETE", f"documents/{document_id}/accesses/{access_id}/"
        )

    # Invitations

    async def create_invitation(
        self,
        document_id: str | UUID,
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

    async def list_invitations(self, document_id: str | UUID) -> list[Invitation]:
        """List invitations for a document."""
        data = await self._request("GET", f"documents/{document_id}/invitations/")

        if "results" in data:
            return [Invitation.parse_obj(item) for item in data["results"]]
        return [Invitation.parse_obj(item) for item in data]

    async def delete_invitation(
        self,
        document_id: str | UUID,
        invitation_id: str | UUID,
    ) -> dict[str, Any]:
        """Delete an invitation."""
        return await self._request(
            "DELETE", f"documents/{document_id}/invitations/{invitation_id}/"
        )

    # User search

    async def search_users(self, query: str, document_id: str | UUID | None = None) -> UserListResponse:
        """Search users by email."""
        params = {"q": query}
        if document_id:
            params["document_id"] = str(document_id)

        data = await self._request("GET", "users/", params=params)

        # Handle case where API returns empty list instead of paginated response
        if isinstance(data, list):
            return UserListResponse(results=data)

        return UserListResponse.parse_obj(data)

    async def get_current_user(self) -> User:
        """Get current user information."""
        data = await self._request("GET", "users/me/")
        return User.parse_obj(data)

    # Favorites

    async def add_favorite(self, document_id: str | UUID) -> dict[str, Any]:
        """Add document to favorites."""
        return await self._request("POST", f"documents/{document_id}/favorite/")

    async def remove_favorite(self, document_id: str | UUID) -> dict[str, Any]:
        """Remove document from favorites."""
        return await self._request("DELETE", f"documents/{document_id}/favorite/")

    async def list_favorites(self) -> DocumentListResponse:
        """List favorite documents."""
        data = await self._request("GET", "documents/favorite_list/")
        return DocumentListResponse.parse_obj(data)

    # Tree operations

    async def get_children(self, document_id: str | UUID) -> list[ListDocument]:
        """Get child documents."""
        data = await self._request("GET", f"documents/{document_id}/children/")

        if "results" in data:
            return [ListDocument.parse_obj(item) for item in data["results"]]
        return [ListDocument.parse_obj(item) for item in data]

    async def get_descendants(self, document_id: str | UUID) -> list[ListDocument]:
        """Get all descendant documents."""
        data = await self._request("GET", f"documents/{document_id}/descendants/")

        if "results" in data:
            return [ListDocument.parse_obj(item) for item in data["results"]]
        return [ListDocument.parse_obj(item) for item in data]

    async def get_tree(self, document_id: str | UUID) -> list[ListDocument]:
        """Get document tree structure."""
        data = await self._request("GET", f"documents/{document_id}/tree/")

        # Handle different response formats
        if isinstance(data, dict):
            # If it's a dict with results key
            if "results" in data:
                return [ListDocument.parse_obj(item) for item in data["results"]]
            # If it's a single document dict, wrap in list
            return [ListDocument.parse_obj(data)]
        elif isinstance(data, list):
            return [ListDocument.parse_obj(item) for item in data]

        # Fallback: return empty list
        return []

    # Document management operations

    async def can_edit(self, document_id: str | UUID) -> dict[str, Any]:
        """Check if current user can edit document."""
        return await self._request("GET", f"documents/{document_id}/can-edit/")

    async def mask_document(self, document_id: str | UUID) -> dict[str, Any]:
        """Mask/hide a document."""
        return await self._request("POST", f"documents/{document_id}/mask/")

    async def unmask_document(self, document_id: str | UUID) -> dict[str, Any]:
        """Unmask/show a document."""
        return await self._request("DELETE", f"documents/{document_id}/mask/")

    # Versions

    async def list_versions(
        self,
        document_id: str | UUID,
        from_version_id: str | None = None,
        page_size: int | None = None,
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
        document_id: str | UUID,
        version_id: str,
    ) -> dict[str, Any]:
        """Get a specific document version."""
        return await self._request(
            "GET", f"documents/{document_id}/versions/{version_id}/"
        )

    async def delete_version(
        self,
        document_id: str | UUID,
        version_id: str,
    ) -> dict[str, Any]:
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
        document_id: str | UUID,
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
        document_id: str | UUID,
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
        document_id: str | UUID,
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

    async def get_config(self) -> dict[str, Any]:
        """Get public configuration."""
        return await self._request("GET", "config/")
