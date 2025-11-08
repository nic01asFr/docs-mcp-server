"""Pydantic models for the Docs API data structures."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


class RoleChoice(str, Enum):
    """Available user roles in Docs."""

    READER = "reader"
    EDITOR = "editor"
    ADMINISTRATOR = "administrator"
    OWNER = "owner"


class LinkReachChoice(str, Enum):
    """Document link reach levels."""

    RESTRICTED = "restricted"
    AUTHENTICATED = "authenticated"
    PUBLIC = "public"


class LinkRoleChoice(str, Enum):
    """Document link roles."""

    READER = "reader"
    EDITOR = "editor"


class MovePositionChoice(str, Enum):
    """Document move positions."""

    FIRST_CHILD = "first-child"
    LAST_CHILD = "last-child"
    LEFT = "left"
    RIGHT = "right"


class User(BaseModel):
    """User model."""

    id: UUID
    email: str
    full_name: str | None = None
    short_name: str | None = None
    language: str | None = None


class UserLight(BaseModel):
    """Lightweight user model with limited fields."""

    id: UUID | None = None
    email: str | None = None
    full_name: str | None = None
    short_name: str | None = None


class DocumentAccess(BaseModel):
    """Document access permissions model."""

    id: UUID
    user: User | None = None
    user_id: UUID | None = None
    team: str | None = None
    role: RoleChoice
    abilities: dict[str, Any] = Field(default_factory=dict)


class DocumentAccessLight(BaseModel):
    """Lightweight document access model."""

    id: UUID
    user: UserLight | None = None
    team: str | None = None
    role: RoleChoice
    abilities: dict[str, Any] = Field(default_factory=dict)


class Invitation(BaseModel):
    """Document invitation model."""

    id: UUID
    email: str
    role: RoleChoice
    document: UUID
    issuer: User | None = None
    is_expired: bool
    created_at: datetime
    abilities: dict[str, Any] = Field(default_factory=dict)


class BaseDocument(BaseModel):
    """Base document model with common fields."""

    id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime
    creator: User | UUID | str | None = None
    depth: int
    path: str
    link_reach: LinkReachChoice = LinkReachChoice.RESTRICTED
    link_role: LinkRoleChoice = LinkRoleChoice.READER
    abilities: dict[str, Any] = Field(default_factory=dict)


class ListDocument(BaseDocument):
    """Document model for list views."""

    excerpt: str | None = None
    is_favorite: bool = False
    nb_accesses_ancestors: int = 0
    nb_accesses_direct: int = 0
    numchild: int = 0
    user_roles: list[RoleChoice] = Field(default_factory=list)


class Document(ListDocument):
    """Full document model with content."""

    content: str | None = None


class DocumentVersion(BaseModel):
    """Document version information."""

    version_id: str
    last_modified: datetime
    etag: str
    is_latest: bool


class DocumentVersionList(BaseModel):
    """List of document versions with pagination."""

    versions: list[DocumentVersion]
    count: int
    is_truncated: bool
    next_version_id_marker: str


class Template(BaseModel):
    """Template model."""

    id: UUID
    title: str
    description: str | None = None
    code: str | None = None
    css: str | None = None
    is_public: bool = False
    abilities: dict[str, Any] = Field(default_factory=dict)
    accesses: list[DocumentAccess] = Field(default_factory=list)


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""

    count: int
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[Any]


class DocumentListResponse(BaseModel):
    """Paginated document list response."""

    count: int
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[ListDocument]


class DocumentAccessListResponse(BaseModel):
    """Paginated document access list response."""

    count: int
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[DocumentAccess]


class InvitationListResponse(BaseModel):
    """Paginated invitation list response."""

    count: int
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[Invitation]


class UserListResponse(BaseModel):
    """User search response."""

    count: int | None = None
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[User]


class ErrorDetail(BaseModel):
    """API error detail model."""

    detail: str | None = None
    field_errors: dict[str, list[str]] | None = None


class APIError(BaseModel):
    """API error response model."""

    error: str
    message: str
    status_code: int
    details: dict[str, Any] | None = None


# Request models for creating/updating resources

class DocumentCreateRequest(BaseModel):
    """Request model for creating a document."""

    title: str
    content: str | None = None
    id: UUID | None = None
    language: str | None = None

    @field_validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class DocumentUpdateRequest(BaseModel):
    """Request model for updating a document."""

    title: str | None = None
    content: str | None = None

    @field_validator("title")
    def validate_title(cls, v: str | None) -> str | None:
        """Validate title if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else None


class DocumentMoveRequest(BaseModel):
    """Request model for moving a document."""

    target_document_id: UUID
    position: MovePositionChoice = MovePositionChoice.LAST_CHILD


class DocumentDuplicateRequest(BaseModel):
    """Request model for duplicating a document."""

    with_accesses: bool = False


class DocumentAccessCreateRequest(BaseModel):
    """Request model for creating document access."""

    user_id: UUID | None = None
    user_email: str | None = None
    role: RoleChoice

    @field_validator("user_email")
    def validate_user_email(cls, v: str | None) -> str | None:
        """Validate email format if provided."""
        if v and "@" not in v:
            raise ValueError("Invalid email address")
        return v


class DocumentAccessUpdateRequest(BaseModel):
    """Request model for updating document access."""

    role: RoleChoice


class InvitationCreateRequest(BaseModel):
    """Request model for creating an invitation."""

    email: str
    role: RoleChoice

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.strip().lower()


class LinkConfigurationRequest(BaseModel):
    """Request model for updating document link configuration."""

    link_reach: LinkReachChoice
    link_role: LinkRoleChoice


class AITransformRequest(BaseModel):
    """Request model for AI text transformation."""

    text: str
    action: str  # prompt, correct, rephrase, summarize

    @field_validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate text is not empty."""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v


class AITranslateRequest(BaseModel):
    """Request model for AI text translation."""

    text: str
    language: str

    @field_validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate text is not empty."""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v


# Response models for specific operations

class DocumentCreateResponse(BaseModel):
    """Response model for document creation."""

    id: UUID
    message: str | None = None


class DocumentMoveResponse(BaseModel):
    """Response model for document move operation."""

    message: str


class DocumentRestoreResponse(BaseModel):
    """Response model for document restore operation."""

    detail: str


class DocumentDuplicateResponse(BaseModel):
    """Response model for document duplication."""

    id: UUID


class AITransformResponse(BaseModel):
    """Response model for AI transformation."""

    answer: str


class AITranslateResponse(BaseModel):
    """Response model for AI translation."""

    answer: str


class FavoriteResponse(BaseModel):
    """Response model for favorite operations."""

    detail: str


class FileUploadResponse(BaseModel):
    """Response model for file upload."""

    file: str  # URL to the uploaded file


class MediaCheckResponse(BaseModel):
    """Response model for media check."""

    status: str
    file: str | None = None
