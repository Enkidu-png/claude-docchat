"""
TXT document processor with encoding detection.
"""

import chardet
from pathlib import Path
from typing import List, Dict, Any

from ...models.document_chunk import DocumentChunk
from ...config.settings import get_settings


class TxtProcessor:
    """Process plain text documents with encoding detection."""

    def __init__(self):
        self.settings = get_settings()

    async def extract_text(self, file_path: Path) -> str:
        """Extract text content from TXT file with encoding detection."""
        try:
            # First, try UTF-8
            content = file_path.read_text(encoding='utf-8')
            return content
        except UnicodeDecodeError:
            # Fall back to encoding detection
            raw_data = file_path.read_bytes()
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')

            try:
                content = raw_data.decode(encoding)
                return content
            except (UnicodeDecodeError, TypeError):
                # Last resort: try with error handling
                content = raw_data.decode('utf-8', errors='replace')
                return content

    async def create_chunks(self, content: str, document_id: str) -> List[DocumentChunk]:
        """Create text chunks from document content."""
        chunk_size = self.settings.document.chunk_size
        chunk_overlap = self.settings.document.chunk_overlap

        chunks = []
        start_pos = 0
        chunk_index = 0

        while start_pos < len(content):
            end_pos = min(start_pos + chunk_size, len(content))

            # Try to break at sentence boundaries
            if end_pos < len(content):
                # Look for sentence endings in the last 100 characters
                search_start = max(end_pos - 100, start_pos)
                sentence_endings = ['.', '!', '?', '\n\n']

                for ending in sentence_endings:
                    last_ending = content.rfind(ending, search_start, end_pos)
                    if last_ending > start_pos:
                        end_pos = last_ending + 1
                        break

            chunk_content = content[start_pos:end_pos].strip()

            if chunk_content:  # Only create non-empty chunks
                chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_content,
                    start_char=start_pos,
                    end_char=end_pos,
                    chunk_index=chunk_index,
                    embedding_vector=[0.0] * 384,  # Placeholder, will be filled by embedding service
                    metadata={"processor": "txt", "encoding_detected": True}
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move to next chunk with overlap
            start_pos = max(end_pos - chunk_overlap, start_pos + 1)

        return chunks