"""
Document processor factory for creating appropriate processors.
"""

from pathlib import Path
from typing import Union

from ...models.enums import DocumentType
from .txt_processor import TxtProcessor
from .pdf_processor import PdfProcessor
from .docx_processor import DocxProcessor


class ProcessorFactory:
    """Factory for creating document processors based on file type."""

    def __init__(self):
        self._processors = {
            DocumentType.TXT: TxtProcessor,
            DocumentType.PDF: PdfProcessor,
            DocumentType.DOCX: DocxProcessor,
        }

    def get_processor(self, file_path: Path) -> Union[TxtProcessor, PdfProcessor, DocxProcessor, None]:
        """
        Get appropriate processor for file type.

        Args:
            file_path: Path to document file

        Returns:
            Processor instance or None if unsupported

        Raises:
            ValueError: If file type is unsupported
        """
        try:
            doc_type = DocumentType.from_extension(file_path.suffix)
            processor_class = self._processors.get(doc_type)

            if processor_class:
                return processor_class()

            raise ValueError(f"No processor available for {doc_type}")

        except ValueError as e:
            raise ValueError(f"Unsupported file type for {file_path}: {e}")

    def is_supported(self, file_path: Path) -> bool:
        """Check if file type is supported."""
        try:
            doc_type = DocumentType.from_extension(file_path.suffix)
            return doc_type in self._processors
        except ValueError:
            return False

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions."""
        return [f".{doc_type.value}" for doc_type in self._processors.keys()]