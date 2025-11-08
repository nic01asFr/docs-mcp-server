# Changelog v0.2.0 - Document Content Editing 🎉

## Major Features

### ✨ Yjs Document Editing Support

**NEW**: Full support for editing document content via Yjs (CRDT) format!

The MCP server can now read and write document content, enabling AI assistants to:
- Read document content as plain text
- Update documents with text or markdown
- Apply AI transformations directly to documents
- Translate document content

### 🛠️ New Tools (4)

1. **`docs_get_content_text`** - Read document content as plain text
   ```json
   {
     "document_id": "uuid"
   }
   ```

2. **`docs_update_content`** - Update document with text or markdown
   ```json
   {
     "document_id": "uuid",
     "content": "New content here",
     "format": "text|markdown"
   }
   ```

3. **`docs_apply_ai_transform`** - Apply AI transformation and save
   ```json
   {
     "document_id": "uuid",
     "action": "correct|rephrase|summarize|prompt|beautify|emojify",
     "text": "optional specific text"
   }
   ```

4. **`docs_apply_ai_translate`** - Translate and save document
   ```json
   {
     "document_id": "uuid",
     "language": "en|fr|es|de|it|pt",
     "text": "optional specific text"
   }
   ```

### 📚 New Python Client Methods

```python
# Read content
text = await client.get_content_text(document_id)

# Update content
doc = await client.update_content(
    document_id,
    "New content",
    format="text"  # or "markdown"
)

# Apply AI transformation
doc = await client.apply_ai_transform_to_content(
    document_id,
    action="correct"
)

# Translate content
doc = await client.apply_ai_translate_to_content(
    document_id,
    language="en"
)
```

### 🔧 Technical Implementation

- **New module**: `yjs_utils.py` - Yjs document manipulation utilities
- **Dependency**: `pycrdt>=0.12.0` - Python implementation of Yjs CRDT
- **Format**: Documents use BlockNote XML structure in Yjs format
- **API**: Uses REST API with `websocket: true` flag for content updates
- **Markdown Conversion**: Uses official Docs API `/api/v1.0/convert/` endpoint with `@blocknote/server-util` for full markdown support (headings, lists, tables, code blocks, etc.)

### 📖 New Documentation

- **CLAUDE.md** - AI assistant guidance for working with this codebase
- **CHANGELOG_v0.2.0.md** - Complete changelog for v0.2.0 release

## Improvements

- ✅ All 27+ tools validated and tested
- ✅ Content editing fully functional
- ✅ AI features integrated with content updates
- ✅ Comprehensive test suite

## Technical Details

### Yjs Document Structure

Documents in Docs use Yjs (CRDT) format:

```xml
<blockGroup>
  <blockContainer id="uuid">
    <paragraph textColor="default" textAlignment="left" backgroundColor="default">
      Your text here
    </paragraph>
  </blockContainer>
</blockGroup>
```

Content is:
1. Encoded as Yjs binary update
2. Base64-encoded
3. Stored in S3 (not PostgreSQL)

### Workflow Examples

**Edit a document:**
```python
# 1. Read current content
text = await client.get_content_text(doc_id)

# 2. Modify
new_text = text + "\n\nNew paragraph added."

# 3. Save
await client.update_content(doc_id, new_text)
```

**Correct grammar:**
```python
# One-step: read, transform, save
await client.apply_ai_transform_to_content(doc_id, "correct")
```

**Translate to English:**
```python
# One-step: read, translate, save
await client.apply_ai_translate_to_content(doc_id, "en")
```

## Breaking Changes

None - v0.2.0 is fully backward compatible with v0.1.0.

## Known Limitations

- No real-time collaborative editing via WebSocket (use REST API updates)
- Content update requires `editor` or `owner` role on the document

## Migration from v0.1.0

No migration needed - all v0.1.0 features work identically.

To use new content editing features:
```bash
pip install --upgrade docs-mcp-server
```

## Testing

All new features have been thoroughly tested:
- ✅ Yjs document manipulation utilities
- ✅ End-to-end content editing workflows
- ✅ Complete validation of all 31 MCP tools
- ✅ Integration with Docs API markdown conversion endpoint

## Contributors

- Nicolas LAVAL - Development & Testing
- Repository: https://github.com/nic01asFr/docs-mcp-server

## Next Steps (v0.3.0)

Potential future enhancements:
- WebSocket support for real-time collaborative editing
- Batch document operations
- Document templates
- Advanced content search and filtering
- Export documents to various formats (PDF, DOCX, etc.)
