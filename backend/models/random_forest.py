"""
Random Forest Agent Implementation

Ensemble classifier using multiple decision trees.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

from typing import Dict, Tuple, Any
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

from .base import AgentBase

logger = logging.getLogger(__name__)


class RandomForestAgent(AgentBase):
    """
    Random Forest Agent - "The Democrat"
    
    Ensemble of decision trees voting on classification.
    Often provides good accuracy with robustness.
    
    Attributes:
        agent_id (str): 'agent_rf'
        model (RandomForestClassifier): Fitted RF model
    """
    
    def __init__(self, agent_id: str = "agent_rf"):
        """
        Initialize Random Forest agent.
        
        Args:
            agent_id (str): Unique identifier (default: 'agent_rf')
        """
        super().__init__(agent_id)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Random Forest model.
        
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
        Predict using Random Forest.
        
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
        
        # Get confidence (majority vote ratio)
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
        Generate reasoning based on tree votes and feature importance.
        
        Args:
            X (np.ndarray): Input features
            prediction (int): The prediction (0=ham, 1=spam)
            
        Returns:
            Dict with reasoning explanation
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get feature importances
        feature_importance = self.model.feature_importances_
        top_feature_indices = np.argsort(feature_importance)[-5:][::-1]
        
        # Get decision paths for ensemble
        proba = self.model.predict_proba(X)[0]
        
        reasoning = {
            'reasoning': (
                f"Random Forest: {('SPAM' if prediction == 1 else 'HAM')} "
                f"based on voting of {self.model.n_estimators} decision trees"
            ),
            'n_trees': self.model.n_estimators,
            'tree_votes_for_class': int(proba[int(prediction)] * self.model.n_estimators),
            'top_important_features': [
                f"feature_{idx}" for idx in top_feature_indices[:3]
            ],
            'ensemble_agreement': float(proba[int(prediction)]),
            'model_name': 'Random Forest',
            'algorithm': 'Ensemble voting of decision trees'
        }
        
        return reasoning
