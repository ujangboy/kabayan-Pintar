@echo off
setlocal
title Kabayan Pintar Launcher
color 0A
pushd "%~dp0" >nul

rem Parse argumen
if /i "%~1"=="--install" goto install
if /i "%~1"=="install" goto install
if /i "%~1"=="feature" goto feature
if /i "%~1"=="--fresh" goto fresh
if /i "%~1"=="fresh" goto fresh
if "%~1"=="" goto run
if /i "%~1"=="run" goto run
if /i "%~1"=="start" goto run
echo Penggunaan: kp [--install|--fresh|feature <rag|documents|media|all>|start]
exit /b 1

:install
echo =========================================
echo      INSTALL KABAYAN PINTAR (CORE)
echo =========================================
echo.
if not exist ".env" copy /y ".env.example" ".env" >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1" -Mode core
if errorlevel 1 goto fail
echo.
echo Selesai install core. Ketik: kp start
exit /b 0

:fresh
echo =========================================
echo      FRESH INSTALL KABAYAN PINTAR
echo      Data lama disimpan ke .env.fresh.bak / storage.fresh.bak
echo =========================================
echo.
if exist ".env" (
    if not exist ".env.fresh.bak" (
        copy /y ".env" ".env.fresh.bak" >nul
        echo [!] .env lama disimpan ke .env.fresh.bak
    )
)
if exist "storage" (
    if not exist "storage.fresh.bak" (
        xcopy /E /I "storage" "storage.fresh.bak" >nul
        echo [!] storage\ lama disimpan ke storage.fresh.bak
    )
)
if not exist ".env" copy /y ".env.example" ".env" >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1" -Mode core
if errorlevel 1 goto fail
echo.
echo Selesai fresh install. Ketik: kp start
exit /b 0

:feature
if "%~2"=="" goto usage
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1" -Mode feature -Feature "%~2"
if errorlevel 1 goto fail
echo.
echo Selesai pasang fitur "%~2". Ketik: kp start
exit /b 0

:run
if not exist ".venv\Scripts\activate.bat" goto notinstalled
call ".\.venv\Scripts\activate.bat"
echo =========================================
echo      MENYALAKAN KABAYAN PINTAR
echo =========================================
echo.
echo Backend : http://127.0.0.1:8000
echo Tekan Ctrl+C untuk berhenti.
echo.

rem Cek apakah frontend dist tersedia (production)
if exist "frontend\dist" (
    echo Mode: production (frontend dist via FastAPI, port 8000)
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    exit /b %errorlevel%
)

rem Development: frontend via Vite dev server
if exist "frontend\node_modules" (
    echo Mode: development (frontend via Vite, port 5173)
    pushd frontend
    call npm run dev:all
    popd
    exit /b %errorlevel%
)

echo Mode: backend saja (frontend belum di-build)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
exit /b %errorlevel%

:usage
echo Penggunaan: kp [--install|--fresh|feature <rag|documents|media|all>|start]
exit /b 1

:notinstalled
echo [!] Belum diinstall. Jalankan: kp --install (atau kp --fresh untuk reset data)
exit /b 1

:fail
echo [!] Install gagal. Periksa pesan di atas.
exit /b 1
