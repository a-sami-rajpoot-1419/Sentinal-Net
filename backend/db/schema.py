"""
Supabase Schema Initialization and Database Setup
"""

from backend.db.supabase_client import get_supabase_client
from typing import Dict, Any


def create_tables():
    """
    Create all necessary tables in Supabase
    
    Run this once during initial setup:
    ```python
    from backend.db.schema import create_tables
    create_tables()
    ```
    
    Or use Supabase SQL Editor with this SQL:
    """
    
    sql_schema = """
    -- Sessions table
    CREATE TABLE IF NOT EXISTS sessions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        session_name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- Consensus results table
    CREATE TABLE IF NOT EXISTS consensus_results (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
        sample_id INTEGER NOT NULL,
        predicted_class INTEGER NOT NULL,
        confidence FLOAT NOT NULL,
        agent_predictions JSONB NOT NULL,
        agent_weights JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        CONSTRAINT fk_session FOREIGN KEY(session_id) REFERENCES sessions(id)
    );

    -- Weight updates table (for RWPV tracking)
    CREATE TABLE IF NOT EXISTS weight_updates (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
        agent_name TEXT NOT NULL,
        previous_weight FLOAT NOT NULL,
        new_weight FLOAT NOT NULL,
        reason TEXT NOT NULL,  -- 'reward_correct', 'penalty_wrong', 'reward_minority', 'penalty_both_wrong'
        true_label INTEGER NOT NULL,
        predicted_label INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        CONSTRAINT fk_session FOREIGN KEY(session_id) REFERENCES sessions(id)
    );

    -- Agent performance table
    CREATE TABLE IF NOT EXISTS agent_performance (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        agent_name TEXT NOT NULL,
        total_predictions INTEGER DEFAULT 0,
        correct_predictions INTEGER DEFAULT 0,
        accuracy FLOAT DEFAULT 0.0,
        confidence_avg FLOAT DEFAULT 0.0,
        current_weight FLOAT DEFAULT 1.0,
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(agent_name)
    );

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_consensus_session ON consensus_results(session_id);
    CREATE INDEX IF NOT EXISTS idx_weight_updates_session ON weight_updates(session_id);
    CREATE INDEX IF NOT EXISTS idx_weight_updates_agent ON weight_updates(agent_name);
    CREATE INDEX IF NOT EXISTS idx_consensus_created ON consensus_results(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_weight_created ON weight_updates(created_at DESC);

    -- Enable Row Level Security (RLS)
    ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
    ALTER TABLE consensus_results ENABLE ROW LEVEL SECURITY;
    ALTER TABLE weight_updates ENABLE ROW LEVEL SECURITY;
    ALTER TABLE agent_performance ENABLE ROW LEVEL SECURITY;

    -- RLS Policies (allow all for now - adjust in production)
    CREATE POLICY "Allow all access" ON sessions FOR ALL USING (true);
    CREATE POLICY "Allow all access" ON consensus_results FOR ALL USING (true);
    CREATE POLICY "Allow all access" ON weight_updates FOR ALL USING (true);
    CREATE POLICY "Allow all access" ON agent_performance FOR ALL USING (true);
    """
    
    return sql_schema


def get_schema_instructions() -> str:
    """Get instructions for manual schema creation"""
    return """
    # Manual Supabase Schema Setup

    1. Go to Supabase Dashboard: https://supabase.com/dashboard
    2. Select your project
    3. Go to SQL Editor
    4. Create a new query
    5. Copy and paste the SQL from backend/db/schema.py::create_tables()
    6. Execute the query

    Or use the Python function:
    ```python
    from backend.db.schema import create_tables
    schema_sql = create_tables()
    # Copy and paste schema_sql into Supabase SQL Editor
    ```

    ## Table Descriptions

    ### sessions
    - Stores consensus sessions/experiments
    - Fields: id (UUID), session_name, description, created_at, updated_at

    ### consensus_results
    - Stores individual consensus predictions
    - Fields: id, session_id, sample_id, predicted_class, confidence, 
              agent_predictions (JSONB), agent_weights (JSONB), created_at

    ### weight_updates
    - Tracks RWPV weight changes for reputation system
    - Fields: id, session_id, agent_name, previous_weight, new_weight, 
              reason (reward/penalty), true_label, predicted_label, created_at

    ### agent_performance
    - Aggregate performance metrics by agent
    - Fields: id, agent_name, total_predictions, correct_predictions, 
              accuracy, confidence_avg, current_weight, updated_at

    ## Row Level Security (RLS)
    - Currently allows all access
    - In production, implement proper auth-based policies
    """


def print_schema():
    """Print schema SQL and instructions"""
    print(create_tables())
    print("\n\n")
    print(get_schema_instructions())
