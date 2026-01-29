-- ============================================================================
-- SENTINEL-NET: COMPLETE RLS POLICY CLEANUP & RECREATION
-- ============================================================================
-- This script safely removes all RLS policies and recreates them fresh
-- Run this in: Supabase Dashboard SQL Editor
-- ============================================================================

-- ============================================================================
-- STEP 1: DROP ALL EXISTING POLICIES (regardless of name)
-- ============================================================================

-- Sessions table - drop all policies
DROP POLICY IF EXISTS "Sessions: Authenticated users can read" ON sessions;
DROP POLICY IF EXISTS "Sessions: Authenticated users can create" ON sessions;
DROP POLICY IF EXISTS "Sessions: Authenticated users can update" ON sessions;
DROP POLICY IF EXISTS "Allow all access on sessions" ON sessions;

-- Consensus Results table - drop all policies
DROP POLICY IF EXISTS "Consensus: Authenticated users can read" ON consensus_results;
DROP POLICY IF EXISTS "Consensus: Authenticated users can create" ON consensus_results;
DROP POLICY IF EXISTS "Allow all access on consensus_results" ON consensus_results;

-- Weight Updates table - drop all policies
DROP POLICY IF EXISTS "WeightUpdates: Authenticated users can read" ON weight_updates;
DROP POLICY IF EXISTS "WeightUpdates: Authenticated users can create" ON weight_updates;
DROP POLICY IF EXISTS "Allow all access on weight_updates" ON weight_updates;

-- Agent Performance table - drop all policies
DROP POLICY IF EXISTS "AgentPerf: Authenticated users can read" ON agent_performance;
DROP POLICY IF EXISTS "AgentPerf: Authenticated users can update" ON agent_performance;
DROP POLICY IF EXISTS "AgentPerf: Authenticated users can create" ON agent_performance;
DROP POLICY IF EXISTS "Allow all access on agent_performance" ON agent_performance;

-- ============================================================================
-- STEP 2: CREATE NEW SECURE POLICIES
-- ============================================================================

-- ============================================================================
-- SESSIONS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Sessions: Authenticated users can read" 
    ON sessions FOR SELECT 
    USING (auth.role() = 'authenticated');

CREATE POLICY "Sessions: Authenticated users can create" 
    ON sessions FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated' AND auth.uid() IS NOT NULL);

CREATE POLICY "Sessions: Authenticated users can update" 
    ON sessions FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- ============================================================================
-- CONSENSUS RESULTS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Consensus: Authenticated users can read" 
    ON consensus_results FOR SELECT 
    USING (auth.role() = 'authenticated');

CREATE POLICY "Consensus: Authenticated users can create" 
    ON consensus_results FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated' AND auth.uid() IS NOT NULL);

-- ============================================================================
-- WEIGHT UPDATES TABLE POLICIES
-- ============================================================================
CREATE POLICY "WeightUpdates: Authenticated users can read" 
    ON weight_updates FOR SELECT 
    USING (auth.role() = 'authenticated');

CREATE POLICY "WeightUpdates: Authenticated users can create" 
    ON weight_updates FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated' AND auth.uid() IS NOT NULL);

-- ============================================================================
-- AGENT PERFORMANCE TABLE POLICIES
-- ============================================================================
CREATE POLICY "AgentPerf: Authenticated users can read" 
    ON agent_performance FOR SELECT 
    USING (auth.role() = 'authenticated');

CREATE POLICY "AgentPerf: Authenticated users can update" 
    ON agent_performance FOR UPDATE 
    USING (auth.role() = 'authenticated');

CREATE POLICY "AgentPerf: Authenticated users can create" 
    ON agent_performance FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated' AND auth.uid() IS NOT NULL);

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Check that all RLS policies are now in place (should show 10 rows)

SELECT 
    tablename,
    policyname,
    cmd,
    CASE WHEN qual IS NULL THEN 'No USING clause' ELSE qual END as policy_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('sessions', 'consensus_results', 'weight_updates', 'agent_performance')
ORDER BY tablename, policyname;

-- ============================================================================
-- SUCCESS: All RLS policies have been recreated
-- You should see 10 policies in the verification query above
-- ============================================================================
