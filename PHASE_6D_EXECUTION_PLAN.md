# 🧪 PHASE 6d - EXECUTION PLAN

## Status: ✅ RLS POLICIES VERIFIED

**Confirmed:** All 10 RLS policies correctly deployed and enforcing authentication:
- ✅ 3 sessions policies (SELECT, INSERT, UPDATE)
- ✅ 2 consensus_results policies (SELECT, INSERT)
- ✅ 2 weight_updates policies (SELECT, INSERT)
- ✅ 3 agent_performance policies (SELECT, INSERT, UPDATE)

**Security Verified:**
- All policies enforce `auth.role() = 'authenticated'`
- INSERT policies include `auth.uid() IS NOT NULL` verification
- "No USING clause" on INSERT is **expected** (INSERT uses WITH CHECK)

---

## 📋 TEST EXECUTION CHECKLIST

### ✅ Prerequisites Met
- [x] RLS policies deployed and verified
- [x] Rate limiting module created (backend/security/rate_limiter.py)
- [x] Security middleware integrated (app.py)
- [x] Security configuration in place (.env)
- [x] API endpoints implemented
- [x] Admin endpoints created

### ⏳ Ready to Execute

#### **1. Unit Tests - Rate Limiting**
```bash
# Test file: backend/security/tests/test_rate_limiter.py
pytest backend/security/tests/test_rate_limiter.py -v --tb=short
```

**What's tested:**
- Global rate limit (10,000 req/min)
- Per-IP rate limit (100 req/min)
- Per-user rate limit (1,000 req/hour)
- Auto-blocking at 50 requests/60s
- Rate limit header propagation

**Expected Result:** All tests pass ✅

---

#### **2. Integration Tests - Authentication**
```bash
# Test file: backend/tests/test_auth_flow.py
pytest backend/tests/test_auth_flow.py -v --tb=short
```

**What's tested:**
- User registration flow
- User login flow
- Token generation and validation
- Token refresh mechanism
- Logout and session cleanup
- Failed auth attempts (brute force detection)

**Expected Result:** All tests pass ✅

---

#### **3. Database Tests - RLS Policies**
```bash
# Test file: backend/tests/test_rls_policies.py
pytest backend/tests/test_rls_policies.py -v --tb=short
```

**What's tested:**
- SELECT policies enforce authentication
- INSERT policies enforce authentication + uid validation
- UPDATE policies enforce authentication
- Unauthenticated access blocked on all tables
- Cross-user data isolation

**Expected Result:** All tests pass ✅

---

#### **4. Security Tests - Brute Force Protection**
```bash
# Test file: backend/tests/test_brute_force_protection.py
pytest backend/tests/test_brute_force_protection.py -v --tb=short
```

**What's tested:**
- Failed login attempts tracked
- Account locked after N attempts
- IP blocked after N requests
- Rate limit headers correctly set
- Recovery mechanisms working

**Expected Result:** All tests pass ✅

---

#### **5. API Endpoint Tests**
```bash
# Test file: backend/tests/test_endpoints.py
pytest backend/tests/test_endpoints.py -v --tb=short
```

**What's tested:**
- Health check endpoint (`/health`)
- Auth endpoints security
- Security headers on all responses
- CORS headers properly set
- Admin endpoints authentication
- Rate limit responses (429)

**Expected Result:** All tests pass ✅

---

#### **6. Load & Performance Tests**
```bash
# Test file: backend/tests/test_load.py
pytest backend/tests/test_load.py -v --tb=short -s
```

**What's tested:**
- Concurrent request handling
- Rate limiter under load
- Memory usage stability
- Response time consistency
- Auto-blocking under attack

**Expected Result:** All tests pass ✅

---

#### **7. Frontend Tests - Auth Flow**
```bash
# Test file: frontend/tests/auth.test.ts
npm test frontend/tests/auth.test.ts
```

**What's tested:**
- Login form submission
- Sign up form validation
- Protected route access
- Token storage in localStorage
- Auto token refresh
- User menu display

**Expected Result:** All tests pass ✅

---

### 🔧 Manual Testing

#### **Test Rate Limiting**
```bash
# Rapid fire requests (should trigger rate limit after 100)
for i in {1..150}; do curl -s http://localhost:8000/health | grep -q '"status"' && echo "✓ $i" || echo "✗ $i"; done
```

**Expected:** First 100 succeed, requests 101-150 return 429 (Too Many Requests)

---

#### **Test Security Headers**
```bash
# Check headers on response
curl -I http://localhost:8000/health
```

**Expected headers:**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000

---

#### **Test Admin Endpoints**
```bash
# Check security stats
curl http://localhost:8000/admin/security-stats

# Unblock an IP (requires admin token)
curl -X POST http://localhost:8000/admin/unblock-ip/192.168.1.100 \
  -H "Authorization: Bearer {ADMIN_TOKEN}"

# Unblock a user
curl -X POST http://localhost:8000/admin/unblock-user/user-id \
  -H "Authorization: Bearer {ADMIN_TOKEN}"
```

**Expected:** All endpoints respond with security data

---

#### **Test RLS Enforcement**
```sql
-- In Supabase SQL Editor
-- Try to insert without auth (should fail)
INSERT INTO sessions (user_id, token) 
VALUES ('test', 'test');

-- Should fail with "new row violates row-level security policy"
```

---

## 🚀 Execution Order

**Recommended sequence:**
1. ✅ RLS Policy Verification (COMPLETED)
2. → Unit Tests (Rate Limiter) - 5 min
3. → Integration Tests (Auth Flow) - 5 min
4. → Database Tests (RLS) - 5 min
5. → Security Tests (Brute Force) - 5 min
6. → API Tests (Endpoints) - 5 min
7. → Load Tests - 10 min
8. → Frontend Tests - 5 min
9. → Manual Testing - 10 min

**Total Time:** ~50 minutes

---

## 📊 Test Results Template

Use this to document results:

```
═══════════════════════════════════════════════════════════════════
PHASE 6d - TEST EXECUTION RESULTS
═══════════════════════════════════════════════════════════════════

Date: [YYYY-MM-DD]
Time: [HH:MM UTC]
Tester: [Name]

───────────────────────────────────────────────────────────────────
RLS POLICY VERIFICATION
───────────────────────────────────────────────────────────────────
Status: ✅ VERIFIED
Policies Found: 10
Tables Protected: 4 (sessions, consensus_results, weight_updates, agent_performance)
Auth Checks: All enforce auth.role() = 'authenticated'

───────────────────────────────────────────────────────────────────
UNIT TESTS
───────────────────────────────────────────────────────────────────
Rate Limiter Tests:       [PASS/FAIL] [X/Y tests]

───────────────────────────────────────────────────────────────────
INTEGRATION TESTS
───────────────────────────────────────────────────────────────────
Auth Flow Tests:          [PASS/FAIL] [X/Y tests]
RLS Policy Tests:         [PASS/FAIL] [X/Y tests]
Brute Force Tests:        [PASS/FAIL] [X/Y tests]

───────────────────────────────────────────────────────────────────
API TESTS
───────────────────────────────────────────────────────────────────
Endpoint Tests:           [PASS/FAIL] [X/Y tests]
Load Tests:               [PASS/FAIL] [X/Y tests]

───────────────────────────────────────────────────────────────────
FRONTEND TESTS
───────────────────────────────────────────────────────────────────
Auth Flow Tests:          [PASS/FAIL] [X/Y tests]

───────────────────────────────────────────────────────────────────
MANUAL TESTING
───────────────────────────────────────────────────────────────────
Rate Limiting:            [PASS/FAIL]
Security Headers:         [PASS/FAIL]
Admin Endpoints:          [PASS/FAIL]
RLS Enforcement:          [PASS/FAIL]

───────────────────────────────────────────────────────────────────
SUMMARY
───────────────────────────────────────────────────────────────────
Overall Status: [PASS/FAIL]
Issues Found: [List any]
Ready for Phase 6e: [YES/NO]

───────────────────────────────────────────────────────────────────
```

---

## ✅ Next Phase Criteria

**Phase 6d Testing is COMPLETE when:**
- [x] All 10 RLS policies verified and active
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All API tests passing
- [ ] All load tests passing
- [ ] All frontend tests passing
- [ ] All manual tests passing
- [ ] No security vulnerabilities found
- [ ] Rate limiting working correctly
- [ ] Admin endpoints functioning

**Then proceed to: PHASE 6e - DEPLOYMENT & MONITORING**

---

## 📝 Notes

- All tests assume backend running on `http://localhost:8000`
- All tests assume frontend running on `http://localhost:3000`
- Tests require proper `.env` configuration
- Rate limiting tests may need adjustment based on configured limits
- Load tests should be run in isolated environment to avoid blocking IPs

---

**Ready to execute Phase 6d testing!** 🚀
