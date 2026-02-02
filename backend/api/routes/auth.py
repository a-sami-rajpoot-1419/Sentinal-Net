"""
Authentication Routes
Handles user registration, login, logout, and profile management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from backend.db.models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    UserUpdate, PasswordReset, AuthResponse
)
from backend.security.jwt import create_tokens, verify_token
from backend.security.auth import get_current_user, require_admin
from backend.db.supabase_client import get_supabase_client
from backend.shared.exceptions_v2 import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> TokenResponse:
    """
    Register a new user account
    
    Args:
        user_data: User registration data (email, password, full_name)
        
    Returns:
        TokenResponse with access token, refresh token, and user info
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        supabase = get_supabase_client()
        
        # Check if user already exists (handle gracefully if users table doesn't exist)
        try:
            if supabase.user_exists(user_data.email):
                logger.warning(f"Registration attempt with existing email: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
        except Exception as check_error:
            # If users table doesn't exist yet, log and continue
            if "users" in str(check_error).lower():
                logger.warning(f"Users table not yet created - proceeding with auth: {str(check_error)}")
            else:
                raise
        
        # Create auth user via Supabase Auth
        try:
            auth_response = supabase.auth_client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
            })
            
            user_id = auth_response.user.id
            logger.info(f"Auth user created: {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating auth user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        # Try to create user profile in database (handle gracefully if table doesn't exist)
        try:
            user_profile = supabase.create_user(
                user_id=user_id,
                email=user_data.email,
                full_name=user_data.full_name,
                role="user"
            )
            
            if not user_profile:
                logger.warning(f"Failed to create user profile for {user_data.email} but auth user exists")
        except Exception as profile_error:
            # If users table doesn't exist, log warning but continue
            if "users" in str(profile_error).lower() or "does not exist" in str(profile_error).lower():
                logger.warning(f"Users table not yet created - skipping profile creation: {str(profile_error)}")
                logger.info(f"⚠️  Auth user created but profile not saved. Create users table to enable full registration.")
            else:
                raise
        
        # Generate tokens
        tokens = create_tokens(
            user_id=user_id,
            email=user_data.email,
            role="user",
            full_name=user_data.full_name
        )
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse(
                id=user_id,
                email=user_data.email,
                full_name=user_data.full_name,
                role="user",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin) -> TokenResponse:
    """
    Authenticate user and return tokens
    
    Args:
        credentials: Login credentials (email, password)
        
    Returns:
        TokenResponse with access token, refresh token, and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        supabase = get_supabase_client()
        
        # Authenticate user via Supabase Auth
        try:
            auth_response = supabase.auth_client.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password,
            })
            
            user_id = auth_response.user.id
            logger.info(f"User logged in: {user_id}")
            
        except Exception as e:
            logger.warning(f"Failed login attempt for {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user profile
        user_profile = supabase.get_user_by_id(user_id)
        
        if not user_profile:
            logger.error(f"User profile not found for authenticated user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile not found"
            )
        
        # Generate tokens
        tokens = create_tokens(
            user_id=user_id,
            email=credentials.email,
            role=user_profile.get("role", "user"),
            full_name=user_profile.get("full_name")
        )
        
        logger.info(f"Authentication successful for {credentials.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse(
                id=user_id,
                email=credentials.email,
                full_name=user_profile.get("full_name"),
                avatar_url=user_profile.get("avatar_url"),
                role=user_profile.get("role", "user"),
                created_at=user_profile.get("created_at", datetime.utcnow()),
                updated_at=user_profile.get("updated_at", datetime.utcnow())
            )
        )
        
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> AuthResponse:
    """
    Logout user by invalidating tokens
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        AuthResponse confirming logout
    """
    try:
        user_id = current_user.get("id")
        
        # Sign out via Supabase Auth
        try:
            supabase = get_supabase_client()
            supabase.client.auth.sign_out()
            logger.info(f"User logged out: {user_id}")
            
        except Exception as e:
            logger.warning(f"Error signing out user {user_id}: {str(e)}")
            # Continue anyway, logout still successful
        
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout error occurred"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user's profile
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse with user profile information
    """
    return UserResponse(
        id=current_user.get("id"),
        email=current_user.get("email"),
        full_name=current_user.get("full_name"),
        avatar_url=current_user.get("avatar_url"),
        role=current_user.get("role", "user"),
        created_at=current_user.get("created_at", datetime.utcnow()),
        updated_at=current_user.get("updated_at", datetime.utcnow())
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(current_user: Dict[str, Any] = Depends(get_current_user)) -> TokenResponse:
    """
    Refresh access token using current valid token
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        TokenResponse with new access token
    """
    try:
        # Create new access token
        tokens = create_tokens(
            user_id=current_user.get("id"),
            email=current_user.get("email"),
            role=current_user.get("role", "user"),
            full_name=current_user.get("full_name")
        )
        
        logger.info(f"Access token refreshed for {current_user.get('id')}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse(
                id=current_user.get("id"),
                email=current_user.get("email"),
                full_name=current_user.get("full_name"),
                avatar_url=current_user.get("avatar_url"),
                role=current_user.get("role", "user"),
                created_at=current_user.get("created_at", datetime.utcnow()),
                updated_at=current_user.get("updated_at", datetime.utcnow())
            )
        )
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user's profile
    
    Args:
        user_update: Updated user data
        current_user: Current authenticated user
        
    Returns:
        Updated UserResponse
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user.get("id")
        
        # Update user profile
        updated_user = supabase.update_user(
            user_id=user_id,
            full_name=user_update.full_name,
            avatar_url=user_update.avatar_url
        )
        
        if not updated_user:
            logger.error(f"Failed to update profile for {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        logger.info(f"Profile updated for {user_id}")
        
        return UserResponse(
            id=updated_user.get("id"),
            email=updated_user.get("email"),
            full_name=updated_user.get("full_name"),
            avatar_url=updated_user.get("avatar_url"),
            role=updated_user.get("role", "user"),
            created_at=updated_user.get("created_at", datetime.utcnow()),
            updated_at=updated_user.get("updated_at", datetime.utcnow())
        )
        
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.post("/password-reset", response_model=AuthResponse)
async def request_password_reset(password_reset: PasswordReset) -> AuthResponse:
    """
    Request password reset for email
    
    Args:
        password_reset: Email address for password reset
        
    Returns:
        AuthResponse confirming reset email sent
    """
    try:
        supabase = get_supabase_client()
        
        # Check if user exists
        if not supabase.user_exists(password_reset.email):
            # Don't reveal if email exists (security best practice)
            logger.warning(f"Password reset requested for non-existent email: {password_reset.email}")
        
        # Request password reset via Supabase Auth
        try:
            supabase.client.auth.reset_password_for_email(
                email=password_reset.email,
                redirect_to="http://localhost:3000/reset-password"
            )
            logger.info(f"Password reset email sent to {password_reset.email}")
            
        except Exception as e:
            logger.warning(f"Error sending password reset email: {str(e)}")
        
        # Always return success message (security best practice)
        return AuthResponse(
            success=True,
            message="If the email exists, a password reset link has been sent"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password reset request"
        )
