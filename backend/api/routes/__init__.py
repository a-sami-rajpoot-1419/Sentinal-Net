"""
API Routes Module
Includes all route handlers for the Sentinel-Net API
"""

from fastapi import FastAPI


def include_routes(app: FastAPI):
    """
    Include all API routes in the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Import routes
    from . import auth, consensus, agents
    
    # Include routers
    app.include_router(auth.router)
    app.include_router(consensus.router)
    app.include_router(agents.router)
