"""
API Security Module - Phase 6c Security Hardening
Implements rate limiting, request counting, DDoS protection, and attack prevention
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import logging
import hashlib
import os
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class RequestTracker:
    """Track request counts and patterns for security monitoring"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)  # {identifier: [timestamps]}
        self.suspicious_ips: set = set()
        self.cleanup_lock = asyncio.Lock()
        
    async def add_request(self, identifier: str, timestamp: datetime = None):
        """Record a request from an identifier (IP, User ID, etc.)"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.requests[identifier].append(timestamp)
        
    async def get_request_count(
        self, 
        identifier: str, 
        time_window_seconds: int = 60
    ) -> int:
        """Get request count within a time window"""
        cutoff = datetime.utcnow() - timedelta(seconds=time_window_seconds)
        count = sum(
            1 for req_time in self.requests[identifier]
            if req_time > cutoff
        )
        return count
    
    async def cleanup_old_requests(self, max_age_hours: int = 1):
        """Remove requests older than max_age_hours"""
        async with self.cleanup_lock:
            cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
            for identifier in list(self.requests.keys()):
                self.requests[identifier] = [
                    req_time for req_time in self.requests[identifier]
                    if req_time > cutoff
                ]
                if not self.requests[identifier]:
                    del self.requests[identifier]


class RateLimiter:
    """
    Multi-level rate limiting:
    - Global rate limit
    - Per-IP rate limit
    - Per-User rate limit
    - Endpoint-specific rate limits
    """
    
    def __init__(self):
        self.tracker = RequestTracker()
        self.blocked_ips: set = set()
        self.blocked_users: set = set()
        
        # Rate limit configurations (requests per time window)
        self.global_limit = int(os.getenv("RATE_LIMIT_GLOBAL", "10000"))  # per minute
        self.global_window = 60  # seconds
        
        self.ip_limit = int(os.getenv("RATE_LIMIT_IP", "100"))  # per minute per IP
        self.ip_window = 60  # seconds
        
        self.user_limit = int(os.getenv("RATE_LIMIT_USER", "1000"))  # per hour per user
        self.user_window = 3600  # seconds
        
        # Endpoint-specific limits
        self.endpoint_limits: Dict[str, Tuple[int, int]] = {
            "/auth/register": (5, 3600),      # 5 per hour
            "/auth/login": (20, 600),         # 20 per 10 minutes
            "/auth/refresh": (10, 60),        # 10 per minute
            "/consensus/predict": (100, 60),  # 100 per minute
        }
        
        # Block list management
        self.auto_block_threshold = int(os.getenv("AUTO_BLOCK_THRESHOLD", "50"))
        self.auto_block_window = 60  # seconds
        
    async def check_rate_limit(
        self, 
        ip: str, 
        user_id: Optional[str] = None,
        endpoint: str = None
    ) -> Tuple[bool, str]:
        """
        Check if request should be allowed
        Returns: (allowed: bool, reason: str)
        """
        
        # Check if IP is permanently blocked
        if ip in self.blocked_ips:
            logger.warning(f"Request from blocked IP: {ip}")
            return False, "IP address is blocked"
        
        # Check if user is blocked
        if user_id and user_id in self.blocked_users:
            logger.warning(f"Request from blocked user: {user_id}")
            return False, "User account is blocked"
        
        # Record request
        await self.tracker.add_request(f"global")
        await self.tracker.add_request(f"ip:{ip}")
        if user_id:
            await self.tracker.add_request(f"user:{user_id}")
        
        # Check global rate limit
        global_count = await self.tracker.get_request_count(
            "global", 
            self.global_window
        )
        if global_count > self.global_limit:
            logger.error(f"Global rate limit exceeded: {global_count}/{self.global_limit}")
            return False, "Service rate limit exceeded"
        
        # Check IP-based rate limit
        ip_count = await self.tracker.get_request_count(
            f"ip:{ip}",
            self.ip_window
        )
        if ip_count > self.ip_limit:
            logger.warning(f"IP rate limit exceeded for {ip}: {ip_count}/{self.ip_limit}")
            
            # Auto-block aggressive IPs
            if ip_count > self.auto_block_threshold:
                self.blocked_ips.add(ip)
                logger.error(f"Auto-blocked IP for aggressive behavior: {ip}")
                return False, "Too many requests - IP blocked"
            
            return False, "Rate limit exceeded"
        
        # Check user-based rate limit
        if user_id:
            user_count = await self.tracker.get_request_count(
                f"user:{user_id}",
                self.user_window
            )
            if user_count > self.user_limit:
                logger.warning(f"User rate limit exceeded for {user_id}: {user_count}/{self.user_limit}")
                return False, "User rate limit exceeded"
        
        # Check endpoint-specific limits
        if endpoint and endpoint in self.endpoint_limits:
            limit, window = self.endpoint_limits[endpoint]
            endpoint_key = f"endpoint:{ip}:{endpoint}"
            endpoint_count = await self.tracker.get_request_count(endpoint_key, window)
            if endpoint_count > limit:
                logger.warning(f"Endpoint rate limit exceeded for {endpoint}: {endpoint_count}/{limit}")
                return False, f"Endpoint rate limit exceeded ({limit} per {window}s)"
        
        return True, "OK"
    
    async def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"Unblocked IP: {ip}")
    
    async def unblock_user(self, user_id: str):
        """Unblock a user"""
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            logger.info(f"Unblocked user: {user_id}")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        """Process incoming request with rate limiting"""
        
        # Get client IP (handle proxies)
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Try to extract user ID from token
        user_id = None
        if "authorization" in request.headers:
            try:
                token = request.headers["authorization"].split(" ")[1]
                # Hash token for privacy (don't store full token)
                user_id = hashlib.sha256(token.encode()).hexdigest()[:16]
            except IndexError:
                pass
        
        # Check rate limits
        allowed, reason = await self.rate_limiter.check_rate_limit(
            client_ip,
            user_id,
            request.url.path
        )
        
        if not allowed:
            logger.warning(f"Rate limit exceeded - IP: {client_ip}, Reason: {reason}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": reason,
                    "error": "rate_limit_exceeded"
                }
            )
        
        # Add request info to state
        request.state.client_ip = client_ip
        request.state.user_id = user_id
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        ip_count = await self.rate_limiter.tracker.get_request_count(
            f"ip:{client_ip}",
            self.rate_limiter.ip_window
        )
        
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.ip_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.rate_limiter.ip_limit - ip_count)
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((datetime.utcnow() + timedelta(seconds=self.rate_limiter.ip_window)).timestamp())
        )
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating requests and preventing common attacks"""
    
    async def dispatch(self, request: Request, call_next):
        """Validate request and prevent attacks"""
        
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-host",
            "x-original-url",
            "x-rewrite-url",
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Check for header injection attempts
                header_value = request.headers[header]
                if any(char in header_value for char in ["\r", "\n", "\x00"]):
                    logger.warning(f"Suspicious header detected: {header}")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Invalid header"}
                    )
        
        # Check request size (prevent large payload attacks)
        if "content-length" in request.headers:
            try:
                content_length = int(request.headers["content-length"])
                max_size = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB default
                if content_length > max_size:
                    logger.warning(f"Request too large: {content_length} bytes")
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "Request payload too large"}
                    )
            except ValueError:
                pass
        
        # Check for SQL injection attempts in query params
        for key, value in request.query_params.items():
            if isinstance(value, str):
                sql_keywords = ["union", "select", "insert", "delete", "drop", "exec"]
                if any(keyword in value.lower() for keyword in sql_keywords):
                    logger.warning(f"Potential SQL injection in query param: {key}")
                    # Note: SQLAlchemy ORM prevents this, but we log it
        
        # Add request timestamp
        request.state.request_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware for enforcing request timeouts"""
    
    def __init__(self, app, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
    
    async def dispatch(self, request: Request, call_next):
        """Process request with timeout"""
        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds
            )
            return response
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {self.timeout_seconds}s: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={"detail": "Request timeout"}
            )


# Global rate limiter instance
rate_limiter = RateLimiter()
