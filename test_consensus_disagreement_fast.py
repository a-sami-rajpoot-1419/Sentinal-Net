"""
Fast Disagreement Analysis - Sample every Nth test sample

Tests disagreement on a representative subset of the test set for speed.
"""

import sys
import json
import logging
import numpy as np
import pickle
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


def fast_disagreement_analysis():
    """
    Analyze disagreement on a sample of test set (every 10th sample = 55 samples)
    """
    logger.info("\n" + "="*80)
    logger.info("FAST DISAGREEMENT ANALYSIS (Sampled Test Set)")
    logger.info("="*80)
    
    try:
        # Load data
        logger.info("\n[1] Loading test data...")
        loader = DataLoader()
        data = loader.load_and_cache()
        X_test_full = data['X_test']
        y_test_full = data['y_test']
        
        # Sample every 10th sample for faster analysis
        SAMPLE_INTERVAL = 10
        X_test = X_test_full[::SAMPLE_INTERVAL]
        y_test = y_test_full[::SAMPLE_INTERVAL]
        
        logger.info(f"    Loaded {len(y_test)} test samples (sampled from {len(y_test_full)} total)")
        
        # Load models the same way test_consensus_final.py does
        logger.info("\n[2] Loading trained models...")
        model_dir = Path(__file__).parent / "outputs" / "models"
        agents = {}
        
        for model_file in sorted(model_dir.glob("*_agent.pkl")):
            agent_name = model_file.stem.replace("_agent", "")
            try:
                with open(model_file, 'rb') as f:
                    agent = pickle.load(f)
                agents[agent_name] = agent
                status = "[OK] Trained" if agent.is_trained else "[??] Untrained"
                logger.info(f"    {agent_name:25s}: {status}")
            except Exception as e:
                logger.warning(f"    Failed to load {model_file.name}: {e}")
        
        engine = ConsensusEngine(agents=agents)
        trained_agents = [name for name, agent in agents.items() if agent.is_trained]
        logger.info(f"    Using {len(trained_agents)} trained agents: {trained_agents}")
        
        # Analyze disagreement
        logger.info(f"\n[3] Analyzing predictions on {len(y_test)} sampled test samples...")
        
        disagreements = []
        unanimous_agreements = []
        model_predictions = defaultdict(lambda: {"correct": 0, "total": 0})
        consensus_correct = 0
        
        for i in range(len(y_test)):
            X_sample = X_test[i:i+1]
            true_label = y_test[i]
            
            # Get predictions from all trained agents
            predictions = {}
            for agent_name in trained_agents:
                agent = agents[agent_name]
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
            consensus_correct += (result.predicted_class == true_label)
            
            # Check for disagreement
            votes = [p["prediction"] for p in predictions.values()]
            has_disagreement = len(set(votes)) > 1
            
            if has_disagreement:
                disagreements.append({
                    "sample_id": i * SAMPLE_INTERVAL,  # Original index
                    "true_label": int(true_label),
                    "predictions": predictions,
                    "consensus": {
                        "prediction": int(result.predicted_class),
                        "confidence": float(result.confidence),
                        "correct": bool(result.predicted_class == true_label)
                    }
                })
        
        unanimous_agreements = len(y_test) - len(disagreements)
        
        # Print summary statistics
        logger.info("\n" + "="*80)
        logger.info("SUMMARY STATISTICS")
        logger.info("="*80)
        
        logger.info(f"\nSampled test set: {len(y_test)} samples (every {SAMPLE_INTERVAL}th sample)")
        logger.info(f"Total test set: {len(y_test_full)} samples")
        logger.info(f"\nSamples with disagreement: {len(disagreements)}")
        logger.info(f"Samples with unanimous agreement: {unanimous_agreements}")
        
        disagreement_rate = len(disagreements) / len(y_test) * 100
        agreement_rate = unanimous_agreements / len(y_test) * 100
        
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
        
        # Overall consensus accuracy
        logger.info("\n" + "-"*80)
        logger.info("CONSENSUS ACCURACY")
        logger.info("-"*80)
        
        consensus_accuracy = consensus_correct / len(y_test) * 100
        logger.info(f"Consensus correct: {consensus_correct}/{len(y_test)}")
        logger.info(f"Consensus accuracy: {consensus_accuracy:.1f}%")
        
        # Disagreement analysis
        if disagreements:
            logger.info("\n" + "-"*80)
            logger.info("DISAGREEMENT ANALYSIS")
            logger.info("-"*80)
            
            consensus_correct_in_disagreement = sum(
                1 for case in disagreements if case["consensus"]["correct"]
            )
            
            logger.info(f"\nWhen models disagree:")
            logger.info(f"  Consensus correct: {consensus_correct_in_disagreement}/{len(disagreements)}")
            logger.info(f"  Consensus accuracy in disagreement: {consensus_correct_in_disagreement/len(disagreements)*100:.1f}%")
            
            # Show first 5 disagreement cases
            logger.info(f"\nFirst 5 disagreement cases:")
            for case_idx, case in enumerate(disagreements[:5]):
                logger.info(f"\n  Case {case_idx + 1}: Sample #{case['sample_id']}")
                label_name = "SPAM" if case['true_label'] == 1 else "HAM"
                logger.info(f"  True Label: {label_name}")
                logger.info(f"  Predictions:")
                
                for model_name, pred_info in case['predictions'].items():
                    pred_name = "SPAM" if pred_info['prediction'] == 1 else "HAM"
                    status = "✓" if pred_info['correct'] else "✗"
                    logger.info(f"    {model_name:20s}: {pred_name} ({pred_info['confidence']:.4f}) {status}")
                
                consensus_pred_name = "SPAM" if case['consensus']['prediction'] == 1 else "HAM"
                consensus_status = "✓" if case['consensus']['correct'] else "✗"
                logger.info(f"    CONSENSUS        : {consensus_pred_name} ({case['consensus']['confidence']:.4f}) {consensus_status}")
        
        # Save results
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_set": {
                "sampled": len(y_test),
                "total": len(y_test_full),
                "sample_interval": SAMPLE_INTERVAL
            },
            "summary": {
                "disagreements": len(disagreements),
                "agreements": unanimous_agreements,
                "disagreement_rate": f"{disagreement_rate:.1f}%",
                "consensus_accuracy": f"{consensus_accuracy:.1f}%"
            },
            "model_accuracy": {
                model_name: {
                    "correct": stats["correct"],
                    "total": stats["total"],
                    "accuracy": f"{stats['correct']/stats['total']*100:.1f}%" if stats["total"] > 0 else "N/A"
                }
                for model_name, stats in model_predictions.items()
            },
            "disagreement_examples": disagreements[:5]
        }
        
        results_file = Path(__file__).parent / "test_consensus_disagreement_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("\n" + "="*80)
        logger.info(f"Results saved to: {results_file}")
        logger.info("="*80)
        
        # Key insight
        logger.info("\nKEY FINDINGS:")
        logger.info(f"✓ Model disagreement rate: {disagreement_rate:.1f}%")
        logger.info(f"✓ Consensus accuracy: {consensus_accuracy:.1f}%")
        logger.info(f"✓ Individual model accuracies:")
        for model_name in sorted(model_predictions.keys()):
            stats = model_predictions[model_name]
            acc = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
            logger.info(f"  - {model_name:20s}: {acc:.1f}%")
        
        if disagreement_rate > 0:
            logger.info(f"\n✓ CONSENSUS VOTING IS NEEDED")
            logger.info(f"  Models disagree on {disagreement_rate:.1f}% of samples")
            logger.info(f"  RWPV mechanism can improve system by learning which models are better")
        else:
            logger.info(f"\n✓ All models agree perfectly on this sample")
            logger.info(f"  Consensus mechanism provides consistency guarantee")
            logger.info(f"  RWPV mechanism has learning opportunities on full dataset")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    fast_disagreement_analysis()
