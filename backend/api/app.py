"""
FastAPI Application Configuration and Initialization
Phase 6: Authentication & Security
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=os.getenv("API_TITLE", "Sentinel-Net Consensus Engine"),
        version=os.getenv("API_VERSION", "0.6.0"),
        description="Phase 6: Authentication, Security & Testing for ML Agent Collaboration",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add security middlewares
    
    # Trusted Host Middleware
    trusted_hosts = os.getenv("API_TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
    trusted_hosts = [host.strip() for host in trusted_hosts]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts,
    )
    
    # GZIP Compression Middleware
    app.add_middleware(GZIPMiddleware, minimum_size=1000)
    
    # CORS Middleware (with secure defaults)
    origins = os.getenv("API_CORS_ORIGINS", "http://localhost:3000").strip("[]").split(",")
    origins = [origin.strip().strip("\"'") for origin in origins]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,  # Cache CORS preflight for 10 minutes
    )
    
    logger.info(f"CORS configured for origins: {origins}")
    logger.info(f"Trusted hosts: {trusted_hosts}")
    
    return app


# Create application instance
app = create_app()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sentinel-Net Consensus Engine",
        "version": os.getenv("API_VERSION", "0.6.0"),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentinel-Net Consensus Engine API",
        "version": os.getenv("API_VERSION", "0.6.0"),
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
