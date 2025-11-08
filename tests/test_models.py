"""Tests for data models."""
import pytest
from datetime import datetime

from docs_mcp_server.models import Document, User, DocumentAccess, DocumentListResponse


def test_user_model():
    """Test User model creation and validation."""
    user_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "test@example.com",
        "full_name": "Test User",
        "short_name": "TU"
    }

    user = User(**user_data)

    assert str(user.id) == "550e8400-e29b-41d4-a716-446655440000"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.short_name == "TU"


def test_document_model():
    """Test Document model creation and validation."""
    doc_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Document",
        "content": "This is test content",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T01:00:00Z",
        "depth": 0,
        "path": "/test-document",
        "is_favorite": False,
        "nb_accesses_ancestors": 0,
        "nb_accesses_direct": 1,
        "numchild": 0,
        "user_roles": ["owner"]
    }

    document = Document(**doc_data)

    assert str(document.id) == "550e8400-e29b-41d4-a716-446655440000"
    assert document.title == "Test Document"
    assert document.content == "This is test content"
    assert document.is_favorite is False
    assert document.depth == 0
    assert document.path == "/test-document"


def test_access_model():
    """Test DocumentAccess model creation and validation."""
    access_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "role": "editor"
    }

    access = DocumentAccess(**access_data)

    assert str(access.id) == "550e8400-e29b-41d4-a716-446655440000"
    assert access.role.value == "editor"


def test_document_list_model():
    """Test DocumentListResponse model for paginated results."""
    doc_list_data = {
        "count": 100,
        "next": "https://api.example.com/documents/?page=2",
        "previous": None,
        "results": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Document 1",
                "content": "Content 1",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "depth": 0,
                "path": "/doc-1",
                "is_favorite": False,
                "nb_accesses_ancestors": 0,
                "nb_accesses_direct": 1,
                "numchild": 0,
                "user_roles": ["owner"]
            }
        ]
    }

    doc_list = DocumentListResponse(**doc_list_data)

    assert doc_list.count == 100
    assert str(doc_list.next) == "https://api.example.com/documents/?page=2"
    assert doc_list.previous is None
    assert len(doc_list.results) == 1
    assert str(doc_list.results[0].id) == "550e8400-e29b-41d4-a716-446655440000"
