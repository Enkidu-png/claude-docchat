#!/usr/bin/env python3
"""
DocChat MCP Server - Official Guidelines Compliant

An MCP server for semantic document search and Q&A across PDF, DOCX, and TXT files.
Built following official MCP development guidelines and best practices.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from .config.settings import get_settings
from .services.indexing_service import DocumentIndexingService

# Configure logging to stderr (required for STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Writes to stderr by default
)
logger = logging.getLogger('docchat-mcp')

# Global indexing service
indexing_service: Optional[DocumentIndexingService] = None

def get_indexing_service() -> DocumentIndexingService:
    """Get or create the global indexing service."""
    global indexing_service
    if indexing_service is None:
        indexing_service = DocumentIndexingService()
        logger.info("Initialized DocChat indexing service")
    return indexing_service

# Create MCP server instance
server = Server("docchat")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.

    Returns all tools that DocChat provides for document processing and search.
    """
    logger.info("Listing available tools")

    return [
        types.Tool(
            name="semantic_search",
            description="Search documents using natural language queries with semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum relevance score (0.0 to 1.0)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.1
                    }
                },
                "required": ["query"]
            }
        ),

        types.Tool(
            name="scan_folder",
            description="Scan a folder to discover available documents (PDF, DOCX, TXT) without indexing them",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "Absolute path to the folder to scan"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to scan subdirectories recursively",
                        "default": True
                    },
                    "show_details": {
                        "type": "boolean",
                        "description": "Whether to show file sizes and modification dates",
                        "default": True
                    }
                },
                "required": ["folder_path"]
            }
        ),

        types.Tool(
            name="index_folder",
            description="Index all supported documents in a folder (PDF, DOCX, TXT)",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "Absolute path to the folder to index"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to recursively index subdirectories",
                        "default": True
                    }
                },
                "required": ["folder_path"]
            }
        ),

        types.Tool(
            name="index_document",
            description="Index a specific document file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the document file to index"
                    }
                },
                "required": ["file_path"]
            }
        ),

        types.Tool(
            name="list_documents",
            description="List all indexed documents with metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_filter": {
                        "type": "string",
                        "description": "Optional folder path to filter results"
                    },
                    "file_type_filter": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["pdf", "docx", "txt"]},
                        "description": "Optional file types to filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to return",
                        "minimum": 1,
                        "default": 100
                    }
                }
            }
        ),

        types.Tool(
            name="get_document_content",
            description="Retrieve the full content of an indexed document",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the document file"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tool execution.

    Routes tool calls to appropriate handlers and returns formatted results.
    """
    logger.info(f"Executing tool: {name}")

    try:
        if name == "semantic_search":
            return await handle_semantic_search(arguments)
        elif name == "scan_folder":
            return await handle_scan_folder(arguments)
        elif name == "index_folder":
            return await handle_index_folder(arguments)
        elif name == "index_document":
            return await handle_index_document(arguments)
        elif name == "list_documents":
            return await handle_list_documents(arguments)
        elif name == "get_document_content":
            return await handle_get_document_content(arguments)
        else:
            logger.error(f"Unknown tool: {name}")
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def handle_semantic_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle semantic search requests."""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 10)
    min_score = arguments.get("min_score", 0.1)

    logger.info(f"Performing semantic search: '{query}' (limit={limit}, min_score={min_score})")

    service = get_indexing_service()
    start_time = datetime.utcnow()

    try:
        results = await service.semantic_search(
            query=query,
            limit=limit,
            min_score=min_score
        )

        end_time = datetime.utcnow()
        query_time = (end_time - start_time).total_seconds()

        # Format response
        response = {
            "query": query,
            "total_results": results.total_count,
            "query_time_seconds": query_time,
            "results": []
        }

        for result in results.results:
            response["results"].append({
                "content": result.content,
                "relevance_score": result.relevance_score,
                "source": {
                    "document_id": str(result.source.document_id),
                    "file_name": result.source.file_name,
                    "file_path": result.source.file_path,
                    "file_type": result.source.file_type,
                    "page_number": result.source.page_number,
                    "section_title": result.source.section_title,
                    "char_range": {
                        "start": result.source.char_range[0],
                        "end": result.source.char_range[1]
                    }
                }
            })

        logger.info(f"Search completed: {results.total_count} results in {query_time:.3f}s")

        return [types.TextContent(
            type="text",
            text=f"Search Results for '{query}':\n\n" +
                 f"Found {results.total_count} results in {query_time:.3f} seconds\n\n" +
                 "\n".join([
                     f"Result {i+1} (Score: {r['relevance_score']:.3f}):\n"
                     f"Source: {r['source']['file_name']}\n"
                     f"Content: {r['content'][:200]}...\n"
                     for i, r in enumerate(response["results"][:5])
                 ])
        )]

    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Search failed: {str(e)}"
        )]

async def handle_scan_folder(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle folder scanning requests to discover available documents."""
    folder_path = arguments.get("folder_path", "")
    recursive = arguments.get("recursive", True)
    show_details = arguments.get("show_details", True)

    if not folder_path:
        return [types.TextContent(
            type="text",
            text="Error: folder_path is required"
        )]

    # Validate path exists
    path = Path(folder_path)
    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"Error: Folder does not exist: {folder_path}"
        )]

    if not path.is_dir():
        return [types.TextContent(
            type="text",
            text=f"Error: Path is not a directory: {folder_path}"
        )]

    logger.info(f"Scanning folder: {folder_path} (recursive={recursive})")

    try:
        from .services.processors.processor_factory import ProcessorFactory
        factory = ProcessorFactory()

        # Discover documents
        discovered_files = []

        def scan_directory(dir_path: Path, current_depth: int = 0, max_depth: int = 10):
            if current_depth >= max_depth:
                return

            try:
                for item in dir_path.iterdir():
                    if item.is_file() and factory.is_supported(item):
                        discovered_files.append(item)
                    elif item.is_dir() and recursive and current_depth < max_depth:
                        scan_directory(item, current_depth + 1, max_depth)
            except PermissionError:
                # Skip directories we can't access
                pass

        scan_directory(path)

        if not discovered_files:
            return [types.TextContent(
                type="text",
                text=f"No supported documents found in: {folder_path}\n\n"
                     f"Supported file types: PDF (.pdf), Word (.docx), Text (.txt)\n"
                     f"Searched recursively: {recursive}"
            )]

        # Group files by type and folder
        files_by_type = {"pdf": [], "docx": [], "txt": []}
        files_by_folder = {}
        total_size = 0

        for file_path in discovered_files:
            extension = file_path.suffix.lower().lstrip('.')
            if extension in files_by_type:
                files_by_type[extension].append(file_path)

            folder = str(file_path.parent)
            if folder not in files_by_folder:
                files_by_folder[folder] = []
            files_by_folder[folder].append(file_path)

            if show_details:
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass

        # Format response
        response_text = f"Available Documents in: {folder_path}\n"
        response_text += f"Searched recursively: {recursive}\n\n"

        # Summary by type
        response_text += "Summary by Type:\n"
        for file_type, files in files_by_type.items():
            if files:
                response_text += f"  {file_type.upper()}: {len(files)} files\n"

        if show_details and total_size > 0:
            size_mb = total_size / (1024 * 1024)
            response_text += f"  Total size: {size_mb:.1f} MB\n"

        response_text += f"\nTotal documents found: {len(discovered_files)}\n\n"

        # List by folder
        response_text += "Documents by Folder:\n\n"
        for folder, files in sorted(files_by_folder.items()):
            # Show relative path if under the scanned folder
            if folder.startswith(folder_path):
                relative_folder = folder[len(folder_path):].lstrip('\\/')
                display_folder = relative_folder if relative_folder else "."
            else:
                display_folder = folder

            response_text += f"[{display_folder}/]\n"

            for file_path in sorted(files, key=lambda x: x.name.lower()):
                file_type_label = {"pdf": "[PDF]", "docx": "[DOCX]", "txt": "[TXT]"}.get(
                    file_path.suffix.lower().lstrip('.'), "[DOC]"
                )

                if show_details:
                    try:
                        stat = file_path.stat()
                        size_kb = stat.st_size / 1024
                        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        response_text += f"  {file_type_label} {file_path.name} ({size_kb:.1f} KB, {mod_time})\n"
                    except:
                        response_text += f"  {file_type_label} {file_path.name}\n"
                else:
                    response_text += f"  {file_type_label} {file_path.name}\n"

            response_text += "\n"

        response_text += "TIP: To index these documents, use the 'index_folder' tool.\n"
        response_text += "     After indexing, you can search them with 'semantic_search'."

        logger.info(f"Folder scan completed: {len(discovered_files)} documents found")

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        logger.error(f"Folder scanning failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Folder scanning failed: {str(e)}"
        )]

async def handle_index_folder(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle folder indexing requests."""
    folder_path = arguments.get("folder_path", "")
    recursive = arguments.get("recursive", True)

    if not folder_path:
        return [types.TextContent(
            type="text",
            text="Error: folder_path is required"
        )]

    # Validate path exists
    path = Path(folder_path)
    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"Error: Folder does not exist: {folder_path}"
        )]

    if not path.is_dir():
        return [types.TextContent(
            type="text",
            text=f"Error: Path is not a directory: {folder_path}"
        )]

    logger.info(f"Indexing folder: {folder_path} (recursive={recursive})")

    service = get_indexing_service()

    try:
        result = await service.index_folder(folder_path, recursive=recursive)

        response_text = f"Folder Indexing Results:\n\n" \
                       f"Folder: {folder_path}\n" \
                       f"Recursive: {recursive}\n\n" \
                       f"Documents discovered: {result.total_discovered}\n" \
                       f"Documents processed: {result.total_processed}\n" \
                       f"Documents indexed: {result.total_indexed}\n" \
                       f"Errors: {result.errors_count}\n"

        if result.errors:
            response_text += "\nErrors encountered:\n"
            for error in result.errors[:5]:  # Show first 5 errors
                response_text += f"- {error.get('file_path', 'Unknown')}: {error.get('error', 'Unknown error')}\n"

        if result.total_indexed > 0:
            response_text += f"\n✅ Successfully indexed {result.total_indexed} documents!"
        else:
            response_text += "\n⚠️ No documents were indexed."

        logger.info(f"Folder indexing completed: {result.total_indexed}/{result.total_discovered} documents indexed")

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        logger.error(f"Folder indexing failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Folder indexing failed: {str(e)}"
        )]

async def handle_index_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle single document indexing requests."""
    file_path = arguments.get("file_path", "")

    if not file_path:
        return [types.TextContent(
            type="text",
            text="Error: file_path is required"
        )]

    # Validate path exists
    path = Path(file_path)
    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"Error: File does not exist: {file_path}"
        )]

    if not path.is_file():
        return [types.TextContent(
            type="text",
            text=f"Error: Path is not a file: {file_path}"
        )]

    logger.info(f"Indexing document: {file_path}")

    service = get_indexing_service()

    try:
        result = await service.index_document(file_path)

        if result.total_indexed > 0:
            # Get document info
            document = await service.get_document_by_path(file_path)

            response_text = f"Document Indexing Results:\n\n" \
                           f"File: {path.name}\n" \
                           f"Path: {file_path}\n" \
                           f"Status: ✅ Successfully indexed\n"

            if document:
                response_text += f"Type: {document.file_type}\n" \
                               f"Size: {document.file_size:,} bytes\n" \
                               f"Modified: {document.modified_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            response_text = f"Document Indexing Results:\n\n" \
                           f"File: {path.name}\n" \
                           f"Path: {file_path}\n" \
                           f"Status: ❌ Failed to index\n"

            if result.errors:
                response_text += f"Error: {result.errors[0].get('error', 'Unknown error')}\n"

        logger.info(f"Document indexing completed: {file_path} ({'success' if result.total_indexed > 0 else 'failed'})")

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        logger.error(f"Document indexing failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Document indexing failed: {str(e)}"
        )]

async def handle_list_documents(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document listing requests."""
    folder_filter = arguments.get("folder_filter")
    file_type_filter = arguments.get("file_type_filter")
    limit = arguments.get("limit", 100)

    logger.info(f"Listing documents (folder_filter={folder_filter}, file_type_filter={file_type_filter}, limit={limit})")

    service = get_indexing_service()

    try:
        documents = await service.list_indexed_documents()

        # Apply filters
        if folder_filter:
            documents = [doc for doc in documents if str(doc.file_path).startswith(folder_filter)]

        if file_type_filter:
            documents = [doc for doc in documents if doc.file_type.value in file_type_filter]

        # Apply limit
        documents = documents[:limit]

        if not documents:
            return [types.TextContent(
                type="text",
                text="No indexed documents found."
            )]

        response_text = f"Indexed Documents ({len(documents)} found):\n\n"

        for i, doc in enumerate(documents, 1):
            response_text += f"{i}. {doc.file_name}\n" \
                            f"   Path: {doc.file_path}\n" \
                            f"   Type: {doc.file_type}\n" \
                            f"   Size: {doc.file_size:,} bytes\n" \
                            f"   Status: {doc.status}\n" \
                            f"   Modified: {doc.modified_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        logger.info(f"Listed {len(documents)} documents")

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        logger.error(f"Document listing failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Document listing failed: {str(e)}"
        )]

async def handle_get_document_content(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document content retrieval requests."""
    file_path = arguments.get("file_path", "")

    if not file_path:
        return [types.TextContent(
            type="text",
            text="Error: file_path is required"
        )]

    logger.info(f"Retrieving content for: {file_path}")

    service = get_indexing_service()

    try:
        # Get document
        document = await service.get_document_by_path(file_path)

        if not document:
            return [types.TextContent(
                type="text",
                text=f"Document not found in index: {file_path}"
            )]

        # Get document chunks to reconstruct content
        chunks = service._chunks.get(document.id, [])

        if not chunks:
            return [types.TextContent(
                type="text",
                text=f"No content available for document: {file_path}"
            )]

        # Sort chunks by position and combine content
        sorted_chunks = sorted(chunks, key=lambda x: x.start_char)
        full_content = "\n\n".join(chunk.content for chunk in sorted_chunks)

        response_text = f"Document Content: {document.file_name}\n" \
                       f"Path: {file_path}\n" \
                       f"Type: {document.file_type}\n" \
                       f"Content Length: {len(full_content):,} characters\n\n" \
                       f"--- Content ---\n{full_content}"

        logger.info(f"Retrieved content for {file_path}: {len(full_content)} characters")

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        logger.error(f"Content retrieval failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Content retrieval failed: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting DocChat MCP server")

    # Run the server using STDIO transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("DocChat MCP server running on STDIO transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="docchat",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    logger.info("DocChat MCP Server starting...")
    asyncio.run(main())