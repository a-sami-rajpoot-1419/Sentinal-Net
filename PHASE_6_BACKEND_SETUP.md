# Phase 6 Backend Implementation - Setup Guide

## Overview
Phase 6 implements a complete authentication system for Sentinel-Net using Supabase Auth and JWT tokens.

## ✅ Completed Backend Components

### 1. **Database Models** (`backend/db/models.py`)
- ✅ `UserCreate` - Registration schema
- ✅ `UserLogin` - Login credentials
- ✅ `UserUpdate` - Profile update schema
- ✅ `UserResponse` - User profile response
- ✅ `TokenResponse` - JWT token response
- ✅ `PasswordReset` - Password reset request
- ✅ `AuthResponse` - Generic auth response

### 2. **JWT Token Management** (`backend/security/jwt.py`)
- ✅ `create_access_token()` - Create short-lived access tokens
- ✅ `create_refresh_token()` - Create long-lived refresh tokens
- ✅ `create_tokens()` - Create both token types
- ✅ `verify_token()` - Validate and decode JWT
- ✅ `refresh_access_token()` - Refresh expired tokens
- ✅ `is_token_expired()` - Check token expiration
- ✅ `get_token_from_header()` - Extract token from Authorization header

### 3. **Role-Based Access Control** (`backend/security/rbac.py`)
- ✅ `Permission` enum - All system permissions
- ✅ `Role` enum - User roles (user, admin, moderator)
- ✅ `ROLE_PERMISSIONS` - Role to permission mapping
- ✅ Permission checking functions:
  - `get_role_permissions()`
  - `has_permission()`
  - `can_access_user_data()`
  - `can_update_user_data()`
  - `can_delete_user()`
  - `is_admin()`
  - `is_moderator()`

### 4. **Authentication Middleware** (`backend/security/auth.py`)
- ✅ `get_current_user()` - Dependency to get authenticated user
- ✅ `get_optional_user()` - Optional authentication
- ✅ `require_admin()` - Admin-only routes
- ✅ `require_moderator()` - Moderator/admin routes
- ✅ `require_role()` - Custom role requirements
- ✅ HTTP Bearer token validation

### 5. **Database Integration** (`backend/db/supabase_client.py`)
- ✅ `get_user_by_id()` - Fetch user by UUID
- ✅ `get_user_by_email()` - Fetch user by email
- ✅ `create_user()` - Create user profile
- ✅ `update_user()` - Update user profile
- ✅ `delete_user()` - Delete user profile
- ✅ `list_users()` - List users with pagination
- ✅ `user_exists()` - Check user existence

### 6. **Authentication Routes** (`backend/api/routes/auth.py`)
- ✅ `POST /auth/register` - User registration
- ✅ `POST /auth/login` - User authentication
- ✅ `POST /auth/logout` - User logout
- ✅ `GET /auth/me` - Get current user profile
- ✅ `POST /auth/refresh` - Refresh access token
- ✅ `PUT /auth/profile` - Update user profile
- ✅ `POST /auth/password-reset` - Request password reset

### 7. **Application Configuration** (`backend/api/app.py`)
- ✅ Enhanced security middleware:
  - TrustedHostMiddleware
  - GZIPMiddleware
  - CORSMiddleware (with secure defaults)
- ✅ Updated version to 0.6.0
- ✅ Health check endpoint

### 8. **Route Integration** (`backend/api/routes/__init__.py`)
- ✅ `include_routes()` function
- ✅ Auto-includes all routers (auth, consensus, agents)

### 9. **Database Migrations** (`PHASE_6_USERS_TABLE.sql`)
- ✅ Users table creation
- ✅ RLS (Row Level Security) policies
- ✅ Automatic timestamp updates
- ✅ Email uniqueness constraint

---

## 🔧 Installation & Setup

### Step 1: Install Dependencies
```bash
cd c:\Sami\Sentinal-net
pip install -r requirements.txt
```

New packages added:
- `python-jose==3.3.0` - JWT handling
- `email-validator==2.1.0` - Email validation
- `supabase==2.4.2` - Supabase SDK

### Step 2: Configure Environment Variables

Add to your `.env` file:

```bash
# ===== JWT Configuration =====
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# ===== Supabase Configuration =====
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ===== API Security Configuration =====
API_TRUSTED_HOSTS=localhost,127.0.0.1,your-domain.com
API_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# ===== API Configuration =====
API_VERSION=0.6.0
API_TITLE=Sentinel-Net Consensus Engine
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development
LOG_LEVEL=INFO
WORKERS=1
```

### Step 3: Setup Supabase Users Table

1. Open your Supabase project dashboard
2. Go to SQL Editor
3. Copy the contents of `PHASE_6_USERS_TABLE.sql`
4. Paste and execute in Supabase SQL Editor
5. Verify: You should see no errors and the users table should be created

**Important:** The users table extends Supabase Auth's built-in users table

### Step 4: Verify Installation

Run the backend to verify all imports work:

```bash
cd backend
python -m api.main
```

You should see:
```
✓ Consensus engine ready
✓ Loaded 4 ML agents
✓ API running at http://0.0.0.0:8000
```

---

## 📚 API Endpoints Documentation

### Authentication Endpoints

#### 1. Register User
```
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}

Response (201):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 2. Login User
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": { ... }
}
```

#### 3. Get Current User Profile
```
GET /auth/me
Authorization: Bearer <access_token>

Response (200):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 4. Update User Profile
```
PUT /auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "avatar_url": "https://example.com/avatar.jpg"
}

Response (200):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T12:00:00Z"
}
```

#### 5. Refresh Access Token
```
POST /auth/refresh
Authorization: Bearer <access_token>

Response (200):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": { ... }
}
```

#### 6. Logout User
```
POST /auth/logout
Authorization: Bearer <access_token>

Response (200):
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### 7. Request Password Reset
```
POST /auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}

Response (200):
{
  "success": true,
  "message": "If the email exists, a password reset link has been sent"
}
```

---

## 🔐 Security Features

### 1. **JWT Tokens**
- **Access Token**: 15-minute expiration for API requests
- **Refresh Token**: 7-day expiration for token refresh
- **HS256 Signature**: HMAC-based signing for verification
- **Claims**: Includes user ID, email, role, and full name

### 2. **Role-Based Access Control**
```
User Role Permissions:
- READ_OWN_PROFILE
- UPDATE_OWN_PROFILE
- DELETE_OWN_ACCOUNT
- READ_AGENTS
- READ_CONSENSUS
- PARTICIPATE_CONSENSUS
- VIEW_WEIGHTS

Moderator Role (includes all User + ):
- CREATE_AGENT
- UPDATE_AGENT
- READ_ALL_PROFILES
- VIEW_ANALYTICS

Admin Role (includes all + ):
- DELETE_AGENT
- UPDATE_ANY_USER
- DELETE_ANY_USER
- MANAGE_ROLES
- MANAGE_SYSTEM
```

### 3. **Row-Level Security (RLS)**
- Users can only see their own profile data
- Admins can see all profiles
- Database enforces access control at the SQL level
- Automatic timestamp updates for audit trail

### 4. **HTTP Security**
- **CORS**: Restricted to configured origins only
- **Trusted Hosts**: Only requests from trusted hosts accepted
- **GZIP**: Response compression for bandwidth optimization
- **HTTPS Ready**: Configure for production deployment

### 5. **Password Security**
- Passwords hashed by Supabase Auth (bcrypt)
- Password reset via secure token-based flow
- No passwords logged or stored in user table

---

## 🧪 Testing the Endpoints

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Get current user (replace TOKEN with actual access token)
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN"

# Update profile
curl -X PUT http://localhost:8000/auth/profile \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'
```

### Using Swagger UI

1. Start the backend: `python -m api.main`
2. Visit: http://localhost:8000/docs
3. Click on authentication endpoints
4. Click "Try it out" button
5. Enter parameters and execute

---

## 🔄 Token Refresh Flow

```
1. User logs in → Receives access_token (15 min) + refresh_token (7 days)
2. Use access_token for API requests
3. When access_token expires → Use refresh_token to get new access_token
4. When refresh_token expires → User must login again
```

### Automatic Refresh Example (Frontend)
```python
# Backend will implement this in Phase 6b (Frontend)
def api_request(method, url, data=None, headers=None):
    # Add current access token to headers
    headers = headers or {}
    headers["Authorization"] = f"Bearer {access_token}"
    
    response = requests.request(method, url, json=data, headers=headers)
    
    # If token expired (401), refresh and retry
    if response.status_code == 401:
        refresh_tokens()  # Get new access_token
        headers["Authorization"] = f"Bearer {new_access_token}"
        response = requests.request(method, url, json=data, headers=headers)
    
    return response
```

---

## ✨ Next Steps (Phase 6b-6c)

### Phase 6b: Frontend Authentication
- [ ] Create auth context with React
- [ ] Build login/signup forms
- [ ] Implement protected routes
- [ ] Add token persistence
- [ ] Create user menu/dropdown

### Phase 6c: Testing & Polish
- [ ] Write unit tests for auth endpoints
- [ ] Write integration tests
- [ ] Test complete auth flow end-to-end
- [ ] Security audit and hardening
- [ ] Commit Phase 6 to GitHub

---

## 🐛 Troubleshooting

### "SUPABASE_URL not configured"
- Add `SUPABASE_URL` to `.env` file

### "Invalid email or password"
- Ensure user is registered in Supabase Auth
- Check email/password are correct

### "User profile not found"
- Ensure user profile was created in Supabase users table
- Run PHASE_6_USERS_TABLE.sql to create table

### "Invalid token"
- Ensure token is properly formatted
- Check token hasn't expired
- Verify JWT_SECRET_KEY matches

### CORS errors
- Add frontend URL to API_CORS_ORIGINS in .env
- Default: http://localhost:3000

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
│                     (Phase 6b)                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Auth Context │ Login Form │ Protected Routes   │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
                  API Request with JWT
                         │
┌────────────────────────▼────────────────────────────────┐
│              FastAPI Backend (Phase 6)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ /auth/* Routes │ Auth Middleware │ RBAC Check  │   │
│  └─────────────────────────────────────────────────┘   │
│              ▼                      ▼                    │
│  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │  Supabase Auth   │  │   Supabase Database (RLS)   │ │
│  │  (Credentials)   │  │   (User Profiles & Roles)   │ │
│  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Summary

**Backend Phase 6 Components Created:**
✅ User authentication models
✅ JWT token management system
✅ Role-based access control
✅ Authentication middleware
✅ Database integration with Supabase
✅ 7 authentication endpoints
✅ Enhanced security middleware
✅ SQL migrations for users table
✅ Comprehensive documentation

**Ready for Phase 6b:** Frontend authentication implementation

---

Generated: 2024
Version: 0.6.0
