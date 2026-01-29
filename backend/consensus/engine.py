"""
Consensus Engine - Core orchestrator for RWPV mechanism
"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from backend.models.base import AgentBase
from backend.shared.utils import compute_weighted_vote, consensus_confidence
from backend.shared.exceptions_v2 import ConsensusError


@dataclass
class ConsensusResult:
    """Result from consensus voting"""
    predicted_class: int
    confidence: float
    agent_predictions: Dict[str, Tuple[int, float]]  # {agent_name: (class, confidence)}
    weights: Dict[str, float]  # {agent_name: weight}
    reasoning: Dict[str, str]  # {agent_name: reasoning}
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "predicted_class": self.predicted_class,
            "confidence": float(self.confidence),
            "agent_predictions": {
                k: {"class": int(v[0]), "confidence": float(v[1])}
                for k, v in self.agent_predictions.items()
            },
            "weights": {k: float(v) for k, v in self.weights.items()},
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
        }


class ConsensusEngine:
    """
    Phase 4: Reward/Weighted/Penalty/Voting (RWPV) Consensus Engine
    
    Combines predictions from 4 ML agents using weighted voting and
    dynamically adjusts agent weights based on prediction accuracy.
    """
    
    def __init__(
        self,
        agents: Dict[str, AgentBase],
        weight_reward_correct: float = 1.05,
        weight_penalty_wrong: float = 0.90,
        weight_reward_minority: float = 1.15,
        weight_penalty_both_wrong: float = 0.85,
        weight_min: float = 0.1,
        weight_max: float = 5.0,
        consensus_threshold: float = 0.5,
    ):
        """
        Initialize Consensus Engine
        
        Args:
            agents: Dict of agent_name -> AgentBase instances
            weight_reward_correct: Multiplier for correct predictions
            weight_penalty_wrong: Multiplier for wrong predictions
            weight_reward_minority: Multiplier when agent is right but minority
            weight_penalty_both_wrong: Multiplier when both agent and majority wrong
            weight_min: Minimum weight for any agent
            weight_max: Maximum weight for any agent
            consensus_threshold: Confidence threshold for final prediction
        """
        self.agents = agents
        self.weight_reward_correct = weight_reward_correct
        self.weight_penalty_wrong = weight_penalty_wrong
        self.weight_reward_minority = weight_reward_minority
        self.weight_penalty_both_wrong = weight_penalty_both_wrong
        self.weight_min = weight_min
        self.weight_max = weight_max
        self.consensus_threshold = consensus_threshold
        
        # Initialize weights to 1.0 for all agents
        self.weights: Dict[str, float] = {name: 1.0 for name in agents.keys()}
        
        # Tracking for reputation system
        self.prediction_history: List[Dict[str, Any]] = []
    
    def predict(self, X: np.ndarray) -> ConsensusResult:
        """
        Get consensus prediction using all agents
        
        Args:
            X: Input features (N, 1004)
            
        Returns:
            ConsensusResult with final prediction and confidence
        """
        if X.shape[0] != 1:
            raise ConsensusError(f"Expected single sample, got {X.shape[0]}")
        
        # Get predictions from all agents
        agent_predictions = {}
        reasoning = {}
        
        for agent_name, agent in self.agents.items():
            predicted_class, confidence = agent.predict(X)
            agent_predictions[agent_name] = (predicted_class, confidence)
            reasoning[agent_name] = agent._generate_reasoning()
        
        # Perform weighted voting
        final_class, final_confidence = compute_weighted_vote(
            predictions=agent_predictions,
            weights=self.weights,
        )
        
        result = ConsensusResult(
            predicted_class=final_class,
            confidence=final_confidence,
            agent_predictions=agent_predictions,
            weights=self.weights.copy(),
            reasoning=reasoning,
        )
        
        return result
    
    def batch_predict(self, X: np.ndarray) -> List[ConsensusResult]:
        """
        Get consensus predictions for multiple samples
        
        Args:
            X: Input features (N, 1004)
            
        Returns:
            List of ConsensusResult objects
        """
        results = []
        for i in range(X.shape[0]):
            sample = X[i:i+1]
            result = self.predict(sample)
            results.append(result)
        return results
    
    def update_weights_from_feedback(
        self,
        true_label: int,
        predictions: Dict[str, Tuple[int, float]],
    ) -> Dict[str, float]:
        """
        Update agent weights based on prediction accuracy (RWPV mechanism)
        
        Args:
            true_label: Ground truth label
            predictions: Dict of agent_name -> (predicted_class, confidence)
            
        Returns:
            Updated weights dictionary
        """
        # Get majority prediction
        majority_class = self._get_majority_prediction(predictions)
        
        # Update weights for each agent
        for agent_name, (predicted_class, confidence) in predictions.items():
            agent_correct = (predicted_class == true_label)
            majority_correct = (majority_class == true_label)
            
            if agent_correct and majority_correct:
                # Reward correct prediction
                multiplier = self.weight_reward_correct
            elif agent_correct and not majority_correct:
                # Reward when agent is right but minority is wrong
                multiplier = self.weight_reward_minority
            elif not agent_correct and majority_correct:
                # Penalty when agent wrong but majority right
                multiplier = self.weight_penalty_wrong
            else:
                # Penalty when both agent and majority wrong
                multiplier = self.weight_penalty_both_wrong
            
            # Apply multiplier and clamp to bounds
            self.weights[agent_name] *= multiplier
            self.weights[agent_name] = np.clip(
                self.weights[agent_name],
                self.weight_min,
                self.weight_max,
            )
        
        # Normalize weights to sum to number of agents
        weight_sum = sum(self.weights.values())
        num_agents = len(self.agents)
        for agent_name in self.weights:
            self.weights[agent_name] = (self.weights[agent_name] / weight_sum) * num_agents
        
        # Store in history
        self.prediction_history.append({
            "true_label": true_label,
            "majority_class": majority_class,
            "predictions": predictions,
            "weights_after": self.weights.copy(),
            "timestamp": datetime.utcnow(),
        })
        
        return self.weights.copy()
    
    def _get_majority_prediction(
        self,
        predictions: Dict[str, Tuple[int, float]],
    ) -> int:
        """Get majority vote among agents"""
        classes = [pred[0] for pred in predictions.values()]
        return max(set(classes), key=classes.count)
    
    def get_agent_reputation(self, agent_name: str) -> Dict[str, Any]:
        """Get reputation statistics for an agent"""
        if agent_name not in self.agents:
            raise ConsensusError(f"Unknown agent: {agent_name}")
        
        agent_predictions = [
            h["predictions"].get(agent_name) 
            for h in self.prediction_history 
            if agent_name in h["predictions"]
        ]
        
        if not agent_predictions:
            return {
                "agent_name": agent_name,
                "total_predictions": 0,
                "accuracy": 0.0,
                "current_weight": self.weights[agent_name],
                "confidence_avg": 0.0,
            }
        
        predictions_valid = [p for p in agent_predictions if p is not None]
        true_labels = [h["true_label"] for h in self.prediction_history]
        
        correct = sum(
            pred[0] == true_label
            for pred, true_label in zip(predictions_valid, true_labels)
        )
        
        confidences = [pred[1] for pred in predictions_valid]
        
        return {
            "agent_name": agent_name,
            "total_predictions": len(predictions_valid),
            "accuracy": correct / len(predictions_valid) if predictions_valid else 0.0,
            "current_weight": self.weights[agent_name],
            "confidence_avg": sum(confidences) / len(confidences) if confidences else 0.0,
        }
    
    def get_all_reputations(self) -> Dict[str, Dict[str, Any]]:
        """Get reputation statistics for all agents"""
        return {
            agent_name: self.get_agent_reputation(agent_name)
            for agent_name in self.agents.keys()
        }
    
    def reset_weights(self) -> None:
        """Reset all weights to 1.0 (equal voting power)"""
        self.weights = {name: 1.0 for name in self.agents.keys()}
    
    def set_weight(self, agent_name: str, weight: float) -> None:
        """Manually set weight for an agent"""
        if agent_name not in self.agents:
            raise ConsensusError(f"Unknown agent: {agent_name}")
        
        weight = np.clip(weight, self.weight_min, self.weight_max)
        self.weights[agent_name] = weight
    
    def get_weights(self) -> Dict[str, float]:
        """Get current weights for all agents"""
        return self.weights.copy()
    
    def get_prediction_history(self) -> List[Dict[str, Any]]:
        """Get complete prediction history"""
        return self.prediction_history.copy()
