"""
Phase 4 Consensus Engine Tests
"""

import pytest
import numpy as np
from typing import Dict, Tuple
from backend.consensus.engine import ConsensusEngine, ConsensusResult
from backend.models.base import AgentBase
from backend.shared.exceptions_v2 import ConsensusException


class MockAgent(AgentBase):
    """Mock agent for testing"""
    
    def __init__(self, name: str, predictions: np.ndarray = None):
        super().__init__(name=name)
        self.predictions_data = predictions
        self.prediction_idx = 0
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Mock training"""
        self.is_trained = True
        self.accuracy = 0.9
    
    def predict(self, X: np.ndarray) -> Tuple[int, float]:
        """Return mock predictions"""
        if self.predictions_data is not None:
            pred = self.predictions_data[self.prediction_idx % len(self.predictions_data)]
            self.prediction_idx += 1
            return int(pred[0]), float(pred[1])
        return 0, 0.8
    
    def _generate_reasoning(self) -> Dict:
        """Mock reasoning"""
        return {"mock": "reasoning"}


@pytest.fixture
def mock_agents():
    """Create mock agents for testing"""
    return {
        "agent1": MockAgent("agent1", np.array([[0, 0.9], [1, 0.8], [0, 0.7]])),
        "agent2": MockAgent("agent2", np.array([[0, 0.8], [1, 0.9], [0, 0.85]])),
        "agent3": MockAgent("agent3", np.array([[0, 0.85], [0, 0.75], [1, 0.8]])),
        "agent4": MockAgent("agent4", np.array([[0, 0.95], [1, 0.85], [1, 0.9]])),
    }


@pytest.fixture
def consensus_engine(mock_agents):
    """Create consensus engine with mock agents"""
    return ConsensusEngine(agents=mock_agents)


class TestConsensusEngineInitialization:
    """Test engine initialization"""
    
    def test_engine_creates_with_agents(self, consensus_engine):
        """Engine should initialize with 4 agents"""
        assert len(consensus_engine.agents) == 4
        assert all(name in consensus_engine.agents for name in ["agent1", "agent2", "agent3", "agent4"])
    
    def test_initial_weights_equal(self, consensus_engine):
        """Initial weights should be 1.0 for all agents"""
        weights = consensus_engine.get_weights()
        assert all(w == 1.0 for w in weights.values())
    
    def test_weight_bounds_respected(self, consensus_engine):
        """Weight bounds should be set correctly"""
        assert consensus_engine.weight_min == 0.1
        assert consensus_engine.weight_max == 5.0


class TestConsensusEnginePrediction:
    """Test consensus prediction functionality"""
    
    def test_single_prediction_returns_result(self, consensus_engine):
        """Single prediction should return ConsensusResult"""
        X = np.random.randn(1, 1004)
        result = consensus_engine.predict(X)
        
        assert isinstance(result, ConsensusResult)
        assert result.predicted_class in [0, 1]
        assert 0.0 <= result.confidence <= 1.0
    
    def test_prediction_includes_all_agents(self, consensus_engine):
        """Prediction should include all agents"""
        X = np.random.randn(1, 1004)
        result = consensus_engine.predict(X)
        
        assert len(result.agent_predictions) == 4
        assert set(result.agent_predictions.keys()) == set(consensus_engine.agents.keys())
    
    def test_prediction_rejects_wrong_shape(self, consensus_engine):
        """Prediction should reject wrong input shape"""
        X = np.random.randn(5, 1004)  # Multiple samples
        
        with pytest.raises(ConsensusException):
            consensus_engine.predict(X)
    
    def test_batch_prediction_returns_list(self, consensus_engine):
        """Batch prediction should return list of results"""
        X = np.random.randn(5, 1004)
        results = consensus_engine.batch_predict(X)
        
        assert isinstance(results, list)
        assert len(results) == 5
        assert all(isinstance(r, ConsensusResult) for r in results)


class TestWeightUpdates:
    """Test RWPV weight update mechanism"""
    
    def test_weight_update_rewards_correct(self, consensus_engine):
        """Weight should increase for correct predictions"""
        initial_weight = consensus_engine.weights["agent1"]
        
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (0, 0.8),
            "agent3": (0, 0.85),
            "agent4": (0, 0.95),
        }
        
        consensus_engine.update_weights_from_feedback(
            true_label=0,
            predictions=predictions,
        )
        
        # Agent1 was correct, should get reward
        assert consensus_engine.weights["agent1"] > initial_weight
    
    def test_weight_update_penalizes_wrong(self, consensus_engine):
        """Weight should decrease for wrong predictions"""
        initial_weight = consensus_engine.weights["agent2"]
        
        predictions = {
            "agent1": (1, 0.9),
            "agent2": (1, 0.8),  # Wrong
            "agent3": (1, 0.85),
            "agent4": (1, 0.95),
        }
        
        consensus_engine.update_weights_from_feedback(
            true_label=0,  # All wrong
            predictions=predictions,
        )
        
        # All agents were wrong
        assert consensus_engine.weights["agent2"] <= initial_weight
    
    def test_weight_respects_bounds(self, consensus_engine):
        """Weights should not exceed min/max bounds"""
        # Manually set weight to max
        consensus_engine.set_weight("agent1", 5.0)
        assert consensus_engine.weights["agent1"] == 5.0
        
        # Manually set weight to min
        consensus_engine.set_weight("agent2", 0.1)
        assert consensus_engine.weights["agent2"] == 0.1
        
        # Try to exceed bounds
        consensus_engine.set_weight("agent3", 10.0)
        assert consensus_engine.weights["agent3"] == 5.0  # Clamped
        
        consensus_engine.set_weight("agent4", 0.01)
        assert consensus_engine.weights["agent4"] == 0.1  # Clamped
    
    def test_weights_normalize_after_update(self, consensus_engine):
        """Weights should sum to number of agents after update"""
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (0, 0.8),
            "agent3": (0, 0.85),
            "agent4": (0, 0.95),
        }
        
        consensus_engine.update_weights_from_feedback(
            true_label=0,
            predictions=predictions,
        )
        
        # Sum should be close to 4 (number of agents)
        weight_sum = sum(consensus_engine.weights.values())
        assert abs(weight_sum - 4.0) < 0.01


class TestReputation:
    """Test reputation tracking"""
    
    def test_reputation_initialization(self, consensus_engine):
        """Reputation should initialize correctly"""
        rep = consensus_engine.get_agent_reputation("agent1")
        
        assert rep["agent_name"] == "agent1"
        assert rep["total_predictions"] == 0
        assert rep["accuracy"] == 0.0
    
    def test_reputation_tracks_predictions(self, consensus_engine):
        """Reputation should track predictions over time"""
        for _ in range(5):
            predictions = {
                "agent1": (0, 0.9),
                "agent2": (0, 0.8),
                "agent3": (0, 0.85),
                "agent4": (0, 0.95),
            }
            consensus_engine.update_weights_from_feedback(
                true_label=0,
                predictions=predictions,
            )
        
        rep = consensus_engine.get_agent_reputation("agent1")
        assert rep["total_predictions"] > 0
    
    def test_all_reputations(self, consensus_engine):
        """Should return reputations for all agents"""
        reputations = consensus_engine.get_all_reputations()
        
        assert len(reputations) == 4
        assert all(name in reputations for name in consensus_engine.agents.keys())


class TestWeightReset:
    """Test weight reset functionality"""
    
    def test_reset_weights(self, consensus_engine):
        """Reset should set all weights to 1.0"""
        # Change weights
        consensus_engine.set_weight("agent1", 2.0)
        consensus_engine.set_weight("agent2", 0.5)
        
        # Reset
        consensus_engine.reset_weights()
        
        # All weights should be 1.0
        weights = consensus_engine.get_weights()
        assert all(w == 1.0 for w in weights.values())


class TestPredictionHistory:
    """Test prediction history tracking"""
    
    def test_history_records_feedback(self, consensus_engine):
        """History should record weight updates"""
        assert len(consensus_engine.get_prediction_history()) == 0
        
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (0, 0.8),
            "agent3": (0, 0.85),
            "agent4": (0, 0.95),
        }
        
        consensus_engine.update_weights_from_feedback(
            true_label=0,
            predictions=predictions,
        )
        
        history = consensus_engine.get_prediction_history()
        assert len(history) == 1
        assert history[0]["true_label"] == 0
