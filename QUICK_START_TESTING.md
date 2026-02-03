# Quick Start - Registration & Login Testing

## Setup (One-Time)
```bash
cd c:\Sami\Sentinal-net

# Verify Python environment
.venv\Scripts\python --version

# Verify dependencies
.venv\Scripts\python -c "import requests; print('✓ requests available')"
```

## Step 1: Start Backend (Terminal 1)
```bash
cd c:\Sami\Sentinal-net
$env:API_ENV='production'
.venv\Scripts\python -m uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --workers 1
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
...
INFO:backend.api.app:✓ Sentinel-Net ready!
INFO:backend.api.app:🎯 Application is fully initialized and ready to serve requests
```

## Step 2: Test Registration (Terminal 2 - NEW Terminal!)
```bash
cd c:\Sami\Sentinal-net
.venv\Scripts\python test_full_registration.py
```

**Expected Output:**
```
✓ Backend is running
✓ Registration successful!
- Access Token: eyJ0eXAi...
- Refresh Token: ...
- Token Type: bearer
- User ID: [uuid]
- User Email: [email]
✓ ALL TESTS PASSED!
```

## Manual Testing with curl (Optional)

### Register
```bash
curl -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!"
  }'
```

## Troubleshooting

### Backend Crashes on Startup
✗ Old Issue: Now FIXED with HTTP REST API
✓ Check logs for specific error messages
✓ Verify .env file exists and has correct API keys

### Registration Returns 500 Error
- Check backend logs for error details
- Verify backend is running (`curl http://localhost:8000/agents/list`)
- Check .env file doesn't have inline comments after API keys

### HTTP Connection Fails
```bash
# Test Supabase connectivity
.venv\Scripts\python -c "
import requests
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_PROJECT_URL')
print(f'Testing: {url}')
response = requests.get(f'{url}/rest/v1/users?limit=1', timeout=10)
print(f'Status: {response.status_code}')
"
```

### User Not Created in Database
1. Check HTTP response status code (should be 200 or 201)
2. Verify admin headers are correct (service role key)
3. Check users table exists in Supabase

## Quick Validation Checklist

- [ ] Backend starts without errors
- [ ] `/agents/list` endpoint responds (HTTP 200)
- [ ] `/auth/register` endpoint accepts requests
- [ ] Registration returns HTTP 201 with tokens
- [ ] User appears in Supabase users table
- [ ] Login works with registered credentials
- [ ] Tokens are valid JWT tokens

## Connection Details

- **API Base URL**: `https://jfhbgfpuusvlreucjvmf.supabase.co`
- **REST API**: `/rest/v1/*` endpoints
- **Auth API**: `/auth/v1/*` endpoints
- **Auth Method**: Bearer token in Authorization header
- **Connection Type**: HTTP REST (no SDK, no connection pool needed)

---
**Status**: ✓ HTTP REST API connection verified and working
**Date**: Feb 3, 2026
