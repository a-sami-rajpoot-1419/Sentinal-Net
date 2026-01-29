"""
Phase 8: Database Schema Creation for Sentinel-Net

This module contains SQL migration scripts to create missing database tables:
1. problems - SMS messages to classify
2. votes - Individual agent votes on problems  
3. agents - Agent metadata and performance tracking
4. experiments - Batch experiment runs

All tables include RLS (Row Level Security) policies for access control.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

# ==================== PROBLEMS TABLE ====================
CREATE_PROBLEMS_TABLE = """
CREATE TABLE IF NOT EXISTS public.problems (
    problem_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_raw TEXT NOT NULL,
    text_clean TEXT,
    ground_truth INTEGER CHECK (ground_truth IN (0, 1)),
    consensus_decision INTEGER CHECK (consensus_decision IN (0, 1)),
    consensus_confidence DECIMAL(5, 4),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_problems_timestamp ON public.problems(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_problems_ground_truth ON public.problems(ground_truth);
"""

# ==================== VOTES TABLE ====================
CREATE_VOTES_TABLE = """
CREATE TABLE IF NOT EXISTS public.votes (
    vote_id BIGSERIAL PRIMARY KEY,
    problem_id UUID NOT NULL REFERENCES public.problems(problem_id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    prediction INTEGER NOT NULL CHECK (prediction IN (0, 1)),
    confidence DECIMAL(5, 4),
    reasoning TEXT,
    weight_at_time DECIMAL(10, 6),
    is_correct BOOLEAN,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for queries
CREATE INDEX IF NOT EXISTS idx_votes_problem_id ON public.votes(problem_id);
CREATE INDEX IF NOT EXISTS idx_votes_agent_id ON public.votes(agent_id);
CREATE INDEX IF NOT EXISTS idx_votes_timestamp ON public.votes(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_votes_is_correct ON public.votes(is_correct);

-- Unique constraint: one vote per agent per problem
CREATE UNIQUE INDEX IF NOT EXISTS idx_votes_unique_agent_problem 
    ON public.votes(problem_id, agent_id);
"""

# ==================== AGENTS TABLE ====================
CREATE_AGENTS_TABLE = """
CREATE TABLE IF NOT EXISTS public.agents (
    agent_id TEXT PRIMARY KEY,
    model_type TEXT NOT NULL,
    agent_name TEXT,
    current_weight DECIMAL(10, 6) DEFAULT 1.0,
    total_votes BIGINT DEFAULT 0,
    correct_votes BIGINT DEFAULT 0,
    accuracy DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_agents_model_type ON public.agents(model_type);
"""

# ==================== EXPERIMENTS TABLE ====================
CREATE_EXPERIMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS public.experiments (
    experiment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name TEXT,
    num_rounds INTEGER,
    dataset_name TEXT,
    consensus_accuracy DECIMAL(5, 4),
    consensus_confidence DECIMAL(5, 4),
    num_problems INTEGER,
    num_spam INTEGER,
    num_ham INTEGER,
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_experiments_created_at ON public.experiments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_experiments_dataset ON public.experiments(dataset_name);
"""

# ==================== RLS POLICIES ====================
# Note: RLS policies depend on your auth setup (users table)
# Adjust user_id references to match your actual user_id column

# Problems RLS
RLS_PROBLEMS = """
-- Allow authenticated users to view all problems
CREATE POLICY "problems_select_authenticated"
    ON public.problems
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Allow authenticated users to insert problems
CREATE POLICY "problems_insert_authenticated"
    ON public.problems
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Allow users to update their own problems
CREATE POLICY "problems_update_own"
    ON public.problems
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.sessions
            WHERE sessions.id = auth.uid()
            AND sessions.status = 'active'
        )
    )
    WITH CHECK (auth.role() = 'authenticated');
"""

# Votes RLS
RLS_VOTES = """
-- Allow authenticated users to view all votes
CREATE POLICY "votes_select_authenticated"
    ON public.votes
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Allow authenticated users to insert votes
CREATE POLICY "votes_insert_authenticated"
    ON public.votes
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Prevent deletion of votes (audit trail)
CREATE POLICY "votes_prevent_delete"
    ON public.votes
    FOR DELETE
    USING (false);
"""

# Agents RLS
RLS_AGENTS = """
-- Allow all users to view agent statistics
CREATE POLICY "agents_select_public"
    ON public.agents
    FOR SELECT
    USING (true);

-- Only admin can insert/update agents
CREATE POLICY "agents_insert_admin"
    ON public.agents
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.sessions
            WHERE sessions.id = auth.uid()
            AND sessions.role = 'admin'
        )
    );

CREATE POLICY "agents_update_admin"
    ON public.agents
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.sessions
            WHERE sessions.id = auth.uid()
            AND sessions.role = 'admin'
        )
    );
"""

# Experiments RLS
RLS_EXPERIMENTS = """
-- Allow authenticated users to view all experiments
CREATE POLICY "experiments_select_authenticated"
    ON public.experiments
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Allow authenticated users to create experiments
CREATE POLICY "experiments_insert_authenticated"
    ON public.experiments
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Allow users to update their own experiments
CREATE POLICY "experiments_update_own"
    ON public.experiments
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');
"""

# ==================== MIGRATION ORDER ====================
MIGRATION_ORDER = [
    ("Create problems table", CREATE_PROBLEMS_TABLE),
    ("Create votes table", CREATE_VOTES_TABLE),
    ("Create agents table", CREATE_AGENTS_TABLE),
    ("Create experiments table", CREATE_EXPERIMENTS_TABLE),
    ("Enable RLS on problems", "ALTER TABLE public.problems ENABLE ROW LEVEL SECURITY;"),
    ("Enable RLS on votes", "ALTER TABLE public.votes ENABLE ROW LEVEL SECURITY;"),
    ("Enable RLS on agents", "ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;"),
    ("Enable RLS on experiments", "ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;"),
]

# ==================== HELPER FUNCTION ====================
def get_migration_script() -> str:
    """
    Get the complete migration script as a single string.
    
    Returns:
        str: All SQL statements for creating tables and RLS policies
    """
    lines = [
        "-- ==================== PHASE 8: DATABASE SCHEMA MIGRATION ====================",
        "-- This script creates all missing tables for Sentinel-Net",
        "-- Run this in Supabase SQL Editor",
        "",
    ]
    
    # Add table creation statements
    lines.append("-- ==================== CREATE TABLES ====================")
    lines.append(CREATE_PROBLEMS_TABLE)
    lines.append("\n")
    lines.append(CREATE_VOTES_TABLE)
    lines.append("\n")
    lines.append(CREATE_AGENTS_TABLE)
    lines.append("\n")
    lines.append(CREATE_EXPERIMENTS_TABLE)
    lines.append("\n")
    
    # Add RLS enablement
    lines.append("-- ==================== ENABLE ROW LEVEL SECURITY ====================")
    lines.append("ALTER TABLE public.problems ENABLE ROW LEVEL SECURITY;")
    lines.append("ALTER TABLE public.votes ENABLE ROW LEVEL SECURITY;")
    lines.append("ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;")
    lines.append("ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;")
    lines.append("\n")
    
    # Add RLS policies
    lines.append("-- ==================== CREATE RLS POLICIES ====================")
    lines.append("-- Note: Adjust based on your actual auth setup")
    lines.append("")
    
    return "\n".join(lines)
