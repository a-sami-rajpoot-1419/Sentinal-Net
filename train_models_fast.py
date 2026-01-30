#!/usr/bin/env python3
"""
Fast ML Training Pipeline - Optimized for speed

Trains 3 fast ML models (skips SVM):
1. Naive Bayes - Fast and effective for text
2. Random Forest - Ensemble method
3. Logistic Regression - Linear baseline

Author: Sentinel-Net Team
"""

import sys
import pickle
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.data.loader import DataLoader
from backend.models.trainer import ModelTrainer
from backend.models.naive_bayes import NaiveBayesAgent
from backend.models.random_forest import RandomForestAgent
from backend.models.logistic_regression import LogisticRegressionAgent

def main():
    print("\n" + "="*70)
    print("SENTINEL-NET ML TRAINING PIPELINE")
    print("="*70)
    
    # Step 1: Load data
    print("\n[1/3] Loading and preprocessing dataset...")
    loader = DataLoader(
        cache_dir="data/cache",
        raw_dir="data/raw",
        processed_dir="data/processed",
        vocab_size=1000,
        random_seed=42
    )
    data = loader.load_and_cache()
    loader.print_statistics()
    
    # Step 2: Train 3 models
    print("\n[2/3] Training 3 ML models...")
    output_dir = Path("outputs/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Naive Bayes
    print("  Training Naive Bayes...")
    nb_agent = NaiveBayesAgent('agent_nb')
    nb_agent.train(data['X_train'], data['y_train'])
    nb_pred, _ = nb_agent.predict(data['X_val'][:5])
    print(f"    [OK] Naive Bayes trained (sample prediction: {nb_pred})")
    
    # Random Forest
    print("  Training Random Forest...")
    rf_agent = RandomForestAgent('agent_rf')
    rf_agent.train(data['X_train'], data['y_train'])
    rf_pred, _ = rf_agent.predict(data['X_val'][:5])
    print(f"    [OK] Random Forest trained (sample prediction: {rf_pred})")
    
    # Logistic Regression
    print("  Training Logistic Regression...")
    lr_agent = LogisticRegressionAgent('agent_lr')
    lr_agent.train(data['X_train'], data['y_train'])
    lr_pred, _ = lr_agent.predict(data['X_val'][:5])
    print(f"    [OK] Logistic Regression trained (sample prediction: {lr_pred})")
    
    # Step 3: Save models
    print("\n[3/3] Saving trained models...")
    
    agents = {
        'naive_bayes': nb_agent,
        'random_forest': rf_agent,
        'logistic_regression': lr_agent
    }
    
    for name, agent in agents.items():
        path = output_dir / f"{name}_agent.pkl"
        with open(path, 'wb') as f:
            pickle.dump(agent, f)
        print(f"  [OK] Saved: {path.name}")
    
    # Verify
    print("\n[4/4] Verifying saved models...")
    for name in agents.keys():
        path = output_dir / f"{name}_agent.pkl"
        with open(path, 'rb') as f:
            agent = pickle.load(f)
        print(f"  [OK] Verified: {name}_agent.pkl")
    
    print("\n" + "="*70)
    print("SUCCESS: All models trained and saved!")
    print("="*70)
    print(f"\nModels saved in: {output_dir}")
    print("Ready for API integration!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
