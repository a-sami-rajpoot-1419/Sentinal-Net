"""
FastAPI Application Configuration and Initialization
Phase 6c: Authentication & Security with Rate Limiting & DDoS Protection
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from dotenv import load_dotenv
import os
import logging
from backend.security.rate_limiter import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    RequestTimeoutMiddleware,
    rate_limiter,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application with comprehensive security"""
    
    app = FastAPI(
        title=os.getenv("API_TITLE", "Sentinel-Net Consensus Engine"),
        version=os.getenv("API_VERSION", "0.6.0"),
        description="Phase 6c: Authentication, Security, Rate Limiting & DDoS Protection",
        docs_url="/docs",
        redoc_url="/redoc",
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
    app.add_middleware(GZIPMiddleware, minimum_size=1000)
    
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

