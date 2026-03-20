#!/bin/bash

echo "============================================"
echo "  FileShare Local - Restart Server"
echo "============================================"
echo ""

# Find and kill the Python process running app.py
echo "Stopping server..."
pkill -f "python.*app.py" || true
sleep 2

echo "Starting server..."
cd "$( dirname "${BASH_SOURCE[0]}" )/.."

# Check if virtual environment exists
if [ -d "venv" ]; then
    venv/bin/python app.py &
else
    python3 app.py &
fi

echo "Server restarted!"
echo "Access at: http://fileserver.local"
echo ""
