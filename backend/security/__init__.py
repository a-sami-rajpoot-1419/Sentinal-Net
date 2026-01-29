"""
Security module for Sentinel-Net
Includes JWT token management, RBAC, and authentication
"""

from .jwt import (
    create_access_token,
    create_refresh_token,
    create_tokens,
    verify_token,
    refresh_access_token,
    decode_token,
    get_token_from_header,
    is_token_expired,
)

from .rbac import (
    Permission,
    Role,
    get_role_permissions,
    has_permission,
    can_access_user_data,
    can_update_user_data,
    can_delete_user,
    is_admin,
    is_moderator,
)

from .auth import (
    get_current_user,
    get_optional_user,
    require_role,
    require_admin,
    require_moderator,
    security,
)

__all__ = [
    # JWT
    "create_access_token",
    "create_refresh_token",
    "create_tokens",
    "verify_token",
    "refresh_access_token",
    "decode_token",
    "get_token_from_header",
    "is_token_expired",
    # RBAC
    "Permission",
    "Role",
    "get_role_permissions",
    "has_permission",
    "can_access_user_data",
    "can_update_user_data",
    "can_delete_user",
    "is_admin",
    "is_moderator",
    # Auth
    "get_current_user",
    "get_optional_user",
    "require_role",
    "require_admin",
    "require_moderator",
    "security",
]
