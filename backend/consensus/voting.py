"""
Weighted Voting System for Consensus
"""

from typing import Dict, Tuple, Any
from dataclasses import dataclass
import numpy as np
from backend.shared.exceptions_v2 import ConsensusError


@dataclass
class VotingResult:
    """Result from voting mechanism"""
    predicted_class: int
    confidence: float
    votes_per_class: Dict[int, float]  # {class: total_weight}
    weight_distribution: Dict[str, float]  # {agent: weight}


class WeightedVoter:
    """
    Weighted voting system for agent predictions
    """
    
    @staticmethod
    def vote(
        predictions: Dict[str, Tuple[int, float]],
        weights: Dict[str, float],
    ) -> VotingResult:
        """
        Perform weighted voting among agents
        
        Args:
            predictions: {agent_name: (predicted_class, confidence)}
            weights: {agent_name: weight}
            
        Returns:
            VotingResult with final prediction and confidence
        """
        if not predictions:
            raise ConsensusError("No predictions provided")
        
        if set(predictions.keys()) != set(weights.keys()):
            raise ConsensusError("Agent names in predictions and weights don't match")
        
        # Aggregate votes weighted by agent weight and confidence
        votes_per_class: Dict[int, float] = {}
        
        for agent_name, (predicted_class, confidence) in predictions.items():
            weight = weights[agent_name]
            vote_weight = weight * confidence  # Combine agent weight with confidence
            
            if predicted_class not in votes_per_class:
                votes_per_class[predicted_class] = 0.0
            
            votes_per_class[predicted_class] += vote_weight
        
        # Get winning class
        final_class = max(votes_per_class, key=votes_per_class.get)
        
        # Calculate confidence as proportion of total weighted votes
        total_votes = sum(votes_per_class.values())
        confidence = votes_per_class[final_class] / total_votes if total_votes > 0 else 0.0
        
        return VotingResult(
            predicted_class=final_class,
            confidence=confidence,
            votes_per_class=votes_per_class,
            weight_distribution=weights.copy(),
        )
    
    @staticmethod
    def get_majority_prediction(
        predictions: Dict[str, Tuple[int, float]],
    ) -> int:
        """Get simple majority prediction (unweighted)"""
        classes = [pred[0] for pred in predictions.values()]
        if not classes:
            raise ConsensusError("No predictions provided")
        return max(set(classes), key=classes.count)
    
    @staticmethod
    def calculate_consensus_confidence(
        votes_per_class: Dict[int, float],
        consensus_threshold: float = 0.5,
    ) -> Tuple[float, bool]:
        """
        Calculate confidence and check if consensus meets threshold
        
        Args:
            votes_per_class: {class: total_weight}
            consensus_threshold: Minimum confidence required
            
        Returns:
            (confidence, meets_threshold)
        """
        if not votes_per_class:
            return 0.0, False
        
        total_votes = sum(votes_per_class.values())
        if total_votes == 0:
            return 0.0, False
        
        max_votes = max(votes_per_class.values())
        confidence = max_votes / total_votes
        
        meets_threshold = confidence >= consensus_threshold
        
        return confidence, meets_threshold
