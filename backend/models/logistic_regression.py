"""
Logistic Regression Agent Implementation

Linear classifier using logistic regression algorithm.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

from typing import Dict, Tuple, Any
import numpy as np
from sklearn.linear_model import LogisticRegression
import logging

from .base import AgentBase

logger = logging.getLogger(__name__)


class LogisticRegressionAgent(AgentBase):
    """
    Logistic Regression Agent - "The Rationalist"
    
    Linear classifier based on logistic function.
    Simple baseline, fast inference.
    
    Attributes:
        agent_id (str): 'agent_lr'
        model (LogisticRegression): Fitted LR model
    """
    
    def __init__(self, agent_id: str = "agent_lr"):
        """
        Initialize Logistic Regression agent.
        
        Args:
            agent_id (str): Unique identifier (default: 'agent_lr')
        """
        super().__init__(agent_id)
        self.model = LogisticRegression(
            C=1.0,
            solver='lbfgs',
            max_iter=1000,
            random_state=42
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Logistic Regression model.
        
        Args:
            X (np.ndarray): Training features
            y (np.ndarray): Training labels (0/1)
        """
        if X.shape[0] == 0:
            raise ValueError("Training data cannot be empty")
        if X.shape[0] != len(y):
            raise ValueError("X and y must have same number of samples")
        
        logger.info(f"{self.agent_id}: Training on {X.shape[0]} samples")
        self.model.fit(X, y)
        self.is_trained = True
        logger.info(f"{self.agent_id}: Training complete")
    
    def predict(
        self,
        X: np.ndarray,
        return_confidence: bool = True
    ) -> Tuple[int, float]:
        """
        Predict using Logistic Regression.
        
        Args:
            X (np.ndarray): Features to predict
            return_confidence (bool): Whether to return confidence
            
        Returns:
            Tuple of (prediction, confidence)
        """
        if not self.is_trained:
            raise ValueError(f"{self.agent_id} not trained yet")
        
        # Ensure 2D array
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        
        # Get confidence (probability)
        if return_confidence:
            proba = self.model.predict_proba(X)[0]
            confidence = float(proba[int(prediction)])
        else:
            confidence = 0.0
        
        return int(prediction), confidence
    
    def _generate_reasoning(
        self,
        X: np.ndarray,
        prediction: int
    ) -> Dict[str, Any]:
        """
        Generate reasoning based on linear coefficients.
        
        Args:
            X (np.ndarray): Input features
            prediction (int): The prediction (0=ham, 1=spam)
            
        Returns:
            Dict with reasoning explanation
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get coefficients (feature weights)
        coefficients = self.model.coef_[0]
        
        # Get top positive and negative features
        top_positive_idx = np.argsort(coefficients)[-5:][::-1]
        top_negative_idx = np.argsort(coefficients)[:5]
        
        # Get decision function value
        decision_value = self.model.decision_function(X)[0]
        
        reasoning = {
            'reasoning': (
                f"Logistic Regression: {('SPAM' if prediction == 1 else 'HAM')} "
                f"based on linear combination of feature weights"
            ),
            'decision_value': float(decision_value),
            'top_spam_features': [f"feature_{idx}" for idx in top_positive_idx[:3]],
            'top_ham_features': [f"feature_{idx}" for idx in top_negative_idx[:3]],
            'model_name': 'Logistic Regression',
            'algorithm': 'Linear logistic classification',
            'complexity': 'Low - linear model'
        }
        
        return reasoning
