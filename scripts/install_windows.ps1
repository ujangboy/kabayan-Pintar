# install_windows.ps1 - Installer modular Kabayan Pintar (Windows)
# Usage:
#   .\install_windows.ps1
#   .\install_windows.ps1 -Mode feature -Feature rag
#   .\install_windows.ps1 -Mode feature -Feature all   # rag+documents+media
#   .\install_windows.ps1 -Mode feature -Feature dev

param(
    [string]$Mode = "core",
    [string]$Feature = ""
)

$ErrorActionPreference = "Stop"
$DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $DIR "..")

function Log ($msg) { Write-Host "==> $msg" }
function Err ($msg) { Write-Host "[!] $msg" -ForegroundColor Red; exit 1 }

function Check-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) { return }
    if (Get-Command python -ErrorAction SilentlyContinue) { return }
    if (Get-Command python3 -ErrorAction SilentlyContinue) { return }
    Err "Python tidak ditemukan di PATH (py/python/python3). Install Python 3.12 dulu, contoh: winget install Python.Python.3.12 lalu buka terminal baru."
}

function Ensure-UV {
    if (Get-Command uv -ErrorAction SilentlyContinue) { return }
    Log "uv belum ditemukan, memasang uv..."
    Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile $env:TEMP\uv-install.ps1
    & $env:TEMP\uv-install.ps1
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
}

function Ensure-Venv {
    if (-not (Test-Path ".venv")) {
        Log "Membuat virtual environment (.venv)..."
        & uv venv .venv
        if (-not $?) { Err "Gagal membuat .venv" }
        return
    }
    if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
        Err "\.venv yang ada bukan environment Windows (kemungkinan hasil Linux/Mac). Rename .venv jadi .venv-linux atau hapus, lalu jalankan installer lagi."
    }
}

function Save-Feature ([string]$f) {
    $stateFile = ".kp-installed-features"
    $existing = if (Test-Path $stateFile) { Get-Content $stateFile } else { @() }
    if ($existing -notcontains $f) {
        Add-Content -Path $stateFile -Value $f
    }
}

# Daftarkan folder proyek ke PATH user (idempoten) agar `kp`/`kabayan`
# bisa diketik dari terminal mana saja setelah install. Tidak perlu manual.
# Sambil itu, perbaiki shim lama WindowsApps\kp.cmd yang menunjuk repo lama
# (kabayan-agent / Ubuntu-24.04) yang membuat `kp start` error
# WSL_E_DISTRO_NOT_FOUND padahal `kabayan` jalan.
function Repair-Stale-Kp-Shim {
    $wa = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps"
    foreach ($name in @("kp.cmd", "kabayan.cmd")) {
        $p = Join-Path $wa $name
        if (Test-Path $p) {
            $txt = Get-Content -Raw -LiteralPath $p -ErrorAction SilentlyContinue
            if ($txt -and ($txt -match 'kabayan-agent|Ubuntu-24\.04')) {
                $bak = "$p.bak"
                if (Test-Path $bak) { Remove-Item -LiteralPath $bak -Force }
                Rename-Item -LiteralPath $p -NewName ([IO.Path]::GetFileName($bak))
                Log "Shim lama $name (kabayan-agent/Ubuntu-24.04) dinonaktifkan ke .bak agar kp dari folder proyek yang dipakai."
            }
        }
    }
}

function Register-Kp-Path {
    Repair-Stale-Kp-Shim
    $p = Join-Path $DIR "install_windows_path.ps1"
    if (Test-Path $p) {
        & $p
    }
}

function Install-Deps ([string]$Groups) {
    Log "Memasang dependensi: $Groups"
    $activate = ".venv\Scripts\Activate.ps1"
    if (-not (Test-Path $activate)) {
        Err "Activate script tidak ditemukan: $activate"
    }
    . $activate
    if ($Groups -eq "core") {
        & uv sync
    } elseif ($Groups -eq "all") {
        # pyproject tidak punya extra "all"; terjemahkan ke tiga extra nyata.
        & uv sync --extra rag --extra documents --extra media
    } else {
        & uv sync --extra $Groups
    }
    if (-not $?) { Err "Gagal memasang dependensi ($Groups)" }
}

switch ($Mode) {
    "core" {
        Check-Python
        Ensure-UV
        Ensure-Venv
        Install-Deps "core"
        Save-Feature "core"
        Log "Instalasi core selesai. Jalankan '.\kp.cmd start' untuk memulai aplikasi."
        Register-Kp-Path
        Log "PATH proyek terdaftar otomatis. Tutup lalu buka lagi terminal, lalu ketik: kp start (atau kabayan start)."
    }
    "feature" {
        if (-not $Feature) { Err "Sebutkan Feature: rag, documents, media, all, dev" }
        switch ($Feature) {
            "rag"       { Check-Python; Ensure-UV; Ensure-Venv; Install-Deps "rag";       Save-Feature "rag";       Log "Fitur 'rag' terpasang." }
            "documents" { Check-Python; Ensure-UV; Ensure-Venv; Install-Deps "documents"; Save-Feature "documents"; Log "Fitur 'documents' terpasang." }
            "media"     { Check-Python; Ensure-UV; Ensure-Venv; Install-Deps "media";     Save-Feature "media";     Log "Fitur 'media' terpasang." }
            "all"       { Check-Python; Ensure-UV; Ensure-Venv; Install-Deps "all";       Save-Feature "all";       Log "Semua fitur terpasang." }
            "dev"       { Check-Python; Ensure-UV; Ensure-Venv; Install-Deps "dev";       Save-Feature "dev";       Log "Fitur 'dev' (testing) terpasang." }
            default     { Err "Fitur tidak dikenal: '$Feature'. Pilihan: rag, documents, media, all, dev" }
        }
        Register-Kp-Path
    }
    default {
        Err "Penggunaan: .\install_windows.ps1 [-Mode core|feature] [-Feature <rag|documents|media|all|dev>]"
    }
}