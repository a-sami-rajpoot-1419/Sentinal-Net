"""
Unit Tests for ModelTrainer - Sentinel-Net

Tests for the model trainer orchestrator.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pytest
import numpy as np
from backend.models.trainer import ModelTrainer


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_data():
    """Generate sample training data."""
    np.random.seed(42)
    n_samples_train = 80
    n_samples_val = 20
    n_features = 1004
    
    X_train = np.random.rand(n_samples_train, n_features)
    y_train = np.random.randint(0, 2, n_samples_train)
    
    X_val = np.random.rand(n_samples_val, n_features)
    y_val = np.random.randint(0, 2, n_samples_val)
    
    return X_train, y_train, X_val, y_val


@pytest.fixture
def sample_single_sample():
    """Generate single sample for prediction."""
    np.random.seed(42)
    X = np.random.rand(1, 1004)
    return X


@pytest.fixture
def trainer():
    """Create ModelTrainer instance."""
    return ModelTrainer()


# ============================================================================
# Trainer Initialization Tests
# ============================================================================

class TestModelTrainerInitialization:
    """Test ModelTrainer initialization."""
    
    def test_initialization(self, trainer):
        """Trainer should initialize with 4 agents."""
        assert len(trainer.agents) == 4
        assert 'naive_bayes' in trainer.agents
        assert 'svm' in trainer.agents
        assert 'random_forest' in trainer.agents
        assert 'logistic_regression' in trainer.agents
    
    def test_agent_types(self, trainer):
        """All agents should be correct type."""
        from backend.models.naive_bayes import NaiveBayesAgent
        from backend.models.svm import SVMAgent
        from backend.models.random_forest import RandomForestAgent
        from backend.models.logistic_regression import LogisticRegressionAgent
        
        assert isinstance(trainer.agents['naive_bayes'], NaiveBayesAgent)
        assert isinstance(trainer.agents['svm'], SVMAgent)
        assert isinstance(trainer.agents['random_forest'], RandomForestAgent)
        assert isinstance(trainer.agents['logistic_regression'], LogisticRegressionAgent)
    
    def test_empty_training_results(self, trainer):
        """Training results should be empty initially."""
        assert trainer.training_results == {}


# ============================================================================
# Training Tests
# ============================================================================

class TestModelTrainerTraining:
    """Test training functionality."""
    
    def test_train_all_without_validation(self, trainer, sample_data):
        """Should train all agents without validation set."""
        X_train, y_train, _, _ = sample_data
        results = trainer.train_all(X_train, y_train)
        
        assert 'naive_bayes' in results
        assert 'svm' in results
        assert 'random_forest' in results
        assert 'logistic_regression' in results
        assert 'total_training_time' in results
    
    def test_train_all_with_validation(self, trainer, sample_data):
        """Should train all agents with validation set."""
        X_train, y_train, X_val, y_val = sample_data
        results = trainer.train_all(X_train, y_train, X_val, y_val)
        
        for agent_name in ['naive_bayes', 'svm', 'random_forest', 'logistic_regression']:
            assert agent_name in results
            assert 'train_accuracy' in results[agent_name]
            assert 'val_accuracy' in results[agent_name]
            assert 'training_time' in results[agent_name]
    
    def test_training_results_accuracy_range(self, trainer, sample_data):
        """Accuracy should be between 0 and 1."""
        X_train, y_train, X_val, y_val = sample_data
        results = trainer.train_all(X_train, y_train, X_val, y_val)
        
        for agent_name in ['naive_bayes', 'svm', 'random_forest', 'logistic_regression']:
            train_acc = results[agent_name]['train_accuracy']
            val_acc = results[agent_name]['val_accuracy']
            assert 0.0 <= train_acc <= 1.0
            assert 0.0 <= val_acc <= 1.0
    
    def test_training_time_positive(self, trainer, sample_data):
        """Training time should be positive."""
        X_train, y_train, X_val, y_val = sample_data
        results = trainer.train_all(X_train, y_train, X_val, y_val)
        
        for agent_name in ['naive_bayes', 'svm', 'random_forest', 'logistic_regression']:
            training_time = results[agent_name]['training_time']
            assert training_time > 0.0
        
        assert results['total_training_time'] > 0.0


# ============================================================================
# Prediction Tests
# ============================================================================

class TestModelTrainerPrediction:
    """Test prediction functionality."""
    
    def test_predict_all(self, trainer, sample_data, sample_single_sample):
        """Should get predictions from all agents."""
        X_train, y_train, _, _ = sample_data
        trainer.train_all(X_train, y_train)
        
        predictions = trainer.predict_all(sample_single_sample)
        
        assert len(predictions) == 4
        assert 'naive_bayes' in predictions
        assert 'svm' in predictions
        assert 'random_forest' in predictions
        assert 'logistic_regression' in predictions
    
    def test_predict_all_types(self, trainer, sample_data, sample_single_sample):
        """Predictions should be tuples of correct types."""
        X_train, y_train, _, _ = sample_data
        trainer.train_all(X_train, y_train)
        
        predictions = trainer.predict_all(sample_single_sample)
        
        for agent_name, (prediction, confidence) in predictions.items():
            assert isinstance(prediction, (int, np.integer))
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0
    
    def test_get_predictions_with_reasoning(self, trainer, sample_data, sample_single_sample):
        """Should get predictions with reasoning from all agents."""
        X_train, y_train, _, _ = sample_data
        trainer.train_all(X_train, y_train)
        
        predictions = trainer.get_predictions_with_reasoning(sample_single_sample)
        
        assert len(predictions) == 4
        assert all(isinstance(p, dict) for p in predictions)
        assert all('agent_id' in p for p in predictions)
        assert all('prediction' in p for p in predictions)
        assert all('confidence' in p for p in predictions)
        assert all('reasoning' in p for p in predictions)
        assert all('weight' in p for p in predictions)


# ============================================================================
# Weight Management Tests
# ============================================================================

class TestModelTrainerWeights:
    """Test weight management."""
    
    def test_get_agent_weights(self, trainer):
        """Should get weights for all agents."""
        weights = trainer.get_agent_weights()
        
        assert len(weights) == 4
        assert all(isinstance(w, float) for w in weights.values())
        assert all(w == 1.0 for w in weights.values())  # Initial weight is 1.0
    
    def test_update_agent_weight(self, trainer):
        """Should update weight for specific agent."""
        trainer.update_agent_weights('naive_bayes', 2.5)
        
        weights = trainer.get_agent_weights()
        assert weights['naive_bayes'] == 2.5
        assert weights['svm'] == 1.0
        assert weights['random_forest'] == 1.0
        assert weights['logistic_regression'] == 1.0
    
    def test_update_multiple_weights(self, trainer):
        """Should update multiple weights."""
        trainer.update_agent_weights('naive_bayes', 1.5)
        trainer.update_agent_weights('svm', 0.8)
        trainer.update_agent_weights('random_forest', 2.0)
        
        weights = trainer.get_agent_weights()
        assert weights['naive_bayes'] == 1.5
        assert weights['svm'] == 0.8
        assert weights['random_forest'] == 2.0
        assert weights['logistic_regression'] == 1.0
    
    def test_update_invalid_agent(self, trainer):
        """Should handle invalid agent name gracefully."""
        trainer.update_agent_weights('invalid_agent', 2.0)
        # Should not raise exception, just silently skip


# ============================================================================
# Evaluation Tests
# ============================================================================

class TestModelTrainerEvaluation:
    """Test evaluation functionality."""
    
    def test_evaluate_on_training_data(self, trainer, sample_data):
        """Should evaluate on training data."""
        X_train, y_train, _, _ = sample_data
        trainer.train_all(X_train, y_train)
        
        agent = trainer.agents['naive_bayes']
        accuracy = trainer._evaluate(agent, X_train, y_train)
        
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0
    
    def test_evaluate_on_validation_data(self, trainer, sample_data):
        """Should evaluate on validation data."""
        X_train, y_train, X_val, y_val = sample_data
        trainer.train_all(X_train, y_train)
        
        agent = trainer.agents['random_forest']
        accuracy = trainer._evaluate(agent, X_val, y_val)
        
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0


# ============================================================================
# Integration Tests
# ============================================================================

class TestModelTrainerIntegration:
    """Integration tests for full workflow."""
    
    def test_complete_workflow(self, trainer, sample_data, sample_single_sample):
        """Test complete train -> predict -> reason workflow."""
        X_train, y_train, X_val, y_val = sample_data
        
        # Train
        train_results = trainer.train_all(X_train, y_train, X_val, y_val)
        assert train_results
        
        # Predict
        predictions = trainer.predict_all(sample_single_sample)
        assert len(predictions) == 4
        
        # Get weights
        weights = trainer.get_agent_weights()
        assert len(weights) == 4
        
        # Modify weights
        trainer.update_agent_weights('svm', 1.5)
        new_weights = trainer.get_agent_weights()
        assert new_weights['svm'] == 1.5
        
        # Get reasoning
        pred_with_reasoning = trainer.get_predictions_with_reasoning(sample_single_sample)
        assert len(pred_with_reasoning) == 4
        assert all('reasoning' in p for p in pred_with_reasoning)
    
    def test_multiple_predictions(self, trainer, sample_data):
        """Should handle multiple sequential predictions."""
        X_train, y_train, _, _ = sample_data
        trainer.train_all(X_train, y_train)
        
        np.random.seed(42)
        for i in range(5):
            X_test = np.random.rand(1, 1004)
            predictions = trainer.predict_all(X_test)
            assert len(predictions) == 4
