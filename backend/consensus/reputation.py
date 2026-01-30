"""
Agent Reputation Management System
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from backend.shared.exceptions_v2 import ConsensusException


@dataclass
class AgentReputation:
    """Reputation metrics for a single agent"""
    agent_name: str
    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy: float = 0.0
    current_weight: float = 1.0
    confidence_avg: float = 0.0
    confidence_std: float = 0.0
    minority_correct: int = 0  # Times agent was right when majority was wrong
    majority_correct: int = 0  # Times agent was right when majority was right
    both_wrong: int = 0  # Times agent and majority both wrong
    last_updated: datetime = field(default_factory=datetime.utcnow)
    weight_history: List[float] = field(default_factory=list)
    accuracy_history: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "agent_name": self.agent_name,
            "total_predictions": self.total_predictions,
            "correct_predictions": self.correct_predictions,
            "accuracy": float(self.accuracy),
            "current_weight": float(self.current_weight),
            "confidence_avg": float(self.confidence_avg),
            "confidence_std": float(self.confidence_std),
            "minority_correct": self.minority_correct,
            "majority_correct": self.majority_correct,
            "both_wrong": self.both_wrong,
            "last_updated": self.last_updated.isoformat(),
            "weight_history": [float(w) for w in self.weight_history[-100:]],  # Last 100
            "accuracy_history": [float(a) for a in self.accuracy_history[-100:]],  # Last 100
        }


class ReputationManager:
    """
    Manages agent reputation scores and history
    """
    
    def __init__(self):
        """Initialize reputation manager"""
        self.reputations: Dict[str, AgentReputation] = {}
        self.prediction_records: List[Dict[str, Any]] = []
    
    def initialize_agent(self, agent_name: str, initial_weight: float = 1.0) -> None:
        """Initialize reputation for a new agent"""
        if agent_name in self.reputations:
            raise ConsensusException(f"Agent {agent_name} already initialized")
        
        self.reputations[agent_name] = AgentReputation(
            agent_name=agent_name,
            current_weight=initial_weight,
        )
    
    def record_prediction(
        self,
        agent_name: str,
        predicted_class: int,
        true_class: int,
        confidence: float,
        majority_class: int,
    ) -> None:
        """
        Record a prediction for reputation tracking
        
        Args:
            agent_name: Name of the agent
            predicted_class: Class predicted by agent
            true_class: Ground truth class
            confidence: Agent's confidence in prediction
            majority_class: Majority vote prediction
        """
        if agent_name not in self.reputations:
            self.initialize_agent(agent_name)
        
        rep = self.reputations[agent_name]
        
        # Update counts
        rep.total_predictions += 1
        agent_correct = (predicted_class == true_class)
        
        if agent_correct:
            rep.correct_predictions += 1
            
            majority_correct = (majority_class == true_class)
            if majority_correct:
                rep.majority_correct += 1
            else:
                rep.minority_correct += 1
        else:
            majority_correct = (majority_class == true_class)
            if not majority_correct:
                rep.both_wrong += 1
        
        # Update accuracy
        rep.accuracy = rep.correct_predictions / rep.total_predictions
        
        # Update confidence stats
        old_avg = rep.confidence_avg
        rep.confidence_avg = (
            (old_avg * (rep.total_predictions - 1) + confidence) / rep.total_predictions
        )
        
        rep.last_updated = datetime.utcnow()
        
        # Record prediction
        self.prediction_records.append({
            "agent_name": agent_name,
            "predicted_class": predicted_class,
            "true_class": true_class,
            "correct": agent_correct,
            "confidence": confidence,
            "majority_class": majority_class,
            "timestamp": datetime.utcnow(),
        })
    
    def update_weight(self, agent_name: str, new_weight: float) -> None:
        """Update agent weight and record history"""
        if agent_name not in self.reputations:
            raise ConsensusException(f"Unknown agent: {agent_name}")
        
        rep = self.reputations[agent_name]
        rep.current_weight = new_weight
        rep.weight_history.append(new_weight)
        rep.accuracy_history.append(rep.accuracy)
        rep.last_updated = datetime.utcnow()
    
    def get_reputation(self, agent_name: str) -> AgentReputation:
        """Get reputation for a single agent"""
        if agent_name not in self.reputations:
            raise ConsensusException(f"Unknown agent: {agent_name}")
        return self.reputations[agent_name]
    
    def get_all_reputations(self) -> Dict[str, AgentReputation]:
        """Get reputations for all agents"""
        return self.reputations.copy()
    
    def get_reputation_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all agent reputations"""
        return {
            agent_name: rep.to_dict()
            for agent_name, rep in self.reputations.items()
        }
    
    def rank_agents_by_accuracy(self) -> List[Tuple[str, float]]:
        """Rank agents by accuracy"""
        ranked = sorted(
            [(name, rep.accuracy) for name, rep in self.reputations.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked
    
    def rank_agents_by_weight(self) -> List[Tuple[str, float]]:
        """Rank agents by current weight"""
        ranked = sorted(
            [(name, rep.current_weight) for name, rep in self.reputations.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed statistics for an agent"""
        if agent_name not in self.reputations:
            raise ConsensusException(f"Unknown agent: {agent_name}")
        
        rep = self.reputations[agent_name]
        
        # Calculate win rate vs majority
        if rep.minority_correct + rep.majority_correct > 0:
            win_vs_majority = rep.minority_correct / (rep.minority_correct + rep.majority_correct)
        else:
            win_vs_majority = 0.0
        
        # Calculate agreement rate with majority
        majority_agreements = rep.majority_correct + rep.both_wrong
        if rep.total_predictions > 0:
            agreement_rate = majority_agreements / rep.total_predictions
        else:
            agreement_rate = 0.0
        
        return {
            "agent_name": agent_name,
            "total_predictions": rep.total_predictions,
            "accuracy": rep.accuracy,
            "current_weight": rep.current_weight,
            "confidence_avg": rep.confidence_avg,
            "minority_correct": rep.minority_correct,
            "majority_correct": rep.majority_correct,
            "both_wrong": rep.both_wrong,
            "win_vs_majority_rate": win_vs_majority,
            "agreement_with_majority": agreement_rate,
            "weight_trend": "increasing" if len(rep.weight_history) > 1 and rep.weight_history[-1] > rep.weight_history[-2] else "decreasing" if len(rep.weight_history) > 1 else "stable",
        }
    
    def reset_all(self) -> None:
        """Reset all reputation data (dangerous - use with caution)"""
        self.reputations = {}
        self.prediction_records = []
