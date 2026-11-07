"""is_ai_enabled: hanya gsk_ + >=20 alfanumerik yang aktif."""
from app.config import is_ai_enabled


def test_ai_disabled_when_empty_or_placeholder():
    assert is_ai_enabled("") is False
    assert is_ai_enabled("<isi-groq-api-key-anda-di-sini>") is False
    assert is_ai_enabled(None) is False


def test_ai_enabled_only_for_valid_format():
    assert is_ai_enabled("gsk_abc123abc123abc123abc123") is True
    assert is_ai_enabled("gsk_short") is False
    assert is_ai_enabled("test-key") is False
