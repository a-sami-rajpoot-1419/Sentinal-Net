"""
Phase 4 Voting System Tests
"""

import pytest
import numpy as np
from backend.consensus.voting import WeightedVoter, VotingResult
from backend.shared.exceptions_v2 import ConsensusError


@pytest.fixture
def sample_predictions():
    """Sample predictions from agents"""
    return {
        "agent1": (0, 0.9),
        "agent2": (0, 0.8),
        "agent3": (1, 0.7),
        "agent4": (0, 0.85),
    }


@pytest.fixture
def sample_weights():
    """Sample agent weights"""
    return {
        "agent1": 1.0,
        "agent2": 1.0,
        "agent3": 1.0,
        "agent4": 1.0,
    }


class TestWeightedVoter:
    """Test weighted voting system"""
    
    def test_vote_basic(self, sample_predictions, sample_weights):
        """Should perform basic weighted voting"""
        result = WeightedVoter.vote(sample_predictions, sample_weights)
        
        assert isinstance(result, VotingResult)
        assert result.predicted_class in [0, 1]
        assert 0.0 <= result.confidence <= 1.0
    
    def test_vote_majority_wins(self, sample_predictions, sample_weights):
        """Majority should win"""
        # 3 agents predict 0, 1 agent predicts 1
        result = WeightedVoter.vote(sample_predictions, sample_weights)
        
        assert result.predicted_class == 0  # Majority class
    
    def test_vote_weighted_by_weight(self):
        """Voting should respect agent weights"""
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (1, 0.9),
            "agent3": (1, 0.9),
            "agent4": (1, 0.9),
        }
        
        # Equal weights: agent1 loses (1 vote vs 3 votes)
        weights_equal = {"agent1": 1.0, "agent2": 1.0, "agent3": 1.0, "agent4": 1.0}
        result_equal = WeightedVoter.vote(predictions, weights_equal)
        assert result_equal.predicted_class == 1
        
        # Heavy agent1: agent1 wins
        weights_heavy = {"agent1": 10.0, "agent2": 1.0, "agent3": 1.0, "agent4": 1.0}
        result_heavy = WeightedVoter.vote(predictions, weights_heavy)
        assert result_heavy.predicted_class == 0
    
    def test_vote_weighted_by_confidence(self):
        """Voting should consider agent confidence"""
        predictions = {
            "agent1": (0, 0.99),  # Very confident
            "agent2": (1, 0.51),  # Barely confident
        }
        
        weights = {"agent1": 1.0, "agent2": 1.0}
        result = WeightedVoter.vote(predictions, weights)
        
        # agent1's high confidence should boost class 0
        assert result.votes_per_class[0] > result.votes_per_class[1]
    
    def test_vote_empty_predictions_fails(self, sample_weights):
        """Empty predictions should raise error"""
        with pytest.raises(ConsensusError):
            WeightedVoter.vote({}, sample_weights)
    
    def test_vote_mismatched_agents_fails(self):
        """Mismatched agent names should raise error"""
        predictions = {"agent1": (0, 0.9), "agent2": (1, 0.8)}
        weights = {"agent1": 1.0, "agent3": 1.0}  # agent2 vs agent3
        
        with pytest.raises(ConsensusError):
            WeightedVoter.vote(predictions, weights)
    
    def test_vote_confidence_affects_result(self):
        """Agent confidence should affect voting confidence"""
        # All agents predict same class with high confidence
        predictions_high = {
            "agent1": (0, 0.99),
            "agent2": (0, 0.98),
        }
        weights = {"agent1": 1.0, "agent2": 1.0}
        result_high = WeightedVoter.vote(predictions_high, weights)
        
        # All agents predict same class with low confidence
        predictions_low = {
            "agent1": (0, 0.51),
            "agent2": (0, 0.52),
        }
        result_low = WeightedVoter.vote(predictions_low, weights)
        
        # High confidence result should have higher confidence
        assert result_high.confidence > result_low.confidence
    
    def test_vote_votes_per_class(self):
        """Vote distribution should be calculated correctly"""
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (0, 0.8),
            "agent3": (1, 0.7),
        }
        weights = {"agent1": 1.0, "agent2": 1.0, "agent3": 1.0}
        
        result = WeightedVoter.vote(predictions, weights)
        
        # Class 0: 0.9 + 0.8 = 1.7
        # Class 1: 0.7
        assert 0 in result.votes_per_class
        assert 1 in result.votes_per_class
        assert result.votes_per_class[0] > result.votes_per_class[1]


class TestMajorityVoting:
    """Test unweighted majority voting"""
    
    def test_majority_simple(self):
        """Should get simple majority"""
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (0, 0.8),
            "agent3": (1, 0.7),
        }
        
        majority = WeightedVoter.get_majority_prediction(predictions)
        assert majority == 0
    
    def test_majority_tie_picks_one(self):
        """Tie should pick one (implementation dependent)"""
        predictions = {
            "agent1": (0, 0.9),
            "agent2": (1, 0.8),
        }
        
        # Should not raise, should pick one
        majority = WeightedVoter.get_majority_prediction(predictions)
        assert majority in [0, 1]


class TestConsensusConfidence:
    """Test consensus confidence calculation"""
    
    def test_confidence_high_consensus(self):
        """High consensus should have high confidence"""
        votes_per_class = {0: 100.0, 1: 20.0}
        confidence, meets_threshold = WeightedVoter.calculate_consensus_confidence(
            votes_per_class,
            consensus_threshold=0.5,
        )
        
        assert confidence > 0.5
        assert meets_threshold is True
    
    def test_confidence_low_consensus(self):
        """Low consensus should have low confidence"""
        votes_per_class = {0: 51.0, 1: 49.0}
        confidence, meets_threshold = WeightedVoter.calculate_consensus_confidence(
            votes_per_class,
            consensus_threshold=0.6,
        )
        
        assert confidence < 0.6
        assert meets_threshold is False
    
    def test_confidence_exact_threshold(self):
        """Exact threshold should meet condition"""
        votes_per_class = {0: 60.0, 1: 40.0}
        confidence, meets_threshold = WeightedVoter.calculate_consensus_confidence(
            votes_per_class,
            consensus_threshold=0.6,
        )
        
        assert meets_threshold is True
    
    def test_confidence_empty_votes(self):
        """Empty votes should return 0 confidence"""
        confidence, meets_threshold = WeightedVoter.calculate_consensus_confidence(
            {},
            consensus_threshold=0.5,
        )
        
        assert confidence == 0.0
        assert meets_threshold is False
