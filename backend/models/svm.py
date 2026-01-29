"""
Support Vector Machine Agent Implementation

Geometric boundary-based classifier using SVM algorithm.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

from typing import Dict, Tuple, Any
import numpy as np
from sklearn.svm import SVC
import logging

from .base import AgentBase

logger = logging.getLogger(__name__)


class SVMAgent(AgentBase):
    """
    Support Vector Machine Agent - "The Boundary Guard"
    
    Uses geometric boundaries in feature space to classify.
    Often robust to noise.
    
    Attributes:
        agent_id (str): 'agent_svm'
        model (SVC): Fitted SVM model
    """
    
    def __init__(self, agent_id: str = "agent_svm"):
        """
        Initialize SVM agent.
        
        Args:
            agent_id (str): Unique identifier (default: 'agent_svm')
        """
        super().__init__(agent_id)
        self.model = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train SVM model.
        
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
        Predict using SVM.
        
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
        Generate reasoning based on decision boundary.
        
        Args:
            X (np.ndarray): Input features
            prediction (int): The prediction (0=ham, 1=spam)
            
        Returns:
            Dict with reasoning explanation
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get decision function value (distance from boundary)
        decision_distance = self.model.decision_function(X)[0]
        distance_magnitude = abs(decision_distance)
        
        reasoning = {
            'reasoning': (
                f"SVM: {('SPAM' if prediction == 1 else 'HAM')} "
                f"based on geometric decision boundary (distance: {distance_magnitude:.2f})"
            ),
            'boundary_distance': float(decision_distance),
            'boundary_side': 'spam_side' if decision_distance > 0 else 'ham_side',
            'confidence_factor': 'High' if distance_magnitude > 1.0 else 'Low',
            'model_name': 'Support Vector Machine',
            'algorithm': 'RBF kernel geometric classification'
        }
        
        return reasoning
