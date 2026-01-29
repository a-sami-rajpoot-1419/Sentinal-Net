"""
FastAPI Application Configuration and Initialization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=os.getenv("API_TITLE", "Sentinel-Net Consensus Engine"),
        version=os.getenv("API_VERSION", "0.4.0"),
        description="Phase 4: RWPV Consensus Engine for ML Agent Collaboration",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    origins = os.getenv("API_CORS_ORIGINS", "http://localhost:3000").strip("[]").split(",")
    origins = [origin.strip().strip("\"'") for origin in origins]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

# Create application instance
app = create_app()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sentinel-Net Consensus Engine",
        "version": os.getenv("API_VERSION", "0.4.0"),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentinel-Net Consensus Engine",
        "version": os.getenv("API_VERSION", "0.4.0"),
        "docs_url": "/docs",
    }
