"""
Supabase PostgreSQL Database Integration
Handles all database operations for Sentinel-Net consensus logs and results
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    from psycopg2.pool import SimpleConnectionPool
except ImportError:
    psycopg2 = None

logger = logging.getLogger(__name__)


class SupabaseDB:
    """
    PostgreSQL database connection pool for Supabase
    Manages all consensus logs, votes, experiments, and metrics
    """

    def __init__(self):
        """Initialize database connection pool"""
        if not psycopg2:
            raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")

        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/sentinel"
        )

        self.min_connections = 2
        self.max_connections = 10

        try:
            self.connection_pool = SimpleConnectionPool(
                self.min_connections,
                self.max_connections,
                self.db_url,
                connect_timeout=10,
            )
            logger.info("✓ Supabase connection pool initialized")
        except psycopg2.OperationalError as e:
            logger.error(f"✗ Failed to connect to Supabase: {e}")
            raise

        self._create_tables()

    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        conn = self.connection_pool.getconn()
        try:
            cursor = conn.cursor()

            # Agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id VARCHAR(50) PRIMARY KEY,
                    model_type VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    current_weight FLOAT DEFAULT 1.0,
                    total_votes INT DEFAULT 0,
                    correct_votes INT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Problems/Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS problems (
                    problem_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    text_raw TEXT NOT NULL,
                    text_clean TEXT,
                    ground_truth INT,
                    consensus_decision INT NOT NULL,
                    consensus_confidence FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Votes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    vote_id SERIAL PRIMARY KEY,
                    problem_id UUID NOT NULL REFERENCES problems(problem_id) ON DELETE CASCADE,
                    agent_id VARCHAR(50) NOT NULL REFERENCES agents(agent_id),
                    prediction INT NOT NULL,
                    confidence FLOAT NOT NULL,
                    reasoning JSONB,
                    weight_at_time FLOAT NOT NULL,
                    is_correct BOOLEAN,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Experiments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255),
                    num_rounds INT NOT NULL,
                    dataset VARCHAR(50),
                    consensus_accuracy FLOAT,
                    individual_accuracies JSONB,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                );
            """)

            # Metrics snapshot table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_snapshots (
                    snapshot_id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    total_predictions INT,
                    consensus_accuracy FLOAT,
                    avg_confidence FLOAT,
                    disagreement_rate FLOAT,
                    agent_weights JSONB,
                    metadata JSONB
                );
            """)

            # Create indexes for faster queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_problems_created ON problems(created_at DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_votes_problem ON votes(problem_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_votes_agent ON votes(agent_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics_snapshots(timestamp DESC);")

            conn.commit()
            logger.info("✓ Database tables initialized successfully")

        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"✗ Error creating tables: {e}")
            raise
        finally:
            cursor.close()
            self.connection_pool.putconn(conn)

    def get_connection(self):
        """Get a connection from the pool"""
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        self.connection_pool.putconn(conn)

    # ===== AGENTS OPERATIONS =====

    def create_agent(self, agent_id: str, model_type: str, weight: float = 1.0) -> bool:
        """Create a new agent in the database"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agents (agent_id, model_type, current_weight)
                VALUES (%s, %s, %s)
                ON CONFLICT (agent_id) DO UPDATE SET
                    current_weight = EXCLUDED.current_weight,
                    updated_at = NOW();
                """,
                (agent_id, model_type, weight),
            )
            conn.commit()
            logger.debug(f"Agent {agent_id} created/updated")
            return True
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error creating agent {agent_id}: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_agent_weight(self, agent_id: str) -> Optional[float]:
        """Get current weight of an agent"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT current_weight FROM agents WHERE agent_id = %s",
                (agent_id,)
            )
            result = cursor.fetchone()
            return result["current_weight"] if result else None
        except psycopg2.Error as e:
            logger.error(f"Error getting agent weight: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def update_agent_weight(self, agent_id: str, new_weight: float) -> bool:
        """Update agent weight"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE agents 
                SET current_weight = %s, updated_at = NOW()
                WHERE agent_id = %s;
                """,
                (new_weight, agent_id),
            )
            conn.commit()
            logger.debug(f"Agent {agent_id} weight updated to {new_weight}")
            return True
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error updating agent weight: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_all_agents(self) -> List[Dict]:
        """Get all agents with their current weights"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT agent_id, model_type, current_weight, total_votes, 
                       correct_votes, created_at
                FROM agents
                ORDER BY agent_id;
                """
            )
            return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error getting agents: {e}")
            return []
        finally:
            cursor.close()
            self.return_connection(conn)

    # ===== PROBLEMS/PREDICTIONS OPERATIONS =====

    def log_prediction(
        self,
        problem_id: str,
        text_raw: str,
        text_clean: str,
        consensus_decision: int,
        consensus_confidence: float,
        ground_truth: Optional[int] = None,
    ) -> bool:
        """Log a consensus prediction"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO problems 
                (problem_id, text_raw, text_clean, consensus_decision, 
                 consensus_confidence, ground_truth)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (problem_id, text_raw, text_clean, consensus_decision,
                 consensus_confidence, ground_truth),
            )
            conn.commit()
            logger.debug(f"Prediction {problem_id} logged")
            return True
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error logging prediction: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_prediction(self, problem_id: str) -> Optional[Dict]:
        """Get prediction details by problem ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM problems WHERE problem_id = %s",
                (problem_id,)
            )
            return cursor.fetchone()
        except psycopg2.Error as e:
            logger.error(f"Error getting prediction: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_recent_predictions(self, limit: int = 100) -> List[Dict]:
        """Get recent predictions with votes"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT p.*, json_agg(json_build_object(
                    'vote_id', v.vote_id,
                    'agent_id', v.agent_id,
                    'prediction', v.prediction,
                    'confidence', v.confidence,
                    'weight_at_time', v.weight_at_time
                )) as votes
                FROM problems p
                LEFT JOIN votes v ON p.problem_id = v.problem_id
                GROUP BY p.problem_id
                ORDER BY p.created_at DESC
                LIMIT %s;
                """,
                (limit,)
            )
            return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error getting recent predictions: {e}")
            return []
        finally:
            cursor.close()
            self.return_connection(conn)

    # ===== VOTES OPERATIONS =====

    def log_vote(
        self,
        problem_id: str,
        agent_id: str,
        prediction: int,
        confidence: float,
        weight_at_time: float,
        reasoning: Optional[Dict] = None,
        is_correct: Optional[bool] = None,
    ) -> bool:
        """Log a single agent vote"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO votes 
                (problem_id, agent_id, prediction, confidence, 
                 weight_at_time, reasoning, is_correct)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (problem_id, agent_id, prediction, confidence,
                 weight_at_time, Json(reasoning) if reasoning else None, is_correct),
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error logging vote: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_problem_votes(self, problem_id: str) -> List[Dict]:
        """Get all votes for a specific problem"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT * FROM votes 
                WHERE problem_id = %s 
                ORDER BY agent_id;
                """,
                (problem_id,)
            )
            return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error getting votes: {e}")
            return []
        finally:
            cursor.close()
            self.return_connection(conn)

    # ===== EXPERIMENTS OPERATIONS =====

    def create_experiment(
        self,
        name: str,
        num_rounds: int,
        dataset: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[str]:
        """Create a new experiment"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                INSERT INTO experiments 
                (name, num_rounds, dataset, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING experiment_id;
                """,
                (name, num_rounds, dataset, Json(metadata) if metadata else None),
            )
            result = cursor.fetchone()
            conn.commit()
            return str(result["experiment_id"]) if result else None
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error creating experiment: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def complete_experiment(
        self,
        experiment_id: str,
        consensus_accuracy: float,
        individual_accuracies: Dict[str, float],
    ) -> bool:
        """Mark experiment as completed with results"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE experiments
                SET consensus_accuracy = %s, 
                    individual_accuracies = %s,
                    completed_at = NOW()
                WHERE experiment_id = %s;
                """,
                (consensus_accuracy, Json(individual_accuracies), experiment_id),
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error completing experiment: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Get experiment details"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM experiments WHERE experiment_id = %s",
                (experiment_id,)
            )
            return cursor.fetchone()
        except psycopg2.Error as e:
            logger.error(f"Error getting experiment: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    # ===== METRICS OPERATIONS =====

    def save_metrics_snapshot(
        self,
        total_predictions: int,
        consensus_accuracy: float,
        avg_confidence: float,
        disagreement_rate: float,
        agent_weights: Dict[str, float],
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Save a metrics snapshot"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO metrics_snapshots
                (total_predictions, consensus_accuracy, avg_confidence, 
                 disagreement_rate, agent_weights, metadata)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (total_predictions, consensus_accuracy, avg_confidence,
                 disagreement_rate, Json(agent_weights), Json(metadata) if metadata else None),
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Error saving metrics snapshot: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_latest_metrics(self) -> Optional[Dict]:
        """Get the latest metrics snapshot"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT * FROM metrics_snapshots
                ORDER BY timestamp DESC
                LIMIT 1;
                """
            )
            return cursor.fetchone()
        except psycopg2.Error as e:
            logger.error(f"Error getting metrics: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_metrics_history(self, limit: int = 100) -> List[Dict]:
        """Get historical metrics"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT * FROM metrics_snapshots
                ORDER BY timestamp DESC
                LIMIT %s;
                """,
                (limit,)
            )
            return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error getting metrics history: {e}")
            return []
        finally:
            cursor.close()
            self.return_connection(conn)

    # ===== SYSTEM OPERATIONS =====

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Total predictions
            cursor.execute("SELECT COUNT(*) as count FROM problems;")
            total_predictions = cursor.fetchone()["count"]

            # Consensus accuracy
            cursor.execute(
                """
                SELECT 
                    COUNT(*) FILTER (WHERE consensus_decision = ground_truth) as correct,
                    COUNT(*) as total
                FROM problems 
                WHERE ground_truth IS NOT NULL;
                """
            )
            accuracy_row = cursor.fetchone()
            accuracy = (
                accuracy_row["correct"] / accuracy_row["total"]
                if accuracy_row["total"] > 0 else 0
            )

            # Agent stats
            cursor.execute(
                """
                SELECT agent_id, current_weight, total_votes, correct_votes
                FROM agents
                ORDER BY current_weight DESC;
                """
            )
            agents = cursor.fetchall()

            return {
                "total_predictions": total_predictions,
                "consensus_accuracy": float(accuracy),
                "agents": agents,
                "timestamp": datetime.now().isoformat(),
            }
        except psycopg2.Error as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
        finally:
            cursor.close()
            self.return_connection(conn)

    def close_all_connections(self):
        """Close all connections in the pool"""
        self.connection_pool.closeall()
        logger.info("Database connection pool closed")


# Global database instance
db: Optional[SupabaseDB] = None


def init_db():
    """Initialize the database connection"""
    global db
    if db is None:
        db = SupabaseDB()
    return db


def get_db() -> SupabaseDB:
    """Get the database instance"""
    global db
    if db is None:
        db = init_db()
    return db
