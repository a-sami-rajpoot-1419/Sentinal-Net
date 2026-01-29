"""
Model Trainer - Orchestrates training of all agents

Handles training, evaluation, and benchmarking of all 4 ML models.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import time
from typing import Dict, List, Tuple, Any
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging

from .base import AgentBase
from .naive_bayes import NaiveBayesAgent
from .svm import SVMAgent
from .random_forest import RandomForestAgent
from .logistic_regression import LogisticRegressionAgent

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Orchestrates training and evaluation of all 4 ML agents.
    
    Manages:
    - Creating all 4 agent instances
    - Training each on provided data
    - Evaluating on validation/test data
    - Generating performance benchmarks
    - Managing agent lifecycle
    
    Attributes:
        agents (Dict[str, AgentBase]): Dictionary of all agents
        training_results (Dict): Results from training and evaluation
    """
    
    def __init__(self):
        """Initialize trainer with all 4 agents."""
        self.agents: Dict[str, AgentBase] = {
            'naive_bayes': NaiveBayesAgent('agent_nb'),
            'svm': SVMAgent('agent_svm'),
            'random_forest': RandomForestAgent('agent_rf'),
            'logistic_regression': LogisticRegressionAgent('agent_lr')
        }
        self.training_results: Dict[str, Any] = {}
        logger.info(f"ModelTrainer initialized with {len(self.agents)} agents")
    
    def train_all(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> Dict[str, float]:
        """
        Train all agents.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training labels
            
        Returns:
            Dict with training times for each agent
        """
        training_times = {}
        
        logger.info("Starting training of all agents...")
        
        for agent_name, agent in self.agents.items():
            start_time = time.time()
            try:
                agent.train(X_train, y_train)
                elapsed = time.time() - start_time
                training_times[agent_name] = elapsed
                logger.info(f"{agent_name}: Training complete in {elapsed:.2f}s")
            except Exception as e:
                logger.error(f"{agent_name}: Training failed - {str(e)}")
                raise
        
        self.training_results['training_times'] = training_times
        logger.info("All agents trained successfully")
        return training_times
    
    def evaluate_all(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray,
        dataset_name: str = "validation"
    ) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all agents on validation/test data.
        
        Args:
            X_val (np.ndarray): Validation features
            y_val (np.ndarray): Validation labels
            dataset_name (str): Name of dataset (for logging)
            
        Returns:
            Dict of evaluation metrics for each agent
        """
        eval_results = {}
        
        logger.info(f"Evaluating all agents on {dataset_name} data...")
        
        for agent_name, agent in self.agents.items():
            if not agent.is_trained:
                logger.warning(f"{agent_name}: Not trained, skipping evaluation")
                continue
            
            # Make predictions
            predictions = []
            start_time = time.time()
            for i in range(len(X_val)):
                pred, _ = agent.predict(X_val[i:i+1])
                predictions.append(pred)
            inference_time = time.time() - start_time
            
            predictions = np.array(predictions)
            
            # Calculate metrics
            accuracy = accuracy_score(y_val, predictions)
            precision = precision_score(y_val, predictions, zero_division=0)
            recall = recall_score(y_val, predictions, zero_division=0)
            f1 = f1_score(y_val, predictions, zero_division=0)
            
            eval_results[agent_name] = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1),
                'inference_time_total': float(inference_time),
                'inference_time_per_sample': float(inference_time / len(X_val)),
                'correct_predictions': int(accuracy * len(y_val)),
                'total_predictions': int(len(y_val))
            }
            
            logger.info(
                f"{agent_name}: Accuracy={accuracy:.4f}, "
                f"Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}"
            )
        
        self.training_results[f'{dataset_name}_results'] = eval_results
        return eval_results
    
    def predict_ensemble(
        self,
        X: np.ndarray,
        voting_strategy: str = 'majority'
    ) -> Tuple[int, float, Dict]:
        """
        Make ensemble prediction (consensus).
        
        Args:
            X (np.ndarray): Features to predict
            voting_strategy (str): 'majority' or 'weighted' (for Phase 4)
            
        Returns:
            Tuple of (consensus_prediction, confidence, details)
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        predictions = []
        confidences = []
        
        for agent_name, agent in self.agents.items():
            if agent.is_trained:
                pred, conf = agent.predict(X)
                predictions.append(pred)
                confidences.append(conf)
        
        if not predictions:
            raise ValueError("No trained agents available for prediction")
        
        # Majority voting
        consensus = int(np.round(np.mean(predictions)))
        ensemble_confidence = float(np.mean(confidences))
        
        details = {
            'individual_predictions': predictions,
            'individual_confidences': confidences,
            'consensus': consensus,
            'ensemble_confidence': ensemble_confidence,
            'agreement': np.sum(np.array(predictions) == consensus) / len(predictions)
        }
        
        return consensus, ensemble_confidence, details
    
    def get_agent(self, agent_name: str) -> AgentBase:
        """
        Get agent by name.
        
        Args:
            agent_name (str): Name of agent (e.g., 'naive_bayes', 'svm')
            
        Returns:
            AgentBase: The requested agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
        return self.agents[agent_name]
    
    def get_all_agents(self) -> Dict[str, AgentBase]:
        """Get all agents."""
        return self.agents.copy()
    
    def get_results_summary(self) -> Dict[str, Any]:
        """
        Get summary of all training and evaluation results.
        
        Returns:
            Dict with comprehensive results
        """
        return self.training_results.copy()
    
    def get_agent_rankings(self, metric: str = 'f1') -> List[Tuple[str, float]]:
        """
        Get agents ranked by metric.
        
        Args:
            metric (str): Metric to rank by (accuracy, precision, recall, f1)
            
        Returns:
            List of (agent_name, metric_value) tuples sorted by metric
        """
        if f'{metric}_results' not in self.training_results:
            logger.warning(f"No evaluation results available")
            return []
        
        results = self.training_results[f'{metric}_results']
        
        rankings = [
            (name, results[name].get(metric, 0.0))
            for name in results.keys()
        ]
        
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
