"""
Vercel API entry point for the Insurance AI Assistant
"""

import os
import sys
from pathlib import Path

# Add the python-backend directory to Python path
backend_dir = Path(__file__).parent.parent / "python-backend"
sys.path.insert(0, str(backend_dir))

# Set environment variables for Vercel
os.environ.setdefault("VERCEL_ENV", "1")
os.environ.setdefault("DATABASE_URL", "sqlite:///./insurance_ai.db")

# Import the main FastAPI app
from main import app

# Vercel expects the app to be available as 'app'
# This is the entry point for Vercel serverless functions
handler = app
