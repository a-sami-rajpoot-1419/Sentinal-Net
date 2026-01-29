"""
Phase 4 Complete Training and Consensus Pipeline
Integrates Phase 3 models with Phase 4 consensus engine
"""

import numpy as np
from typing import Dict, Tuple, List
from backend.models.trainer import ModelTrainer
from backend.data.loader import DataLoader
from backend.consensus.engine import ConsensusEngine
from backend.consensus.reputation import ReputationManager
from backend.db.supabase_client import get_supabase_client
import json
from datetime import datetime
import os


def main_pipeline():
    """
    Complete Phase 3 + Phase 4 pipeline
    
    Steps:
    1. Load Phase 3 trained models and data
    2. Initialize consensus engine
    3. Make predictions on test set
    4. Update weights based on feedback
    5. Track reputation and save to database
    6. Generate statistics report
    """
    
    print("=" * 80)
    print("PHASE 3 + PHASE 4: Complete ML Consensus Pipeline")
    print("=" * 80)
    print()
    
    # Step 1: Load data and models
    print("[1/6] Loading Phase 3 models and data...")
    try:
        data_loader = DataLoader()
        X_train, y_train = data_loader.load_train_set()
        X_val, y_val = data_loader.load_validation_set()
        X_test, y_test = data_loader.load_test_set()
        
        print(f"  ✓ Loaded training data: {X_train.shape}")
        print(f"  ✓ Loaded validation data: {X_val.shape}")
        print(f"  ✓ Loaded test data: {X_test.shape}")
        
        model_trainer = ModelTrainer()
        print(f"  ✓ Loaded {len(model_trainer.agents)} agents")
    except Exception as e:
        print(f"  ✗ Error loading data/models: {e}")
        return
    
    # Step 2: Initialize consensus engine
    print()
    print("[2/6] Initializing consensus engine...")
    try:
        consensus_engine = ConsensusEngine(
            agents=model_trainer.agents,
            weight_reward_correct=1.05,
            weight_penalty_wrong=0.90,
            weight_reward_minority=1.15,
            weight_penalty_both_wrong=0.85,
        )
        reputation_manager = ReputationManager()
        
        # Initialize all agents in reputation system
        for agent_name in consensus_engine.agents.keys():
            reputation_manager.initialize_agent(agent_name, initial_weight=1.0)
        
        print(f"  ✓ Consensus engine initialized")
        print(f"  ✓ Reputation manager initialized")
    except Exception as e:
        print(f"  ✗ Error initializing consensus: {e}")
        return
    
    # Step 3: Make predictions on test set
    print()
    print("[3/6] Making consensus predictions on test set...")
    try:
        test_predictions = []
        total_samples = min(100, X_test.shape[0])  # Process first 100 for demo
        
        for i in range(total_samples):
            X_sample = X_test[i:i+1]
            y_true = y_test[i]
            
            # Get consensus prediction
            result = consensus_engine.predict(X_sample)
            
            test_predictions.append({
                "sample_id": i,
                "true_label": int(y_true),
                "predicted_label": result.predicted_class,
                "confidence": float(result.confidence),
                "agent_predictions": {
                    name: {
                        "class": int(pred[0]),
                        "confidence": float(pred[1]),
                    }
                    for name, pred in result.agent_predictions.items()
                },
                "weights": {
                    name: float(w) for name, w in result.weights.items()
                },
            })
            
            if (i + 1) % 20 == 0:
                print(f"  ✓ Processed {i + 1}/{total_samples} samples")
        
        print(f"  ✓ Generated {len(test_predictions)} predictions")
    except Exception as e:
        print(f"  ✗ Error making predictions: {e}")
        return
    
    # Step 4: Update weights based on feedback (RWPV mechanism)
    print()
    print("[4/6] Updating agent weights based on feedback (RWPV)...")
    try:
        correct_count = 0
        
        for pred in test_predictions:
            y_true = pred["true_label"]
            y_pred = pred["predicted_label"]
            
            # Check if prediction correct
            if y_pred == y_true:
                correct_count += 1
            
            # Update weights with feedback
            agent_predictions = {
                name: (int(p["class"]), float(p["confidence"]))
                for name, p in pred["agent_predictions"].items()
            }
            
            new_weights = consensus_engine.update_weights_from_feedback(
                true_label=y_true,
                predictions=agent_predictions,
            )
            
            # Record in reputation manager
            for agent_name, (pred_class, confidence) in agent_predictions.items():
                reputation_manager.record_prediction(
                    agent_name=agent_name,
                    predicted_class=pred_class,
                    true_class=y_true,
                    confidence=confidence,
                    majority_class=pred["predicted_label"],
                )
        
        consensus_accuracy = correct_count / len(test_predictions)
        print(f"  ✓ Consensus accuracy: {consensus_accuracy:.2%}")
        print(f"  ✓ Updated weights {len(test_predictions)} times")
    except Exception as e:
        print(f"  ✗ Error updating weights: {e}")
        return
    
    # Step 5: Track reputation and statistics
    print()
    print("[5/6] Generating reputation and statistics report...")
    try:
        print()
        print("AGENT REPUTATION STATISTICS:")
        print("-" * 80)
        
        for agent_name in consensus_engine.agents.keys():
            rep = consensus_engine.get_agent_reputation(agent_name)
            print(f"\n{agent_name.upper()}:")
            print(f"  Accuracy:  {rep['accuracy']:.2%}")
            print(f"  Predictions: {rep['total_predictions']}")
            print(f"  Weight: {rep['current_weight']:.3f}")
            print(f"  Avg Confidence: {rep['confidence_avg']:.3f}")
        
        print()
        print("AGENT RANKINGS:")
        print("-" * 80)
        
        ranked_by_accuracy = reputation_manager.rank_agents_by_accuracy()
        ranked_by_weight = reputation_manager.rank_agents_by_weight()
        
        print("\nBy Accuracy:")
        for i, (agent, accuracy) in enumerate(ranked_by_accuracy, 1):
            print(f"  {i}. {agent}: {accuracy:.2%}")
        
        print("\nBy Weight:")
        for i, (agent, weight) in enumerate(ranked_by_weight, 1):
            print(f"  {i}. {agent}: {weight:.3f}")
        
    except Exception as e:
        print(f"  ✗ Error generating statistics: {e}")
        return
    
    # Step 6: Save results and create report
    print()
    print("[6/6] Saving results to database and creating report...")
    try:
        # Create output directory if not exists
        os.makedirs("outputs/phase4", exist_ok=True)
        
        # Save predictions to JSON
        with open("outputs/phase4/consensus_predictions.json", "w") as f:
            json.dump(test_predictions, f, indent=2)
        print(f"  ✓ Saved {len(test_predictions)} predictions")
        
        # Save reputation statistics
        reputation_summary = reputation_manager.get_reputation_summary()
        with open("outputs/phase4/reputation_summary.json", "w") as f:
            json.dump(reputation_summary, f, indent=2, default=str)
        print(f"  ✓ Saved reputation summary")
        
        # Save final weights
        final_weights = consensus_engine.get_weights()
        with open("outputs/phase4/final_weights.json", "w") as f:
            json.dump(final_weights, f, indent=2)
        print(f"  ✓ Saved final agent weights")
        
        # Create summary report
        report = f"""
SENTINEL-NET: PHASE 3 + PHASE 4 CONSENSUS PIPELINE REPORT
Generated: {datetime.now().isoformat()}

SUMMARY
=======
Total Predictions: {len(test_predictions)}
Consensus Accuracy: {consensus_accuracy:.2%}
Agents: {len(consensus_engine.agents)}

AGENT PERFORMANCE
================
"""
        
        for agent_name in consensus_engine.agents.keys():
            rep = consensus_engine.get_agent_reputation(agent_name)
            report += f"\n{agent_name}:\n"
            report += f"  - Accuracy: {rep['accuracy']:.2%}\n"
            report += f"  - Predictions: {rep['total_predictions']}\n"
            report += f"  - Final Weight: {rep['current_weight']:.3f}\n"
        
        report += f"\n\nFILES GENERATED\n"
        report += f"- outputs/phase4/consensus_predictions.json\n"
        report += f"- outputs/phase4/reputation_summary.json\n"
        report += f"- outputs/phase4/final_weights.json\n"
        report += f"- outputs/phase4/pipeline_report.txt\n"
        
        with open("outputs/phase4/pipeline_report.txt", "w") as f:
            f.write(report)
        
        print(f"  ✓ Saved pipeline report")
        
    except Exception as e:
        print(f"  ✗ Error saving results: {e}")
        return
    
    print()
    print("=" * 80)
    print("✓ PIPELINE COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Start FastAPI server: uvicorn backend.api.app:app --reload")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Test predictions: curl http://localhost:8000/health")
    print()


if __name__ == "__main__":
    main_pipeline()
