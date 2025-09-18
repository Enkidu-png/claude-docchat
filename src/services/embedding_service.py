"""
Embedding service with sentence-transformers integration.
"""

import asyncio
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from ..config.settings import get_settings


class EmbeddingService:
    """Service for generating text embeddings using sentence transformers."""

    def __init__(self):
        self.settings = get_settings()
        self._model = None
        self._model_name = self.settings.embedding.model_name

    async def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        if self._model is None:
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()

            def load_model():
                try:
                    # Create model with proper device handling
                    model = SentenceTransformer(self._model_name, device='cpu')

                    # Ensure model is properly initialized and moved to CPU
                    model.eval()

                    # Test encoding to ensure model works
                    _ = model.encode(["test"], convert_to_numpy=True)

                    return model
                except Exception as e:
                    # Fallback: try loading with explicit CPU device and no cache
                    import logging
                    logging.warning(f"Model loading failed, trying fallback: {e}")
                    model = SentenceTransformer(self._model_name, device='cpu', cache_folder=None)
                    model.eval()
                    return model

            self._model = await loop.run_in_executor(None, load_model)
        return self._model

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            384-dimensional embedding vector
        """
        model = await self._load_model()

        # Run encoding in thread pool with error handling
        loop = asyncio.get_event_loop()

        def encode_text():
            try:
                # Ensure text is clean and not empty
                clean_text = str(text).strip()
                if not clean_text:
                    clean_text = "empty document"

                embedding = model.encode([clean_text], convert_to_numpy=True, device='cpu')
                return embedding[0].tolist()
            except Exception as e:
                # Log the error and return a zero vector as fallback
                import logging
                logging.error(f"Embedding generation failed for text (length={len(text)}): {e}")
                # Return a zero vector with correct dimensions
                return [0.0] * 384

        return await loop.run_in_executor(None, encode_text)

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of 384-dimensional embedding vectors
        """
        if not texts:
            return []

        model = await self._load_model()
        batch_size = self.settings.embedding.batch_size

        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Run encoding in thread pool with error handling
            loop = asyncio.get_event_loop()

            def encode_batch():
                try:
                    # Clean the batch texts
                    clean_batch = [str(text).strip() or "empty document" for text in batch]
                    embeddings = model.encode(clean_batch, convert_to_numpy=True, device='cpu')
                    return [emb.tolist() for emb in embeddings]
                except Exception as e:
                    # Log error and return zero vectors for the batch
                    import logging
                    logging.error(f"Batch embedding generation failed for {len(batch)} texts: {e}")
                    return [[0.0] * 384 for _ in batch]

            batch_embeddings = await loop.run_in_executor(None, encode_batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Normalize to 0-1 range
        return float((similarity + 1) / 2)

    def get_vector_dimension(self) -> int:
        """Get the dimension of embedding vectors."""
        return 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors