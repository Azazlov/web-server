#!/bin/bash

echo "============================================"
echo "  FileShare Local - Stop Server"
echo "============================================"
echo ""
echo "Stopping Python processes running app.py..."
echo ""

pkill -f "python.*app.py"
if [ $? -eq 0 ]; then
    echo "Server stopped successfully!"
else
    echo "No running server found."
fi

echo ""
