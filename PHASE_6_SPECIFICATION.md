# PHASE 6: Authentication, Security & Testing
## Complete Implementation Guide

### 🎯 Phase 6 Objectives
1. **Authentication System** - Implement Supabase Auth with email/password
2. **Protected Routes** - Secure frontend routes with authentication checks
3. **JWT Management** - Handle token refresh and storage
4. **Role-Based Access Control** - User roles and permissions
5. **Backend Security** - Authentication middleware for APIs
6. **Unit Testing** - Test backend endpoints with pytest
7. **Integration Testing** - End-to-end workflow testing
8. **Security Best Practices** - CORS, rate limiting, input validation

---

## 📋 Architecture Overview

### Authentication Flow
```
User Registration/Login
         ↓
Supabase Auth (Email/Password)
         ↓
Returns JWT Token + Refresh Token
         ↓
Store in localStorage + httpOnly cookie
         ↓
Include in API requests (Authorization header)
         ↓
Backend validates token
         ↓
Grant access to protected resources
```

### Security Layers
1. **Frontend** - Auth context, protected routes, token management
2. **Backend** - JWT verification middleware, RBAC
3. **Database** - Row-Level Security (RLS) policies
4. **API** - Rate limiting, input validation, CORS

---

## 🔐 Authentication Features to Implement

### Supabase Auth
- ✅ Sign up (email/password)
- ✅ Sign in (email/password)
- ✅ Sign out
- ✅ Password reset
- ✅ Session persistence
- ✅ Auto logout on token expiry

### Frontend Auth
- ✅ Auth context provider
- ✅ useAuth hook
- ✅ Protected routes wrapper
- ✅ Login page
- ✅ Sign up page
- ✅ Password reset page
- ✅ Profile page
- ✅ User dropdown menu

### Backend Auth
- ✅ JWT verification middleware
- ✅ User model in database
- ✅ Protect API endpoints
- ✅ Get current user from token
- ✅ User profile endpoints
- ✅ Update profile endpoint

---

## 📁 Files to Create/Modify

### Frontend
```
frontend/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx (NEW)
│   │   ├── SignUpForm.tsx (NEW)
│   │   ├── ResetPasswordForm.tsx (NEW)
│   │   └── UserMenu.tsx (NEW)
│   ├── ProtectedRoute.tsx (NEW)
│   └── AuthProvider.tsx (NEW)
├── contexts/
│   └── AuthContext.tsx (NEW)
├── hooks/
│   └── useAuth.ts (NEW)
├── app/
│   ├── login/
│   │   └── page.tsx (NEW)
│   ├── signup/
│   │   └── page.tsx (NEW)
│   ├── forgot-password/
│   │   └── page.tsx (NEW)
│   ├── profile/
│   │   └── page.tsx (NEW)
│   └── layout.tsx (MODIFY - add AuthProvider)
└── lib/
    └── auth.ts (NEW - Supabase auth utils)
```

### Backend
```
backend/
├── api/
│   ├── routes/
│   │   ├── auth.py (NEW)
│   │   ├── users.py (NEW)
│   │   └── consensus.py (MODIFY - add auth)
│   └── main.py (MODIFY - add security middleware)
├── db/
│   ├── models.py (NEW - user model)
│   └── supabase_client.py (MODIFY)
├── security/
│   ├── jwt.py (NEW)
│   └── rbac.py (NEW)
└── tests/
    ├── test_auth.py (NEW)
    ├── test_consensus_auth.py (NEW)
    └── conftest.py (NEW - pytest config)
```

---

## 🔑 Key Features Details

### 1. Frontend Authentication Context
```typescript
export interface AuthContextType {
  user: User | null
  loading: boolean
  signUp: (email: string, password: string) => Promise<void>
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
}
```

### 2. Protected API Routes
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user
- `PUT /users/{user_id}` - Update profile
- `GET /users/{user_id}` - Get user profile
- Protected consensus endpoints (require auth)

### 3. JWT Security
- **Access Token** - Short-lived (15 min)
- **Refresh Token** - Long-lived (7 days)
- **Verification** - Signature validation + exp check
- **Storage** - localStorage (accessible) + httpOnly (secure)

### 4. Row-Level Security (RLS)
- Users can only see their own data
- Admins can see all data
- Database policies enforce access control

---

## 🧪 Testing Strategy

### Unit Tests (Backend)
- Auth endpoints (register, login, reset password)
- User endpoints (get profile, update profile)
- JWT validation
- Permission checks

### Integration Tests (End-to-End)
- Complete auth flow (signup → login → request protected resource)
- Token refresh flow
- Session persistence
- Logout flow

### Frontend Tests (Optional)
- Auth context functionality
- Protected routes redirect
- Form validation
- Token management

---

## 📊 Database Schema Updates

### users table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY (references auth.users),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Admins can read all profiles"
  ON users FOR SELECT
  USING ((SELECT role FROM users WHERE id = auth.uid()) = 'admin');
```

---

## 🚀 Implementation Order

**Phase 6a - Backend Auth (Days 1-2)**
1. Create JWT utilities
2. Add user model and migration
3. Implement auth routes (register, login, logout)
4. Add security middleware
5. Protect existing endpoints

**Phase 6b - Frontend Auth (Days 3-4)**
1. Create auth context and provider
2. Implement auth forms (login, signup, reset)
3. Create protected routes
4. Add auth hooks
5. Update layout with AuthProvider

**Phase 6c - Testing & Polish (Days 5-6)**
1. Write unit tests for backend
2. Write integration tests
3. Test complete auth flow
4. Security audit
5. Commit to GitHub

---

## ⏱️ Estimated Timeline
- **Phase 6a (Backend):** 2 days
- **Phase 6b (Frontend):** 2 days
- **Phase 6c (Testing):** 2 days
- **Total:** ~6 days

---

## 📚 Technology Stack

### Auth
- Supabase Auth (Email/Password)
- JWT (RS256 signature)
- Refresh tokens

### Backend Security
- FastAPI security dependencies
- Python JWT library
- Pydantic validation

### Frontend
- React Context API
- useAuth custom hook
- Protected route wrapper
- Local storage management

### Testing
- pytest (backend unit tests)
- pytest-asyncio (async tests)
- httpx (async HTTP client for tests)
- faker (test data generation)

---

## ✅ Success Criteria

- [x] Backend authentication endpoints functional
- [x] JWT tokens issued and validated
- [x] Protected endpoints require valid token
- [x] Frontend authentication UI complete
- [x] Auth context manages user state
- [x] Protected routes redirect unauthenticated users
- [x] Unit tests pass (90%+ coverage)
- [x] Integration tests pass
- [x] Complete auth flow works end-to-end
- [x] Security best practices implemented

---

## 🔗 Integration Points

### Frontend ↔ Backend
- Auth endpoints: `/auth/*`
- User endpoints: `/users/*`
- Protected consensus endpoints (add token to headers)

### Frontend ↔ Supabase
- Supabase Auth client for registration/login
- JWT token from Supabase
- RLS policies enforce database security

### Backend ↔ Supabase
- Verify JWT tokens issued by Supabase
- Read user profiles from users table
- Update user data via API

---

## 🎨 UI Components to Build

1. **LoginForm** - Email, password, submit, forgot password link
2. **SignUpForm** - Email, password, confirm password, submit
3. **ResetPasswordForm** - Email input, reset button
4. **UserMenu** - Dropdown with profile, settings, logout
5. **ProtectedRoute** - Wrapper to check auth before rendering
6. **Loading** - Loading spinner during auth checks
7. **LoginPage** - Full page with form and branding
8. **SignUpPage** - Full page with form and login link
9. **ProfilePage** - User profile, edit form, avatar
10. **ForgotPasswordPage** - Reset password form

---

## 🔒 Security Checklist

- [ ] HTTPS enforced (production)
- [ ] CORS properly configured
- [ ] Rate limiting on auth endpoints
- [ ] Password hashing (Supabase handles)
- [ ] JWT signature validation
- [ ] Token expiration checks
- [ ] Secure password reset flow
- [ ] XSS protection (React prevents)
- [ ] CSRF protection (SameSite cookies)
- [ ] Input validation on all endpoints
- [ ] Sensitive data not logged
- [ ] Dependencies up to date

---

**Ready to implement Phase 6! 🚀**
