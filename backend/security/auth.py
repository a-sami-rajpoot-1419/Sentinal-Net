"""
Authentication Middleware for FastAPI
Handles JWT token validation and user context
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from backend.security.jwt import verify_token, get_token_from_header
from backend.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    
    if not token:
        logger.warning("No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    payload = verify_token(token, token_type="access")
    
    if not payload:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role", "user")
    full_name = payload.get("full_name")
    
    if not user_id or not email:
        logger.warning("Token missing required claims")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database to ensure they still exist
    try:
        supabase = get_supabase_client()
        user = supabase.get_user_by_id(user_id)
        
        if not user:
            logger.warning(f"User {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Enhance user data with info from token
        user["role"] = role
        logger.debug(f"User {user_id} authenticated successfully")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )


async def get_optional_user(request) -> Optional[Dict[str, Any]]:
    """
    Get optional authenticated user (doesn't fail if not authenticated)
    
    Args:
        request: FastAPI request object
        
    Returns:
        User data dictionary or None if not authenticated
    """
    auth_header = request.headers.get("Authorization")
    token = get_token_from_header(auth_header)
    
    if not token:
        return None
    
    payload = verify_token(token, token_type="access")
    
    if not payload:
        return None
    
    try:
        supabase = get_supabase_client()
        user_id = payload.get("sub")
        user = supabase.get_user_by_id(user_id)
        
        if user:
            user["role"] = payload.get("role", "user")
            return user
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting optional user: {str(e)}")
        return None


async def require_role(*roles: str):
    """
    Create a dependency that requires specific roles
    
    Args:
        roles: Allowed role names
        
    Returns:
        Dependency function
    """
    async def check_role(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        
        if user_role not in roles:
            logger.warning(f"User {current_user.get('id')} with role {user_role} lacks required role")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role {user_role} not allowed. Required: {', '.join(roles)}",
            )
        
        return current_user
    
    return check_role


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User data if admin, raises HTTPException otherwise
    """
    user_role = current_user.get("role", "user")
    
    if user_role != "admin":
        logger.warning(f"User {current_user.get('id')} attempted admin-only action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    return current_user


async def require_moderator(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require moderator or admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User data if moderator/admin, raises HTTPException otherwise
    """
    user_role = current_user.get("role", "user")
    
    if user_role not in ["admin", "moderator"]:
        logger.warning(f"User {current_user.get('id')} attempted moderator-only action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin role required",
        )
    
    return current_user
