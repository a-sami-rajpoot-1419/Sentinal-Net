"""
Role-Based Access Control (RBAC) Utilities
Implements authorization checks and permission management
"""

from typing import List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Available system permissions"""
    # User permissions
    READ_OWN_PROFILE = "read:own_profile"
    UPDATE_OWN_PROFILE = "update:own_profile"
    DELETE_OWN_ACCOUNT = "delete:own_account"
    
    # Agent permissions
    READ_AGENTS = "read:agents"
    CREATE_AGENT = "create:agent"
    UPDATE_AGENT = "update:agent"
    DELETE_AGENT = "delete:agent"
    
    # Consensus permissions
    READ_CONSENSUS = "read:consensus"
    PARTICIPATE_CONSENSUS = "participate:consensus"
    VIEW_WEIGHTS = "view:weights"
    
    # Admin permissions
    READ_ALL_PROFILES = "read:all_profiles"
    UPDATE_ANY_USER = "update:any_user"
    DELETE_ANY_USER = "delete:any_user"
    MANAGE_ROLES = "manage:roles"
    VIEW_ANALYTICS = "view:analytics"
    MANAGE_SYSTEM = "manage:system"


class Role(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


# Role to Permissions mapping
ROLE_PERMISSIONS: dict = {
    Role.USER: [
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.DELETE_OWN_ACCOUNT,
        Permission.READ_AGENTS,
        Permission.READ_CONSENSUS,
        Permission.PARTICIPATE_CONSENSUS,
        Permission.VIEW_WEIGHTS,
    ],
    Role.MODERATOR: [
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.DELETE_OWN_ACCOUNT,
        Permission.READ_AGENTS,
        Permission.CREATE_AGENT,
        Permission.UPDATE_AGENT,
        Permission.READ_ALL_PROFILES,
        Permission.READ_CONSENSUS,
        Permission.PARTICIPATE_CONSENSUS,
        Permission.VIEW_WEIGHTS,
        Permission.VIEW_ANALYTICS,
    ],
    Role.ADMIN: [
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.DELETE_OWN_ACCOUNT,
        Permission.READ_AGENTS,
        Permission.CREATE_AGENT,
        Permission.UPDATE_AGENT,
        Permission.DELETE_AGENT,
        Permission.READ_ALL_PROFILES,
        Permission.UPDATE_ANY_USER,
        Permission.DELETE_ANY_USER,
        Permission.MANAGE_ROLES,
        Permission.READ_CONSENSUS,
        Permission.PARTICIPATE_CONSENSUS,
        Permission.VIEW_WEIGHTS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_SYSTEM,
    ],
}


def get_role_permissions(role: str) -> List[Permission]:
    """
    Get list of permissions for a given role
    
    Args:
        role: Role name (user, admin, moderator)
        
    Returns:
        List of Permission enums for the role
    """
    try:
        role_enum = Role(role.lower())
        return ROLE_PERMISSIONS.get(role_enum, [])
    except ValueError:
        logger.warning(f"Unknown role: {role}")
        return []


def has_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a user role has a specific permission
    
    Args:
        user_role: User's role
        required_permission: Required permission string
        
    Returns:
        True if user has permission, False otherwise
    """
    try:
        permission = Permission(required_permission)
        permissions = get_role_permissions(user_role)
        has_perm = permission in permissions
        
        if not has_perm:
            logger.warning(f"User with role {user_role} denied permission {required_permission}")
        
        return has_perm
    except ValueError:
        logger.error(f"Invalid permission: {required_permission}")
        return False


def can_access_user_data(user_id: str, target_user_id: str, user_role: str) -> bool:
    """
    Check if user can access another user's data
    
    Args:
        user_id: Requesting user's ID
        target_user_id: Target user's ID
        user_role: Requesting user's role
        
    Returns:
        True if access is allowed, False otherwise
    """
    # Users can always access their own data
    if user_id == target_user_id:
        return has_permission(user_role, Permission.READ_OWN_PROFILE.value)
    
    # Admins and moderators can access all data
    if has_permission(user_role, Permission.READ_ALL_PROFILES.value):
        return True
    
    logger.warning(f"User {user_id} denied access to user {target_user_id} data")
    return False


def can_update_user_data(user_id: str, target_user_id: str, user_role: str) -> bool:
    """
    Check if user can update another user's data
    
    Args:
        user_id: Requesting user's ID
        target_user_id: Target user's ID
        user_role: Requesting user's role
        
    Returns:
        True if update is allowed, False otherwise
    """
    # Users can only update their own data
    if user_id == target_user_id:
        return has_permission(user_role, Permission.UPDATE_OWN_PROFILE.value)
    
    # Only admins can update other users
    if has_permission(user_role, Permission.UPDATE_ANY_USER.value):
        return True
    
    logger.warning(f"User {user_id} denied permission to update user {target_user_id}")
    return False


def can_delete_user(user_id: str, target_user_id: str, user_role: str) -> bool:
    """
    Check if user can delete another user's account
    
    Args:
        user_id: Requesting user's ID
        target_user_id: Target user's ID
        user_role: Requesting user's role
        
    Returns:
        True if deletion is allowed, False otherwise
    """
    # Users can only delete their own account
    if user_id == target_user_id:
        return has_permission(user_role, Permission.DELETE_OWN_ACCOUNT.value)
    
    # Only admins can delete other users
    if has_permission(user_role, Permission.DELETE_ANY_USER.value):
        return True
    
    logger.warning(f"User {user_id} denied permission to delete user {target_user_id}")
    return False


def is_admin(user_role: str) -> bool:
    """
    Check if user is an admin
    
    Args:
        user_role: User's role
        
    Returns:
        True if user is admin, False otherwise
    """
    return user_role.lower() == Role.ADMIN.value


def is_moderator(user_role: str) -> bool:
    """
    Check if user is a moderator or admin
    
    Args:
        user_role: User's role
        
    Returns:
        True if user is moderator or admin, False otherwise
    """
    role_lower = user_role.lower()
    return role_lower in [Role.MODERATOR.value, Role.ADMIN.value]
