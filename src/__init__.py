"""
DocChat MCP Server - Semantic Document Search for Claude Desktop.

A Model Context Protocol (MCP) server that enables Claude Desktop to
semantically search and interact with documents (PDF, DOCX, TXT).
"""

__version__ = "1.0.0"
__author__ = "DocChat Contributors"
__email__ = "contact@docchat.dev"
__description__ = "Semantic Document Search and Q&A System for Claude Desktop via MCP"

from .config.settings import get_settings
from .models.enums import DocumentStatus, FileType, ProcessingStatus
from .services.embedding_service import EmbeddingService
from .services.indexing_service import DocumentIndexingService

__all__ = [
    "get_settings",
    "DocumentStatus",
    "FileType",
    "ProcessingStatus",
    "EmbeddingService",
    "DocumentIndexingService",
]