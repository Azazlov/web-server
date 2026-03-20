#!/bin/bash

echo "============================================"
echo "  FileShare Local - Host File Setup"
echo "============================================"
echo ""
echo "This script will add fileserver.local to your hosts file."
echo "ROOT PRIVILEGES REQUIRED"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run with sudo"
  exit 1
fi

# Add to hosts file
if grep -q "fileserver.local" /etc/hosts; then
    echo "Entry already exists in hosts file"
else
    echo "127.0.0.1 fileserver.local" >> /etc/hosts
    echo "Entry added successfully"
fi

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Server will be available at: http://fileserver.local"
echo ""
