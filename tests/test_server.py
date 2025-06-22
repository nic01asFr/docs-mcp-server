"""Tests for MCP server."""
import pytest
from unittest.mock import AsyncMock, patch

from mcp.types import CallToolRequest, ListToolsRequest, ListResourcesRequest
from docs_mcp_server.server import DocsServer


@pytest.mark.asyncio
async def test_list_tools(mock_server):
    """Test listing available tools."""
    request = ListToolsRequest()
    
    result = await mock_server.list_tools(request)
    
    assert len(result.tools) > 20  # Should have 25+ tools
    
    # Check some key tools exist
    tool_names = [tool.name for tool in result.tools]
    assert "docs_list_documents" in tool_names
    assert "docs_get_document" in tool_names
    assert "docs_create_document" in tool_names
    assert "docs_update_document" in tool_names
    assert "docs_delete_document" in tool_names


@pytest.mark.asyncio
async def test_list_resources(mock_server):
    """Test listing available resources."""
    request = ListResourcesRequest()
    
    result = await mock_server.list_resources(request)
    
    assert len(result.resources) == 4  # Should have 4 resources
    
    # Check resource URIs
    resource_uris = [resource.uri for resource in result.resources]
    assert "docs://documents" in resource_uris
    assert "docs://favorites" in resource_uris
    assert "docs://trashbin" in resource_uris
    assert "docs://user" in resource_uris


@pytest.mark.asyncio
@patch('docs_mcp_server.server.DocsAPIClient')
async def test_call_tool_list_documents(mock_client_class, mock_server, mock_document):
    """Test calling the list_documents tool."""
    # Setup mock client
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    mock_client.list_documents.return_value = {
        "count": 1,
        "results": [mock_document.dict()]
    }
    
    # Create tool request
    request = CallToolRequest(
        params={
            "name": "docs_list_documents",
            "arguments": {"page_size": 10}
        }
    )
    
    result = await mock_server.call_tool(request)
    
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    mock_client.list_documents.assert_called_once_with({"page_size": 10})


@pytest.mark.asyncio
@patch('docs_mcp_server.server.DocsAPIClient')
async def test_call_tool_get_document(mock_client_class, mock_server, mock_document):
    """Test calling the get_document tool."""
    # Setup mock client
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    mock_client.get_document.return_value = mock_document
    
    # Create tool request
    request = CallToolRequest(
        params={
            "name": "docs_get_document",
            "arguments": {"document_id": "doc-123"}
        }
    )
    
    result = await mock_server.call_tool(request)
    
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    mock_client.get_document.assert_called_once_with("doc-123")


@pytest.mark.asyncio
async def test_call_tool_unknown(mock_server):
    """Test calling an unknown tool."""
    request = CallToolRequest(
        params={
            "name": "unknown_tool",
            "arguments": {}
        }
    )
    
    result = await mock_server.call_tool(request)
    
    assert len(result.content) == 1
    assert "Unknown tool: unknown_tool" in result.content[0].text
