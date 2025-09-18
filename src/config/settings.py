"""
Configuration settings for DocChat MCP server.

This module defines all configuration parameters using Pydantic settings
with environment variable support and validation.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class QdrantSettings(BaseSettings):
    """Qdrant vector database configuration."""

    host: str = Field(default="localhost", description="Qdrant host")
    port: int = Field(default=6333, description="Qdrant HTTP port")
    grpc_port: int = Field(default=6334, description="Qdrant gRPC port")
    collection_name: str = Field(default="documents", description="Collection name for document chunks")
    vector_size: int = Field(default=384, description="Vector embedding size")
    distance_metric: str = Field(default="Cosine", description="Distance metric for similarity")

    class Config:
        env_prefix = "QDRANT_"


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration."""

    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model name"
    )
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key for embeddings")
    use_openai: bool = Field(default=False, description="Use OpenAI embeddings instead of local")
    batch_size: int = Field(default=32, description="Batch size for embedding generation")
    max_seq_length: int = Field(default=512, description="Maximum sequence length for embeddings")

    class Config:
        env_prefix = "EMBEDDING_"


class DocumentProcessingSettings(BaseSettings):
    """Document processing configuration."""

    chunk_size: int = Field(default=1000, description="Text chunk size in characters")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks in characters")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Max file size in bytes (100MB)")
    max_folder_depth: int = Field(default=10, description="Maximum folder traversal depth")
    supported_extensions: List[str] = Field(
        default=[".pdf", ".txt", ".docx"],
        description="Supported file extensions"
    )

    @validator('max_file_size')
    def validate_max_file_size(cls, v: int) -> int:
        """Ensure file size limit is reasonable."""
        if v > 200 * 1024 * 1024:  # 200MB absolute limit
            raise ValueError("Maximum file size cannot exceed 200MB")
        return v

    @validator('max_folder_depth')
    def validate_folder_depth(cls, v: int) -> int:
        """Ensure folder depth is within constitutional limits."""
        if v > 10:
            raise ValueError("Maximum folder depth cannot exceed 10 levels")
        return v

    class Config:
        env_prefix = "DOC_"


class MCPServerSettings(BaseSettings):
    """MCP server configuration."""

    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8000, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    max_workers: int = Field(default=4, description="Maximum worker threads")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")

    class Config:
        env_prefix = "MCP_"


class PerformanceSettings(BaseSettings):
    """Performance and resource limits."""

    max_memory_mb: int = Field(default=500, description="Maximum memory usage in MB")
    query_timeout: int = Field(default=10, description="Query timeout in seconds")
    indexing_batch_size: int = Field(default=10, description="Documents to process in parallel")
    cache_size: int = Field(default=1000, description="LRU cache size for embeddings")

    @validator('max_memory_mb')
    def validate_memory_limit(cls, v: int) -> int:
        """Ensure memory limit is within constitutional bounds."""
        if v > 500:
            raise ValueError("Memory limit cannot exceed 500MB (constitutional requirement)")
        return v

    @validator('query_timeout')
    def validate_query_timeout(cls, v: int) -> int:
        """Ensure query timeout meets constitutional requirements."""
        if v > 10:
            raise ValueError("Query timeout cannot exceed 10 seconds (constitutional requirement)")
        return v

    class Config:
        env_prefix = "PERF_"


class Settings(BaseSettings):
    """Main application settings."""

    # Application metadata
    app_name: str = Field(default="DocChat MCP", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Working directories
    work_dir: Path = Field(default_factory=lambda: Path.cwd(), description="Working directory")
    data_dir: Path = Field(default_factory=lambda: Path.cwd() / "data", description="Data directory")
    logs_dir: Path = Field(default_factory=lambda: Path.cwd() / "logs", description="Logs directory")

    # Component settings
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    document: DocumentProcessingSettings = Field(default_factory=DocumentProcessingSettings)
    server: MCPServerSettings = Field(default_factory=MCPServerSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)

    @validator('data_dir', 'logs_dir')
    def create_directories(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings