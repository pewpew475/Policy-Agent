"""
Vercel API entry point for the Insurance AI Assistant
"""

import os
import sys
from pathlib import Path

try:
    # Add the python-backend directory to Python path
    backend_dir = Path(__file__).parent.parent / "python-backend"
    sys.path.insert(0, str(backend_dir))

    # Set environment variables for Vercel
    os.environ.setdefault("VERCEL_ENV", "1")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./insurance_ai.db")

    # Ensure required directories exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed_documents", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Import the main FastAPI app
    from main import app

    # Vercel expects the app to be available as 'app'
    # This is the entry point for Vercel serverless functions
    handler = app

except Exception as e:
    print(f"Error initializing API: {e}")

    # Fallback handler for debugging
    def handler(request=None):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': {'error': f'API initialization failed: {str(e)}'}
        }
