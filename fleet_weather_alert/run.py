#!/usr/bin/env python3
"""Startup script for the Fleet Weather Alert System."""

import uvicorn
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.config import settings

if __name__ == "__main__":
    print("🚛 Starting Fleet Weather Alert System...")
    print(f"   Host: {settings.host}")
    print(f"   Port: {settings.port}")
    print(f"   Debug: {settings.debug}")
    print(f"   Database: {settings.database_url}")
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )