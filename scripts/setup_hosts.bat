@echo off
echo ============================================
echo   FileShare Local - Host File Setup
echo ============================================
echo.
echo This script will add fileserver.local to your hosts file.
echo ADMINISTRATOR PRIVILEGES REQUIRED
echo.
pause

echo 127.0.0.1 fileserver.local >> C:\Windows\System32\drivers\etc\hosts

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Domain fileserver.local has been added.
echo Server will be available at: http://fileserver.local
echo.
pause
