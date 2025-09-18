# DocChat MCP Server

**🎯 Semantic Document Search and Q&A System for Claude Desktop**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

DocChat is a **Model Context Protocol (MCP) server** that enables Claude Desktop to semantically search and interact with your documents. Search across PDF, DOCX, and TXT files using natural language queries.

## ✨ Features

- **🔍 Semantic Search**: Natural language queries across all your documents
- **📁 Document Discovery**: Scan folders to see available documents before indexing
- **📄 Multi-Format Support**: PDF, DOCX, and TXT files
- **🏠 Local Processing**: No external APIs required (uses local embeddings)
- **🔒 Privacy-First**: Documents never leave your machine
- **⚡ Fast**: Sub-10 second query responses with local caching
- **🎯 MCP Compliant**: Follows official MCP guidelines

## 🚀 Quick Start

### Prerequisites

- **Claude Desktop** (latest version)
- **Python 3.10 or higher**
- **Git** (for cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Enkidu-png/docchat-mcp-server.git
   cd docchat-mcp-server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv docchat_env

   # Windows
   docchat_env\Scripts\activate.bat

   # macOS/Linux
   source docchat_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   pip install fastmcp mcp sentence-transformers pymupdf python-docx watchdog psutil chardet
   ```

4. **Configure Claude Desktop**

   Open Claude Desktop → Settings → Developer → Edit Config

   Add this configuration (update paths to match your installation):

   ```json
   {
     "mcpServers": {
       "docchat": {
         "command": "python",
         "args": [
           "-m",
           "src.mcp_server_official"
         ],
         "cwd": "/path/to/docchat-mcp-server",
         "env": {
           "PYTHONPATH": "/path/to/docchat-mcp-server"
         }
       }
     }
   }
   ```

5. **Restart Claude Desktop**

6. **Test the integration**
   ```
   What documents do I have in my Documents folder?
   ```

## 🛠️ Available Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `scan_folder` | Discover available documents without indexing | *"What documents are in my Documents folder?"* |
| `index_folder` | Process all documents in a directory | *"Index my Documents folder recursively"* |
| `index_document` | Process a specific file | *"Index this project_plan.pdf file"* |
| `semantic_search` | Search documents using natural language | *"Search for machine learning research"* |
| `list_documents` | Show all indexed documents | *"List all my indexed PDF files"* |
| `get_document_content` | Retrieve full document text | *"Show me the content of report.docx"* |

## 🎯 Usage Examples

### Document Discovery
```
What documents are available in my C:\Users\MyName\Documents folder?
```

### Indexing Documents
```
Claude, please index all documents in my research folder
```

### Semantic Search
```
Search my documents for information about "machine learning algorithms"
```

### Document Management
```
List all the PDF documents you have indexed
```

## 📁 Project Structure

```
docchat-mcp-server/
├── src/
│   ├── mcp_server_official.py      # Main MCP server
│   ├── config/
│   │   └── settings.py             # Configuration management
│   ├── models/                     # Data models
│   │   ├── document.py
│   │   ├── document_chunk.py
│   │   ├── search_result.py
│   │   └── enums.py
│   ├── services/                   # Core business logic
│   │   ├── indexing_service.py
│   │   ├── embedding_service.py
│   │   └── processors/
│   │       ├── pdf_processor.py
│   │       ├── docx_processor.py
│   │       └── txt_processor.py
│   └── utils/                      # Utilities
├── tests/                          # Test suite
├── docs/                           # Documentation
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── claude_desktop_config.json      # Example Claude config
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

- `DOCCHAT_LOG_LEVEL`: Set to "DEBUG" for verbose logging
- `OPENAI_API_KEY`: Optional, for OpenAI embeddings
- `EMBEDDING_USE_OPENAI`: Set to "true" to use OpenAI embeddings

### Settings

Key settings in `src/config/settings.py`:

- `max_file_size`: 100MB per document
- `max_memory_mb`: 500MB total usage
- `query_timeout`: 10 seconds max
- `chunk_size`: 1000 characters per text chunk
- `chunk_overlap`: 200 characters between chunks

## 🔍 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Ensure virtual environment is activated
docchat_env\Scripts\activate.bat  # Windows
source docchat_env/bin/activate   # macOS/Linux

# Check PYTHONPATH
echo $PYTHONPATH
```

#### Claude Desktop can't connect
- Check logs in `%APPDATA%\Claude\logs` (Windows) or `~/Library/Application Support/Claude/logs` (macOS)
- Verify JSON configuration syntax
- Ensure file paths use proper separators
- Restart Claude Desktop completely

#### Server won't start
```bash
# Test module loading
python -c "import src.mcp_server_official; print('OK')"

# Check dependencies
pip list | grep mcp
```

### Performance Tips

- **First Run**: Downloads ~90MB sentence transformer model
- **Memory Usage**: Typically under 500MB
- **Query Speed**: 0.1-2 seconds for semantic search
- **Model Caching**: Subsequent runs use cached model

## 🔒 Security & Privacy

- **Local-First**: Uses local embedding models by default
- **No External APIs**: Documents processed entirely on your machine
- **User Approval**: All file operations require explicit approval
- **Controlled Access**: Only processes files you specify

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the excellent MCP framework
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) for local embeddings
- [Anthropic](https://www.anthropic.com/) for Claude Desktop integration

## 📞 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting) above
2. Review Claude Desktop logs for error messages
3. Verify configuration paths and JSON syntax
4. Open an issue on GitHub with detailed error information

---

**Bringing powerful document search to Claude Desktop with official MCP compliance** 🚀