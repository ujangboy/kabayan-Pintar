# Kabayan Pintar

Study workspace berbasis FastAPI + React untuk mengelola mata kuliah, materi,
catatan, flashcard, quiz, simulasi ujian, dan tutor AI.

Proyek ini dibangun dengan **vibe coding** — ditulis sejumlah besar oleh AI
(Kilo/Claude) dengan panduan desain sistem dan arsitektur yang konsisten, lalu
diverifikasi oleh manusia lewat tes dan audit. Cocok sebagai starter untuk
proyek AI-assisted atau untuk dipelajari cara membangun aplikasi AI full-stack.

## Nama

**Kabayan Pintar** (lengkap) / **Kabayan** (pendek). Identifier internal
memakai prefix `kabayan` (database, backup, theme) dan tidak di-rename.

---

## AI yang digunakan

| Leksi | Digunakan untuk |
|-------|-----------------|
| **Groq (openai/gpt-oss-20b / qwen-vision)** | Chat AI, tutor, generate flashcard & quiz, analisis ujian, RAG |
| **FastEmbed (ONNX Runtime, model `sentence-transformers/all-MiniLM-L6-v2`)** | Embedding lokal untuk pencarian vektor (RAG) |
| **LanceDB** | Penyimpanan vektor persisten |

API key Groq **tidak di-commit** — isi di `.env` milik Anda sendiri (lihat di bawah).

---

## Isi proyek

- `app/` — backend FastAPI (entry `app.main:app`): config, database, models, routers, services, parsers, agents, prompts
- `frontend/` — UI React 19 + Vite + Tailwind (port 5173 dev)
- `alembic/` — migrasi database SQLite (source of truth skema)
- `scripts/` — skrip operasi (backup, seed, install)
- `tests/` — tes backend (pytest) + frontend (vitest)
- `docs/` — aturan agent, baseline, konteks AI
- `storage/` — database, upload, vector store (runtime, **tidak di-commit**)

---

## Panduan pemasangan cepat

Kabayan Pintar sekarang dipasang secara **modular**. Versi core hanya berisi
dependensi untuk fitur utama (AI Chat, Tutor, Flashcard, Quiz). Fitur lain
dipasang terpisah bila dibutuhkan.

### Apa yang dipasang?

Konfigurasi Python dikelola dengan **`uv`** (astral.sh), package manager cepat
berbasis Rust. `uv` menggantikan `pip`/`venv` untuk proyek ini:

- membuat virtual environment `.venv`,
- membaca dependensi dari `pyproject.toml`,
- memasukan versi persis dari `uv.lock`,
- memasang fitur optional dengan `uv sync --extra <nama>`.

Anda **tidak perlu memahami `uv`** untuk memakainya — semua dijalankan lewat
perintah `kp`.

### Persyaratan

- Windows 10/11 dengan PowerShell **atau** Linux/WSL dengan Python yang sesuai.
- Python 3.12 dianjurkan (Python 3.13 juga bisa jalan, muncul peringatan).
- Internet untuk download package.
- **Tidak perlu Node.js** untuk penggunaan normal.
- Groq API key untuk fitur AI. Tanpa key, aplikasi **tetap bisa dibuka**
  (port 8000) tapi AI chat/tutor nonaktif — peringatan tampil di
  halaman chat saja, fitur lain tetap bisa dipakai minimal.

### Instalasi

**Linux / WSL / Git Bash**

```bash
git clone <repo-url> kabayan-pintar
cd kabayan-pintar
chmod +x kp
./kp --install
```

**Windows (PowerShell / CMD)**

```powershell
git clone <repo-url> kabayan-pintar
cd kabayan-pintar
.\kp --install
```

Installer akan:

1. Membuat `.env` dari `.env.example` jika belum ada.
2. Memeriksa Python.
3. Memasang `uv` jika belum tersedia.
4. Membuat folder `.venv`.
5. Memasang **core dependencies saja**.
6. Tidak menyentuh `storage/` pada instalasi pertama.

Dari folder proyek, jalankan `./kp` (Linux) atau `.\kp.cmd` (Windows) untuk menjalankan aplikasi.

#### Dari folder mana saja (`kp` / `kabayan` global)

Setelah install sekali, perintah `kp` dan `kabayan` bisa dipanggil dari
folder mana pun — keduanya memanggil launcher python terpusat
`scripts/kp.py` (stdlib, tanpa reinstall library).

- **Linux/WSL:** symlink ke `~/.local/bin` (pastikan ada di PATH):
  ```bash
  ln -sf "$PWD/kp" ~/.local/bin/kp
  ln -sf "$PWD/kabayan" ~/.local/bin/kabayan
  kp --help   # atau ketik: kp start
  kabayan start
  ```
- **Windows (PowerShell):** daftarkan folder proyek ke PATH user:
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts\install_windows_path.ps1
  # Tutup lalu buka lagi terminal, lalu:
  kp start
  kabayan start
  ```
  Tanpa langkah ini, tetap bisa jalan dari folder proyek via
  `.\kp.cmd` / `.\kabayan.cmd`. Port tetap **8000** setelah
  inisialisasi (lihat banner terminal).

### Menjalankan aplikasi (production)

Frontend hasil build produksi sudah disertakan dalam repositori
(`frontend/dist/`), sehingga hanya satu URL yang dibutuhkan: **API & UI di
port 8000**.

- **Linux:** `./kp` atau `./kp start`
- **Windows:** `.\kp`, `.\kp start`, atau `.\kp.cmd`

Saat start, launcher (a) memeriksa `GROQ_API_KEY` dan menanya
satu-satu bila belum valid, (b) menampilkan banner versi, port,
status API, fitur terpasang, dan contoh `kp feature ...`, lalu
(c) menyalakan backend tanpa menginstal ulang library. Setelah
inisialisasi, port tetap **8000** seperti berikut:

Backend membuka URL:

- **http://127.0.0.1:8000**
- API docs: **http://127.0.0.1:8000/docs**
- Frontend dev (hanya mode development): **http://127.0.0.1:5173**

> Jika `frontend/dist/` ada, FastAPI menyajikan UI React langsung. Node.js
> tidak diperlukan.
>
> Bila ingin development mode, install Node.js lalu jalankan
> `cd frontend && npm install`, lalu `npm run dev:all`.

### Fitur utama dan fitur yang harus diaktifkan

| Fitur | `kp feature` | Kebutuhan tambahan |
|---|---|---|
| AI Chat, Tutor, Flashcard, Quiz | **Core** (otomatis) | Groq API key |
| Pencarian vektor / RAG lokal | `./kp feature rag` | ~250 MB tambahan, tunjang untuk dokumen besar |
| Pemrosesan dokumen (PDF, DOCX, XLSX, PPTX) | `./kp feature documents` | PyMuPDF, python-docx, openpyxl, python-pptx |
| YouTube, TTS, media | `./kp feature media` | yt-dlp, edge-tts, imageio-ffmpeg |
| Semua fitur | `./kp feature all` | Semua di atas |
| Development / testing | `./kp feature dev` | pytest, httpx, pytest-asyncio |

Contoh:

```bash
./kp feature rag          # Linux
.\kp.cmd feature rag      # Windows
```

### Instalasi fresh

```bash
./kp --fresh             # Linux
.\kp.cmd --fresh         # Windows
```

`--fresh` memindahkan `.env` ke `.env.fresh.bak` dan `storage/` ke
`storage.fresh.bak`, lalu membuat instalasi bersih. Data lama tetap
tersimpan dan bisa dipulihkan.

### Pengaturan wajib sebelum fitur AI jalan

**Cara termudah — lewat terminal (`kp start` akan menanya satu-satu):**

1. Buka https://console.groq.com/keys di browser, buat/salin API key.
2. Jalankan `kp start` (atau `kabayan start`) dari folder mana saja.
3. Tempel key saat diminta (format `gsk_` + minimal 20 huruf/angka).
4. Key tersimpan ke `.env` (hanya baris `GROQ_API_KEY` yang diubah).
5. Tekan Enter kosong untuk lanjut **tanpa API** (AI mati, web tetap dibuka).

**Cara manual — edit `.env` langsung:**

```bash
cp .env.example .env
# isi GROQ_API_KEY dari https://console.groq.com/keys
# lalu restart: kp start
```

`.env` tidak pernah di-commit. Setiap pengguna memiliki data sendiri di
`storage/`.

#### Jalan tanpa API (AI mati, web tetap dibuka)

| Fitur | Dengan GROQ_API_KEY valid | Tanpa API (minimal) |
|---|---|---|
| Dashboard, Materi (upload/lihat), Catatan, Pengaturan, Sampah | OK | OK (tetap jalan) |
| Chat AI, Tutor, Flashcard/Quiz via AI, Analisis ujian AI | OK | Mati — banner peringatan **hanya di halaman chat**, backend balas 503 jelas |
| RAG lokal, pemrosesan dokumen, YouTube/TTS | OK bila `kp feature ...` terpasang | Sama, tapi tanpa AI tidak bisa generate dari dokumen |
| Port | **8000** tetap | **8000** tetap |

### Penyimpanan & data pengguna

- `.env` tidak disertakan di repository.
- `storage/` (database, upload, vector store) **tidak disertakan**.
- `storage/` baru dibuat ketika aplikasi pertama kali dijalankan.
- Setiap pengguna baru mulai dengan data kosong.
- `.kp-installed-features` adalah file penanda fitur yang terpasang, juga
  tidak disertakan di repository.

### Jika `.venv` tidak kompatibel

Jika sebelumnya menggunakan versi Linux dan sekarang di Windows (atau
sebaliknya), hapus atau rename `.venv`, lalu jalankan installer lagi:

```bash
# Linux
mv .venv .venv-win   # jika berasal dari Windows
# Windows (PowerShell)
Rename-Item .venv .venv-linux
```

### Troubleshooting

- **`uv` tidak ditemukan** → installer otomatis mencobanya; pastikan internet.
- **Port 8000 sudah dipakai** → tutup aplikasi/instance lain pada port itu.
- **Fitur AI error** → cek `GROQ_API_KEY` di `.env`.
- **RAG error** → jalankan `./kp feature rag`.
- **Dokumen tidak terbaca** → jalankan `./kp feature documents`.
- **YouTube/TTS bermasalah** → jalankan `./kp feature media`.

---

## Tes & quality gates

```bash
# Backend
pytest -q

# Frontend (di folder frontend/)
cd frontend
npm test      # vitest
npm run build # vite production build
npm run lint  # oxlint
```

---

## Database & migrasi

Alembic adalah source of truth skema. Saat aplikasi start, `app/main.py`
menjalankan `alembic upgrade head`.

```bash
alembic current
alembic check   # harus: "No new upgrade operations detected."
```

---

## Teknologi

- Python 3.12 / FastAPI
- SQLAlchemy + Alembic (SQLite)
- React 19 + Vite + Tailwind CSS
- FastEmbed (ONNX Runtime) + LanceDB (RAG)
- Groq (AI chat/tutor/generate)
- `uv` (Python package manager) + `pyproject.toml` + `uv.lock`
- Frontend produksi disajikan langsung oleh FastAPI (`frontend/dist/`)

---

## Lisensi

MIT. Lihat berkas `LICENSE`.

Dokumen penting (folder `docs/`): `ATURAN_KERJA_DENGAN_AGENT.md`,
`PROTECTED_BASELINE.md`, `ai_context.md`.
