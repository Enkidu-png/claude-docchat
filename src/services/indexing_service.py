"""
Document indexing service for processing and storing documents.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..models.document import Document
from ..models.document_chunk import DocumentChunk
from ..models.enums import DocumentType, IndexStatus
from ..config.settings import get_settings
from .processors.processor_factory import ProcessorFactory
from .embedding_service import EmbeddingService


class IndexingResult:
    """Result of document indexing operation."""

    def __init__(self):
        self.total_discovered = 0
        self.total_processed = 0
        self.total_indexed = 0
        self.errors_count = 0
        self.indexed_documents: List[Document] = []
        self.errors: List[Dict[str, Any]] = []


class DocumentIndexingService:
    """Service for indexing documents and managing the search index."""

    def __init__(self):
        self.settings = get_settings()
        self.processor_factory = ProcessorFactory()
        self.embedding_service = EmbeddingService()
        self._documents: Dict[str, Document] = {}  # In-memory storage for now
        self._chunks: Dict[UUID, List[DocumentChunk]] = {}

    async def index_document(self, file_path: str) -> IndexingResult:
        """
        Index a single document.

        Args:
            file_path: Path to document file

        Returns:
            Indexing result with status and metadata
        """
        result = IndexingResult()
        path = Path(file_path)

        try:
            # Check if file exists and is supported
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not self.processor_factory.is_supported(path):
                raise ValueError(f"Unsupported file type: {path.suffix}")

            # Create or update document
            document = Document.from_file_path(path)
            document.mark_as_processing()

            # Extract text content
            processor = self.processor_factory.get_processor(path)
            content = await processor.extract_text(path)

            # Create text chunks
            chunks = await processor.create_chunks(content, str(document.id))

            # Generate embeddings for chunks
            texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.generate_embeddings_batch(texts)

            # Update chunks with embeddings
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding_vector = embedding

            # Mark as indexed
            document.mark_as_indexed(content)

            # Store in memory (in real implementation, this would go to database)
            self._documents[file_path] = document
            self._chunks[document.id] = chunks

            result.total_processed = 1
            result.total_indexed = 1
            result.indexed_documents.append(document)

        except Exception as e:
            result.errors_count = 1
            result.errors.append({
                "file_path": file_path,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

        return result

    async def index_folder(self, folder_path: str, recursive: bool = True, max_depth: int = 10) -> IndexingResult:
        """
        Index all supported documents in a folder.

        Args:
            folder_path: Path to folder to index
            recursive: Whether to process subfolders
            max_depth: Maximum folder depth to traverse

        Returns:
            Indexing result with aggregated statistics
        """
        result = IndexingResult()
        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        # Discover documents
        documents = await self._discover_documents(folder, recursive, max_depth)
        result.total_discovered = len(documents)

        # Process documents in batches
        batch_size = self.settings.performance.indexing_batch_size
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            # Process batch in parallel
            tasks = [self.index_document(str(doc_path)) for doc_path in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for batch_result in batch_results:
                if isinstance(batch_result, IndexingResult):
                    result.total_processed += batch_result.total_processed
                    result.total_indexed += batch_result.total_indexed
                    result.errors_count += batch_result.errors_count
                    result.indexed_documents.extend(batch_result.indexed_documents)
                    result.errors.extend(batch_result.errors)

        return result

    async def _discover_documents(self, folder: Path, recursive: bool, max_depth: int, current_depth: int = 0) -> List[Path]:
        """Discover all supported documents in folder."""
        documents = []

        if current_depth >= max_depth:
            return documents

        try:
            for item in folder.iterdir():
                if item.is_file() and self.processor_factory.is_supported(item):
                    documents.append(item)
                elif item.is_dir() and recursive:
                    sub_documents = await self._discover_documents(
                        item, recursive, max_depth, current_depth + 1
                    )
                    documents.extend(sub_documents)
        except PermissionError:
            # Skip folders we can't access
            pass

        return documents

    async def list_indexed_documents(self) -> List[Document]:
        """Get list of all indexed documents."""
        return list(self._documents.values())

    async def get_document_by_path(self, file_path: str) -> Optional[Document]:
        """Get document by file path."""
        return self._documents.get(file_path)

    async def get_document_chunks(self, document_id: UUID) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        return self._chunks.get(document_id, [])

    async def semantic_search(self, query: str, limit: int = 10, min_score: float = 0.1) -> 'SearchResults':
        """
        Perform semantic search across indexed documents.

        Args:
            query: Search query text
            limit: Maximum number of results
            min_score: Minimum relevance score threshold

        Returns:
            Search results with ranked chunks
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)

        # Search through all chunks
        all_results = []
        for document_id, chunks in self._chunks.items():
            document = next((doc for doc in self._documents.values() if doc.id == document_id), None)
            if not document or document.status != IndexStatus.INDEXED:
                continue

            for chunk in chunks:
                # Calculate similarity
                similarity = await self.embedding_service.compute_similarity(
                    query_embedding, chunk.embedding_vector
                )

                if similarity >= min_score:
                    result = {
                        "content": chunk.content,
                        "score": similarity,
                        "chunk": chunk,
                        "document": document
                    }
                    all_results.append(result)

        # Sort by relevance and limit
        all_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = all_results[:limit]

        # Create search results object
        from ..models.search_result import SearchResult, SourceAttribution
        search_results = []

        for i, result in enumerate(top_results):
            chunk = result["chunk"]
            document = result["document"]

            source = SourceAttribution(
                document_id=document.id,
                file_name=document.file_name,
                file_path=str(document.file_path),
                file_type=document.file_type,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                char_range=(chunk.start_char, chunk.end_char)
            )

            search_result = SearchResult(
                query_id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
                chunk_id=chunk.id,
                content=chunk.content,
                relevance_score=result["score"],
                rank_position=i + 1,
                source=source
            )
            search_results.append(search_result)

        return SearchResults(
            results=search_results,
            total_count=len(all_results),
            query_time=0.0,  # Would measure actual time in real implementation
            query=query
        )


class SearchResults:
    """Container for search results."""

    def __init__(self, results: List, total_count: int, query_time: float, query: str):
        self.results = results
        self.total_count = total_count
        self.query_time = query_time
        self.query = query