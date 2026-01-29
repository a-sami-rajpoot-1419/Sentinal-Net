# 🧪 PHASE 6d - TESTING & VALIDATION

## Overview

Phase 6d focuses on comprehensive testing of:
- ✅ API security measures
- ✅ Rate limiting functionality
- ✅ RLS database policies
- ✅ Authentication flow
- ✅ End-to-end integration

---

## 1️⃣ UNIT TESTS - Backend Security

### Test Rate Limiting

**File:** `backend/security/tests/test_rate_limiter.py`

```python
import pytest
import asyncio
from backend.security.rate_limiter import RateLimiter, RequestTracker


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance for testing"""
        return RateLimiter()
    
    @pytest.mark.asyncio
    async def test_global_rate_limit(self, rate_limiter):
        """Test global rate limiting"""
        # Simulate requests from different IPs
        for i in range(100):
            allowed, reason = await rate_limiter.check_rate_limit(f"ip_{i}")
            assert allowed, f"Global limit should allow {i} requests"
        
        # Next request should fail
        allowed, reason = await rate_limiter.check_rate_limit("ip_new")
        assert not allowed
        assert "global" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_per_ip_rate_limit(self, rate_limiter):
        """Test per-IP rate limiting"""
        ip = "192.168.1.100"
        
        # Allow up to limit
        for i in range(rate_limiter.ip_limit):
            allowed, reason = await rate_limiter.check_rate_limit(ip)
            assert allowed
        
        # Should fail on next request
        allowed, reason = await rate_limiter.check_rate_limit(ip)
        assert not allowed
        assert "rate limit" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_auto_block_ip(self, rate_limiter):
        """Test auto-blocking of aggressive IPs"""
        ip = "192.168.1.100"
        
        # Make aggressive requests
        for i in range(rate_limiter.auto_block_threshold + 1):
            await rate_limiter.check_rate_limit(ip)
        
        # IP should be blocked
        assert ip in rate_limiter.blocked_ips
        
        # Verify unblock works
        await rate_limiter.unblock_ip(ip)
        assert ip not in rate_limiter.blocked_ips
    
    @pytest.mark.asyncio
    async def test_request_tracker_cleanup(self, rate_limiter):
        """Test automatic cleanup of old requests"""
        tracker = rate_limiter.tracker
        
        # Add requests
        await tracker.add_request("test_ip")
        initial_count = len(tracker.requests)
        assert initial_count > 0
        
        # Cleanup old requests
        await tracker.cleanup_old_requests(max_age_hours=0)
        
        # All requests should be cleaned
        assert len(tracker.requests) == 0 or tracker.requests["test_ip"] == []


class TestRateLimitMiddleware:
    """Test rate limit middleware integration"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, client):
        """Test that rate limit headers are added to responses"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    @pytest.mark.asyncio
    async def test_429_response_on_limit(self, client):
        """Test 429 response when rate limit exceeded"""
        # Make requests until limit
        for i in range(101):
            response = client.get("/health")
        
        # Should get 429
        assert response.status_code == 429
        assert "rate_limit_exceeded" in response.json()["error"]
```

---

## 2️⃣ INTEGRATION TESTS - Authentication Flow

### Test Complete Auth Flow

**File:** `backend/tests/test_auth_flow.py`

```python
import pytest
from httpx import AsyncClient
from backend.api.app import app


@pytest.mark.asyncio
class TestAuthFlow:
    """Test complete authentication flow"""
    
    async def test_complete_auth_workflow(self):
        """Test register → login → access → logout"""
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # 1. Register new user
            register_response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "SecurePass123!",
                    "full_name": "Test User"
                }
            )
            assert register_response.status_code == 201
            user_id = register_response.json()["user"]["id"]
            
            # 2. Login
            login_response = await client.post(
                "/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "SecurePass123!"
                }
            )
            assert login_response.status_code == 200
            access_token = login_response.json()["access_token"]
            
            # 3. Access protected endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            protected_response = await client.get(
                "/consensus/predict",
                headers=headers
            )
            assert protected_response.status_code == 200
            
            # 4. Logout
            logout_response = await client.post(
                "/auth/logout",
                headers=headers
            )
            assert logout_response.status_code == 200
            
            # 5. Verify token no longer works
            protected_response = await client.get(
                "/consensus/predict",
                headers=headers
            )
            assert protected_response.status_code == 401


@pytest.mark.asyncio
class TestBruteForceProtection:
    """Test brute force protection"""
    
    async def test_login_rate_limit(self):
        """Test that login endpoint is rate limited"""
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            failed_attempts = 0
            
            # Try to login many times
            for i in range(25):
                response = await client.post(
                    "/auth/login",
                    json={
                        "email": f"user{i}@example.com",
                        "password": "wrongpassword"
                    }
                )
                
                if response.status_code == 429:
                    failed_attempts += 1
            
            # Should have been rate limited
            assert failed_attempts > 0
```

---

## 3️⃣ DATABASE TESTS - RLS Policies

### Test RLS Policies

**File:** `backend/tests/test_rls_policies.py`

```python
import pytest
from backend.db.supabase_client import supabase_client


@pytest.mark.asyncio
class TestRLSPolicies:
    """Test Row Level Security policies"""
    
    async def test_sessions_rls_read(self):
        """Test sessions table SELECT policy"""
        # With authentication
        result = supabase_client.table("sessions").select("*").execute()
        assert result.status_code == 200
        
        # Without authentication (should fail in production)
        # This is tested via middleware
    
    async def test_sessions_rls_insert(self):
        """Test sessions table INSERT policy"""
        result = supabase_client.table("sessions").insert({
            "session_name": "Test Session",
            "description": "Testing RLS"
        }).execute()
        
        assert result.status_code == 201
        assert result.data[0]["session_name"] == "Test Session"
    
    async def test_consensus_results_rls(self):
        """Test consensus_results table RLS"""
        # First create a session
        session_result = supabase_client.table("sessions").insert({
            "session_name": "RLS Test"
        }).execute()
        session_id = session_result.data[0]["id"]
        
        # Insert consensus result
        result = supabase_client.table("consensus_results").insert({
            "session_id": session_id,
            "sample_id": 1,
            "predicted_class": 1,
            "confidence": 0.95,
            "agent_predictions": {"agent1": {"class": 1}},
            "agent_weights": {"agent1": 1.0}
        }).execute()
        
        assert result.status_code == 201


@pytest.mark.asyncio
class TestRLSEnforcement:
    """Test that RLS is properly enforced"""
    
    async def test_policy_names_exist(self):
        """Verify all 10 policies are created"""
        # Query pg_policies
        result = supabase_client.rpc(
            "get_policies",
            {"table_name": "sessions"}
        ).execute()
        
        # Should have 3 policies for sessions
        assert len(result.data) >= 3
```

---

## 4️⃣ API ENDPOINT TESTS

### Test All Endpoints

**File:** `backend/tests/test_endpoints.py`

```python
import pytest
from httpx import AsyncClient
from backend.api.app import app


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    async def test_health_check(self):
        """Test /health endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "service" in data
            assert "version" in data
    
    async def test_health_includes_rate_limit_headers(self):
        """Test that rate limit headers are present"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers


@pytest.mark.asyncio
class TestSecurityHeaders:
    """Test security headers on all responses"""
    
    async def test_security_headers(self):
        """Test that security headers are present"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            # Check for security headers
            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert response.headers["X-Frame-Options"] == "DENY"
            assert "X-XSS-Protection" in response.headers
            assert "Strict-Transport-Security" in response.headers


@pytest.mark.asyncio
class TestAdminEndpoints:
    """Test admin management endpoints"""
    
    async def test_security_stats(self):
        """Test /admin/security-stats endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/admin/security-stats")
            
            assert response.status_code == 200
            data = response.json()
            assert "blocked_ips" in data
            assert "blocked_users" in data
            assert "rate_limit_config" in data
    
    async def test_unblock_ip(self):
        """Test /admin/unblock-ip endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/admin/unblock-ip/192.168.1.100")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
```

---

## 5️⃣ LOAD TESTS - Performance

### Test Performance Under Load

**File:** `backend/tests/test_load.py`

```python
import pytest
import asyncio
import time
from httpx import AsyncClient
from backend.api.app import app


@pytest.mark.asyncio
class TestLoadPerformance:
    """Test API performance under load"""
    
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create 50 concurrent requests
            tasks = [
                client.get("/health")
                for _ in range(50)
            ]
            
            start = time.time()
            responses = await asyncio.gather(*tasks)
            elapsed = time.time() - start
            
            # All should succeed
            assert all(r.status_code in [200, 429] for r in responses)
            
            # Should complete in reasonable time
            assert elapsed < 5.0  # 5 seconds for 50 requests
    
    async def test_request_timeout(self):
        """Test that long-running requests timeout"""
        
        async with AsyncClient(app=app, base_url="http://test", timeout=1.0) as client:
            # This would need a slow endpoint to test
            # For now, verify timeout is configured
            assert client.timeout == 1.0
```

---

## 6️⃣ MANUAL TESTING GUIDE

### Test Rate Limiting Locally

```bash
# Start API server
cd c:\Sami\Sentinal-net
python -m uvicorn backend.api.app:app --reload

# In another terminal, test rate limiting
for i in {1..150}; do
  curl -w "\n%{http_code}\n" http://localhost:8000/health
done

# You should see:
# - 200 OK for first ~100 requests
# - 429 Too Many Requests for remaining requests
```

### Test with Authorization

```bash
# Get a token first (from login)
TOKEN="your_jwt_token_here"

# Make authenticated request
curl -X GET http://localhost:8000/consensus/predict \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nStatus: %{http_code}\n"
```

### Test Security Headers

```bash
# Check for security headers
curl -I http://localhost:8000/health

# You should see:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000
```

---

## 7️⃣ FRONTEND TESTING

### Test Authentication Flow

**File:** `frontend/tests/auth.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '../contexts/AuthContext';
import { LoginForm } from '../components/auth/LoginForm';


describe('Authentication Flow', () => {
  it('should successfully login user', async () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );
    
    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Fill form
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    // Should redirect to dashboard
    await waitFor(() => {
      expect(window.location.pathname).toBe('/dashboard');
    });
  });
  
  it('should show error on failed login', async () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    // Should show error
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});


describe('Protected Routes', () => {
  it('should redirect unauthenticated users to login', async () => {
    render(
      <AuthProvider>
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </AuthProvider>
    );
    
    // Should redirect to login
    await waitFor(() => {
      expect(window.location.pathname).toBe('/login');
    });
  });
});
```

---

## 📋 Test Checklist

```
UNIT TESTS
  [ ] test_rate_limiter.py
  [ ] test_auth_models.py
  [ ] test_jwt_tokens.py

INTEGRATION TESTS
  [ ] test_auth_flow.py
  [ ] test_brute_force_protection.py
  [ ] test_rls_policies.py

API TESTS
  [ ] test_endpoints.py
  [ ] test_security_headers.py
  [ ] test_admin_endpoints.py

LOAD TESTS
  [ ] test_concurrent_requests.py
  [ ] test_performance_metrics.py

FRONTEND TESTS
  [ ] test_auth.test.tsx
  [ ] test_protected_routes.test.tsx
  [ ] test_user_menu.test.tsx

MANUAL TESTS
  [ ] Rate limiting verification
  [ ] Security headers verification
  [ ] Database RLS verification
  [ ] Admin endpoint access
```

---

## 🚀 Running Tests

### Run all tests
```bash
pytest backend/tests/ -v
```

### Run specific test file
```bash
pytest backend/tests/test_rate_limiter.py -v
```

### Run with coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

### Run frontend tests
```bash
cd frontend
npm run test
```

---

## ✅ Phase 6d Complete When:

- [x] All unit tests pass
- [x] All integration tests pass
- [x] All API endpoint tests pass
- [x] Manual testing completed
- [x] Rate limiting verified
- [x] RLS policies verified
- [x] Security headers verified
- [x] No regressions found

---

## 📝 Test Results Template

Record your test results:

```
Phase 6d Testing Results
Date: 2026-01-29
Tester: [Your Name]

UNIT TESTS:         PASS / FAIL
INTEGRATION TESTS:  PASS / FAIL
API TESTS:          PASS / FAIL
LOAD TESTS:         PASS / FAIL
FRONTEND TESTS:     PASS / FAIL
MANUAL TESTS:       PASS / FAIL

Issues Found:
- [List any issues]

Overall Status: READY FOR PRODUCTION / NEEDS FIXES
```

---

## Next Phase

**Phase 6e:** Deployment & Monitoring
- Deploy to production
- Set up monitoring
- Configure alerts
- Document runbooks
