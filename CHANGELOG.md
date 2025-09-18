# Changelog

All notable changes to DocChat MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-XX-XX

### Added
- **Document Discovery**: New `scan_folder` tool to discover available documents without indexing
- **Semantic Search**: Natural language search across PDF, DOCX, and TXT documents
- **Multi-format Support**: Comprehensive document processing pipeline
- **Local Embeddings**: Privacy-first approach using sentence-transformers
- **MCP Compliance**: Full compatibility with Claude Desktop via Model Context Protocol
- **Robust Error Handling**: Graceful handling of document processing errors
- **Performance Optimization**: Sub-10 second query responses with caching
- **Recursive Folder Processing**: Deep directory traversal for document indexing
- **Constitutional Programming**: Built-in memory and time limits for safety

### Features
- `scan_folder`: Discover documents without indexing
- `index_folder`: Process all documents in a directory recursively
- `index_document`: Process individual files
- `semantic_search`: Natural language search with relevance scoring
- `list_documents`: View all indexed documents with filtering
- `get_document_content`: Retrieve full document text

### Technical Details
- **Python 3.10+** support
- **Local processing** with sentence-transformers/all-MiniLM-L6-v2
- **Document formats**: PDF (PyMuPDF), DOCX (python-docx), TXT (chardet)
- **Vector similarity**: Cosine similarity search
- **Memory management**: 500MB constitutional limit
- **Query timeout**: 10-second constitutional limit
- **File size limit**: 100MB per document

### Documentation
- Comprehensive README with installation instructions
- Troubleshooting guide for common issues
- Example Claude Desktop configuration
- Development setup and contribution guidelines

### Security
- Local-first processing (no external APIs by default)
- User approval required for all file operations
- Controlled file access permissions
- No background data collection

## [Unreleased]

### Planned
- Web interface for document management
- Additional document formats (RTF, HTML, Markdown)
- Advanced search operators and filters
- Document summarization capabilities
- Integration with cloud storage providers
- Multi-language support for embeddings