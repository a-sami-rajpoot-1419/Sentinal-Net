"""
Phase 7 API Server Startup Script
Run this to start the FastAPI server with model loading and consensus engine
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from backend.api.app import app
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the FastAPI server
    
    The app startup and shutdown are now handled by the lifespan
    context manager in backend/api/app.py. This ensures:
    
    - Models are loaded on startup
    - Consensus engine is initialized
    - Resources are cleaned up on shutdown
    """
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    logger.info(f"Starting Sentinel-Net API on {host}:{port}")
    logger.info(f"Environment: {os.getenv('API_ENV', 'development')}")
    logger.info(f"Allow uninitialized models: {os.getenv('ALLOW_UNINITIALIZED_MODELS', 'true')}")
    
    uvicorn.run(
        "backend.api.main:app",
        host=host,
        port=port,
        reload=os.getenv("API_ENV", "development") == "development",
        workers=int(os.getenv("WORKERS", 1)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()
