"""Paket adaptor embedding (lazy).

Modul ini diimpor oleh RAGService hanya saat fitur RAG dipakai, bukan
saat backend core pertama kali nyala. Dengan demikian instalasi core
tidak membutuhkan FastEmbed / ONNX Runtime / model embedding.
"""

from app.services.embedding.base import EmbeddingProvider
from app.services.embedding.fastembed_provider import FastEmbedProvider
from app.services.embedding.model_manager import model_manager

__all__ = ["EmbeddingProvider", "FastEmbedProvider", "model_manager"]
