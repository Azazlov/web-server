@echo off
echo ============================================
echo   FileShare Local - Stop Server
echo ============================================
echo.
echo Stopping all Python processes running app.py...
echo.

taskkill /F /FI "WINDOWTITLE eq FileShare*" /IM python.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Server stopped successfully!
) else (
    echo No running server found.
)

echo.
pause
