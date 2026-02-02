"""
FastAPI Application Configuration and Initialization
Phase 7: Model Loading and Consensus Engine Initialization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from typing import AsyncGenerator
from pathlib import Path

from backend.security.rate_limiter import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    RequestTimeoutMiddleware,
    rate_limiter,
)
from backend.models.loader import ModelLoader
from backend.consensus.engine import ConsensusEngine
from backend.database import init_db, get_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Global instances - will be populated on startup
consensus_engine: ConsensusEngine = None
agents_dict: dict = None
preprocessor = None  # Fitted data preprocessor


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage app lifecycle: startup and shutdown.
    
    Startup:
    - Load/initialize ML agents
    - Initialize consensus engine
    
    Shutdown:
    - Clean up resources
    """
    # ==================== STARTUP ====================
    logger.info("🚀 Starting Sentinel-Net Consensus Engine...")
    
    try:
        # Initialize database
        logger.info("🗄️  Initializing Supabase database...")
        db = init_db()
        logger.info("✓ Database initialized")
        
        # Load or initialize agents
        logger.info("📦 Loading ML agents...")
        allow_uninitialized = os.getenv("ALLOW_UNINITIALIZED_MODELS", "true").lower() == "true"
        agents = ModelLoader.load_models(allow_uninitialized=allow_uninitialized)
        logger.info(f"✓ Loaded {len(agents)} agents")
        
        # Create agents in database
        for agent_id, agent in agents.items():
            db.create_agent(agent_id, agent.model_type if hasattr(agent, 'model_type') else 'unknown')
        
        # Count trained vs untrained
        trained_count = sum(1 for a in agents.values() if a.is_trained)
        logger.info(f"  - Trained: {trained_count}/{len(agents)}")
        logger.info(f"  - Untrained: {len(agents) - trained_count}/{len(agents)}")
        
        # Initialize consensus engine
        logger.info("🧠 Initializing consensus engine...")
        global consensus_engine, agents_dict, preprocessor
        consensus_engine = ConsensusEngine(agents=agents)
        agents_dict = agents
        logger.info(f"✓ Consensus engine initialized")
        logger.info(f"  - Agents: {list(agents.keys())}")
        logger.info(f"  - Weights: {consensus_engine.get_weights()}")
        
        # Initialize preprocessor with feature names from cached training data
        logger.info("📝 Initializing text preprocessor...")
        from backend.data.preprocessor import DataPreprocessor
        import pandas as pd
        import numpy as np
        
        try:
            # Create preprocessor instance
            preprocessor = DataPreprocessor()
            
            # Load raw texts for fitting the TF-IDF vectorizer
            raw_data_path = Path("data/raw/spam.csv")
            if raw_data_path.exists():
                # Load raw texts from CSV with proper encoding and parsing
                df = pd.read_csv(raw_data_path, encoding='latin-1', on_bad_lines='skip')
                # First column is label, second is text
                raw_texts = df.iloc[:, 1].values  # SMS column
                # Remove NaN/None values and convert to string
                raw_texts = [str(t).strip() for t in raw_texts if pd.notna(t) and str(t).strip() and str(t).strip().lower() != 'nan']
                
                # Fit the preprocessor on raw texts - this initializes the TF-IDF vectorizer properly
                logger.info(f"Fitting preprocessor on {len(raw_texts)} raw texts...")
                preprocessor.fit_transform(raw_texts)
                logger.info(f"✓ Preprocessor fitted with vocabulary ({len(preprocessor.feature_names)} features)")
            else:
                logger.warning(f"⚠ Raw data file not found: {raw_data_path}")
                
        except Exception as e:
            logger.error(f"⚠ Failed to initialize preprocessor: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("⚠ Preprocessor will be unfit - text classification may fail")
            preprocessor = DataPreprocessor()
        
        logger.info("✓ Sentinel-Net ready!")
        logger.info("=" * 50)
        logger.info("🎯 Application is fully initialized and ready to serve requests")
        logger.info("=" * 50)
        
        yield  # Server is now running
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {str(e)}", exc_info=True)
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise
    
    # ==================== SHUTDOWN ====================
    logger.info("🛑 Shutting down Sentinel-Net...")
    logger.info("✓ Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application with comprehensive security"""
    
    app = FastAPI(
        title=os.getenv("API_TITLE", "Sentinel-Net Consensus Engine"),
        version=os.getenv("API_VERSION", "0.7.0"),
        description="Phase 7: Model Loading, Consensus Engine & API Security",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,  # Enable startup/shutdown lifecycle management
    )
    
    # ==================== SECURITY MIDDLEWARES ====================
    # Order matters! Apply from bottom to top (reverse order of add_middleware)
    
    # 1. Request Timeout (outermost - catches hung requests)
    timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    app.add_middleware(RequestTimeoutMiddleware, timeout_seconds=timeout_seconds)
    
    # 2. Request Validation (check headers, payload size, injection attempts)
    app.add_middleware(RequestValidationMiddleware)
    
    # 3. Rate Limiting (prevent DDoS, enforce per-IP/per-user limits)
    app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
    
    # 4. GZIP Compression (before CORS to compress efficiently)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 5. CORS Middleware (validate origins)
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
    
    # 6. Trusted Host Middleware (innermost - only after validation)
    trusted_hosts = os.getenv("API_TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
    trusted_hosts = [host.strip() for host in trusted_hosts]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts,
    )
    
    logger.info(f"✓ CORS configured for origins: {origins}")
    logger.info(f"✓ Trusted hosts: {trusted_hosts}")
    logger.info(f"✓ Rate limiting enabled:")
    logger.info(f"  - Global limit: {rate_limiter.global_limit} requests/min")
    logger.info(f"  - Per-IP limit: {rate_limiter.ip_limit} requests/min")
    logger.info(f"  - Per-user limit: {rate_limiter.user_limit} requests/hour")
    logger.info(f"✓ Auto-block threshold: {rate_limiter.auto_block_threshold} requests")
    logger.info(f"✓ Request timeout: {timeout_seconds}s")
    
    return app


# Create application instance
app = create_app()


# ==================== HELPER FUNCTIONS FOR ACCESSING GLOBAL STATE ====================

def get_consensus_engine() -> ConsensusEngine:
    """
    Get the consensus engine instance.
    
    Call this in route handlers to access the consensus engine.
    The engine is initialized on app startup.
    
    Returns:
        ConsensusEngine: The initialized consensus engine
        
    Raises:
        RuntimeError: If engine not initialized (app not started)
    """
    if consensus_engine is None:
        raise RuntimeError(
            "Consensus engine not initialized. "
            "Make sure the app has started and models loaded successfully."
        )
    return consensus_engine


def get_agents() -> dict:
    """
    Get the agents dictionary.
    
    Call this in route handlers to access individual agents.
    
    Returns:
        dict: Dictionary of {agent_name: AgentBase instance}
        
    Raises:
        RuntimeError: If agents not initialized
    """
    if agents_dict is None:
        raise RuntimeError(
            "Agents not initialized. "
            "Make sure the app has started and models loaded successfully."
        )
    return agents_dict


def get_preprocessor():
    """
    Get the fitted data preprocessor instance.
    
    Call this in route handlers to access the preprocessor.
    The preprocessor is initialized on app startup with vocabulary
    from the trained agents.
    
    Returns:
        DataPreprocessor: The initialized and fitted preprocessor
        
    Raises:
        RuntimeError: If preprocessor not initialized
    """
    if preprocessor is None:
        raise RuntimeError(
            "Preprocessor not initialized. "
            "Make sure the app has started successfully."
        )
    return preprocessor


@app.get("/health")
async def health_check():
    """
    Health check endpoint with model and consensus engine status.
    
    Returns:
        dict with status, service info, and component health
    """
    health_status = {
        "status": "healthy",
        "service": "Sentinel-Net Consensus Engine",
        "version": os.getenv("API_VERSION", "0.7.0"),
    }
    
    # Check consensus engine
    try:
        engine = get_consensus_engine()
        agents = get_agents()
        
        # Count trained agents
        trained_count = sum(1 for a in agents.values() if a.is_trained)
        
        health_status["consensus_engine"] = {
            "status": "ready",
            "agents": {
                "total": len(agents),
                "trained": trained_count,
                "untrained": len(agents) - trained_count,
                "names": list(agents.keys()),
            },
            "weights": engine.agent_weights,
        }
    except RuntimeError as e:
        health_status["consensus_engine"] = {
            "status": "not_initialized",
            "error": str(e),
        }
    
    return health_status


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentinel-Net Consensus Engine API",
        "version": os.getenv("API_VERSION", "0.6.0"),
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


# ==================== ADMIN ENDPOINTS ====================
# Only accessible in development or with admin credentials

@app.post("/admin/unblock-ip/{ip_address}")
async def unblock_ip(ip_address: str):
    """Unblock a previously blocked IP address (admin only)"""
    await rate_limiter.unblock_ip(ip_address)
    return {
        "status": "success",
        "message": f"IP {ip_address} has been unblocked",
        "blocked_ips": list(rate_limiter.blocked_ips)
    }


@app.post("/admin/unblock-user/{user_id}")
async def unblock_user(user_id: str):
    """Unblock a previously blocked user (admin only)"""
    await rate_limiter.unblock_user(user_id)
    return {
        "status": "success",
        "message": f"User {user_id} has been unblocked",
        "blocked_users": list(rate_limiter.blocked_users)
    }


@app.get("/admin/security-stats")
async def get_security_stats():
    """Get security statistics (admin only)"""
    return {
        "blocked_ips": list(rate_limiter.blocked_ips),
        "blocked_users": list(rate_limiter.blocked_users),
        "total_tracked_identifiers": len(rate_limiter.tracker.requests),
        "rate_limit_config": {
            "global_limit": rate_limiter.global_limit,
            "global_window": rate_limiter.global_window,
            "ip_limit": rate_limiter.ip_limit,
            "ip_window": rate_limiter.ip_window,
            "user_limit": rate_limiter.user_limit,
            "user_window": rate_limiter.user_window,
            "auto_block_threshold": rate_limiter.auto_block_threshold,
        }
    }


# ==================== INCLUDE ROUTES ====================
# Import and include routes AFTER all functions are defined to avoid circular imports
# Routes: auth, consensus, agents, classify
# Force reload after fixing consensus.py line 238
from backend.api.routes import include_routes
include_routes(app)