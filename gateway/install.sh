#!/bin/bash
echo "Installing MSA Gateway dependencies..."

echo "Upgrading pip and build tools..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing core dependencies..."
pip install fastapi>=0.100.0,<0.105.0
pip install "uvicorn[standard]>=0.20.0,<0.25.0"
pip install httpx>=0.24.0,<0.26.0
pip install pydantic>=2.0.0,<3.0.0
pip install python-multipart>=0.0.5,<0.1.0

echo "Installation completed!"
echo "To run the gateway, use: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" 