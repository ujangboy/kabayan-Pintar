"""FastEmbed implementation of EmbeddingProvider.

Lazy import: `fastembed` tidak diimpor di level module agar backend
core bisa nyala tanpa FastEmbed terpasang. Model diunduh on-demand
melalui ModelManager saat pertama kali dipakai.
"""

from typing import List

from app.services.embedding.base import EmbeddingProvider
from app.services.embedding.model_manager import model_manager


class FastEmbedProvider(EmbeddingProvider):
    """Provider embedding berbasis FastEmbed (ONNX Runtime)."""

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_DIMENSION = 384

    def __init__(self, model_name: str = None):
        self._model_name = model_name or self.DEFAULT_MODEL
        self._embedder = None

    def _ensure_loaded(self):
        """Muat model FastEmbed secara lazy (on-demand)."""
        if self._embedder is not None:
            return
        # Jika model belum ada di cache, unduh terlebih dahulu.
        if not model_manager.is_model_available():
            model_manager.download_model()
        from fastembed import TextEmbedding  # lazy import

        self._embedder = TextEmbedding(model_name=self._model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._ensure_loaded()
        return list(self._embedder.embed(texts))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Alias untuk kompatibilitas dengan kode lama yang memanggil
        embed_documents (digunakan RAGService.index_document)."""
        return self.embed_texts(texts)

    def embed_query(self, text: str) -> List[float]:
        self._ensure_loaded()
        return list(self._embedder.embed([text]))[0]

    def dimension(self) -> int:
        return self.DEFAULT_DIMENSION

    def is_available(self) -> bool:
        try:
            import fastembed  # noqa: F401

            return True
        except ImportError:
            return False
