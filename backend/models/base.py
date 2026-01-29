"""
Base Agent Interface for Sentinel-Net

Abstract base class defining the interface for all ML model agents.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AgentBase(ABC):
    """
    Abstract base class for all ML model agents.
    
    Defines the interface that all agents must implement. Each agent:
    - Makes predictions on SMS messages
    - Provides confidence scores
    - Generates reasoning for decisions
    - Maintains reputation weight
    
    Attributes:
        agent_id (str): Unique identifier for this agent
        weight (float): Current reputation weight (starts at 1.0)
        model: The underlying ML model
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize agent.
        
        Args:
            agent_id (str): Unique identifier for this agent
                           (e.g., 'agent_nb', 'agent_svm')
        """
        self.agent_id = agent_id
        self.weight = 1.0  # Start with neutral reputation
        self.model = None
        self.is_trained = False
        logger.info(f"Initialized agent: {agent_id}")
    
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the model on provided data.
        
        Args:
            X (np.ndarray): Training features of shape (n_samples, n_features)
            y (np.ndarray): Training labels of shape (n_samples,)
            
        Raises:
            ValueError: If X or y are invalid
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        X: np.ndarray,
        return_confidence: bool = True
    ) -> Tuple[int, float]:
        """
        Make prediction on new data.
        
        Args:
            X (np.ndarray): Features to predict on. Shape (1, n_features) or (n_samples, n_features)
            return_confidence (bool): Whether to return confidence score
            
        Returns:
            Tuple of (prediction, confidence):
            - prediction (int): Class label (0 or 1)
            - confidence (float): Confidence score (0.0 to 1.0)
            
        Example:
            >>> prediction, confidence = agent.predict(X_test)
            >>> print(f"Predicted: {prediction}, Confidence: {confidence:.2f}")
        """
        pass
    
    @abstractmethod
    def _generate_reasoning(
        self,
        X: np.ndarray,
        prediction: int
    ) -> Dict[str, Any]:
        """
        Generate human-readable reasoning for the prediction.
        
        Args:
            X (np.ndarray): Input features
            prediction (int): The prediction made
            
        Returns:
            Dict with reasoning details. Should include:
            - 'reasoning': str - Human-readable explanation
            - 'top_features': List[str] - Top influential features
            - 'confidence_factors': Dict - Why confident or not
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information.
        
        Returns:
            Dict with agent metadata
        """
        return {
            'agent_id': self.agent_id,
            'model_type': self.__class__.__name__,
            'is_trained': self.is_trained,
            'weight': self.weight
        }
    
    def reset_weight(self) -> None:
        """Reset weight to initial value (1.0)."""
        self.weight = 1.0
    
    def update_weight(self, multiplier: float) -> None:
        """
        Update weight by multiplying with factor.
        
        Args:
            multiplier (float): Factor to multiply weight by
                              (e.g., 1.05 for +5%, 0.90 for -10%)
        """
        self.weight *= multiplier
        # Clamp to reasonable bounds
        self.weight = max(0.1, min(5.0, self.weight))
