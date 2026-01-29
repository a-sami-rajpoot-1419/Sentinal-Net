"""
Unit Tests for ML Agents - Sentinel-Net

Comprehensive tests for all agent implementations.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from backend.models.base import AgentBase
from backend.models.naive_bayes import NaiveBayesAgent
from backend.models.svm import SVMAgent
from backend.models.random_forest import RandomForestAgent
from backend.models.logistic_regression import LogisticRegressionAgent


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_data():
    """Generate sample training data."""
    np.random.seed(42)
    n_samples = 100
    n_features = 1004
    
    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, 2, n_samples)
    
    return X, y


@pytest.fixture
def sample_single_sample():
    """Generate single sample for prediction."""
    np.random.seed(42)
    X = np.random.rand(1, 1004)
    return X


# ============================================================================
# Base Agent Tests
# ============================================================================

class TestAgentBase:
    """Test AgentBase abstract class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Base class should not be instantiable."""
        with pytest.raises(TypeError):
            AgentBase("test_agent")
    
    def test_agent_id_assignment(self):
        """Agent should store ID correctly."""
        agent = NaiveBayesAgent("my_agent")
        assert agent.agent_id == "my_agent"
    
    def test_initial_weight(self):
        """Agent should start with weight=1.0."""
        agent = NaiveBayesAgent()
        assert agent.weight == 1.0
    
    def test_initial_vote_counts(self):
        """Agent should start with zero votes."""
        agent = NaiveBayesAgent()
        assert agent.total_votes == 0
        assert agent.correct_votes == 0
    
    def test_initial_accuracy(self):
        """Accuracy should be 0 with no votes."""
        agent = NaiveBayesAgent()
        assert agent.accuracy == 0.0
    
    def test_update_accuracy_correct(self):
        """Accuracy should increase with correct predictions."""
        agent = NaiveBayesAgent()
        agent.update_accuracy(True)
        assert agent.total_votes == 1
        assert agent.correct_votes == 1
        assert agent.accuracy == 1.0
    
    def test_update_accuracy_incorrect(self):
        """Accuracy should handle incorrect predictions."""
        agent = NaiveBayesAgent()
        agent.update_accuracy(True)
        agent.update_accuracy(False)
        assert agent.total_votes == 2
        assert agent.correct_votes == 1
        assert agent.accuracy == 0.5
    
    def test_multiple_accuracy_updates(self):
        """Multiple updates should accumulate correctly."""
        agent = NaiveBayesAgent()
        for _ in range(10):
            agent.update_accuracy(True)
        for _ in range(5):
            agent.update_accuracy(False)
        assert agent.total_votes == 15
        assert agent.correct_votes == 10
        assert abs(agent.accuracy - (10/15)) < 1e-6
    
    def test_weight_modification(self):
        """Agent weight should be modifiable."""
        agent = NaiveBayesAgent()
        agent.weight = 2.5
        assert agent.weight == 2.5


# ============================================================================
# Naive Bayes Agent Tests
# ============================================================================

class TestNaiveBayesAgent:
    """Test Naive Bayes agent."""
    
    def test_initialization(self):
        """Should initialize with default ID."""
        agent = NaiveBayesAgent()
        assert agent.agent_id == "agent_nb"
        assert agent.model is not None
    
    def test_custom_id(self):
        """Should accept custom agent ID."""
        agent = NaiveBayesAgent("custom_nb")
        assert agent.agent_id == "custom_nb"
    
    def test_train(self, sample_data):
        """Should train successfully."""
        X, y = sample_data
        agent = NaiveBayesAgent()
        agent.train(X, y)
        assert agent.model is not None
        assert agent.feature_log_prob is not None
    
    def test_predict_shape(self, sample_data, sample_single_sample):
        """Prediction should return tuple of correct types."""
        X, y = sample_data
        agent = NaiveBayesAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        assert isinstance(prediction, (int, np.integer))
        assert isinstance(confidence, float)
    
    def test_predict_confidence_range(self, sample_data, sample_single_sample):
        """Confidence should be between 0 and 1."""
        X, y = sample_data
        agent = NaiveBayesAgent()
        agent.train(X, y)
        
        _, confidence = agent.predict(sample_single_sample)
        assert 0.0 <= confidence <= 1.0
    
    def test_predict_without_confidence(self, sample_data, sample_single_sample):
        """Should return 0.5 confidence when not requested."""
        X, y = sample_data
        agent = NaiveBayesAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample, return_confidence=False)
        assert confidence == 0.5
    
    def test_reasoning_generation(self, sample_data, sample_single_sample):
        """Should generate reasoning dict."""
        X, y = sample_data
        agent = NaiveBayesAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        reasoning = agent._generate_reasoning(sample_single_sample, prediction, confidence)
        
        assert 'reasoning' in reasoning
        assert 'key_features' in reasoning
        assert 'model_explanation' in reasoning
        assert isinstance(reasoning['reasoning'], str)
        assert isinstance(reasoning['key_features'], list)
    
    def test_prediction_with_reasoning(self, sample_data, sample_single_sample):
        """Should get full prediction with reasoning."""
        X, y = sample_data
        agent = NaiveBayesAgent()
        agent.train(X, y)
        
        pred_dict = agent.get_prediction_with_reasoning(sample_single_sample)
        
        assert 'agent_id' in pred_dict
        assert 'prediction' in pred_dict
        assert 'confidence' in pred_dict
        assert 'reasoning' in pred_dict
        assert 'weight' in pred_dict
        assert pred_dict['agent_id'] == 'agent_nb'


# ============================================================================
# SVM Agent Tests
# ============================================================================

class TestSVMAgent:
    """Test SVM agent."""
    
    def test_initialization(self):
        """Should initialize with default ID."""
        agent = SVMAgent()
        assert agent.agent_id == "agent_svm"
        assert agent.model is not None
    
    def test_train(self, sample_data):
        """Should train successfully."""
        X, y = sample_data
        agent = SVMAgent()
        agent.train(X, y)
        assert agent.model.n_support_ > 0  # Should have support vectors
    
    def test_predict_shape(self, sample_data, sample_single_sample):
        """Prediction should return correct types."""
        X, y = sample_data
        agent = SVMAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        assert isinstance(prediction, (int, np.integer))
        assert 0.0 <= confidence <= 1.0
    
    def test_reasoning_contains_decision_distance(self, sample_data, sample_single_sample):
        """Reasoning should include decision distance."""
        X, y = sample_data
        agent = SVMAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        reasoning = agent._generate_reasoning(sample_single_sample, prediction, confidence)
        
        assert 'decision_distance' in reasoning
        assert isinstance(reasoning['decision_distance'], float)


# ============================================================================
# Random Forest Agent Tests
# ============================================================================

class TestRandomForestAgent:
    """Test Random Forest agent."""
    
    def test_initialization(self):
        """Should initialize with default ID."""
        agent = RandomForestAgent()
        assert agent.agent_id == "agent_rf"
        assert agent.model is not None
        assert agent.model.n_estimators == 100
    
    def test_train(self, sample_data):
        """Should train successfully."""
        X, y = sample_data
        agent = RandomForestAgent()
        agent.train(X, y)
        assert agent.model.n_estimators == 100
    
    def test_predict_shape(self, sample_data, sample_single_sample):
        """Prediction should return correct types."""
        X, y = sample_data
        agent = RandomForestAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        assert isinstance(prediction, (int, np.integer))
        assert 0.0 <= confidence <= 1.0
    
    def test_reasoning_contains_feature_importance(self, sample_data, sample_single_sample):
        """Reasoning should include feature importance."""
        X, y = sample_data
        agent = RandomForestAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        reasoning = agent._generate_reasoning(sample_single_sample, prediction, confidence)
        
        assert 'top_feature_importance' in reasoning
        assert isinstance(reasoning['top_feature_importance'], float)


# ============================================================================
# Logistic Regression Agent Tests
# ============================================================================

class TestLogisticRegressionAgent:
    """Test Logistic Regression agent."""
    
    def test_initialization(self):
        """Should initialize with default ID."""
        agent = LogisticRegressionAgent()
        assert agent.agent_id == "agent_lr"
        assert agent.model is not None
    
    def test_train(self, sample_data):
        """Should train successfully."""
        X, y = sample_data
        agent = LogisticRegressionAgent()
        agent.train(X, y)
        assert agent.model.coef_ is not None
    
    def test_predict_shape(self, sample_data, sample_single_sample):
        """Prediction should return correct types."""
        X, y = sample_data
        agent = LogisticRegressionAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        assert isinstance(prediction, (int, np.integer))
        assert 0.0 <= confidence <= 1.0
    
    def test_reasoning_contains_max_coefficient(self, sample_data, sample_single_sample):
        """Reasoning should include max coefficient."""
        X, y = sample_data
        agent = LogisticRegressionAgent()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        reasoning = agent._generate_reasoning(sample_single_sample, prediction, confidence)
        
        assert 'max_coefficient' in reasoning
        assert isinstance(reasoning['max_coefficient'], float)


# ============================================================================
# Cross-Agent Tests
# ============================================================================

class TestAllAgents:
    """Test all agents with common interface."""
    
    @pytest.fixture(params=[
        NaiveBayesAgent,
        SVMAgent,
        RandomForestAgent,
        LogisticRegressionAgent
    ])
    def agent_class(self, request):
        """Parametrized fixture for all agent classes."""
        return request.param
    
    def test_all_agents_have_required_methods(self, agent_class):
        """All agents should implement required methods."""
        agent = agent_class()
        assert hasattr(agent, 'train')
        assert hasattr(agent, 'predict')
        assert hasattr(agent, '_generate_reasoning')
        assert hasattr(agent, 'get_prediction_with_reasoning')
    
    def test_all_agents_trainable(self, agent_class, sample_data):
        """All agents should be trainable."""
        X, y = sample_data
        agent = agent_class()
        agent.train(X, y)
        # If no exception, test passes
        assert True
    
    def test_all_agents_predict(self, agent_class, sample_data, sample_single_sample):
        """All agents should make predictions."""
        X, y = sample_data
        agent = agent_class()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        assert isinstance(prediction, (int, np.integer))
        assert 0.0 <= confidence <= 1.0
    
    def test_all_agents_generate_reasoning(self, agent_class, sample_data, sample_single_sample):
        """All agents should generate reasoning."""
        X, y = sample_data
        agent = agent_class()
        agent.train(X, y)
        
        prediction, confidence = agent.predict(sample_single_sample)
        reasoning = agent._generate_reasoning(sample_single_sample, prediction, confidence)
        
        assert isinstance(reasoning, dict)
        assert 'reasoning' in reasoning
        assert 'key_features' in reasoning
