#!/usr/bin/env python3
import os
import sys
import subprocess

# Set environment variables for Metal acceleration
os.environ['CT_METAL'] = '1'
os.environ['GPU_LAYERS'] = '4'

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Import and run the FastAPI app
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting backend with Metal acceleration...")
    print(f"CT_METAL: {os.environ.get('CT_METAL')}")
    print(f"GPU_LAYERS: {os.environ.get('GPU_LAYERS')}")
    uvicorn.run(app, host="0.0.0.0", port=8010, reload=True) 