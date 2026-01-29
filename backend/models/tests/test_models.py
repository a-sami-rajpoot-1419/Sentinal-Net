"""
Unit Tests for ML Agents

Tests for base agent, all 4 model implementations, and trainer.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pytest
import numpy as np
from sklearn.datasets import make_classification

from backend.models.base import AgentBase
from backend.models.naive_bayes import NaiveBayesAgent
from backend.models.svm import SVMAgent
from backend.models.random_forest import RandomForestAgent
from backend.models.logistic_regression import LogisticRegressionAgent
from backend.models.trainer import ModelTrainer


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_data():
    """Create sample training/test data."""
    X_train, y_train = make_classification(
        n_samples=200, n_features=1004, n_informative=100,
        n_redundant=50, random_state=42
    )
    X_test, y_test = make_classification(
        n_samples=50, n_features=1004, n_informative=100,
        n_redundant=50, random_state=43
    )
    return X_train, y_train, X_test, y_test


@pytest.fixture
def naive_bayes_agent():
    """Create Naive Bayes agent."""
    return NaiveBayesAgent()


@pytest.fixture
def svm_agent():
    """Create SVM agent."""
    return SVMAgent()


@pytest.fixture
def rf_agent():
    """Create Random Forest agent."""
    return RandomForestAgent()


@pytest.fixture
def lr_agent():
    """Create Logistic Regression agent."""
    return LogisticRegressionAgent()


@pytest.fixture
def trainer():
    """Create ModelTrainer."""
    return ModelTrainer()


# ============================================================================
# Test Base Agent Class
# ============================================================================

class TestAgentBase:
    """Tests for AgentBase abstract class."""
    
    def test_cannot_instantiate_abstract(self):
        """AgentBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AgentBase("test")
    
    def test_agent_initialization(self, naive_bayes_agent):
        """Agent initializes with correct defaults."""
        assert naive_bayes_agent.agent_id == "agent_nb"
        assert naive_bayes_agent.weight == 1.0
        assert naive_bayes_agent.is_trained is False
        assert naive_bayes_agent.model is not None
    
    def test_weight_management(self, naive_bayes_agent):
        """Weight management works correctly."""
        agent = naive_bayes_agent
        
        # Test reset
        agent.weight = 0.5
        agent.reset_weight()
        assert agent.weight == 1.0
        
        # Test update
        agent.update_weight(1.2)
        assert abs(agent.weight - 1.2) < 0.01
    
    def test_get_info(self, naive_bayes_agent):
        """get_info returns correct structure."""
        info = naive_bayes_agent.get_info()
        assert 'agent_id' in info
        assert 'model_type' in info
        assert 'is_trained' in info
        assert 'weight' in info
        assert info['agent_id'] == 'agent_nb'
        assert info['is_trained'] is False


# ============================================================================
# Test Naive Bayes Agent
# ============================================================================

class TestNaiveBayesAgent:
    """Tests for Naive Bayes agent."""
    
    def test_training(self, naive_bayes_agent, sample_data):
        """NB agent trains successfully."""
        X_train, y_train, _, _ = sample_data
        
        assert naive_bayes_agent.is_trained is False
        naive_bayes_agent.train(X_train, y_train)
        assert naive_bayes_agent.is_trained is True
    
    def test_training_validation(self, naive_bayes_agent, sample_data):
        """Training validates input."""
        X_train, y_train, _, _ = sample_data
        
        # Empty data
        with pytest.raises(ValueError):
            naive_bayes_agent.train(np.array([]), np.array([]))
        
        # Mismatched lengths
        with pytest.raises(ValueError):
            naive_bayes_agent.train(X_train[:10], y_train)
    
    def test_prediction(self, naive_bayes_agent, sample_data):
        """NB agent makes valid predictions."""
        X_train, y_train, X_test, y_test = sample_data
        naive_bayes_agent.train(X_train, y_train)
        
        # Single prediction
        pred, conf = naive_bayes_agent.predict(X_test[0])
        assert pred in [0, 1]
        assert 0.0 <= conf <= 1.0
        
        # Batch prediction
        pred, conf = naive_bayes_agent.predict(X_test[:5])
        assert pred in [0, 1]
        assert 0.0 <= conf <= 1.0
    
    def test_prediction_before_training(self, naive_bayes_agent, sample_data):
        """Cannot predict before training."""
        X_test, _, = sample_data[2:3]
        
        with pytest.raises(ValueError):
            naive_bayes_agent.predict(X_test[0])
    
    def test_reasoning_generation(self, naive_bayes_agent, sample_data):
        """NB generates valid reasoning."""
        X_train, y_train, X_test, _ = sample_data
        naive_bayes_agent.train(X_train, y_train)
        
        pred, _ = naive_bayes_agent.predict(X_test[0])
        reasoning = naive_bayes_agent._generate_reasoning(X_test[0:1], pred)
        
        assert 'reasoning' in reasoning
        assert 'top_spam_indicators' in reasoning
        assert 'top_ham_indicators' in reasoning
        assert 'active_features_count' in reasoning
        assert 'model_name' in reasoning


# ============================================================================
# Test SVM Agent
# ============================================================================

class TestSVMAgent:
    """Tests for SVM agent."""
    
    def test_training(self, svm_agent, sample_data):
        """SVM agent trains successfully."""
        X_train, y_train, _, _ = sample_data
        
        assert svm_agent.is_trained is False
        svm_agent.train(X_train, y_train)
        assert svm_agent.is_trained is True
    
    def test_prediction(self, svm_agent, sample_data):
        """SVM agent makes valid predictions."""
        X_train, y_train, X_test, _ = sample_data
        svm_agent.train(X_train, y_train)
        
        pred, conf = svm_agent.predict(X_test[0])
        assert pred in [0, 1]
        assert 0.0 <= conf <= 1.0
    
    def test_reasoning_generation(self, svm_agent, sample_data):
        """SVM generates valid reasoning."""
        X_train, y_train, X_test, _ = sample_data
        svm_agent.train(X_train, y_train)
        
        pred, _ = svm_agent.predict(X_test[0])
        reasoning = svm_agent._generate_reasoning(X_test[0:1], pred)
        
        assert 'reasoning' in reasoning
        assert 'boundary_distance' in reasoning
        assert 'boundary_side' in reasoning
        assert 'confidence_factor' in reasoning
        assert 'model_name' in reasoning


# ============================================================================
# Test Random Forest Agent
# ============================================================================

class TestRandomForestAgent:
    """Tests for Random Forest agent."""
    
    def test_training(self, rf_agent, sample_data):
        """RF agent trains successfully."""
        X_train, y_train, _, _ = sample_data
        
        assert rf_agent.is_trained is False
        rf_agent.train(X_train, y_train)
        assert rf_agent.is_trained is True
    
    def test_prediction(self, rf_agent, sample_data):
        """RF agent makes valid predictions."""
        X_train, y_train, X_test, _ = sample_data
        rf_agent.train(X_train, y_train)
        
        pred, conf = rf_agent.predict(X_test[0])
        assert pred in [0, 1]
        assert 0.0 <= conf <= 1.0
    
    def test_reasoning_generation(self, rf_agent, sample_data):
        """RF generates valid reasoning."""
        X_train, y_train, X_test, _ = sample_data
        rf_agent.train(X_train, y_train)
        
        pred, _ = rf_agent.predict(X_test[0])
        reasoning = rf_agent._generate_reasoning(X_test[0:1], pred)
        
        assert 'reasoning' in reasoning
        assert 'n_trees' in reasoning
        assert 'tree_votes_for_class' in reasoning
        assert 'top_important_features' in reasoning
        assert 'ensemble_agreement' in reasoning


# ============================================================================
# Test Logistic Regression Agent
# ============================================================================

class TestLogisticRegressionAgent:
    """Tests for Logistic Regression agent."""
    
    def test_training(self, lr_agent, sample_data):
        """LR agent trains successfully."""
        X_train, y_train, _, _ = sample_data
        
        assert lr_agent.is_trained is False
        lr_agent.train(X_train, y_train)
        assert lr_agent.is_trained is True
    
    def test_prediction(self, lr_agent, sample_data):
        """LR agent makes valid predictions."""
        X_train, y_train, X_test, _ = sample_data
        lr_agent.train(X_train, y_train)
        
        pred, conf = lr_agent.predict(X_test[0])
        assert pred in [0, 1]
        assert 0.0 <= conf <= 1.0
    
    def test_reasoning_generation(self, lr_agent, sample_data):
        """LR generates valid reasoning."""
        X_train, y_train, X_test, _ = sample_data
        lr_agent.train(X_train, y_train)
        
        pred, _ = lr_agent.predict(X_test[0])
        reasoning = lr_agent._generate_reasoning(X_test[0:1], pred)
        
        assert 'reasoning' in reasoning
        assert 'decision_value' in reasoning
        assert 'top_spam_features' in reasoning
        assert 'top_ham_features' in reasoning


# ============================================================================
# Test Model Trainer
# ============================================================================

class TestModelTrainer:
    """Tests for ModelTrainer orchestration."""
    
    def test_initialization(self, trainer):
        """Trainer initializes with 4 agents."""
        assert len(trainer.agents) == 4
        assert 'naive_bayes' in trainer.agents
        assert 'svm' in trainer.agents
        assert 'random_forest' in trainer.agents
        assert 'logistic_regression' in trainer.agents
    
    def test_get_agent(self, trainer):
        """Can retrieve specific agents."""
        nb_agent = trainer.get_agent('naive_bayes')
        assert isinstance(nb_agent, NaiveBayesAgent)
    
    def test_get_agent_invalid(self, trainer):
        """Invalid agent name raises error."""
        with pytest.raises(ValueError):
            trainer.get_agent('invalid_agent')
    
    def test_train_all(self, trainer, sample_data):
        """Training all agents succeeds."""
        X_train, y_train, _, _ = sample_data
        
        times = trainer.train_all(X_train, y_train)
        
        assert len(times) == 4
        assert all(isinstance(t, float) for t in times.values())
        assert all(trainer.agents[name].is_trained for name in trainer.agents)
    
    def test_evaluate_all(self, trainer, sample_data):
        """Evaluation of all agents succeeds."""
        X_train, y_train, X_test, y_test = sample_data
        
        trainer.train_all(X_train, y_train)
        results = trainer.evaluate_all(X_test, y_test)
        
        assert len(results) == 4
        assert all('accuracy' in results[name] for name in results)
        assert all('precision' in results[name] for name in results)
        assert all('recall' in results[name] for name in results)
        assert all('f1' in results[name] for name in results)
    
    def test_predict_ensemble(self, trainer, sample_data):
        """Ensemble predictions work correctly."""
        X_train, y_train, X_test, _ = sample_data
        
        trainer.train_all(X_train, y_train)
        consensus, conf, details = trainer.predict_ensemble(X_test[0])
        
        assert consensus in [0, 1]
        assert 0.0 <= conf <= 1.0
        assert 'individual_predictions' in details
        assert 'individual_confidences' in details
        assert len(details['individual_predictions']) == 4
    
    def test_ensemble_no_trained_agents(self, trainer):
        """Ensemble fails if no agents trained."""
        X_test = np.random.rand(1, 1004)
        
        with pytest.raises(ValueError):
            trainer.predict_ensemble(X_test)
    
    def test_get_results_summary(self, trainer, sample_data):
        """Results summary captures all info."""
        X_train, y_train, X_test, y_test = sample_data
        
        trainer.train_all(X_train, y_train)
        trainer.evaluate_all(X_test, y_test)
        
        summary = trainer.get_results_summary()
        assert 'training_times' in summary
        assert 'validation_results' in summary
    
    def test_get_agent_rankings(self, trainer, sample_data):
        """Agent rankings work correctly."""
        X_train, y_train, X_test, y_test = sample_data
        
        trainer.train_all(X_train, y_train)
        trainer.evaluate_all(X_test, y_test)
        
        rankings = trainer.get_agent_rankings('accuracy')
        
        assert len(rankings) > 0
        assert all(isinstance(name, str) for name, _ in rankings)
        assert all(isinstance(score, float) for _, score in rankings)
        # Rankings should be sorted
        assert rankings == sorted(rankings, key=lambda x: x[1], reverse=True)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for full pipeline."""
    
    def test_full_pipeline(self, sample_data):
        """Full training and evaluation pipeline works."""
        X_train, y_train, X_test, y_test = sample_data
        
        trainer = ModelTrainer()
        
        # Train all
        times = trainer.train_all(X_train, y_train)
        assert len(times) == 4
        
        # Evaluate all
        results = trainer.evaluate_all(X_test, y_test)
        assert len(results) == 4
        
        # Make ensemble prediction
        consensus, conf, details = trainer.predict_ensemble(X_test[0])
        assert consensus in [0, 1]
        
        # Get summary
        summary = trainer.get_results_summary()
        assert 'training_times' in summary
    
    def test_multiple_agents_agreement(self, sample_data):
        """Test ensemble with all agents trained."""
        X_train, y_train, X_test, _ = sample_data
        
        trainer = ModelTrainer()
        trainer.train_all(X_train, y_train)
        
        # All agents should make predictions
        for agent_name, agent in trainer.agents.items():
            assert agent.is_trained, f"{agent_name} not trained"
            pred, conf = agent.predict(X_test[0])
            assert pred in [0, 1]
            assert 0.0 <= conf <= 1.0
