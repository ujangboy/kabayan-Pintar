#!/usr/bin/env python3
"""Kabayan Pintar launcher terpusat (stdlib only, tanpa Textual).

Jalankan via shim `kp`/`kabayan` dari folder mana saja:
  kp start        # tanya GROQ_API_KEY dulu, lalu nyalakan backend :8000
  kp --install    # instalasi core (uv sync)
  kp feature rag  # pasang extra rag/documents/media/all/dev
  kp --fresh      # backup .env+storage lalu install bersih
"""
import getpass
import os
import re
import shutil
import subprocess
import sys

# Resolve symlink (~/.local/bin/kp) ke file asli di folder proyek.
_REAL = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(_REAL))
ENV_PATH = os.path.join(BASE_DIR, ".env")
EXAMPLE_PATH = os.path.join(BASE_DIR, ".env.example")
GROQ_URL = "https://console.groq.com/keys"


def _read_env(key: str) -> str:
    if not os.path.isfile(ENV_PATH):
        return ""
    try:
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    except OSError:
        return ""
    return ""


def _valid(key: str) -> bool:
    key = (key or "").strip()
    if not key or (key.startswith("<") and key.endswith(">")):
        return False
    return bool(re.fullmatch(r"gsk_[A-Za-z0-9]{20,}", key))


def _mask(key: str) -> str:
    key = (key or "").strip()
    if len(key) < 8:
        return "gsk_•••"
    return key[:4] + "•••" + key[-4:]


def _ensure_env() -> None:
    if os.path.isfile(ENV_PATH):
        return
    if os.path.isfile(EXAMPLE_PATH):
        shutil.copyfile(EXAMPLE_PATH, ENV_PATH)
        print(f"==> .env dibuat dari .env.example")
    else:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"GROQ_API_KEY=\nGROQ_MODEL=openai/gpt-oss-20b\n")


def _save_key(key: str) -> None:
    lines = []
    found = False
    if os.path.isfile(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GROQ_API_KEY="):
                    lines.append(f"GROQ_API_KEY={key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"GROQ_API_KEY={key}\n")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _version() -> str:
    p = os.path.join(BASE_DIR, "version.txt")
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().strip() or "dev"
    except OSError:
        return "dev"


def _features() -> list[str]:
    p = os.path.join(BASE_DIR, ".kp-installed-features")
    try:
        with open(p, encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except OSError:
        return []


def _venv_python() -> str | None:
    if os.name == "nt":
        cand = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
        if not os.path.isfile(cand):
            cand = os.path.join(BASE_DIR, ".venv", "Scripts", "python")
    else:
        cand = os.path.join(BASE_DIR, ".venv", "bin", "python")
    return cand if os.path.isfile(cand) else None


def _mode() -> str:
    if os.path.isdir(os.path.join(BASE_DIR, "frontend", "dist")):
        return "production (frontend dist via FastAPI, port 8000)"
    if os.path.isdir(os.path.join(BASE_DIR, "frontend", "node_modules")):
        return "development (frontend via Vite, port 5173)"
    return "backend saja (frontend belum di-build)"


def prompt_api() -> bool:
    """Tanya GROQ_API_KEY satu-satu. Return True bila AI aktif."""
    cur = _read_env("GROQ_API_KEY")
    if _valid(cur):
        return True
    if cur and not (cur.startswith("<") and cur.endswith(">")):
        print(f"[!] GROQ_API_KEY saat ini tidak valid ({_mask(cur)}).")
    print("=" * 56)
    print("  GROQ_API_KEY belum valid — fitur chat/tutor/quiz butuh ini")
    print(f"  Ambil key di: {GROQ_URL}")
    print("  Format: gsk_ + minimal 20 huruf/angka, contoh: gsk_abc123...")
    print("  Tekan Enter kosong untuk lanjut TANPA API (AI mati, web tetap bisa dibuka).")
    print("=" * 56)
    for _ in range(2):
        print(f"\nLangkah 1/3: buka {GROQ_URL} lalu buat/salin key [Enter]")
        try:
            input()
        except EOFError:
            break
        raw = ""
        try:
            raw = getpass.getpass("\nLangkah 2/3: tempel GROQ_API_KEY di sini lalu Enter: ")
        except (EOFError, KeyboardInterrupt):
            raw = ""
        raw = (raw or "").strip()
        if not raw:
            print("  -> Lanjut tanpa API. AI chat/tutor/quiz nonaktif, fitur lain tetap jalan.")
            print("  -> Untuk isi belakangan: edit .env lalu balas 'N' saat launcher bertanya, atau hapus baris GROQ_API_KEY.")
            return False
        if _valid(raw):
            _save_key(raw)
            print(f"  -> Tersimpan di .env ({_mask(raw)}). AI AKTIF.")
            return True
        print("  [!] Format belum benar (harus gsk_ + >=20 alfanumerik). Coba lagi / kosongkan untuk tanpa API.")
    print("  -> Lanjut tanpa API karena key belum valid. Web tetap bisa dibuka.")
    return False


def show_banner(ai_on: bool) -> None:
    print("=" * 56)
    print(f"  KABAYAN PINTAR  v{_version()} — MENYALAKAN")
    print("=" * 56)
    print(f"  Backend : http://127.0.0.1:8000")
    print(f"  Docs    : http://127.0.0.1:8000/docs")
    print(f"  Mode    : {_mode()}")
    print(f"  API     : {'AKTIF (AI bisa dipakai)' if ai_on else 'NONAKTIF — AI mati, Dashboard/Materi/Catatan tetap jalan'}")
    feats = _features()
    print(f"  Fitur   : {', '.join(feats) if feats else 'core'}")
    print("  Install : kp --install | kp --fresh | kp feature rag | kp feature documents | kp feature media | kp feature all")
    print("  Bantuan : kp --help")
    print("  Tekan Ctrl+C untuk berhenti.\n")


def ensure_global_links() -> None:
    """Daftarkan kp/kabayan global bila belum ada (Windows PATH / Linux symlink).

    Idempoten. Dipanggil otomatis setelah install sukses agar pemula tidak
    perlu langkah manual — cukup tutup & buka lagi terminal lalu ketik
    'kp start' / 'kabayan start'.
    Di Windows, shim lama WindowsApps\\kp.cmd dari repo kabayan-agent lama
    (menunjuk Ubuntu-24.04) dinonaktifkan dulu, yang membuat `kp start`
    error WSL_E_DISTRO_NOT_FOUND padahal `kabayan` jalan.
    """
    if os.name == "nt":
        try:
            wa = os.environ.get("LOCALAPPDATA", "")
            if wa:
                for name in ("kp.cmd", "kabayan.cmd"):
                    p = os.path.join(wa, "Microsoft", "WindowsApps", name)
                    if os.path.isfile(p):
                        try:
                            with open(p, encoding="utf-8", errors="ignore") as f:
                                txt = f.read()
                        except OSError:
                            continue
                        if "kabayan-agent" in txt or "Ubuntu-24.04" in txt:
                            bak = p + ".bak"
                            try:
                                if os.path.exists(bak):
                                    os.remove(bak)
                                os.rename(p, bak)
                                print(f"==> Shim lama {name} dinonaktifkan (.bak) agar kp dari folder proyek yang dipakai.")
                            except OSError:
                                pass
        except Exception:
            pass
        p = os.path.join(BASE_DIR, "scripts", "install_windows_path.ps1")
        if os.path.isfile(p):
            try:
                subprocess.call(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                                 "-File", p], cwd=BASE_DIR)
                print("==> PATH proyek terdaftar otomatis. Tutup & buka lagi terminal, lalu ketik: kp start")
            except FileNotFoundError:
                print("[!] powershell tidak ditemukan. Jalankan manual: powershell -ExecutionPolicy Bypass -File scripts\\install_windows_path.ps1")
        return
    bindir = os.path.expanduser("~/.local/bin")
    try:
        os.makedirs(bindir, exist_ok=True)
        for name in ("kp", "kabayan"):
            src = os.path.join(BASE_DIR, name)
            dst = os.path.join(bindir, name)
            if os.path.isfile(src):
                try:
                    if os.path.lexists(dst):
                        os.remove(dst)
                    os.symlink(src, dst)
                except OSError:
                    break
        if (os.pathsep + bindir) in (os.pathsep + os.environ.get("PATH", "")):
            print("==> Perintah global terdaftar: kp / kabayan (kini ketik 'kp start' dari folder mana saja).")
        else:
            print(f"==> Symlink dibuat di {bindir}. Tambahkan ke PATH bila belum ada.")
    except OSError:
        pass


def run_install() -> int:
    if os.name == "nt":
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", os.path.join(BASE_DIR, "scripts", "install_windows.ps1"), "-Mode", "core"]
    else:
        cmd = ["bash", os.path.join(BASE_DIR, "scripts", "install.sh"), "core"]
    code = subprocess.call(cmd, cwd=BASE_DIR)
    if code == 0:
        ensure_global_links()
    return code


def run_fresh() -> int:
    if os.name == "nt":
        # .bat menangani backup .env/storage; panggil langsung.
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", os.path.join(BASE_DIR, "scripts", "install_windows.ps1"), "-Mode", "core"]
        # Backup manual paritas dengan .bat
        if os.path.isfile(ENV_PATH) and not os.path.isfile(ENV_PATH + ".fresh.bak"):
            shutil.copyfile(ENV_PATH, ENV_PATH + ".fresh.bak")
        src = os.path.join(BASE_DIR, "storage")
        dst = src + ".fresh.bak"
        if os.path.isdir(src) and not os.path.isdir(dst):
            shutil.copytree(src, dst)
        code = subprocess.call(cmd, cwd=BASE_DIR)
    else:
        code = subprocess.call(["bash", os.path.join(BASE_DIR, "scripts", "install.sh"), "--fresh"], cwd=BASE_DIR)
    if code == 0:
        ensure_global_links()
    return code


def run_feature(name: str) -> int:
    if name not in ("rag", "documents", "media", "all", "dev"):
        print("Fitur tidak dikenal. Pilihan: rag, documents, media, all, dev")
        return 1
    if os.name == "nt":
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", os.path.join(BASE_DIR, "scripts", "install_windows.ps1"),
               "-Mode", "feature", "-Feature", name]
    else:
        cmd = ["bash", os.path.join(BASE_DIR, "scripts", "install.sh"), "feature", name]
    code = subprocess.call(cmd, cwd=BASE_DIR)
    if code == 0:
        ensure_global_links()
    return code


def cmd_start() -> int:
    if not os.path.isdir(os.path.join(BASE_DIR, ".venv")):
        print("[!] Belum diinstall. Jalankan: kp --install")
        return 1
    _ensure_env()
    ai_on = prompt_api()
    show_banner(ai_on)
    py = _venv_python() or sys.executable
    if os.path.isdir(os.path.join(BASE_DIR, "frontend", "dist")):
        return subprocess.call([py, "-m", "uvicorn", "app.main:app",
                                "--host", "127.0.0.1", "--port", "8000"], cwd=BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, "frontend", "node_modules")):
        # Development: frontend vite di 5173 + backend 8000
        return subprocess.call(["npm", "run", "dev:all"],
                               cwd=os.path.join(BASE_DIR, "frontend"))
    return subprocess.call([py, "-m", "uvicorn", "app.main:app",
                            "--host", "127.0.0.1", "--port", "8000"], cwd=BASE_DIR)


def main(argv: list[str]) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg in ("--install", "install"):
        return run_install()
    if arg in ("--fresh", "fresh"):
        return run_fresh()
    if arg == "feature":
        return run_feature(argv[2] if len(argv) > 2 else "")
    if arg in ("", "run", "start"):
        return cmd_start()
    if arg in ("--help", "help", "-h"):
        print(__doc__.strip())
        print("  kp               # jalankan (tanya API dulu)")
        print("  kp --install     # instalasi core saja")
        print("  kp --fresh       # backup .env+storage, install bersih")
        print("  kp feature rag   # ekstra RAG (~250MB)")
        return 0
    print("Penggunaan: kp [--install|--fresh|feature rag|documents|media|all|dev|start]")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except KeyboardInterrupt:
        print("\nBerhenti.")
        raise SystemExit(130)
