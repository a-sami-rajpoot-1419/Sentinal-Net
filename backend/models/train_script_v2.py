"""
Complete Training Script for Phase 3 - Sentinel-Net

Full pipeline demonstrating:
1. Load data from Phase 2
2. Train all 4 ML agents
3. Evaluate on validation set
4. Generate predictions with reasoning
5. Save results

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import sys
import os
import numpy as np
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.loader import DataLoader
from backend.models.trainer import ModelTrainer
from backend.shared.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_data():
    """
    Load preprocessed data from Phase 2.
    
    Returns:
        Tuple of (X_train, y_train, X_val, y_val, X_test, y_test)
    """
    logger.info("=" * 80)
    logger.info("PHASE 3: ML MODEL TRAINING")
    logger.info("=" * 80)
    logger.info("\n[STEP 1] Loading data from Phase 2...")
    
    config = Config()
    loader = DataLoader(
        data_dir=config.data_dir,
        cache_dir=config.cache_dir,
        test_size=0.1,
        val_size=0.1,
        random_state=42
    )
    
    data = loader.load_and_cache()
    X_train = data['X_train']
    y_train = data['y_train']
    X_val = data['X_val']
    y_val = data['y_val']
    X_test = data['X_test']
    y_test = data['y_test']
    
    logger.info(f"✓ Data loaded successfully")
    logger.info(f"  - Training set: {X_train.shape}")
    logger.info(f"  - Validation set: {X_val.shape}")
    logger.info(f"  - Test set: {X_test.shape}")
    logger.info(f"  - Feature dimension: {X_train.shape[1]}")
    logger.info(f"  - Class distribution (train): {np.bincount(y_train)}")
    
    return X_train, y_train, X_val, y_val, X_test, y_test


def train_models(X_train, y_train, X_val, y_val):
    """
    Train all 4 ML agents.
    
    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        
    Returns:
        ModelTrainer instance with trained agents
    """
    logger.info("\n[STEP 2] Training all 4 ML agents...")
    logger.info("-" * 80)
    
    trainer = ModelTrainer()
    
    start_time = datetime.now()
    results = trainer.train_all(X_train, y_train, X_val, y_val)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"\n✓ All agents trained in {elapsed:.2f} seconds")
    logger.info("\nAgent Performance:")
    logger.info("-" * 80)
    
    for agent_name, metrics in results.items():
        if agent_name == 'total_training_time':
            continue
        
        train_acc = metrics['train_accuracy']
        val_acc = metrics['val_accuracy']
        train_time = metrics['training_time']
        
        logger.info(
            f"{agent_name:20s} | "
            f"Train Acc: {train_acc:.3f} | "
            f"Val Acc: {val_acc:.3f} | "
            f"Time: {train_time:.2f}s"
        )
    
    logger.info("-" * 80)
    logger.info(f"Total training time: {results['total_training_time']:.2f}s")
    
    return trainer, results


def evaluate_on_test_set(trainer, X_test, y_test):
    """
    Evaluate trained agents on test set.
    
    Args:
        trainer: Trained ModelTrainer
        X_test, y_test: Test data
        
    Returns:
        Dict of test accuracies
    """
    logger.info("\n[STEP 3] Evaluating on test set...")
    logger.info("-" * 80)
    
    test_results = {}
    
    for agent_name, agent in trainer.agents.items():
        correct = 0
        for i in range(len(y_test)):
            prediction, _ = agent.predict(X_test[i:i+1])
            if prediction == y_test[i]:
                correct += 1
        
        accuracy = correct / len(y_test)
        test_results[agent_name] = accuracy
        logger.info(f"{agent_name:20s} | Test Accuracy: {accuracy:.3f}")
    
    logger.info("-" * 80)
    
    return test_results


def demonstrate_predictions(trainer, X_test, y_test):
    """
    Demonstrate predictions on sample test cases.
    
    Args:
        trainer: Trained ModelTrainer
        X_test, y_test: Test data
    """
    logger.info("\n[STEP 4] Sample predictions with reasoning...")
    logger.info("-" * 80)
    
    # Show first 5 test samples
    num_samples = min(5, len(y_test))
    
    for i in range(num_samples):
        X_sample = X_test[i:i+1]
        y_true = y_test[i]
        
        logger.info(f"\nSample {i+1} (True label: {y_true}):")
        
        # Get predictions from all agents
        pred_dicts = trainer.get_predictions_with_reasoning(X_sample)
        
        for pred in pred_dicts:
            agent_id = pred['agent_id']
            prediction = pred['prediction']
            confidence = pred['confidence']
            reasoning = pred['reasoning']
            weight = pred['weight']
            
            match = "✓" if prediction == y_true else "✗"
            logger.info(
                f"  {match} {agent_id:15s} | "
                f"Pred: {prediction} | "
                f"Conf: {confidence:.1%} | "
                f"Weight: {weight:.2f}"
            )
            logger.info(f"      {reasoning}")
    
    logger.info("-" * 80)


def save_model_info(trainer, output_dir=None):
    """
    Save information about trained models.
    
    Args:
        trainer: Trained ModelTrainer
        output_dir: Directory to save info (optional)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / 'trained_models'
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n[STEP 5] Saving model information...")
    logger.info(f"Output directory: {output_dir}")
    
    # Save agent weights
    weights_file = output_dir / 'agent_weights.txt'
    with open(weights_file, 'w') as f:
        f.write("Agent Weights (Reputation System)\n")
        f.write("=" * 50 + "\n\n")
        for agent_name, weight in trainer.get_agent_weights().items():
            f.write(f"{agent_name}: {weight:.3f}\n")
    
    logger.info(f"✓ Saved agent weights to {weights_file}")
    
    # Save agent info
    info_file = output_dir / 'agent_info.txt'
    with open(info_file, 'w') as f:
        f.write("ML Agent Information\n")
        f.write("=" * 50 + "\n\n")
        for agent_name, agent in trainer.agents.items():
            f.write(f"Agent: {agent_name}\n")
            f.write(f"  Type: {agent.__class__.__name__}\n")
            f.write(f"  ID: {agent.agent_id}\n")
            f.write(f"  Weight: {agent.weight:.3f}\n")
            f.write(f"  Total Votes: {agent.total_votes}\n")
            f.write(f"  Correct Votes: {agent.correct_votes}\n")
            f.write(f"  Accuracy: {agent.accuracy:.3f}\n")
            f.write("\n")
    
    logger.info(f"✓ Saved agent info to {info_file}")


def main():
    """Execute complete training pipeline."""
    try:
        # Load data
        X_train, y_train, X_val, y_val, X_test, y_test = load_data()
        
        # Train models
        trainer, train_results = train_models(X_train, y_train, X_val, y_val)
        
        # Evaluate on test set
        test_results = evaluate_on_test_set(trainer, X_test, y_test)
        
        # Demonstrate predictions
        demonstrate_predictions(trainer, X_test, y_test)
        
        # Save model info
        save_model_info(trainer)
        
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3 TRAINING COMPLETE")
        logger.info("=" * 80)
        logger.info("\nNext: Phase 4 - Build RWPV Consensus Engine")
        
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
