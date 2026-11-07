"""Core-only install harus tetap bisa import tanpa extra documents/media."""
import tempfile
from pathlib import Path

from app.parsers import document_parser


def test_document_parser_importable_without_documents_extra():
    # Bila pymupdf/docx memang hilang, modul tetap harus bisa diimport
    # (untuk startup core). Bila terpasang, test ini sekadar lolos.
    assert hasattr(document_parser, "extract_text")


def test_extract_pdf_returns_friendly_when_missing(tmp_path):
    if document_parser.fitz is not None:
        return  # documents terpasang, tidak bisa uji path missing
    p = Path(tmp_path) / "x.pdf"
    p.write_bytes(b"%PDF-1.4 fake")
    out = document_parser.extract_text(str(p))
    assert "documents" in out.lower()


def test_extract_txt_still_works_without_extras(tmp_path):
    p = Path(tmp_path) / "a.txt"
    p.write_text("halo kabayan", encoding="utf-8")
    assert document_parser.extract_text(str(p)) == "halo kabayan"


def test_audio_service_importable_without_media_extra(monkeypatch):
    # Simulasikan core: edge_tts/imageio-ffmpeg hilang → audio_service
    # tetap bisa diimport, generate menolak dengan pesan jelas.
    import sys

    class _Missing:
        def __getattr__(self, name):
            raise ImportError("simulated missing")

    saved = {k: sys.modules.get(k) for k in ("edge_tts", "imageio_ffmpeg")}
    sys.modules["edge_tts"] = _Missing()
    sys.modules["imageio_ffmpeg"] = _Missing()
    # Pastikan modul media dimuat ulang dari nol
    sys.modules.pop("app.services.audio_service", None)
    try:
        from app.services import audio_service

        assert audio_service.HAS_EDGE_TTS is False
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        sys.modules.pop("app.services.audio_service", None)
