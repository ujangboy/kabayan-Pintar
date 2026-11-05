"""Local Model Manager untuk embedding FastEmbed.

Mengelola unduhan, cache, dan integritas model embedding secara
cross-platform (Windows + Linux). Model disimpan di direktori cache
konsisten dan dapat digunakan secara offline setelah diunduh.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


class ModelManager:
    """Pengelola model embedding lokal."""

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    CACHE_SUBDIR = ".cache/kabayan-pintar/embedding-models"
    MANIFEST_FILE = "manifest.json"

    def __init__(self, model_name: str = None, cache_dir: str = None):
        self._model_name = model_name or self.DEFAULT_MODEL
        if cache_dir:
            self._cache_dir = Path(cache_dir)
        else:
            home = Path.home()
            self._cache_dir = home / Path(self.CACHE_SUBDIR)
        self._model_dir = self._cache_dir / self._model_name.replace("/", "_")
        self._manifest_path = self._cache_dir / self.MANIFEST_FILE

    def get_cache_dir(self) -> str:
        return str(self._cache_dir)

    def get_model_dir(self) -> str:
        return str(self._model_dir)

    def is_model_available(self) -> bool:
        """Cek apakah model sudah tersedia di cache (bisa dipakai offline)."""
        if not self._model_dir.is_dir():
            return False
        onnx_files = list(self._model_dir.rglob("*.onnx"))
        return len(onnx_files) > 0 and self._check_manifest()

    def _check_manifest(self) -> bool:
        if not self._manifest_path.exists():
            return True
        try:
            with open(self._manifest_path, "r") as f:
                manifest = json.load(f)
            return manifest.get("model") == self._model_name
        except Exception:
            return False

    def download_model(self) -> str:
        """Pastikan direktori cache siap (fastembed akan unduh model saat
        TextEmbedding pertama kali di-instansiasi)."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._write_manifest()
        return str(self._model_dir)

    def _write_manifest(self):
        manifest = {
            "model": self._model_name,
            "dimension": 384,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self._manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

    def check_integrity(self) -> bool:
        """Verifikasi integritas file model (file .onnx ada dan tidak kosong)."""
        if not self.is_model_available():
            return False
        for f in self._model_dir.rglob("*.onnx"):
            if f.stat().st_size == 0:
                return False
        return True

    def get_status(self) -> Dict:
        """Info status model untuk ditampilkan ke user."""
        return {
            "model": self._model_name,
            "cache_dir": str(self._cache_dir),
            "model_dir": str(self._model_dir),
            "available": self.is_model_available(),
            "integrity_ok": self.check_integrity(),
        }


# Singleton instance untuk digunakan di seluruh aplikasi.
model_manager = ModelManager()
