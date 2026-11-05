"""Interface EmbeddingProvider (adapter abstraction).

Mengabstraksi provider embedding agar pergantian provider di masa depan
tidak memerlukan perubahan di RAGService. Implementasi konkret (mis.
FastEmbedProvider) diambil lazy oleh RAGService hanya saat fitur RAG
digunakan.
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Interface untuk provider embedding lokal."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed banyak teks sekaligus. Mengembalikan list vektor."""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed satu query. Mengembalikan satu vektor."""
        raise NotImplementedError

    @abstractmethod
    def dimension(self) -> int:
        """Dimensi vektor hasil embedding (mis. 384 untuk all-MiniLM-L6-v2)."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """True jika dependensi provider dan model sudah tersedia."""
        raise NotImplementedError
