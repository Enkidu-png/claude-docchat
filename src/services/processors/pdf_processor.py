"""
PDF document processor using PyMuPDF and LangChain.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional

from ...models.document_chunk import DocumentChunk
from ...config.settings import get_settings


class PdfProcessor:
    """Process PDF documents with text extraction and metadata preservation."""

    def __init__(self):
        self.settings = get_settings()

    async def extract_text(self, file_path: Path) -> str:
        """
        Extract text content from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            Exception: If PDF cannot be processed
        """
        try:
            # Open PDF document
            pdf_document = fitz.open(str(file_path))

            if pdf_document.is_encrypted:
                # Try to decrypt with empty password first
                if not pdf_document.authenticate(""):
                    raise ValueError("PDF is password-protected and requires a password")

            full_text = []

            # Extract text from each page
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()

                if text.strip():  # Only add non-empty pages
                    # Add page marker for reference
                    full_text.append(f"\n--- Page {page_num + 1} ---\n")
                    full_text.append(text)

            pdf_document.close()

            return "\n".join(full_text)

        except Exception as e:
            raise Exception(f"Failed to extract text from PDF {file_path}: {str(e)}")

    async def create_chunks(self, content: str, document_id: str) -> List[DocumentChunk]:
        """
        Create text chunks from PDF content with page tracking.

        Args:
            content: Extracted text content
            document_id: Document identifier

        Returns:
            List of document chunks with page numbers
        """
        chunk_size = self.settings.document.chunk_size
        chunk_overlap = self.settings.document.chunk_overlap

        chunks = []
        start_pos = 0
        chunk_index = 0
        current_page = 1

        while start_pos < len(content):
            end_pos = min(start_pos + chunk_size, len(content))

            # Extract chunk content
            chunk_content = content[start_pos:end_pos]

            # Find page number for this chunk
            page_number = self._find_page_number(content, start_pos, end_pos)
            if page_number is None:
                page_number = current_page

            # Try to break at natural boundaries
            if end_pos < len(content):
                # Look for sentence or paragraph endings
                search_start = max(end_pos - 200, start_pos)

                # Prefer paragraph breaks, then sentence endings
                for boundary in ['\n\n', '. ', '! ', '? ', '\n']:
                    last_boundary = chunk_content.rfind(boundary, search_start - start_pos)
                    if last_boundary > 0:
                        end_pos = start_pos + last_boundary + len(boundary)
                        chunk_content = content[start_pos:end_pos]
                        break

            chunk_content = chunk_content.strip()

            if chunk_content and not chunk_content.startswith("--- Page"):
                # Remove page markers from chunk content but keep for reference
                clean_content = self._clean_page_markers(chunk_content)

                if clean_content.strip():  # Only create non-empty chunks
                    chunk = DocumentChunk(
                        document_id=document_id,
                        content=clean_content,
                        start_char=start_pos,
                        end_char=end_pos,
                        chunk_index=chunk_index,
                        page_number=page_number,
                        embedding_vector=[0.0] * 384,  # Placeholder
                        metadata={
                            "processor": "pdf",
                            "page_number": page_number,
                            "has_page_markers": "--- Page" in chunk_content
                        }
                    )
                    chunks.append(chunk)
                    chunk_index += 1

            # Update current page tracking
            page_markers_in_chunk = chunk_content.count("--- Page")
            if page_markers_in_chunk > 0:
                current_page = page_number

            # Move to next chunk with overlap
            start_pos = max(end_pos - chunk_overlap, start_pos + 1)

        return chunks

    def _find_page_number(self, content: str, start_pos: int, end_pos: int) -> Optional[int]:
        """
        Find the page number for a given text range.

        Args:
            content: Full document content
            start_pos: Start position of chunk
            end_pos: End position of chunk

        Returns:
            Page number or None if not found
        """
        # Look backwards from start_pos to find the most recent page marker
        search_text = content[:start_pos]

        # Find all page markers before this position
        import re
        page_markers = re.findall(r'--- Page (\d+) ---', search_text)

        if page_markers:
            return int(page_markers[-1])  # Return the last (most recent) page number

        return 1  # Default to page 1 if no markers found

    def _clean_page_markers(self, text: str) -> str:
        """
        Remove page markers from text while preserving content.

        Args:
            text: Text that may contain page markers

        Returns:
            Cleaned text without page markers
        """
        import re
        # Remove page markers but keep the content
        cleaned = re.sub(r'\n--- Page \d+ ---\n', '\n', text)
        return cleaned.strip()

    def get_document_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from PDF document.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with document metadata
        """
        try:
            pdf_document = fitz.open(str(file_path))
            metadata = pdf_document.metadata

            result = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "page_count": len(pdf_document),
                "is_encrypted": pdf_document.is_encrypted,
            }

            pdf_document.close()
            return result

        except Exception as e:
            return {"error": f"Failed to extract metadata: {str(e)}"}

    def is_text_based_pdf(self, file_path: Path) -> bool:
        """
        Check if PDF contains extractable text (not just images).

        Args:
            file_path: Path to PDF file

        Returns:
            True if PDF contains text, False if image-only
        """
        try:
            pdf_document = fitz.open(str(file_path))

            # Check first few pages for text content
            pages_to_check = min(3, len(pdf_document))
            total_text_length = 0

            for page_num in range(pages_to_check):
                page = pdf_document.load_page(page_num)
                text = page.get_text().strip()
                total_text_length += len(text)

            pdf_document.close()

            # If we found reasonable amount of text, it's text-based
            return total_text_length > 100

        except Exception:
            return False