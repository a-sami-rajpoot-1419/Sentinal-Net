# 🔧 Supabase Database Setup Guide

## ✅ Your .env is Correct!

All Supabase credentials are properly configured.

---

## 📋 Setup Steps (5 minutes)

### Step 1: Copy the SQL Script

**File:** `SUPABASE_SETUP.sql` (in project root)

This file contains:
- 4 database tables
- 8 indexes for optimization
- Row Level Security (RLS) policies
- Initial agent records

### Step 2: Go to Supabase Dashboard

1. Open: **https://supabase.com/dashboard**
2. Log in with your credentials
3. Select project: **`jfhbgfpuusvlreucjvmf`**

### Step 3: Open SQL Editor

1. Click **SQL Editor** (top menu)
2. Click **New Query** (button)

### Step 4: Paste SQL

1. Copy entire content of `SUPABASE_SETUP.sql`
2. Paste into the SQL editor
3. You should see syntax highlighting

### Step 5: Execute

1. Click **Run** button (top right)
2. Wait for completion
3. You should see: **✓ Success**

---

## 🎯 What Gets Created

### Tables

#### `sessions` - Experiment tracking
```
├── id (UUID) - Primary key
├── session_name (TEXT) - Name of session
├── description (TEXT) - Optional description
├── created_at (TIMESTAMP) - Creation time
└── updated_at (TIMESTAMP) - Last update
```

#### `consensus_results` - Individual predictions
```
├── id (UUID) - Primary key
├── session_id (UUID) - Foreign key to sessions
├── sample_id (INTEGER) - Sample identifier
├── predicted_class (INTEGER) - Final prediction
├── confidence (FLOAT) - Confidence score
├── agent_predictions (JSONB) - All agent predictions
├── agent_weights (JSONB) - Agent weights used
└── created_at (TIMESTAMP) - Creation time
```

#### `weight_updates` - RWPV tracking
```
├── id (UUID) - Primary key
├── session_id (UUID) - Foreign key to sessions
├── agent_name (TEXT) - Agent name
├── previous_weight (FLOAT) - Weight before update
├── new_weight (FLOAT) - Weight after update
├── reason (TEXT) - Why weight changed
├── true_label (INTEGER) - Ground truth
├── predicted_label (INTEGER) - Agent's prediction
└── created_at (TIMESTAMP) - Creation time
```

#### `agent_performance` - Aggregate statistics
```
├── id (UUID) - Primary key
├── agent_name (TEXT UNIQUE) - Agent name
├── total_predictions (INTEGER) - Count of predictions
├── correct_predictions (INTEGER) - Count correct
├── accuracy (FLOAT) - Accuracy percentage
├── confidence_avg (FLOAT) - Average confidence
├── current_weight (FLOAT) - Current agent weight
└── updated_at (TIMESTAMP) - Last update
```

### Indexes (for performance)

| Index | Purpose |
|-------|---------|
| `idx_sessions_created` | Fast session queries by date |
| `idx_consensus_session` | Find results by session |
| `idx_consensus_created` | Find recent predictions |
| `idx_consensus_sample` | Find predictions by sample |
| `idx_weight_updates_session` | Find weight changes by session |
| `idx_weight_updates_agent` | Find agent weight history |
| `idx_weight_created` | Find recent weight updates |
| `idx_agent_performance_name` | Fast agent lookups |

---

## 🔒 Row Level Security (RLS)

**Development Mode:** All users can read/write all data

**Production Mode:** Will implement:
- Authentication via Supabase Auth
- User-based access policies
- Session-based data isolation

---

## ✅ Verification Steps

### After Running SQL, Verify:

**1. Check tables exist:**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

Should return:
- `sessions`
- `consensus_results`
- `weight_updates`
- `agent_performance`

**2. Check initial agent data:**
```sql
SELECT * FROM agent_performance;
```

Should return 4 rows:
- naive_bayes
- svm
- random_forest
- logistic_regression

**3. Check indexes:**
```sql
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('sessions', 'consensus_results', 'weight_updates', 'agent_performance');
```

Should show 8 indexes

---

## 🧪 Test Connection from Python

```python
from backend.db.supabase_client import get_supabase_client

# Create client
client = get_supabase_client()
print("✓ Supabase connected")

# Test query
response = client.client.table('agent_performance').select('*').execute()
print(f"✓ Found {len(response.data)} agents")

# Expected output:
# ✓ Supabase connected
# ✓ Found 4 agents
```

---

## 📊 SQL Preview

First few lines of `SUPABASE_SETUP.sql`:

```sql
-- ============================================================================
-- SENTINEL-NET PHASE 4: SUPABASE DATABASE SCHEMA
-- ============================================================================

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_name TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ... (rest of schema)
```

---

## 🚨 Troubleshooting

### Error: "Relation does not exist"

**Solution:** Run `SUPABASE_SETUP.sql` again in SQL Editor

### Error: "Permission denied"

**Solution:** Use correct Supabase role (should be automatic)

### Error: "Connection refused"

**Solution:** 
- Check .env has correct `SUPABASE_PROJECT_URL`
- Verify project exists in Supabase Dashboard
- Check internet connection

### Error: "Duplicate key value"

**Solution:** Tables already exist (safe, use `IF NOT EXISTS` in SQL)

---

## 📋 Quick Checklist

- [ ] Opened Supabase Dashboard
- [ ] Selected correct project
- [ ] Opened SQL Editor
- [ ] Pasted `SUPABASE_SETUP.sql`
- [ ] Clicked "Run"
- [ ] Verified success message
- [ ] Ran verification query (optional)
- [ ] Tested Python connection (optional)

---

## ✅ Setup Complete!

Once SQL runs successfully:

**Next:**
```bash
# 1. Run tests
pytest backend/consensus/tests/ -v

# 2. Start API server
python -m uvicorn backend.api.app:app --reload

# 3. Test endpoints
# Use: requests/phase4-consensus.http
```

---

## 📞 What Each Table Does

| Table | Purpose | Used By |
|-------|---------|---------|
| `sessions` | Group predictions into experiments | Pipeline, Dashboard |
| `consensus_results` | Store individual predictions | FastAPI, Supabase client |
| `weight_updates` | Track RWPV weight changes | Reputation system, Analytics |
| `agent_performance` | Summary statistics per agent | Dashboard, API responses |

---

## 🎯 After Setup

### You can:
✅ Save predictions to database  
✅ Track agent weights over time  
✅ Query prediction history  
✅ Analyze agent performance  
✅ Create visualization dashboards  

### Next phases:
→ Build Next.js frontend  
→ Add real-time WebSocket updates  
→ Implement analytics dashboard  

---

*Database setup takes ~2 minutes*  
*Your credentials are secure and validated* ✅
