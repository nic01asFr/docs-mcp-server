"""Utilities for working with Yjs documents used by Docs.

Docs uses Yjs (CRDT) for collaborative editing with BlockNote editor.
Content is stored as Yjs binary updates encoded in base64.

Structure:
- Yjs Document contains a "document-store" key
- document-store is an XmlFragment containing BlockNote blocks
- BlockNote uses: <blockGroup><blockContainer><paragraph>...</paragraph></blockContainer></blockGroup>
"""

import base64
import re
from typing import Any

import pycrdt


class YjsDocumentError(Exception):
    """Error working with Yjs documents."""


class YjsDocumentUtils:
    """Utilities for Yjs document manipulation."""

    @staticmethod
    def extract_text(ydoc_b64: str | None) -> str:
        """Extract plain text from a Yjs document.

        Args:
            ydoc_b64: Base64-encoded Yjs document update

        Returns:
            Plain text content extracted from the document

        Raises:
            YjsDocumentError: If document cannot be decoded or parsed
        """
        if not ydoc_b64:
            return ""

        try:
            # Decode base64
            content_bytes = base64.b64decode(ydoc_b64)

            # Create Yjs doc and apply update
            ydoc = pycrdt.Doc()
            ydoc.apply_update(content_bytes)

            # Get document-store
            if "document-store" not in ydoc:
                return ""

            doc_store = ydoc.get("document-store", type=pycrdt.XmlFragment)

            # Convert to string and extract text
            xml_str = str(doc_store)

            # Remove XML tags to get plain text
            # Remove <blockGroup>, <blockContainer>, <paragraph> etc.
            text = re.sub(r"<[^>]+>", " ", xml_str)

            # Clean up multiple spaces and newlines
            text = re.sub(r"\s+", " ", text)
            text = text.strip()

            return text

        except Exception as e:
            raise YjsDocumentError(f"Failed to extract text from Yjs document: {e}") from e

    @staticmethod
    def create_from_text(text: str) -> str:
        """Create a Yjs document from plain text.

        Creates a simple BlockNote structure with the text in a paragraph.

        Args:
            text: Plain text content

        Returns:
            Base64-encoded Yjs document update

        Raises:
            YjsDocumentError: If document cannot be created
        """
        try:
            # Create new Yjs document
            ydoc = pycrdt.Doc()

            # Create BlockNote structure
            # <blockGroup>
            #   <blockContainer id="...">
            #     <paragraph>text</paragraph>
            #   </blockContainer>
            # </blockGroup>

            # Create structure with attributes in constructors
            import uuid

            block_id = str(uuid.uuid4())

            # Create paragraph with text (if provided)
            if text:
                paragraph = pycrdt.XmlElement(
                    "paragraph",
                    {
                        "textColor": "default",
                        "textAlignment": "left",
                        "backgroundColor": "default",
                    },
                    [pycrdt.XmlText(text)],
                )
            else:
                paragraph = pycrdt.XmlElement(
                    "paragraph",
                    {
                        "textColor": "default",
                        "textAlignment": "left",
                        "backgroundColor": "default",
                    },
                )

            # Create blockContainer with paragraph
            block_container = pycrdt.XmlElement(
                "blockContainer", {"id": block_id}, [paragraph]
            )

            # Create blockGroup with blockContainer
            block_group = pycrdt.XmlElement("blockGroup", {}, [block_container])

            # Create document-store fragment with blockGroup and assign to document
            doc_store = pycrdt.XmlFragment([block_group])
            ydoc["document-store"] = doc_store

            # Get update and encode
            update = ydoc.get_update()
            return base64.b64encode(update).decode("utf-8")

        except Exception as e:
            raise YjsDocumentError(f"Failed to create Yjs document from text: {e}") from e

    @staticmethod
    def create_from_markdown(markdown: str, base_url: str | None = None, api_token: str | None = None) -> str:
        """Create a Yjs document from markdown using Docs conversion API.

        Uses the official @blocknote/server-util conversion service via the
        Docs API /api/v1.0/convert/ endpoint. This ensures 100% compatibility
        with all BlockNote features (headings, lists, code blocks, tables, etc.).

        Args:
            markdown: Markdown content to convert
            base_url: Optional Docs base URL (uses config if not provided)
            api_token: Optional API token (uses config if not provided)

        Returns:
            Base64-encoded Yjs document update

        Raises:
            YjsDocumentError: If document cannot be created or API call fails

        Note:
            Supports ALL BlockNote markdown features:
            - Headings (H1-H6)
            - Paragraphs with inline formatting (bold, italic, strikethrough, code)
            - Bullet lists and numbered lists
            - Checkboxes
            - Quotes
            - Code blocks with syntax highlighting
            - Tables
            - Links and images
            - Callouts
        """
        try:
            import httpx
            from .config import DocsConfig

            # Get config if not provided
            if base_url is None or api_token is None:
                config = DocsConfig()
                base_url = base_url or config.base_url
                api_token = api_token or config.api_token

            # Call the Docs conversion API
            # Convert HttpUrl to string if necessary
            base_url_str = str(base_url).rstrip("/")
            api_url = f"{base_url_str}/api/v1.0/convert/"

            response = httpx.post(
                api_url,
                json={"markdown": markdown},
                headers={
                    "Authorization": f"Token {api_token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data['content']
            elif response.status_code == 400:
                error_detail = response.json().get('error', 'Invalid request')
                raise YjsDocumentError(f"Invalid markdown: {error_detail}")
            elif response.status_code == 401:
                raise YjsDocumentError("Authentication failed. Check your API token.")
            elif response.status_code == 503:
                raise YjsDocumentError("Conversion service temporarily unavailable. Try again later.")
            else:
                raise YjsDocumentError(
                    f"Markdown conversion failed: HTTP {response.status_code} - {response.text[:200]}"
                )

        except httpx.HTTPError as e:
            raise YjsDocumentError(f"Network error during markdown conversion: {e}") from e
        except Exception as e:
            if isinstance(e, YjsDocumentError):
                raise
            raise YjsDocumentError(f"Failed to convert markdown to Yjs: {e}") from e

    @staticmethod
    def get_structure_info(ydoc_b64: str | None) -> dict[str, Any]:
        """Get structural information about a Yjs document.

        Useful for debugging and understanding document structure.

        Args:
            ydoc_b64: Base64-encoded Yjs document update

        Returns:
            Dictionary with document structure information

        Raises:
            YjsDocumentError: If document cannot be decoded
        """
        if not ydoc_b64:
            return {"empty": True, "keys": []}

        try:
            content_bytes = base64.b64decode(ydoc_b64)
            ydoc = pycrdt.Doc()
            ydoc.apply_update(content_bytes)

            info = {
                "empty": False,
                "keys": list(ydoc.keys()),
                "has_document_store": "document-store" in ydoc,
            }

            if "document-store" in ydoc:
                doc_store = ydoc.get("document-store", type=pycrdt.XmlFragment)
                info["document_store_xml"] = str(doc_store)[:500]  # First 500 chars
                info["document_store_type"] = str(type(doc_store))

            return info

        except Exception as e:
            raise YjsDocumentError(f"Failed to get structure info: {e}") from e


# Convenience functions
def extract_text(ydoc_b64: str | None) -> str:
    """Extract plain text from a Yjs document.

    Convenience wrapper around YjsDocumentUtils.extract_text()

    Args:
        ydoc_b64: Base64-encoded Yjs document update

    Returns:
        Plain text content
    """
    return YjsDocumentUtils.extract_text(ydoc_b64)


def create_from_text(text: str) -> str:
    """Create a Yjs document from plain text.

    Convenience wrapper around YjsDocumentUtils.create_from_text()

    Args:
        text: Plain text content

    Returns:
        Base64-encoded Yjs document update
    """
    return YjsDocumentUtils.create_from_text(text)


def create_from_markdown(markdown: str, base_url: str | None = None, api_token: str | None = None) -> str:
    """Create a Yjs document from markdown using Docs conversion API.

    Convenience wrapper around YjsDocumentUtils.create_from_markdown()

    Args:
        markdown: Markdown content
        base_url: Optional Docs base URL (uses config if not provided)
        api_token: Optional API token (uses config if not provided)

    Returns:
        Base64-encoded Yjs document update
    """
    return YjsDocumentUtils.create_from_markdown(markdown, base_url, api_token)
