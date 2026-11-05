"""Informasi aplikasi + versi — untuk halaman Tentang (Settings)."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import uuid

from app.database import SessionLocal
from app.services.settings_service import APP_VERSION, settings_service
from app.schemas.responses import InfoResponse

router = APIRouter()


@router.get("/api/info", response_model=InfoResponse)
async def get_app_info():
    """Kembalikan info aplikasi lengkap dengan install identity."""
    db = SessionLocal()
    try:
        # Ambil atau buat install_id agar bisa mendeteksi instalasi fresh vs upgrade.
        install_id = settings_service.get_setting(db, "app.install_id", None)
        if not install_id:
            install_id = str(uuid.uuid4())
            try:
                settings_service.set_setting(
                    db, "app.install_id", install_id,
                    "UUID yang mengidentifikasi instalasi ini; berubah hanya saat fresh-install.",
                )
                db.commit()
            except Exception:
                db.rollback()  # gagal simpan tidak boleh menggagalkan /api/info

        fresh_install = settings_service.get_setting(db, "app.fresh_install", "0") == "1"
    finally:
        db.close()

    return JSONResponse({
        "app_name": "Kabayan Pintar",
        "version": APP_VERSION,
        "description": "Ruang belajar cerdas berbasis AI: materi, chat, flashcard, quiz, dan simulasi ujian.",
        "install_id": install_id,
        "fresh_install": fresh_install,
    })