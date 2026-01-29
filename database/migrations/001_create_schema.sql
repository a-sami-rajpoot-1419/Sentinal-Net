-- ==================== PHASE 8: DATABASE SCHEMA MIGRATION ====================
-- Sentinel-Net Database Setup
-- 
-- This script creates all necessary tables for the Sentinel-Net consensus engine.
-- Run this in Supabase SQL Editor (https://supabase.com/dashboard)
--
-- Tables:
-- 1. problems - SMS messages to classify
-- 2. votes - Individual agent votes on problems
-- 3. agents - Agent metadata and performance tracking
-- 4. experiments - Batch experiment runs
--
-- All tables include RLS (Row Level Security) policies
-- Date: 2026-01-29

-- ==================== CREATE PROBLEMS TABLE ====================
-- Stores SMS messages and their consensus classification results

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

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_problems_timestamp ON public.problems(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_problems_ground_truth ON public.problems(ground_truth);
CREATE INDEX IF NOT EXISTS idx_problems_created_at ON public.problems(created_at DESC);

-- ==================== CREATE VOTES TABLE ====================
-- Stores individual agent votes on each problem

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

-- Create indexes for queries
CREATE INDEX IF NOT EXISTS idx_votes_problem_id ON public.votes(problem_id);
CREATE INDEX IF NOT EXISTS idx_votes_agent_id ON public.votes(agent_id);
CREATE INDEX IF NOT EXISTS idx_votes_timestamp ON public.votes(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_votes_is_correct ON public.votes(is_correct);

-- Unique constraint: one vote per agent per problem
CREATE UNIQUE INDEX IF NOT EXISTS idx_votes_unique_agent_problem 
    ON public.votes(problem_id, agent_id);

-- ==================== CREATE AGENTS TABLE ====================
-- Stores agent metadata and performance statistics

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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_agents_model_type ON public.agents(model_type);

-- ==================== CREATE EXPERIMENTS TABLE ====================
-- Stores batch experiment runs and results

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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_experiments_created_at ON public.experiments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_experiments_dataset ON public.experiments(dataset_name);

-- ==================== ENABLE ROW LEVEL SECURITY ====================

ALTER TABLE public.problems ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;

-- ==================== CREATE RLS POLICIES ====================

-- PROBLEMS POLICIES
CREATE POLICY "problems_select"
    ON public.problems
    FOR SELECT
    USING (true);

CREATE POLICY "problems_insert"
    ON public.problems
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "problems_update"
    ON public.problems
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- VOTES POLICIES
CREATE POLICY "votes_select"
    ON public.votes
    FOR SELECT
    USING (true);

CREATE POLICY "votes_insert"
    ON public.votes
    FOR INSERT
    WITH CHECK (true);

-- Prevent deletion of votes (audit trail)
CREATE POLICY "votes_no_delete"
    ON public.votes
    FOR DELETE
    USING (false);

-- AGENTS POLICIES
CREATE POLICY "agents_select"
    ON public.agents
    FOR SELECT
    USING (true);

CREATE POLICY "agents_insert"
    ON public.agents
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "agents_update"
    ON public.agents
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- EXPERIMENTS POLICIES
CREATE POLICY "experiments_select"
    ON public.experiments
    FOR SELECT
    USING (true);

CREATE POLICY "experiments_insert"
    ON public.experiments
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "experiments_update"
    ON public.experiments
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- ==================== VERIFY TABLES ====================
-- Check that all tables were created

SELECT 
    schemaname,
    tablename,
    (SELECT count(*) FROM information_schema.columns WHERE table_schema=schemaname AND table_name=tablename) as column_count
FROM pg_tables
WHERE schemaname = 'public' 
AND tablename IN ('problems', 'votes', 'agents', 'experiments')
ORDER BY tablename;
