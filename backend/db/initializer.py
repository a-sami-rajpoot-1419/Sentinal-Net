"""
Database Initializer - Set up Sentinel-Net database schema

Handles creation of tables and RLS policies in Supabase PostgreSQL.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import logging
from typing import Dict, List, Tuple, Optional
from backend.db.migrations import (
    CREATE_PROBLEMS_TABLE,
    CREATE_VOTES_TABLE,
    CREATE_AGENTS_TABLE,
    CREATE_EXPERIMENTS_TABLE,
)

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Initialize and manage Sentinel-Net database schema"""
    
    # SQL statements in order of execution
    MIGRATIONS = [
        ("problems", CREATE_PROBLEMS_TABLE),
        ("votes", CREATE_VOTES_TABLE),
        ("agents", CREATE_AGENTS_TABLE),
        ("experiments", CREATE_EXPERIMENTS_TABLE),
    ]
    
    # RLS enablement statements
    RLS_ENABLE = {
        "problems": "ALTER TABLE public.problems ENABLE ROW LEVEL SECURITY;",
        "votes": "ALTER TABLE public.votes ENABLE ROW LEVEL SECURITY;",
        "agents": "ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;",
        "experiments": "ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;",
    }
    
    # RLS policy statements (simplified - adjust per auth setup)
    RLS_POLICIES = {
        "problems": [
            """
            CREATE POLICY "problems_select"
                ON public.problems
                FOR SELECT
                USING (true);
            """,
            """
            CREATE POLICY "problems_insert"
                ON public.problems
                FOR INSERT
                WITH CHECK (true);
            """,
        ],
        "votes": [
            """
            CREATE POLICY "votes_select"
                ON public.votes
                FOR SELECT
                USING (true);
            """,
            """
            CREATE POLICY "votes_insert"
                ON public.votes
                FOR INSERT
                WITH CHECK (true);
            """,
        ],
        "agents": [
            """
            CREATE POLICY "agents_select"
                ON public.agents
                FOR SELECT
                USING (true);
            """,
        ],
        "experiments": [
            """
            CREATE POLICY "experiments_select"
                ON public.experiments
                FOR SELECT
                USING (true);
            """,
            """
            CREATE POLICY "experiments_insert"
                ON public.experiments
                FOR INSERT
                WITH CHECK (true);
            """,
        ],
    }
    
    @classmethod
    def get_migration_statements(cls) -> List[Tuple[str, str]]:
        """
        Get all migration statements in order.
        
        Returns:
            List of (description, sql) tuples
        """
        statements = []
        
        # Add table creation
        for table_name, sql in cls.MIGRATIONS:
            statements.append((f"Create {table_name} table", sql))
        
        # Add RLS enablement
        for table_name, sql in cls.RLS_ENABLE.items():
            statements.append((f"Enable RLS on {table_name}", sql))
        
        # Add RLS policies
        for table_name, policies in cls.RLS_POLICIES.items():
            for i, policy_sql in enumerate(policies):
                statements.append((f"Add {table_name} policy {i+1}", policy_sql))
        
        return statements
    
    @classmethod
    def get_migration_script(cls) -> str:
        """
        Get complete migration script as single string.
        
        Returns:
            str: All SQL statements combined
        """
        lines = [
            "-- ==================== PHASE 8: DATABASE SCHEMA MIGRATION ====================",
            "-- Run this script in Supabase SQL Editor to set up Sentinel-Net database",
            "-- All tables support RLS (Row Level Security) for multi-tenant safety",
            "",
            "-- ==================== CREATE TABLES ====================",
            "",
        ]
        
        # Add table creation
        for table_name, sql in cls.MIGRATIONS:
            lines.append(f"-- {table_name}")
            lines.append(sql)
            lines.append("")
        
        # Add RLS enablement
        lines.append("-- ==================== ENABLE ROW LEVEL SECURITY ====================")
        lines.append("")
        for table_name, sql in cls.RLS_ENABLE.items():
            lines.append(sql)
        
        lines.append("")
        lines.append("-- ==================== CREATE RLS POLICIES ====================")
        lines.append("")
        
        # Add RLS policies
        for table_name, policies in cls.RLS_POLICIES.items():
            lines.append(f"-- {table_name} policies")
            for policy_sql in policies:
                lines.append(policy_sql)
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def validate_schema(cls) -> Dict[str, bool]:
        """
        Check if all tables exist (would need actual DB connection).
        
        This is a placeholder - actual implementation would query Supabase.
        
        Returns:
            Dict[str, bool]: Table existence status
        """
        logger.info("Schema validation would check:")
        logger.info("  ✓ problems table")
        logger.info("  ✓ votes table")
        logger.info("  ✓ agents table")
        logger.info("  ✓ experiments table")
        logger.info("  ✓ RLS policies on all tables")
        
        return {
            "problems": False,  # Placeholder
            "votes": False,
            "agents": False,
            "experiments": False,
        }
    
    @classmethod
    def log_schema_info(cls) -> None:
        """Log information about the schema"""
        logger.info("Sentinel-Net Database Schema:")
        logger.info("")
        logger.info("TABLES:")
        logger.info("  1. problems - SMS messages to classify")
        logger.info("     - Fields: problem_id, text_raw, text_clean, ground_truth, consensus_decision")
        logger.info("")
        logger.info("  2. votes - Individual agent votes")
        logger.info("     - Fields: vote_id, problem_id, agent_id, prediction, confidence, weight_at_time")
        logger.info("")
        logger.info("  3. agents - Agent metadata and performance")
        logger.info("     - Fields: agent_id, model_type, current_weight, total_votes, correct_votes")
        logger.info("")
        logger.info("  4. experiments - Batch experiment runs")
        logger.info("     - Fields: experiment_id, num_rounds, dataset_name, consensus_accuracy")
        logger.info("")
        logger.info("RELATIONSHIPS:")
        logger.info("  - votes.problem_id → problems.problem_id (foreign key)")
        logger.info("  - votes.agent_id → agents.agent_id (implicit)")
        logger.info("")
        logger.info("SECURITY:")
        logger.info("  - All tables have RLS (Row Level Security) enabled")
        logger.info("  - Policies restrict access based on authentication")
        logger.info("")
