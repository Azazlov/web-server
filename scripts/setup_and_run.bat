@echo off
echo ============================================
echo   FileShare Local v2.1 - Setup and Run
echo ============================================
echo.
echo This script will:
echo   1. Add fileserver.local to hosts file
echo   2. Create virtual environment (if needed)
echo   3. Install dependencies
echo   4. Start the server on port 80
echo.
echo ADMINISTRATOR PRIVILEGES REQUIRED
echo.
pause

REM Step 1: Add to hosts file
echo [1/4] Adding fileserver.local to hosts file...
echo 127.0.0.1 fileserver.local >> C:\Windows\System32\drivers\etc\hosts
echo Done!
echo.

REM Step 2: Check if virtual environment exists
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/4] Virtual environment already exists...
)
echo Done!
echo.

REM Step 3: Install dependencies
echo [3/4] Installing dependencies...
venv\Scripts\pip.exe install -r requirements.txt
echo Done!
echo.

REM Step 4: Start server
echo [4/4] Starting FileShare Local server...
echo.
echo ============================================
echo   Server starting...
echo   Access at: http://fileserver.local
echo   Or at: http://localhost
echo ============================================
echo.
venv\Scripts\python.exe app.py

pause
