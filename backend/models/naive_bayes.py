"""
Naive Bayes Agent Implementation

Probabilistic classifier using multinomial Naive Bayes algorithm.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

from typing import Dict, Tuple, Any
import numpy as np
from sklearn.naive_bayes import MultinomialNB
import logging

from .base import AgentBase

logger = logging.getLogger(__name__)


class NaiveBayesAgent(AgentBase):
    """
    Naive Bayes ML Agent - "The Linguist"
    
    Uses probabilistic approach based on word frequencies.
    Fast training and inference.
    
    Attributes:
        agent_id (str): 'agent_nb'
        model (MultinomialNB): Fitted Naive Bayes model
        feature_names (np.ndarray): Names of TF-IDF features
    """
    
    def __init__(self, agent_id: str = "agent_nb"):
        """
        Initialize Naive Bayes agent.
        
        Args:
            agent_id (str): Unique identifier (default: 'agent_nb')
        """
        super().__init__(agent_id)
        self.model = MultinomialNB(alpha=1.0)  # Laplace smoothing
        self.feature_names = None
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Naive Bayes model.
        
        Args:
            X (np.ndarray): Training features (TF-IDF vectors)
            y (np.ndarray): Training labels (0/1)
        """
        if X.shape[0] == 0:
            raise ValueError("Training data cannot be empty")
        if X.shape[0] != len(y):
            raise ValueError("X and y must have same number of samples")
        
        logger.info(f"{self.agent_id}: Training on {X.shape[0]} samples, {X.shape[1]} features")
        self.model.fit(X, y)
        self.is_trained = True
        logger.info(f"{self.agent_id}: Training complete")
    
    def predict(
        self,
        X: np.ndarray,
        return_confidence: bool = True
    ) -> Tuple[int, float]:
        """
        Predict using Naive Bayes.
        
        Args:
            X (np.ndarray): Features to predict (shape: 1 or n samples x features)
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
        
        # Get confidence (probability of predicted class)
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
        Generate reasoning based on word probabilities.
        
        Args:
            X (np.ndarray): Input features
            prediction (int): The prediction (0=ham, 1=spam)
            
        Returns:
            Dict with reasoning explanation
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get feature log probabilities
        feature_log_prob = self.model.feature_log_prob_
        
        # Get top spam and ham indicators
        spam_features_idx = np.argsort(feature_log_prob[1])[-5:][::-1]
        ham_features_idx = np.argsort(feature_log_prob[0])[-5:][::-1]
        
        # Get active features in this sample
        active_features = np.where(X[0] > 0)[0]
        
        reasoning = {
            'reasoning': (
                f"Naive Bayes: {('SPAM' if prediction == 1 else 'HAM')} "
                f"based on word frequency patterns and probabilities"
            ),
            'top_spam_indicators': [
                f"word_{idx}" for idx in spam_features_idx[:3]
            ],
            'top_ham_indicators': [
                f"word_{idx}" for idx in ham_features_idx[:3]
            ],
            'active_features_count': len(active_features),
            'model_name': 'Multinomial Naive Bayes',
            'algorithm': 'Probabilistic word frequency analysis'
        }
        
        return reasoning
