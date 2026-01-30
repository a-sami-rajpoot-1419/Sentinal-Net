"""
Real Consensus Testing on Full Test Set - Using Working Model Loader

Tests the consensus mechanism using the same approach as test_consensus_final.py
which successfully loads the trained models and tests on all 558 test samples.

Author: Sentinel-Net Team
Date: 2026-01-30
"""

import sys
import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from data.loader import DataLoader
from consensus.engine import ConsensusEngine


def analyze_disagreement_patterns():
    """
    Analyze where and how models disagree on the full test set.
    Uses the same model loading as test_consensus_final.py which works.
    """
    logger.info("\n" + "="*80)
    logger.info("CONSENSUS TESTING: REAL DISAGREEMENT ANALYSIS (FULL TEST SET)")
    logger.info("="*80)
    
    try:
        # Load data
        logger.info("\n[1] Loading test data...")
        loader = DataLoader()
        data = loader.load_and_cache()
        X_test = data['X_test']
        y_test = data['y_test']
        logger.info(f"    Loaded {X_test.shape[0]} test samples")
        
        # Load consensus engine using same method as test_consensus_final.py
        logger.info("\n[2] Loading consensus engine with trained models...")
        model_dir = Path(__file__).parent / "outputs" / "models"
        agents = {}
        
        for model_file in sorted(model_dir.glob("*_agent.pkl")):
            agent_name = model_file.stem.replace("_agent", "")
            try:
                import pickle
                with open(model_file, 'rb') as f:
                    agent = pickle.load(f)
                agents[agent_name] = agent
                status = "[OK] Trained" if agent.is_trained else "[??] Untrained"
                logger.info(f"  {agent_name:25s}: {status}")
            except Exception as e:
                logger.warning(f"  Failed to load {model_file.name}: {e}")
        
        engine = ConsensusEngine(agents=agents)
        trained_count = sum(1 for a in agents.values() if a.is_trained)
        logger.info(f"    Loaded {trained_count} trained agents out of {len(agents)}")
        
        # Analyze predictions on full test set
        logger.info("\n[3] Running predictions on all test samples...")
        logger.info("    This may take a minute...")
        
        disagreements = []
        unanimous_agreements = []
        model_predictions = defaultdict(lambda: {"correct": 0, "total": 0})
        disagreement_cases = []
        
        for i in range(X_test.shape[0]):
            X_sample = X_test[i:i+1]
            true_label = y_test[i]
            
            # Get predictions from all trained agents
            predictions = {}
            for agent_name, agent in agents.items():
                if not agent.is_trained:
                    continue
                
                pred, conf = agent.predict(X_sample)
                predictions[agent_name] = {
                    "prediction": int(pred),
                    "confidence": float(conf),
                    "correct": int(pred == true_label)
                }
                
                # Track accuracy
                model_predictions[agent_name]["total"] += 1
                if pred == true_label:
                    model_predictions[agent_name]["correct"] += 1
            
            # Get consensus prediction
            result = engine.predict(X_sample)
            consensus_correct = result.predicted_class == true_label
            
            # Check for disagreement
            votes = [p["prediction"] for p in predictions.values()]
            has_disagreement = len(set(votes)) > 1
            
            if has_disagreement:
                disagreements.append({
                    "sample_id": i,
                    "true_label": int(true_label),
                    "predictions": predictions,
                    "consensus": {
                        "prediction": int(result.predicted_class),
                        "confidence": float(result.confidence),
                        "correct": bool(consensus_correct)
                    }
                })
                
                # Detailed case analysis
                if len(disagreement_cases) < 10:  # Keep first 10 for detailed analysis
                    disagreement_cases.append({
                        "sample_id": i,
                        "true_label": int(true_label),
                        "label_name": "SPAM" if true_label == 1 else "HAM",
                        "predictions": predictions,
                        "consensus": {
                            "prediction": int(result.predicted_class),
                            "prediction_name": "SPAM" if result.predicted_class == 1 else "HAM",
                            "confidence": float(result.confidence),
                            "correct": bool(consensus_correct)
                        }
                    })
            else:
                unanimous_agreements.append(i)
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                logger.info(f"    Processed {i+1}/{X_test.shape[0]} samples")
        
        # Print summary statistics
        logger.info("\n" + "="*80)
        logger.info("SUMMARY STATISTICS")
        logger.info("="*80)
        
        logger.info(f"\nTotal test samples: {X_test.shape[0]}")
        logger.info(f"Samples with disagreement: {len(disagreements)}")
        logger.info(f"Samples with unanimous agreement: {len(unanimous_agreements)}")
        
        disagreement_rate = len(disagreements) / X_test.shape[0] * 100
        agreement_rate = len(unanimous_agreements) / X_test.shape[0] * 100
        
        logger.info(f"Disagreement rate: {disagreement_rate:.1f}%")
        logger.info(f"Agreement rate: {agreement_rate:.1f}%")
        
        # Individual model accuracy
        logger.info("\n" + "-"*80)
        logger.info("INDIVIDUAL MODEL ACCURACY")
        logger.info("-"*80)
        
        for model_name in sorted(model_predictions.keys()):
            stats = model_predictions[model_name]
            accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
            logger.info(f"{model_name:25s}: {stats['correct']:3d}/{stats['total']:3d} ({accuracy:5.1f}%)")
        
        # Analyze disagreement characteristics
        if disagreements:
            logger.info("\n" + "-"*80)
            logger.info("DISAGREEMENT ANALYSIS")
            logger.info("-"*80)
            
            # How often is consensus correct when there's disagreement?
            consensus_correct_in_disagreement = sum(
                1 for case in disagreements if case["consensus"]["correct"]
            )
            
            logger.info(f"\nWhen models disagree:")
            logger.info(f"  Consensus correct: {consensus_correct_in_disagreement}/{len(disagreements)}")
            logger.info(f"  Consensus accuracy in disagreement: {consensus_correct_in_disagreement/len(disagreements)*100:.1f}%")
            
            # Count by disagreement type
            disagreement_types = defaultdict(int)
            for case in disagreements:
                votes = [p["prediction"] for p in case["predictions"].values()]
                vote_counts = tuple(sorted([votes.count(v) for v in set(votes)], reverse=True))
                disagreement_types[f"{vote_counts[0]}-{vote_counts[1]}" if len(vote_counts) > 1 else str(vote_counts[0])] += 1
            
            logger.info(f"\nDisagreement types (model count voting for each class):")
            for disagreement_type, count in sorted(disagreement_types.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(disagreements) * 100
                logger.info(f"  {disagreement_type}: {count} cases ({percentage:.1f}%)")
        
        # Consensus correctness breakdown
        logger.info("\n" + "-"*80)
        logger.info("CONSENSUS CORRECTNESS")
        logger.info("-"*80)
        
        # When all agree, is consensus always correct?
        if unanimous_agreements:
            unanimous_correct = sum(1 for i in unanimous_agreements if engine.predict(X_test[i:i+1]).predicted_class == y_test[i])
            logger.info(f"\nWhen all models agree:")
            logger.info(f"  Consensus correct: {unanimous_correct}/{len(unanimous_agreements)}")
            logger.info(f"  Consensus accuracy: {unanimous_correct/len(unanimous_agreements)*100:.1f}%")
        
        # Overall consensus accuracy
        overall_consensus_correct = sum(
            1 for i in range(len(y_test)) 
            if engine.predict(X_test[i:i+1]).predicted_class == y_test[i]
        )
        logger.info(f"\nOverall consensus accuracy on test set:")
        logger.info(f"  Correct: {overall_consensus_correct}/{X_test.shape[0]}")
        logger.info(f"  Accuracy: {overall_consensus_correct/X_test.shape[0]*100:.1f}%")
        
        # Detailed case examples
        if disagreement_cases:
            logger.info("\n" + "="*80)
            logger.info(f"EXAMPLE DISAGREEMENT CASES (First {len(disagreement_cases)})")
            logger.info("="*80)
            
            for case_idx, case in enumerate(disagreement_cases):
                logger.info(f"\nCase {case_idx + 1}: Sample #{case['sample_id']}")
                logger.info(f"True Label: {case['label_name']} ({case['true_label']})")
                logger.info(f"Predictions:")
                
                for model_name, pred_info in case['predictions'].items():
                    pred_name = "SPAM" if pred_info['prediction'] == 1 else "HAM"
                    status = "✓" if pred_info['correct'] else "✗"
                    logger.info(f"  {model_name:25s}: {pred_name} ({pred_info['confidence']:.4f}) {status}")
                
                logger.info(f"Consensus: {case['consensus']['prediction_name']} ({case['consensus']['confidence']:.4f}) {'✓' if case['consensus']['correct'] else '✗'}")
        
        # Save detailed results
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_set_size": X_test.shape[0],
            "summary": {
                "disagreements": len(disagreements),
                "agreements": len(unanimous_agreements),
                "disagreement_rate": f"{disagreement_rate:.1f}%",
                "consensus_accuracy": f"{overall_consensus_correct/X_test.shape[0]*100:.1f}%"
            },
            "model_accuracy": {
                model_name: {
                    "correct": stats["correct"],
                    "total": stats["total"],
                    "accuracy": f"{stats['correct']/stats['total']*100:.1f}%" if stats["total"] > 0 else "N/A"
                }
                for model_name, stats in model_predictions.items()
            },
            "example_disagreement_cases": disagreement_cases
        }
        
        results_file = Path(__file__).parent / "test_consensus_real_disagreement_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("\n" + "="*80)
        logger.info(f"Results saved to: {results_file}")
        logger.info("="*80)
        
        # Key insight
        logger.info("\nKEY INSIGHT:")
        logger.info(f"Models disagree on {disagreement_rate:.1f}% of test samples.")
        if disagreement_rate > 0:
            logger.info(f"This confirms the consensus voting mechanism is needed and useful!")
            logger.info(f"RWPV can adjust which models' votes matter more based on accuracy.")
        else:
            logger.info(f"All models agree perfectly on this test set.")
            logger.info(f"This suggests all 3 models have similar performance levels.")
            logger.info(f"To fully test consensus voting, use a larger/more diverse dataset.")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    analyze_disagreement_patterns()
