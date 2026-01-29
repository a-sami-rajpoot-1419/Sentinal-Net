-- ============================================================================
-- SENTINEL-NET: FIX RLS SECURITY WARNINGS
-- ============================================================================
-- This script replaces overly permissive RLS policies with proper
-- authentication-based security policies
-- 
-- Run this in: psql or Supabase Dashboard SQL Editor
-- ============================================================================

-- ============================================================================
-- DROP OLD INSECURE POLICIES
-- ============================================================================

DROP POLICY IF EXISTS "Allow all access on sessions" ON sessions;
DROP POLICY IF EXISTS "Allow all access on consensus_results" ON consensus_results;
DROP POLICY IF EXISTS "Allow all access on weight_updates" ON weight_updates;
DROP POLICY IF EXISTS "Allow all access on agent_performance" ON agent_performance;

-- ============================================================================
-- CREATE NEW SECURE POLICIES
-- ============================================================================

-- ============================================================================
-- SESSIONS TABLE POLICIES
-- ============================================================================
-- Everyone (authenticated) can read sessions
CREATE POLICY "Sessions: Authenticated users can read" 
    ON sessions FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Only authenticated users can insert sessions
CREATE POLICY "Sessions: Authenticated users can create" 
    ON sessions FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- Only authenticated users can update sessions
CREATE POLICY "Sessions: Authenticated users can update" 
    ON sessions FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- ============================================================================
-- CONSENSUS RESULTS TABLE POLICIES
-- ============================================================================
-- Everyone (authenticated) can read consensus results
CREATE POLICY "Consensus: Authenticated users can read" 
    ON consensus_results FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Only authenticated users can insert new consensus results
CREATE POLICY "Consensus: Authenticated users can create" 
    ON consensus_results FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- ============================================================================
-- WEIGHT UPDATES TABLE POLICIES
-- ============================================================================
-- Everyone (authenticated) can read weight updates
CREATE POLICY "WeightUpdates: Authenticated users can read" 
    ON weight_updates FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Only authenticated users can insert weight updates
CREATE POLICY "WeightUpdates: Authenticated users can create" 
    ON weight_updates FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- ============================================================================
-- AGENT PERFORMANCE TABLE POLICIES
-- ============================================================================
-- Everyone (authenticated) can read agent performance metrics
CREATE POLICY "AgentPerf: Authenticated users can read" 
    ON agent_performance FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Only authenticated users can update agent performance
CREATE POLICY "AgentPerf: Authenticated users can update" 
    ON agent_performance FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- Only authenticated users can insert agent performance
CREATE POLICY "AgentPerf: Authenticated users can create" 
    ON agent_performance FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Check that all RLS policies are now in place

SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('sessions', 'consensus_results', 'weight_updates', 'agent_performance')
ORDER BY tablename, policyname;

-- ============================================================================
-- COMPLETE: All RLS policies have been updated
-- ============================================================================
