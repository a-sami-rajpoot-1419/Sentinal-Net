"""
JWT Token Management and Security Utilities
Handles JWT creation, verification, and token refresh logic
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


class TokenData:
    """JWT Token payload data"""
    
    def __init__(
        self,
        user_id: str,
        email: str,
        role: str = "user",
        full_name: Optional[str] = None
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.full_name = full_name
        self.iat = datetime.utcnow()
        self.exp = None
        self.token_type = None


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing token claims
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Created access token for user {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Dictionary containing token claims
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Created refresh token for user {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {str(e)}")
        raise


def create_tokens(
    user_id: str,
    email: str,
    role: str = "user",
    full_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create both access and refresh tokens
    
    Args:
        user_id: User UUID
        email: User email
        role: User role
        full_name: User's full name
        
    Returns:
        Dictionary with access_token, refresh_token, and expiration info
    """
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role,
        "full_name": full_name
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload or None if invalid
        
    Raises:
        JWTError: If token verification fails
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            return None
        
        logger.debug(f"Token verified for user {user_id}")
        return payload
        
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Create a new access token using a valid refresh token
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New access token or None if refresh token is invalid
    """
    payload = verify_token(refresh_token, token_type="refresh")
    
    if not payload:
        logger.warning("Failed to refresh access token: invalid refresh token")
        return None
    
    # Create new access token with same claims
    access_token_data = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "full_name": payload.get("full_name")
    }
    
    new_access_token = create_access_token(access_token_data)
    logger.info(f"Refreshed access token for user {payload.get('sub')}")
    return new_access_token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a token without verification (useful for debugging)
    Use with caution - only for trusted contexts
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None


def get_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header
    
    Args:
        auth_header: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        Token string or None if invalid format
    """
    if not auth_header:
        return None
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid authorization header format")
        return None
    
    return parts[1]


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired without verification
    
    Args:
        token: JWT token string
        
    Returns:
        True if expired, False if valid or can't determine
    """
    payload = decode_token(token)
    
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return False
    
    return datetime.utcfromtimestamp(exp) < datetime.utcnow()
