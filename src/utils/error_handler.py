"""
Error handling and logging utilities for DocChat MCP.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import traceback

from ..config.settings import get_settings


class DocChatLogger:
    """Centralized logging configuration for DocChat MCP."""

    def __init__(self):
        self.settings = get_settings()
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with file and console handlers."""
        # Create logs directory
        logs_dir = self.settings.logs_dir
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.settings.server.log_level.upper()))

        # Clear existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for general logs
        file_handler = logging.FileHandler(logs_dir / "docchat.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Error file handler
        error_handler = logging.FileHandler(logs_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

        logging.info("Logging configured successfully")


class DocChatError(Exception):
    """Base exception class for DocChat MCP errors."""

    def __init__(self, message: str, error_code: str = "DOCCHAT_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class DocumentProcessingError(DocChatError):
    """Errors related to document processing."""

    def __init__(self, message: str, file_path: Optional[str] = None, processor_type: Optional[str] = None):
        details = {}
        if file_path:
            details["file_path"] = file_path
        if processor_type:
            details["processor_type"] = processor_type

        super().__init__(message, "DOCUMENT_PROCESSING_ERROR", details)


class EmbeddingError(DocChatError):
    """Errors related to embedding generation."""

    def __init__(self, message: str, model_name: Optional[str] = None, text_length: Optional[int] = None):
        details = {}
        if model_name:
            details["model_name"] = model_name
        if text_length:
            details["text_length"] = text_length

        super().__init__(message, "EMBEDDING_ERROR", details)


class SearchError(DocChatError):
    """Errors related to search operations."""

    def __init__(self, message: str, query: Optional[str] = None, index_size: Optional[int] = None):
        details = {}
        if query:
            details["query"] = query
        if index_size:
            details["index_size"] = index_size

        super().__init__(message, "SEARCH_ERROR", details)


class MCPError(DocChatError):
    """Errors related to MCP protocol operations."""

    def __init__(self, message: str, tool_name: Optional[str] = None, arguments: Optional[Dict] = None):
        details = {}
        if tool_name:
            details["tool_name"] = tool_name
        if arguments:
            details["arguments"] = arguments

        super().__init__(message, "MCP_ERROR", details)


class FileSystemError(DocChatError):
    """Errors related to file system operations."""

    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None):
        details = {}
        if file_path:
            details["file_path"] = file_path
        if operation:
            details["operation"] = operation

        super().__init__(message, "FILESYSTEM_ERROR", details)


def handle_error(error: Exception, logger: Optional[logging.Logger] = None) -> DocChatError:
    """
    Convert any exception to a DocChatError with proper logging.

    Args:
        error: Original exception
        logger: Logger instance (optional)

    Returns:
        DocChatError instance
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # If already a DocChatError, just log and return
    if isinstance(error, DocChatError):
        logger.error(f"DocChat error: {error.message}", extra={"error_details": error.details})
        return error

    # Convert other exceptions
    error_message = str(error)
    error_details = {
        "original_type": type(error).__name__,
        "traceback": traceback.format_exc()
    }

    # Determine appropriate error type
    if isinstance(error, FileNotFoundError):
        docchat_error = FileSystemError(
            f"File not found: {error_message}",
            operation="file_access"
        )
    elif isinstance(error, PermissionError):
        docchat_error = FileSystemError(
            f"Permission denied: {error_message}",
            operation="file_access"
        )
    elif isinstance(error, ValueError):
        docchat_error = DocumentProcessingError(f"Invalid value: {error_message}")
    elif isinstance(error, ConnectionError):
        docchat_error = MCPError(f"Connection error: {error_message}")
    else:
        docchat_error = DocChatError(f"Unexpected error: {error_message}", "UNEXPECTED_ERROR", error_details)

    logger.error(f"Converted exception to DocChatError: {docchat_error.message}", extra={"error_details": docchat_error.details})
    return docchat_error


def log_performance(operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
    """
    Log performance metrics for operations.

    Args:
        operation: Name of the operation
        duration: Duration in seconds
        details: Additional details to log
    """
    logger = logging.getLogger("performance")

    log_details = {"duration_seconds": duration}
    if details:
        log_details.update(details)

    # Log warning if operation exceeds constitutional limits
    if "search" in operation.lower() and duration > 10.0:
        logger.warning(f"Search operation exceeded 10s limit: {operation} took {duration:.3f}s", extra=log_details)
    elif duration > 30.0:  # General long operation warning
        logger.warning(f"Long operation detected: {operation} took {duration:.3f}s", extra=log_details)
    else:
        logger.info(f"Operation completed: {operation} in {duration:.3f}s", extra=log_details)


def log_memory_usage(operation: str, memory_mb: float):
    """
    Log memory usage for operations.

    Args:
        operation: Name of the operation
        memory_mb: Memory usage in MB
    """
    logger = logging.getLogger("performance")

    log_details = {"memory_mb": memory_mb}

    # Log warning if memory exceeds constitutional limit
    if memory_mb > 500.0:
        logger.warning(f"Memory usage exceeded 500MB limit: {operation} using {memory_mb:.1f}MB", extra=log_details)
    elif memory_mb > 400.0:  # Warning when approaching limit
        logger.warning(f"High memory usage detected: {operation} using {memory_mb:.1f}MB", extra=log_details)
    else:
        logger.debug(f"Memory usage: {operation} using {memory_mb:.1f}MB", extra=log_details)


# Initialize logging when module is imported
_logger_instance = None

def get_logger() -> DocChatLogger:
    """Get the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = DocChatLogger()
    return _logger_instance


# Auto-initialize logging
get_logger()