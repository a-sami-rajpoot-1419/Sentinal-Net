-- ============================================================================
-- SENTINEL-NET PHASE 4: SUPABASE DATABASE SCHEMA
-- ============================================================================
-- 
-- Copy and paste this entire SQL into Supabase Dashboard:
-- 1. Go to: https://supabase.com/dashboard
-- 2. Select your project: jfhbgfpuusvlreucjvmf
-- 3. SQL Editor (top menu) → New Query
-- 4. Paste this entire script
-- 5. Click "Run" button
--
-- ============================================================================

-- ============================================================================
-- 1. SESSIONS TABLE - Track consensus experiments/sessions
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_name TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC);

-- ============================================================================
-- 2. CONSENSUS RESULTS TABLE - Store individual predictions
-- ============================================================================
CREATE TABLE IF NOT EXISTS consensus_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE NOT NULL,
    sample_id INTEGER NOT NULL,
    predicted_class INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    agent_predictions JSONB NOT NULL,  -- {agent_name: {class: int, confidence: float}}
    agent_weights JSONB NOT NULL,      -- {agent_name: weight_value}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_consensus_session ON consensus_results(session_id);
CREATE INDEX IF NOT EXISTS idx_consensus_created ON consensus_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_consensus_sample ON consensus_results(sample_id);

-- ============================================================================
-- 3. WEIGHT UPDATES TABLE - Track RWPV weight adjustments
-- ============================================================================
CREATE TABLE IF NOT EXISTS weight_updates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE NOT NULL,
    agent_name TEXT NOT NULL,
    previous_weight FLOAT NOT NULL,
    new_weight FLOAT NOT NULL,
    reason TEXT NOT NULL,  -- 'reward_correct', 'penalty_wrong', 'reward_minority', 'penalty_both_wrong'
    true_label INTEGER NOT NULL,
    predicted_label INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_weight_updates_session ON weight_updates(session_id);
CREATE INDEX IF NOT EXISTS idx_weight_updates_agent ON weight_updates(agent_name);
CREATE INDEX IF NOT EXISTS idx_weight_created ON weight_updates(created_at DESC);

-- ============================================================================
-- 4. AGENT PERFORMANCE TABLE - Aggregate agent statistics
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_name TEXT UNIQUE NOT NULL,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy FLOAT DEFAULT 0.0,
    confidence_avg FLOAT DEFAULT 0.0,
    current_weight FLOAT DEFAULT 1.0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for agent lookups
CREATE INDEX IF NOT EXISTS idx_agent_performance_name ON agent_performance(agent_name);

-- ============================================================================
-- 5. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Restrict access by user (configure in production)

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE consensus_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE weight_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_performance ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 6. ROW LEVEL SECURITY POLICIES
-- ============================================================================
-- Development: Allow all access
-- Production: Implement proper authentication-based policies

CREATE POLICY "Allow all access on sessions" 
    ON sessions FOR ALL 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Allow all access on consensus_results" 
    ON consensus_results FOR ALL 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Allow all access on weight_updates" 
    ON weight_updates FOR ALL 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Allow all access on agent_performance" 
    ON agent_performance FOR ALL 
    USING (true) 
    WITH CHECK (true);

-- ============================================================================
-- 7. INITIAL DATA (Optional)
-- ============================================================================
-- Insert initial agent performance records

INSERT INTO agent_performance (agent_name, total_predictions, correct_predictions, accuracy, confidence_avg, current_weight)
VALUES 
    ('naive_bayes', 0, 0, 0.0, 0.0, 1.0),
    ('svm', 0, 0, 0.0, 0.0, 1.0),
    ('random_forest', 0, 0, 0.0, 0.0, 1.0),
    ('logistic_regression', 0, 0, 0.0, 0.0, 1.0)
ON CONFLICT (agent_name) DO NOTHING;

-- ============================================================================
-- 8. VERIFICATION QUERIES (Run these to verify setup)
-- ============================================================================

-- List all tables
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Verify tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check table structure
-- \d sessions
-- \d consensus_results
-- \d weight_updates
-- \d agent_performance

-- Verify agent data
-- SELECT * FROM agent_performance;

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================
-- Tables created: sessions, consensus_results, weight_updates, agent_performance
-- Indexes created: 9 indexes for performance optimization
-- RLS enabled: All tables have row-level security enabled
-- Initial data: 4 agent records inserted
--
-- You can now:
-- 1. Test FastAPI endpoints
-- 2. Run predictions
-- 3. Update weights
-- 4. Query results from database
-- ============================================================================
