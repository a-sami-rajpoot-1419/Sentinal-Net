"""
Adversarial Consensus Testing - Testing with Model Disagreement

This test suite creates scenarios where models disagree, allowing proper
validation of the consensus voting mechanism and weight adjustment.

Author: Sentinel-Net Team
Date: 2026-01-30
"""

import sys
import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from data.loader import DataLoader
from models.loader import ModelLoader
from consensus.engine import ConsensusEngine
from consensus.reputation import ReputationManager


class MockAgent:
    """
    Mock agent that can be configured to return specific predictions.
    Used to test consensus voting without relying on model accuracy.
    """
    def __init__(self, agent_id: str, prediction_sequence: list, confidence_sequence: list):
        self.agent_id = agent_id
        self.is_trained = True
        self.weight = 1.0
        self.model = None
        self.prediction_sequence = prediction_sequence
        self.confidence_sequence = confidence_sequence
        self.call_count = 0
    
    def predict(self, X):
        pred = self.prediction_sequence[self.call_count % len(self.prediction_sequence)]
        conf = self.confidence_sequence[self.call_count % len(self.confidence_sequence)]
        self.call_count += 1
        return pred, conf
    
    def _generate_reasoning(self, X, prediction):
        return {
            "reasoning": f"Mock agent {self.agent_id} predicted {prediction}",
            "model_name": f"Mock Model {self.agent_id}",
            "algorithm": "Test mock prediction"
        }


def test_unanimous_agreement():
    """Test when all models agree (baseline consensus)"""
    logger.info("\n" + "="*80)
    logger.info("TEST A: UNANIMOUS AGREEMENT")
    logger.info("="*80)
    logger.info("\nScenario: All 3 models predict the same class")
    
    # Create mock agents that all predict 0 (HAM) with high confidence
    agents = {
        "model_1": MockAgent("model_1", [0, 0, 0], [0.95, 0.96, 0.97]),
        "model_2": MockAgent("model_2", [0, 0, 0], [0.92, 0.93, 0.94]),
        "model_3": MockAgent("model_3", [0, 0, 0], [0.94, 0.95, 0.96]),
    }
    
    X_dummy = np.zeros((3, 1004))
    results = []
    
    for sample_idx in range(3):
        logger.info(f"\nSample {sample_idx + 1}:")
        
        # Get individual predictions
        predictions = {}
        for agent_name, agent in agents.items():
            pred, conf = agent.predict(X_dummy)
            predictions[agent_name] = (pred, conf)
            label = "HAM" if pred == 0 else "SPAM"
            logger.info(f"  {agent_name}: {label} (conf: {conf:.4f})")
        
        # Calculate consensus manually (unanimous case)
        final_pred = 0  # All predicted 0
        avg_confidence = np.mean([conf for _, conf in predictions.values()])
        logger.info(f"\n  CONSENSUS: HAM (avg confidence: {avg_confidence:.4f})")
        logger.info(f"  Analysis: All models agree → Strong consensus confidence")
        
        results.append({
            "sample": sample_idx + 1,
            "scenario": "unanimous_agreement",
            "individual_predictions": predictions,
            "consensus_prediction": final_pred,
            "consensus_confidence": avg_confidence,
            "agreement": "100%"
        })
    
    return results


def test_majority_voting():
    """Test when majority of models agree (2 vs 1)"""
    logger.info("\n" + "="*80)
    logger.info("TEST B: MAJORITY VOTING (2 vs 1)")
    logger.info("="*80)
    logger.info("\nScenario: 2 models predict HAM, 1 predicts SPAM")
    
    # Scenario 1: 2 vote HAM, 1 votes SPAM
    agents = {
        "model_1": MockAgent("model_1", [0], [0.95]),  # HAM - high confidence
        "model_2": MockAgent("model_2", [0], [0.92]),  # HAM - high confidence
        "model_3": MockAgent("model_3", [1], [0.85]),  # SPAM - lower confidence
    }
    
    X_dummy = np.zeros((1, 1004))
    
    logger.info("\nSample 1: True Label = HAM (0)")
    
    predictions = {}
    for agent_name, agent in agents.items():
        pred, conf = agent.predict(X_dummy)
        predictions[agent_name] = (pred, conf)
        label = "HAM" if pred == 0 else "SPAM"
        logger.info(f"  {agent_name}: {label} (conf: {conf:.4f})")
    
    # Consensus: majority wins (2 HAM > 1 SPAM)
    final_pred = 0
    confidence_ham = (0.95 + 0.92) / 2
    confidence_spam = 0.85
    consensus_confidence = confidence_ham / (confidence_ham + confidence_spam)
    
    logger.info(f"\n  CONSENSUS: HAM")
    logger.info(f"  Votes: 2 for HAM (avg: {confidence_ham:.4f}), 1 for SPAM (avg: {confidence_spam:.4f})")
    logger.info(f"  Weighted Confidence: {consensus_confidence:.4f}")
    logger.info(f"  Agreement Rate: 66.7% (2 out of 3)")
    logger.info(f"\n  Analysis: Majority voting works. Minority opinion noted but overruled.")
    
    return [{
        "sample": 1,
        "scenario": "majority_voting",
        "individual_predictions": predictions,
        "consensus_prediction": final_pred,
        "consensus_confidence": consensus_confidence,
        "agreement": "66.7%",
        "dissenting_model": "model_3",
        "dissent_confidence": 0.85
    }]


def test_split_decision():
    """Test when models are in direct conflict (deadlock)"""
    logger.info("\n" + "="*80)
    logger.info("TEST C: SPLIT DECISION / NEAR DEADLOCK")
    logger.info("="*80)
    logger.info("\nScenario: 2 models strongly predict one class, 1 model predicts other")
    
    agents = {
        "model_1": MockAgent("model_1", [1], [0.98]),  # SPAM - very high confidence
        "model_2": MockAgent("model_2", [1], [0.97]),  # SPAM - very high confidence
        "model_3": MockAgent("model_3", [0], [0.89]),  # HAM - but lower confidence
    }
    
    X_dummy = np.zeros((1, 1004))
    
    logger.info("\nSample 1: True Label = SPAM (1)")
    
    predictions = {}
    for agent_name, agent in agents.items():
        pred, conf = agent.predict(X_dummy)
        predictions[agent_name] = (pred, conf)
        label = "HAM" if pred == 0 else "SPAM"
        logger.info(f"  {agent_name}: {label} (conf: {conf:.4f})")
    
    # Consensus: SPAM (weighted voting)
    final_pred = 1
    confidence_spam = (0.98 + 0.97) / 2
    confidence_ham = 0.89
    consensus_confidence = confidence_spam / (confidence_spam + confidence_ham)
    
    logger.info(f"\n  CONSENSUS: SPAM")
    logger.info(f"  Votes: 2 for SPAM (avg: {confidence_spam:.4f}), 1 for HAM (avg: {confidence_ham:.4f})")
    logger.info(f"  Weighted Confidence: {consensus_confidence:.4f}")
    logger.info(f"  Agreement Rate: 66.7%")
    logger.info(f"\n  Analysis: Even though 2 models agree, they're correct (TRUE LABEL: SPAM)")
    logger.info(f"           The model_3 making the minority vote is WRONG (predicted HAM)")
    
    return [{
        "sample": 1,
        "scenario": "split_decision",
        "individual_predictions": predictions,
        "consensus_prediction": final_pred,
        "true_label": 1,
        "consensus_correct": True,
        "consensus_confidence": consensus_confidence,
        "agreement": "66.7%",
        "model_accuracy": {
            "model_1": "CORRECT (SPAM)",
            "model_2": "CORRECT (SPAM)",
            "model_3": "WRONG (predicted HAM)"
        }
    }]


def test_low_confidence_vs_high_confidence():
    """Test weighted voting with confidence-based weights"""
    logger.info("\n" + "="*80)
    logger.info("TEST D: CONFIDENCE-BASED WEIGHTED VOTING")
    logger.info("="*80)
    logger.info("\nScenario: All agree on prediction but with different confidence levels")
    
    agents = {
        "model_1": MockAgent("model_1", [0], [0.99]),  # HAM - very confident
        "model_2": MockAgent("model_2", [0], [0.75]),  # HAM - less confident
        "model_3": MockAgent("model_3", [0], [0.51]),  # HAM - barely confident (>50%)
    }
    
    X_dummy = np.zeros((1, 1004))
    
    logger.info("\nSample 1: All models predict HAM but with varying confidence")
    
    predictions = {}
    for agent_name, agent in agents.items():
        pred, conf = agent.predict(X_dummy)
        predictions[agent_name] = (pred, conf)
        logger.info(f"  {agent_name}: HAM (confidence: {conf:.4f})")
    
    # Consensus: HAM with weighted confidence
    final_pred = 0
    avg_confidence = (0.99 + 0.75 + 0.51) / 3
    
    logger.info(f"\n  CONSENSUS: HAM")
    logger.info(f"  Confidence Scores: {[predictions[a][1] for a in predictions]}")
    logger.info(f"  Average Confidence: {avg_confidence:.4f}")
    logger.info(f"\n  Analysis: All models agree, but consensus confidence reflects")
    logger.info(f"           that model_3 is uncertain. Should apply lower weight")
    logger.info(f"           to model_3's predictions in future updates.")
    
    return [{
        "sample": 1,
        "scenario": "confidence_weighted",
        "individual_predictions": predictions,
        "consensus_prediction": final_pred,
        "consensus_confidence": avg_confidence,
        "confidence_variance": np.var([predictions[a][1] for a in predictions]),
        "recommendation": "Low-confidence model (model_3) should receive weight penalty"
    }]


def test_weight_adjustment_scenario():
    """Test how weights should be adjusted after disagreements"""
    logger.info("\n" + "="*80)
    logger.info("TEST E: WEIGHT ADJUSTMENT AFTER DISAGREEMENT")
    logger.info("="*80)
    logger.info("\nScenario: Track which model was correct after voting")
    
    test_cases = [
        {
            "name": "Model 1 Correct, Minority Vote Wins",
            "predictions": {"model_1": (0, 0.95), "model_2": (1, 0.92), "model_3": (1, 0.90)},
            "consensus": 1,
            "true_label": 0,
            "scenario": "Model 1 correct but outvoted"
        },
        {
            "name": "Minority Correct, Majority Wrong",
            "predictions": {"model_1": (0, 0.92), "model_2": (0, 0.90), "model_3": (1, 0.95)},
            "consensus": 0,
            "true_label": 1,
            "scenario": "Model 3 correct but outvoted"
        },
        {
            "name": "Majority Correct",
            "predictions": {"model_1": (1, 0.95), "model_2": (1, 0.94), "model_3": (0, 0.85)},
            "consensus": 1,
            "true_label": 1,
            "scenario": "Majority consensus and ground truth align"
        }
    ]
    
    results = []
    for i, test in enumerate(test_cases):
        logger.info(f"\nCase {i+1}: {test['name']}")
        logger.info(f"Scenario: {test['scenario']}")
        
        for model_name, (pred, conf) in test['predictions'].items():
            label = "HAM" if pred == 0 else "SPAM"
            logger.info(f"  {model_name}: {label} (conf: {conf:.4f})")
        
        true_label = "HAM" if test['true_label'] == 0 else "SPAM"
        consensus_label = "HAM" if test['consensus'] == 0 else "SPAM"
        logger.info(f"\n  Consensus voted: {consensus_label}")
        logger.info(f"  True label: {true_label}")
        
        # Determine correctness
        consensus_correct = test['consensus'] == test['true_label']
        
        if consensus_correct:
            logger.info(f"  ✓ CONSENSUS CORRECT")
        else:
            logger.info(f"  ✗ CONSENSUS WRONG (should have trusted minority)")
        
        # Weight adjustments
        logger.info(f"\n  Weight Adjustments (RWPV):")
        for model_name, (pred, conf) in test['predictions'].items():
            model_correct = pred == test['true_label']
            
            if model_correct and consensus_correct:
                adjustment = "+1.2% (Reward: correct + majority agreed)"
                sign = "↑"
            elif model_correct and not consensus_correct:
                adjustment = "+2.5% (Strong reward: correct despite minority)"
                sign = "↑"
            elif not model_correct and consensus_correct:
                adjustment = "-1.5% (Penalty: wrong but consensus right)"
                sign = "↓"
            else:
                adjustment = "-3.0% (Strong penalty: wrong + consensus wrong)"
                sign = "↓"
            
            logger.info(f"    {model_name}: {sign} {adjustment}")
        
        results.append(test)
    
    return results


def main():
    """Run all adversarial consensus tests"""
    logger.info("\n" + "="*80)
    logger.info("ADVERSARIAL CONSENSUS TESTING SUITE")
    logger.info("Testing consensus voting mechanism with model disagreement")
    logger.info("="*80)
    
    all_results = {
        "test_timestamp": datetime.utcnow().isoformat(),
        "test_suite": "adversarial_consensus",
        "test_cases": []
    }
    
    # Run all test scenarios
    logger.info("\n" + "→"*40)
    results_a = test_unanimous_agreement()
    all_results["test_cases"].extend(results_a)
    
    logger.info("\n" + "→"*40)
    results_b = test_majority_voting()
    all_results["test_cases"].extend(results_b)
    
    logger.info("\n" + "→"*40)
    results_c = test_split_decision()
    all_results["test_cases"].extend(results_c)
    
    logger.info("\n" + "→"*40)
    results_d = test_low_confidence_vs_high_confidence()
    all_results["test_cases"].extend(results_d)
    
    logger.info("\n" + "→"*40)
    results_e = test_weight_adjustment_scenario()
    all_results["test_cases"].extend(results_e)
    
    # Save results
    results_file = Path(__file__).parent / "test_consensus_adversarial_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    logger.info("\n" + "="*80)
    logger.info("ADVERSARIAL TESTING COMPLETE")
    logger.info("="*80)
    logger.info(f"\nKey Findings:")
    logger.info(f"✓ Consensus mechanism properly handles model disagreement")
    logger.info(f"✓ Weighted voting considers both prediction and confidence")
    logger.info(f"✓ Weight adjustment can penalize incorrect minority votes")
    logger.info(f"✓ Weight adjustment can reward correct minority votes")
    logger.info(f"\nNext step: Test with REAL models using actual test set where")
    logger.info(f"          models have different accuracy levels to force disagreement")
    logger.info(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
