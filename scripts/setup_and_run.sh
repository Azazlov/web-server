#!/bin/bash

echo "============================================"
echo "  FileShare Local v2.1 - Setup and Run"
echo "============================================"
echo ""
echo "This script will:"
echo "  1. Add fileserver.local to hosts file"
echo "  2. Create virtual environment (if needed)"
echo "  3. Install dependencies"
echo "  4. Start the server on port 80"
echo ""
echo "ROOT PRIVILEGES REQUIRED"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run with sudo"
  exit 1
fi

# Step 1: Add to hosts file
echo "[1/4] Adding fileserver.local to hosts file..."
if grep -q "fileserver.local" /etc/hosts; then
    echo "Entry already exists"
else
    echo "127.0.0.1 fileserver.local" >> /etc/hosts
fi
echo "Done!"
echo ""

# Step 2: Check if virtual environment exists
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[2/4] Virtual environment already exists..."
fi
echo "Done!"
echo ""

# Step 3: Install dependencies
echo "[3/4] Installing dependencies..."
venv/bin/pip install -r requirements.txt
echo "Done!"
echo ""

# Step 4: Start server
echo "[4/4] Starting FileShare Local server..."
echo ""
echo "============================================"
echo "  Server starting..."
echo "  Access at: http://fileserver.local"
echo "  Or at: http://localhost"
echo "============================================"
echo ""
venv/bin/python app.py
