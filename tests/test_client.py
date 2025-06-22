"""Tests for API client."""
import pytest
from unittest.mock import AsyncMock, patch

from docs_mcp_server.client import DocsAPIClient
from docs_mcp_server.exceptions import DocsAPIError, DocsNotFoundError
from docs_mcp_server.models import Document, User


@pytest.mark.asyncio
async def test_get_current_user(mock_api_client, mock_user):
    """Test getting current user."""
    # Mock the HTTP response
    mock_api_client._http_client.get.return_value.json.return_value = mock_user.dict()
    mock_api_client._http_client.get.return_value.status_code = 200
    
    user = await mock_api_client.get_current_user()
    
    assert isinstance(user, User)
    assert user.id == mock_user.id
    assert user.email == mock_user.email
    mock_api_client._http_client.get.assert_called_once_with("/api/users/me/")


@pytest.mark.asyncio
async def test_list_documents(mock_api_client, mock_document):
    """Test listing documents."""
    # Mock the HTTP response
    response_data = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [mock_document.dict()]
    }
    mock_api_client._http_client.get.return_value.json.return_value = response_data
    mock_api_client._http_client.get.return_value.status_code = 200
    
    doc_list = await mock_api_client.list_documents()
    
    assert doc_list.count == 1
    assert len(doc_list.results) == 1
    assert doc_list.results[0].id == mock_document.id
    mock_api_client._http_client.get.assert_called_once_with("/api/documents/", params={})


@pytest.mark.asyncio
async def test_get_document(mock_api_client, mock_document):
    """Test getting a specific document."""
    document_id = "doc-123"
    
    # Mock the HTTP response
    mock_api_client._http_client.get.return_value.json.return_value = mock_document.dict()
    mock_api_client._http_client.get.return_value.status_code = 200
    
    document = await mock_api_client.get_document(document_id)
    
    assert isinstance(document, Document)
    assert document.id == mock_document.id
    assert document.title == mock_document.title
    mock_api_client._http_client.get.assert_called_once_with(f"/api/documents/{document_id}/")


@pytest.mark.asyncio
async def test_get_document_not_found(mock_api_client):
    """Test getting a non-existent document."""
    document_id = "non-existent"
    
    # Mock 404 response
    mock_api_client._http_client.get.return_value.status_code = 404
    mock_api_client._http_client.get.return_value.json.return_value = {"detail": "Not found"}
    
    with pytest.raises(DocsNotFoundError):
        await mock_api_client.get_document(document_id)


@pytest.mark.asyncio
async def test_create_document(mock_api_client, mock_document):
    """Test creating a new document."""
    title = "New Document"
    content = "New content"
    
    # Mock the HTTP response
    new_doc_data = mock_document.dict()
    new_doc_data["title"] = title
    new_doc_data["content"] = content
    
    mock_api_client._http_client.post.return_value.json.return_value = new_doc_data
    mock_api_client._http_client.post.return_value.status_code = 201
    
    document = await mock_api_client.create_document(title=title, content=content)
    
    assert isinstance(document, Document)
    assert document.title == title
    assert document.content == content
    mock_api_client._http_client.post.assert_called_once_with(
        "/api/documents/",
        json={"title": title, "content": content}
    )


@pytest.mark.asyncio
async def test_api_error_handling(mock_api_client):
    """Test API error handling."""
    # Mock 500 error response
    mock_api_client._http_client.get.return_value.status_code = 500
    mock_api_client._http_client.get.return_value.json.return_value = {"error": "Internal server error"}
    
    with pytest.raises(DocsAPIError, match="Internal server error"):
        await mock_api_client.get_current_user()
