"""
Phase 4 Reputation Manager Tests
"""

import pytest
from datetime import datetime
from backend.consensus.reputation import ReputationManager, AgentReputation
from backend.shared.exceptions_v2 import ConsensusException


@pytest.fixture
def reputation_manager():
    """Create reputation manager for testing"""
    return ReputationManager()


class TestReputationManagerInitialization:
    """Test reputation manager initialization"""
    
    def test_manager_initializes_empty(self, reputation_manager):
        """Manager should initialize with no agents"""
        assert len(reputation_manager.reputations) == 0
        assert len(reputation_manager.prediction_records) == 0
    
    def test_initialize_agent(self, reputation_manager):
        """Should initialize new agent reputation"""
        reputation_manager.initialize_agent("agent1")
        
        assert "agent1" in reputation_manager.reputations
        rep = reputation_manager.reputations["agent1"]
        assert rep.agent_name == "agent1"
        assert rep.total_predictions == 0
        assert rep.current_weight == 1.0
    
    def test_initialize_agent_with_weight(self, reputation_manager):
        """Should initialize agent with custom weight"""
        reputation_manager.initialize_agent("agent1", initial_weight=2.0)
        
        assert reputation_manager.reputations["agent1"].current_weight == 2.0
    
    def test_cannot_reinitialize_agent(self, reputation_manager):
        """Should not allow reinitializing existing agent"""
        reputation_manager.initialize_agent("agent1")
        
        with pytest.raises(ConsensusException):
            reputation_manager.initialize_agent("agent1")


class TestPredictionRecording:
    """Test prediction recording"""
    
    def test_record_correct_prediction(self, reputation_manager):
        """Should record correct prediction"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=0,
            confidence=0.9,
            majority_class=0,
        )
        
        rep = reputation_manager.reputations["agent1"]
        assert rep.total_predictions == 1
        assert rep.correct_predictions == 1
        assert rep.accuracy == 1.0
    
    def test_record_wrong_prediction(self, reputation_manager):
        """Should record wrong prediction"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=1,
            confidence=0.9,
            majority_class=1,
        )
        
        rep = reputation_manager.reputations["agent1"]
        assert rep.total_predictions == 1
        assert rep.correct_predictions == 0
        assert rep.accuracy == 0.0
    
    def test_record_minority_correct(self, reputation_manager):
        """Should track minority correct prediction"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=0,
            confidence=0.9,
            majority_class=1,  # Majority was wrong
        )
        
        rep = reputation_manager.reputations["agent1"]
        assert rep.minority_correct == 1
        assert rep.majority_correct == 0
    
    def test_record_majority_correct(self, reputation_manager):
        """Should track majority correct prediction"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=0,
            confidence=0.9,
            majority_class=0,  # Majority was right
        )
        
        rep = reputation_manager.reputations["agent1"]
        assert rep.majority_correct == 1
        assert rep.minority_correct == 0
    
    def test_record_both_wrong(self, reputation_manager):
        """Should track when both agent and majority wrong"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=1,
            confidence=0.9,
            majority_class=0,  # Majority also wrong
        )
        
        rep = reputation_manager.reputations["agent1"]
        assert rep.both_wrong == 1
    
    def test_auto_initialize_on_record(self, reputation_manager):
        """Should auto-initialize agent if not exists"""
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=0,
            confidence=0.9,
            majority_class=0,
        )
        
        assert "agent1" in reputation_manager.reputations
    
    def test_confidence_averaging(self, reputation_manager):
        """Should correctly average confidence"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=0,
            true_class=0,
            confidence=0.8,
            majority_class=0,
        )
        
        reputation_manager.record_prediction(
            agent_name="agent1",
            predicted_class=1,
            true_class=1,
            confidence=0.9,
            majority_class=1,
        )
        
        rep = reputation_manager.reputations["agent1"]
        assert abs(rep.confidence_avg - 0.85) < 0.01


class TestWeightUpdating:
    """Test weight updates"""
    
    def test_update_weight(self, reputation_manager):
        """Should update agent weight"""
        reputation_manager.initialize_agent("agent1")
        reputation_manager.update_weight("agent1", 1.5)
        
        rep = reputation_manager.reputations["agent1"]
        assert rep.current_weight == 1.5
        assert len(rep.weight_history) == 1
    
    def test_weight_update_unknown_agent_fails(self, reputation_manager):
        """Should fail updating unknown agent"""
        with pytest.raises(ConsensusException):
            reputation_manager.update_weight("unknown", 1.5)


class TestRanking:
    """Test agent ranking"""
    
    def test_rank_by_accuracy(self, reputation_manager):
        """Should rank agents by accuracy"""
        reputation_manager.initialize_agent("agent1")
        reputation_manager.initialize_agent("agent2")
        reputation_manager.initialize_agent("agent3")
        
        # Give agent1 100% accuracy
        reputation_manager.record_prediction("agent1", 0, 0, 0.9, 0)
        reputation_manager.record_prediction("agent1", 1, 1, 0.9, 1)
        
        # Give agent2 50% accuracy
        reputation_manager.record_prediction("agent2", 0, 0, 0.9, 0)
        reputation_manager.record_prediction("agent2", 1, 0, 0.9, 0)
        
        # Give agent3 0% accuracy
        reputation_manager.record_prediction("agent3", 0, 1, 0.9, 1)
        reputation_manager.record_prediction("agent3", 1, 0, 0.9, 1)
        
        ranked = reputation_manager.rank_agents_by_accuracy()
        
        assert ranked[0][0] == "agent1"  # Best
        assert ranked[1][0] == "agent2"  # Middle
        assert ranked[2][0] == "agent3"  # Worst
    
    def test_rank_by_weight(self, reputation_manager):
        """Should rank agents by weight"""
        reputation_manager.initialize_agent("agent1", initial_weight=1.0)
        reputation_manager.initialize_agent("agent2", initial_weight=2.0)
        reputation_manager.initialize_agent("agent3", initial_weight=0.5)
        
        ranked = reputation_manager.rank_agents_by_weight()
        
        assert ranked[0][0] == "agent2"  # Heaviest
        assert ranked[1][0] == "agent1"  # Middle
        assert ranked[2][0] == "agent3"  # Lightest


class TestStatistics:
    """Test statistics generation"""
    
    def test_get_agent_stats(self, reputation_manager):
        """Should return detailed agent statistics"""
        reputation_manager.initialize_agent("agent1")
        
        reputation_manager.record_prediction("agent1", 0, 0, 0.9, 0)
        reputation_manager.record_prediction("agent1", 1, 1, 0.85, 1)
        reputation_manager.record_prediction("agent1", 0, 1, 0.8, 0)
        
        stats = reputation_manager.get_agent_stats("agent1")
        
        assert stats["agent_name"] == "agent1"
        assert stats["total_predictions"] == 3
        assert stats["accuracy"] == 2/3
        assert stats["minority_correct"] == 0
        assert stats["majority_correct"] == 2
        assert stats["both_wrong"] == 1
    
    def test_get_reputation_summary(self, reputation_manager):
        """Should return summary of all agents"""
        reputation_manager.initialize_agent("agent1")
        reputation_manager.initialize_agent("agent2")
        
        summary = reputation_manager.get_reputation_summary()
        
        assert len(summary) == 2
        assert "agent1" in summary
        assert "agent2" in summary


class TestReset:
    """Test reset functionality"""
    
    def test_reset_all(self, reputation_manager):
        """Should reset all data"""
        reputation_manager.initialize_agent("agent1")
        reputation_manager.record_prediction("agent1", 0, 0, 0.9, 0)
        
        reputation_manager.reset_all()
        
        assert len(reputation_manager.reputations) == 0
        assert len(reputation_manager.prediction_records) == 0
