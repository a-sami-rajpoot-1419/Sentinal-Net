# PHASE 8: DATABASE SCHEMA CREATION

**Status:** ✅ COMPLETE (SQL Migration Scripts Ready)  
**Date:** January 29, 2026  
**Version:** 0.8.0

---

## 🎯 OBJECTIVE

Create missing database tables in Supabase PostgreSQL to support storing predictions, votes, agent metrics, and experiments.

**Key Deliverables:**
1. ✅ 4 new database tables with proper schemas
2. ✅ RLS (Row Level Security) policies on all tables
3. ✅ Indexes for query optimization
4. ✅ Foreign key relationships
5. ✅ Python migration utilities
6. ✅ SQL migration script ready to execute
7. ✅ Database initialization module

---

## 📊 DATABASE SCHEMA

### 1. `problems` Table
Stores SMS messages and their consensus classification results.

```sql
CREATE TABLE problems (
    problem_id UUID PRIMARY KEY,
    text_raw TEXT NOT NULL,
    text_clean TEXT,
    ground_truth INTEGER (0/1),
    consensus_decision INTEGER (0/1),
    consensus_confidence DECIMAL(0-1),
    timestamp TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Purpose:** Store SMS messages to be classified  
**Rows:** One per SMS  
**Key Fields:**
- `problem_id` - UUID, unique identifier
- `text_raw` - Original SMS text
- `ground_truth` - Actual label (0=ham, 1=spam) from dataset
- `consensus_decision` - Final prediction from consensus engine
- `consensus_confidence` - Confidence of consensus decision

**Indexes:**
- `idx_problems_timestamp` - For time-based queries
- `idx_problems_ground_truth` - For accuracy calculations
- `idx_problems_created_at` - For recent problems

---

### 2. `votes` Table
Stores individual agent votes on each problem.

```sql
CREATE TABLE votes (
    vote_id BIGSERIAL PRIMARY KEY,
    problem_id UUID REFERENCES problems,
    agent_id TEXT NOT NULL,
    prediction INTEGER (0/1),
    confidence DECIMAL(0-1),
    reasoning TEXT,
    weight_at_time DECIMAL,
    is_correct BOOLEAN,
    timestamp TIMESTAMP,
    created_at TIMESTAMP
);
```

**Purpose:** Store individual agent predictions for deliberation analysis  
**Rows:** 4 per problem (one per agent)  
**Key Fields:**
- `vote_id` - Unique vote identifier
- `problem_id` - Foreign key to problems table
- `agent_id` - Which agent voted (e.g., 'agent_nb', 'agent_svm', 'agent_rf', 'agent_lr')
- `prediction` - Agent's prediction (0 or 1)
- `confidence` - Agent's confidence score
- `weight_at_time` - Agent's reputation weight when vote was cast
- `is_correct` - Whether agent's prediction matched ground truth

**Constraints:**
- One vote per agent per problem (unique constraint on problem_id + agent_id)
- Foreign key to problems table (cascade delete)

**Indexes:**
- `idx_votes_problem_id` - Find all votes for a problem
- `idx_votes_agent_id` - Find all votes by an agent
- `idx_votes_timestamp` - Time-based queries
- `idx_votes_is_correct` - Find correct/incorrect votes
- `idx_votes_unique_agent_problem` - Enforce one vote per agent-problem

---

### 3. `agents` Table
Stores agent metadata and performance statistics.

```sql
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    model_type TEXT NOT NULL,
    agent_name TEXT,
    current_weight DECIMAL,
    total_votes BIGINT DEFAULT 0,
    correct_votes BIGINT DEFAULT 0,
    accuracy DECIMAL(0-1),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata JSONB
);
```

**Purpose:** Track agent performance and weights  
**Rows:** 4 (one per agent: NB, SVM, RF, LR)  
**Key Fields:**
- `agent_id` - Primary key (e.g., 'agent_nb', 'agent_svm')
- `model_type` - Type of model ('naive_bayes', 'svm', 'random_forest', 'logistic_regression')
- `current_weight` - Current reputation weight (starts at 1.0)
- `total_votes` - Lifetime vote count
- `correct_votes` - Lifetime correct predictions
- `accuracy` - Current accuracy (correct_votes / total_votes)
- `metadata` - JSON for extensibility (model hyperparams, training details, etc.)

**Indexes:**
- `idx_agents_model_type` - Find agents by model type

**Initial Data:**
The app should initialize this table with 4 rows on first run:
```
agent_id | model_type        | current_weight | total_votes | correct_votes
---------|-------------------|----------------|-------------|---------------
agent_nb | naive_bayes       | 1.0            | 0           | 0
agent_svm| svm               | 1.0            | 0           | 0
agent_rf | random_forest     | 1.0            | 0           | 0
agent_lr | logistic_regression | 1.0          | 0           | 0
```

---

### 4. `experiments` Table
Stores batch experiment runs and their results.

```sql
CREATE TABLE experiments (
    experiment_id UUID PRIMARY KEY,
    experiment_name TEXT,
    num_rounds INTEGER,
    dataset_name TEXT,
    consensus_accuracy DECIMAL(0-1),
    consensus_confidence DECIMAL(0-1),
    num_problems INTEGER,
    num_spam INTEGER,
    num_ham INTEGER,
    results JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Purpose:** Store results from batch experiment runs  
**Rows:** One per experiment run  
**Key Fields:**
- `experiment_id` - UUID, unique identifier
- `experiment_name` - Human-readable name
- `num_rounds` - Number of predictions made
- `dataset_name` - Which dataset was used
- `consensus_accuracy` - Overall consensus engine accuracy
- `num_spam` - Number of spam messages in dataset
- `num_ham` - Number of ham (legitimate) messages
- `results` - JSON with full results (agent accuracies, weight evolution, etc.)

**Indexes:**
- `idx_experiments_created_at` - Recent experiments
- `idx_experiments_dataset` - Find experiments by dataset

---

## 🔐 ROW LEVEL SECURITY (RLS) POLICIES

All tables have RLS enabled for multi-tenant safety.

### Simple Policies (Current)
```sql
-- PROBLEMS
- SELECT: Allow all (true)
- INSERT: Allow all (true)
- UPDATE: Allow all (true)

-- VOTES
- SELECT: Allow all (true)
- INSERT: Allow all (true)
- DELETE: Deny all (false) -- Audit trail, prevent deletion

-- AGENTS
- SELECT: Allow all (true)
- INSERT: Allow all (true)
- UPDATE: Allow all (true)

-- EXPERIMENTS
- SELECT: Allow all (true)
- INSERT: Allow all (true)
- UPDATE: Allow all (true)
```

**Note:** These are permissive for development. In production, restrict based on:
- Authentication: `auth.role() = 'authenticated'`
- User ownership: Compare to `auth.uid()`
- Admin roles: Check user's role in sessions table

---

## 📋 FILE STRUCTURE

### New Files Created

1. **`backend/db/migrations.py`** (310+ lines)
   - SQL migration statements as Python strings
   - `MIGRATION_ORDER` - Ordered list of migrations
   - `get_migration_script()` - Combine all statements

2. **`backend/db/initializer.py`** (220+ lines)
   - `DatabaseInitializer` class
   - `get_migration_statements()` - Returns ordered list
   - `get_migration_script()` - Full migration as string
   - `validate_schema()` - Check table existence
   - `log_schema_info()` - Print schema info

3. **`database/migrations/001_create_schema.sql`** (290+ lines)
   - Complete SQL migration script
   - Ready to copy-paste into Supabase SQL Editor
   - Includes all tables, indexes, and RLS policies

---

## 🚀 HOW TO APPLY THIS MIGRATION

### Option 1: Supabase Dashboard (Easiest)

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project
3. Click "SQL Editor" in left sidebar
4. Click "New Query"
5. Copy entire contents of `database/migrations/001_create_schema.sql`
6. Paste into editor
7. Click "Run"
8. Verify: Check "Table editor" to see 4 new tables

### Option 2: Python Script (When Ready)

```python
from backend.db.initializer import DatabaseInitializer

# Get the SQL script
script = DatabaseInitializer.get_migration_script()

# Execute with Supabase client (Phase 9)
supabase.execute(script)
```

### Option 3: Database URL (psql command)

```bash
psql postgres://user:password@db.supabase.co:5432/postgres < database/migrations/001_create_schema.sql
```

---

## ✅ VERIFICATION CHECKLIST

After running the migration, verify:

- [ ] `problems` table exists with 9 columns
- [ ] `votes` table exists with 11 columns
- [ ] `agents` table exists with 10 columns
- [ ] `experiments` table exists with 12 columns
- [ ] All indexes created successfully
- [ ] RLS is enabled on all 4 tables
- [ ] Foreign key constraint exists: votes.problem_id → problems.problem_id
- [ ] Unique constraint exists: votes(problem_id, agent_id)

**To verify in Supabase SQL Editor:**

```sql
-- Check tables exist
SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;

-- Check RLS status
SELECT schemaname, tablename, rowsecurity FROM pg_tables 
WHERE schemaname='public' AND tablename IN ('problems', 'votes', 'agents', 'experiments');

-- Check indexes
SELECT indexname FROM pg_indexes WHERE schemaname='public' ORDER BY indexname;

-- Check RLS policies
SELECT policyname, tablename FROM pg_policies WHERE schemaname='public' ORDER BY tablename;
```

---

## 🔗 DATA RELATIONSHIPS

```
problems
├── problem_id (PK, UUID)
├── text_raw
├── ground_truth
├── consensus_decision
└── consensus_confidence

votes (4 rows per problem)
├── vote_id (PK)
├── problem_id (FK → problems.problem_id)
├── agent_id (references agents.agent_id)
├── prediction
├── confidence
└── weight_at_time

agents (4 rows total)
├── agent_id (PK) ← referenced by votes.agent_id
├── model_type
├── current_weight
├── total_votes
└── accuracy

experiments
├── experiment_id (PK, UUID)
├── num_problems
├── consensus_accuracy
└── results (JSONB)
```

---

## 📊 EXAMPLE DATA

### Problems Table
```
| problem_id | text_raw | ground_truth | consensus_decision |
|------------|----------|--------------|-------------------|
| uuid-001   | "Free iPhone!" | 1 (spam) | 1 (spam) |
| uuid-002   | "Meeting at 3pm" | 0 (ham) | 0 (ham) |
```

### Votes Table
```
| vote_id | problem_id | agent_id | prediction | confidence | weight_at_time |
|---------|------------|----------|------------|------------|----------------|
| 1 | uuid-001 | agent_nb | 1 | 0.92 | 1.0 |
| 2 | uuid-001 | agent_svm | 1 | 0.88 | 1.0 |
| 3 | uuid-001 | agent_rf | 1 | 0.95 | 1.0 |
| 4 | uuid-001 | agent_lr | 1 | 0.85 | 1.0 |
```

### Agents Table
```
| agent_id | model_type | current_weight | total_votes | correct_votes | accuracy |
|----------|------------|----------------|-------------|---------------|----------|
| agent_nb | naive_bayes | 1.0 | 100 | 85 | 0.85 |
| agent_svm | svm | 1.05 | 100 | 92 | 0.92 |
| agent_rf | random_forest | 1.08 | 100 | 94 | 0.94 |
| agent_lr | logistic_regression | 0.95 | 100 | 80 | 0.80 |
```

---

## 🔄 NEXT PHASE: PHASE 9

After this migration runs:
1. API needs code to persist predictions to `problems` table
2. Consensus engine votes stored in `votes` table
3. Weight updates stored in `agents` table
4. Experiments stored in `experiments` table

---

## 📝 PHASE 8 CHECKLIST

- ✅ Created `problems` table (SMS storage)
- ✅ Created `votes` table (Agent votes)
- ✅ Created `agents` table (Agent metadata)
- ✅ Created `experiments` table (Experiment results)
- ✅ Added RLS policies to all tables
- ✅ Created indexes for performance
- ✅ Created foreign key constraints
- ✅ Created Python migration module
- ✅ Created Python initializer module
- ✅ Created SQL migration script
- ✅ Documentation complete
- ✅ Verification guide included

---

## 📚 FILES CHANGED

| File | Type | Size | Purpose |
|------|------|------|---------|
| `backend/db/migrations.py` | NEW | 310+ | SQL statements as Python |
| `backend/db/initializer.py` | NEW | 220+ | Migration execution helper |
| `database/migrations/001_create_schema.sql` | NEW | 290+ | Ready-to-execute SQL |

---

## ⚠️ IMPORTANT NOTES

1. **RLS Policies:** Current policies are permissive for development. Tighten before production.
2. **Indexes:** Optimized for common queries (timestamp-based, agent-based). Add more if needed.
3. **JSONB Field:** `experiments.results` can store complex data (agent accuracies, weight evolution, etc.)
4. **Cascade Delete:** Deleting a problem automatically deletes all its votes (referential integrity)
5. **Audit Trail:** Votes cannot be deleted (RLS policy prevents deletion) for audit trail

---

**Status:** Ready for Phase 9 (Connect Consensus to Predict Endpoint)
