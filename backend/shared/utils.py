"""
Utilities Module - Sentinel-Net

Helper functions and utilities.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        str: Timestamp (e.g., "2026-01-29T14:30:45.123456")
    """
    return datetime.now().isoformat()


def log_section(title: str, char: str = "=", length: int = 80) -> None:
    """
    Log a formatted section header.
    
    Args:
        title (str): Section title
        char (str): Character to use for border (default: "=")
        length (int): Total line length (default: 80)
    """
    line = char * length
    logger.info(line)
    logger.info(title.center(length))
    logger.info(line)


def log_subsection(title: str, char: str = "-", length: int = 80) -> None:
    """
    Log a formatted subsection header.
    
    Args:
        title (str): Subsection title
        char (str): Character to use for border (default: "-")
        length (int): Total line length (default: 80)
    """
    logger.info(char * length)
    logger.info(title)
    logger.info(char * length)


def format_accuracy_dict(accuracy_dict: Dict[str, float]) -> str:
    """
    Format accuracy dictionary for logging.
    
    Args:
        accuracy_dict (Dict[str, float]): Dict of accuracies
        
    Returns:
        str: Formatted string
    """
    lines = []
    for agent_name, accuracy in accuracy_dict.items():
        if agent_name == 'total_training_time':
            lines.append(f"Total time: {accuracy:.2f}s")
        else:
            lines.append(f"{agent_name}: {accuracy:.3f}")
    return "\n".join(lines)


def compute_weighted_vote(
    predictions: Dict[str, Tuple[int, float]],
    weights: Dict[str, float]
) -> Tuple[int, float]:
    """
    Compute weighted majority vote.
    
    Args:
        predictions: Dict of {agent_name: (prediction, confidence)}
        weights: Dict of {agent_name: weight}
        
    Returns:
        Tuple of (final_prediction, weighted_confidence)
    """
    weighted_votes = {}
    
    for agent_name, (prediction, confidence) in predictions.items():
        weight = weights.get(agent_name, 1.0)
        weighted_score = weight * confidence
        
        if prediction not in weighted_votes:
            weighted_votes[prediction] = 0.0
        
        weighted_votes[prediction] += weighted_score
    
    if not weighted_votes:
        return 0, 0.5
    
    final_prediction = max(weighted_votes, key=weighted_votes.get)
    confidence = weighted_votes[final_prediction]
    
    # Normalize confidence to 0-1 range
    total_weight = sum(weighted_votes.values())
    normalized_confidence = confidence / total_weight if total_weight > 0 else 0.5
    
    return final_prediction, min(normalized_confidence, 1.0)


def compute_consensus_confidence(
    predictions: Dict[str, Tuple[int, float]],
    final_prediction: int
) -> float:
    """
    Compute consensus confidence (agreement strength).
    
    Args:
        predictions: Dict of {agent_name: (prediction, confidence)}
        final_prediction: Consensus prediction
        
    Returns:
        float: Consensus confidence (0-1)
    """
    matching_preds = []
    total_confidence = 0.0
    
    for pred, conf in predictions.values():
        total_confidence += conf
        if pred == final_prediction:
            matching_preds.append(conf)
    
    if not matching_preds:
        return 0.5
    
    # Average confidence of agents agreeing with consensus
    agreement_confidence = np.mean(matching_preds)
    # Ratio of agreeing agents
    agreement_ratio = len(matching_preds) / len(predictions)
    
    # Combined metric: weight confidence heavily, agreement as secondary
    consensus_confidence = 0.7 * agreement_confidence + 0.3 * agreement_ratio
    
    return min(consensus_confidence, 1.0)


def get_class_name(prediction: int) -> str:
    """
    Convert prediction to human-readable class name.
    
    Args:
        prediction (int): 0 for ham, 1 for spam
        
    Returns:
        str: "Ham" or "Spam"
    """
    return "Spam" if prediction == 1 else "Ham"


def log_agent_weights(weights: Dict[str, float]) -> None:
    """
    Log agent weights in formatted table.
    
    Args:
        weights (Dict[str, float]): Dict of {agent_name: weight}
    """
    logger.info("Agent Weights:")
    for agent_name, weight in sorted(weights.items()):
        logger.info(f"  {agent_name:20s}: {weight:.3f}")


def get_top_agents(
    weights: Dict[str, float],
    n: int = 2
) -> List[str]:
    """
    Get top N agents by weight.
    
    Args:
        weights (Dict[str, float]): Agent weights
        n (int): Number of top agents to return
        
    Returns:
        List of agent names sorted by weight descending
    """
    return [name for name, _ in sorted(weights.items(), key=lambda x: x[1], reverse=True)[:n]]


def get_bottom_agents(
    weights: Dict[str, float],
    n: int = 2
) -> List[str]:
    """
    Get bottom N agents by weight.
    
    Args:
        weights (Dict[str, float]): Agent weights
        n (int): Number of bottom agents to return
        
    Returns:
        List of agent names sorted by weight ascending
    """
    return [name for name, _ in sorted(weights.items(), key=lambda x: x[1])[:n]]


def compute_weight_statistics(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Compute statistics on agent weights.
    
    Args:
        weights (Dict[str, float]): Agent weights
        
    Returns:
        Dict with mean, std, min, max, ratio (max/min)
    """
    if not weights:
        return {}
    
    values = list(weights.values())
    
    return {
        'mean': np.mean(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        'ratio': np.max(values) / np.min(values) if np.min(values) > 0 else np.inf
    }
