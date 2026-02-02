# Database Setup - Create Users Table in Supabase

## Quick Setup (2 minutes)

### Method 1: Using Supabase Dashboard (Recommended)

1. **Go to Supabase Dashboard**
   - Open: https://supabase.com/dashboard
   - Select your project: "jfhbgfpuusvlreucjvmf"

2. **Open SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Copy and Paste SQL**

   ```sql
   -- Create users table for authentication
   CREATE TABLE IF NOT EXISTS public.users (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       auth_id UUID NOT NULL UNIQUE,
       email TEXT NOT NULL UNIQUE,
       full_name TEXT,
       avatar_url TEXT,
       role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
       is_active BOOLEAN DEFAULT true,
       email_verified BOOLEAN DEFAULT false,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

   -- Create indexes for performance
   CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
   CREATE INDEX IF NOT EXISTS idx_users_auth_id ON public.users(auth_id);
   CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
   CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at DESC);

   -- Enable Row Level Security
   ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

   -- Create RLS policies (allow all for now)
   CREATE POLICY "Allow all access" ON public.users FOR ALL USING (true);
   ```

4. **Run Query**
   - Click "Run" button (blue play icon)
   - Wait for success message
   - You should see: "Query executed successfully"

5. **Verify**
   - Click "Table Editor" in sidebar
   - Look for "users" table in the list
   - Click it to view the structure

### Method 2: Using Python Script

If you prefer to run the migration via Python:

```python
from backend.db.supabase_client import get_supabase_client
from backend.db.migrations import CREATE_USERS_TABLE

# Get Supabase client
supabase = get_supabase_client()

# Execute the SQL
try:
    result = supabase.client.rpc('exec', {'sql': CREATE_USERS_TABLE})
    print("✓ Users table created successfully")
except Exception as e:
    print(f"✗ Error creating table: {str(e)}")
```

Run from project root:

```bash
python -c "from backend.db.migrations import CREATE_USERS_TABLE; print(CREATE_USERS_TABLE)"
```

---

## Verify Table Creation

### Check in Supabase Dashboard

1. Go to Table Editor
2. Look for "users" table
3. Click to expand and verify columns:
   - id (UUID)
   - auth_id (UUID)
   - email (text)
   - full_name (text)
   - avatar_url (text)
   - role (text)
   - is_active (boolean)
   - email_verified (boolean)
   - created_at (timestamp)
   - updated_at (timestamp)

### Check in SQL

```sql
-- Verify table exists
SELECT * FROM information_schema.tables
WHERE table_name = 'users' AND table_schema = 'public';

-- Verify columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND table_schema = 'public';

-- Verify indexes
SELECT indexname FROM pg_indexes
WHERE tablename = 'users' AND schemaname = 'public';
```

---

## Test Registration After Setup

### 1. Restart Backend

```bash
# In terminal with virtual environment activated
cd c:\Sami\Sentinal-net
python -m uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Registration via curl

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

### Expected Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "user",
    "created_at": "2026-02-02T..."
  }
}
```

### 3. Verify in Supabase

- Check auth.users table → Should see new user in Supabase Auth
- Check public.users table → Should see user profile with auth_id

---

## Troubleshooting

### Error: "Invalid API key"

**Solution:** Check .env file has SUPABASE_ANON_KEY

### Error: "users table does not exist"

**Solution:** Run the SQL create table script above in Supabase SQL Editor

### Error: "duplicate key value violates unique constraint"

**Solution:** User already exists. Use different email or delete from auth.users first

### Error: "permission denied for schema public"

**Solution:**

- Check that your Supabase SERVICE_ROLE_KEY has admin permissions
- Regenerate the key in Supabase dashboard if needed

---

## Fields Explanation

| Field          | Type      | Purpose                                              |
| -------------- | --------- | ---------------------------------------------------- |
| id             | UUID      | Database primary key (auto-generated)                |
| auth_id        | UUID      | Reference to Supabase auth.users.id (foreign key)    |
| email          | TEXT      | User email (unique, from Supabase auth)              |
| full_name      | TEXT      | User's display name (optional)                       |
| avatar_url     | TEXT      | User's profile image URL (optional)                  |
| role           | TEXT      | User role: 'user' (default), 'admin', or 'moderator' |
| is_active      | BOOLEAN   | Account active status (default: true)                |
| email_verified | BOOLEAN   | Email verification status (default: false)           |
| created_at     | TIMESTAMP | Account creation time (auto-set to now)              |
| updated_at     | TIMESTAMP | Last update time (auto-set to now)                   |

---

## Security Policies

The RLS (Row Level Security) policy allows all authenticated users to access the users table:

```sql
CREATE POLICY "Allow all access" ON public.users FOR ALL USING (true);
```

**⚠️ Production Note:** This is permissive for development. In production, implement stricter policies:

```sql
-- Users can only see their own profile
CREATE POLICY "Users see own profile" ON public.users
  FOR SELECT USING (auth.uid() = auth_id);

-- Users can only update their own profile
CREATE POLICY "Users update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = auth_id);

-- Only admins can delete users
CREATE POLICY "Admins can delete users" ON public.users
  FOR DELETE USING (
    EXISTS (SELECT 1 FROM public.users
            WHERE auth_id = auth.uid() AND role = 'admin')
  );
```

---

## Next: Test the Full Flow

Once the users table is created:

1. **Start Backend**

   ```bash
   python -m uvicorn backend.api.app:app --reload
   ```

2. **Start Frontend**

   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Registration**
   - Go to http://localhost:3000
   - Navigate to registration/signup
   - Fill form and submit
   - Should redirect to dashboard or show success

4. **Test Login**
   - Logout if needed
   - Go to login page
   - Enter credentials
   - Should authenticate successfully

5. **Test Predictions**
   - Go to /predict
   - Enter SMS text
   - Click Classify
   - Should see full results with RED/GREEN badge

---

**Last Updated:** February 2, 2026
**Status:** Ready for implementation
