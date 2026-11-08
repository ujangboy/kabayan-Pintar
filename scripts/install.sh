#!/usr/bin/env bash
# install.sh — Installer modular Kabayan Pintar (Linux / WSL)
# Penggunaan:
#   bash install.sh                        # instalasi core saja
#   bash install.sh --install              # sama di atas
#   bash install.sh --fresh                # backup .env + storage lalu install
#   bash install.sh feature rag            # pasang extra RAG
#   bash install.sh feature documents      # pasang extra dokumen
#   bash install.sh feature media          # pasang extra media
#   bash install.sh feature all            # pasang semua extra (rag+documents+media)
#   bash install.sh feature dev            # pasang alat testing
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/.."

# ── Helper ──────────────────────────────────────────────────────────
log()  { echo "==> $*"; }
err()  { echo "[!] $*" >&2; exit 1; }

# ── Cek Python 3.12 ────────────────────────────────────────────────
check_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        err "Python 3 tidak ditemukan. Silakan install Python 3.12 terlebih dahulu."
    fi
    local ver
    ver=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' || true)
    if [ -n "$ver" ] && [ "$ver" != "3.12" ]; then
        echo "[!] Peringatan: Python $ver terdeteksi, target 3.12. Lanjutkan comunque."
    fi
}

# ── Cek / pasang uv ────────────────────────────────────────────────
ensure_uv() {
    if command -v uv >/dev/null 2>&1; then
        return
    fi
    # Fallback: uv sudah ada di ~/.local/bin (default pip/install.sh)
    if [ -x "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
        return
    fi
    log "uv belum ditemukan, memasang uv..."
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        err "curl/wget tidak ditemukan. Pasang uv secara manual: https://github.com/astral-sh/uv"
    fi
    export PATH="$HOME/.local/bin:$PATH"
}

# ── Buat virtual environment ───────────────────────────────────────
ensure_venv() {
    if [ ! -d ".venv" ]; then
        log "Membuat virtual environment (.venv)..."
        uv venv .venv
        return
    fi
    if [ ! -f ".venv/bin/activate" ]; then
        err ".venv yang ada bukan environment Linux/Mac (kemungkinan hasil Windows). Rename jadi .venv-win atau hapus, lalu jalankan installer lagi."
    fi
}

# ── Pasang dependensi ──────────────────────────────────────────────
install_deps() {
    local groups="$1"
    log "Memasang dependensi: $groups"
    # shellcheck disable=SC1091
    . .venv/bin/activate
    if [ "$groups" = "core" ]; then
        uv sync
    elif [ "$groups" = "all" ]; then
        # pyproject tidak punya extra "all"; terjemahkan ke tiga extra nyata.
        uv sync --extra rag --extra documents --extra media
    else
        uv sync --extra "$groups"
    fi
}

# ── Backup data user untuk install fresh ─────────────────────────────
backup_user_data() {
    local out="${APPDATA:-}"
    if [ -f .env ] && [ ! -f .env.fresh.bak ]; then
        cp .env .env.fresh.bak
        log ".env lama disimpan ke .env.fresh.bak"
    fi
    if [ -d storage ] && [ ! -d storage.fresh.bak ]; then
        cp -a storage storage.fresh.bak
        log "storage/ lama disimpan ke storage.fresh.bak"
    fi
}

# ── Simpan konfigurasi fitur yang terpasang ─────────────────────────
save_feature() {
    local feature="$1"
    local state_file=".kp-installed-features"
    if [ ! -f "$state_file" ] || ! grep -qx "$feature" "$state_file"; then
        echo "$feature" >> "$state_file"
    fi
}

# ── Daftarkan kp/kabayan global (Linux/WSL) ─────────────────────────
# Idempoten: buat symlink ~/.local/bin/kp dan kabayan bila belum ada.
ensure_global_links() {
    local bindir="$HOME/.local/bin"
    mkdir -p "$bindir"
    ln -sf "$PWD/kp" "$bindir/kp"
    ln -sf "$PWD/kabayan" "$bindir/kabayan"
    if [[ ":$PATH:" == *":$bindir:"* ]]; then
        log "Perintah global terdaftar: kp / kabayan (kini ketik 'kp start' dari folder mana saja)."
    else
        log "[!] $bindir belum di PATH. Tambahkan: export PATH=\"$bindir:\$PATH\" (lalu simpan di ~/.bashrc)."
        log "Atau jalankan dari folder proyek via ./kp start."
    fi
}

# ── Main ────────────────────────────────────────────────────────────
case "${1:-core}" in
    core|--install|install)
        check_python
        ensure_uv
        ensure_venv
        install_deps core
        save_feature core
        ensure_global_links
        log "Instalasi core selesai. Jalankan './kp start' atau 'kp start' untuk memulai aplikasi."
        ;;
    --fresh|fresh)
        check_python
        backup_user_data
        ensure_uv
        ensure_venv
        install_deps core
        save_feature core
        ensure_global_links
        log "Instalasi fresh selesai. Data lama disimpan di .env.fresh.bak dan storage.fresh.bak."
        ;;
    feature)
        shift || true
        feature="${1:-}"
        case "$feature" in
            rag|documents|media|all|dev)
                check_python
                ensure_uv
                ensure_venv
                install_deps "$feature"
                save_feature "$feature"
                ensure_global_links
                log "Fitur '$feature' terpasang. Jalankan './kp start' atau 'kp start' untuk memulai aplikasi."
                ;;
            *)
                err "Fitur tidak dikenal: '$feature'. Pilihan: rag, documents, media, all"
                ;;
        esac
        ;;
    *)
        err "Penggunaan: bash install.sh [core|--install|--fresh|feature <rag|documents|media|all|dev>]"
        ;;
esac
