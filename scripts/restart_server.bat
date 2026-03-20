@echo off
echo ============================================
echo   FileShare Local - Restart Server
echo ============================================
echo.

echo Stopping server...
taskkill /F /FI "WINDOWTITLE eq FileShare*" /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting server...
cd /d "%~dp0.."

REM Check if virtual environment exists
if exist "venv" (
    start "FileShare Server" venv\Scripts\python.exe app.py
) else (
    start "FileShare Server" python app.py
)

echo.
echo ============================================
echo   Server restarted!
echo   Access at: http://fileserver.local
echo ============================================
echo.
pause
