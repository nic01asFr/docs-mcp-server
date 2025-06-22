"""Tests for data models."""
import pytest
from datetime import datetime

from docs_mcp_server.models import Document, User, Access, DocumentList


def test_user_model():
    """Test User model creation and validation."""
    user_data = {
        "id": "user-123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "date_joined": "2024-01-01T00:00:00Z"
    }
    
    user = User(**user_data)
    
    assert user.id == "user-123"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True


def test_document_model():
    """Test Document model creation and validation."""
    doc_data = {
        "id": "doc-123",
        "title": "Test Document", 
        "content": "This is test content",
        "creator_id": "user-123",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T01:00:00Z",
        "is_favorite": False,
        "accesses": []
    }
    
    document = Document(**doc_data)
    
    assert document.id == "doc-123"
    assert document.title == "Test Document"
    assert document.content == "This is test content"
    assert document.is_favorite is False


def test_access_model():
    """Test Access model creation and validation."""
    access_data = {
        "id": "access-123",
        "user_id": "user-123",
        "role": "editor",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    access = Access(**access_data)
    
    assert access.id == "access-123"
    assert access.user_id == "user-123"
    assert access.role == "editor"


def test_document_list_model():
    """Test DocumentList model for paginated results."""
    doc_list_data = {
        "count": 100,
        "next": "https://api.example.com/documents/?page=2",
        "previous": None,
        "results": [
            {
                "id": "doc-1",
                "title": "Document 1",
                "content": "Content 1",
                "creator_id": "user-123",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "is_favorite": False,
                "accesses": []
            }
        ]
    }
    
    doc_list = DocumentList(**doc_list_data)
    
    assert doc_list.count == 100
    assert doc_list.next == "https://api.example.com/documents/?page=2"
    assert doc_list.previous is None
    assert len(doc_list.results) == 1
    assert doc_list.results[0].id == "doc-1"
