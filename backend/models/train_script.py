"""
Phase 3: Train ML Models

Main script to train all 4 ML models using the data pipeline.

Usage:
    python -m backend.models.train_script

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import sys
import logging
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
from backend.data.loader import DataLoader
from backend.models.trainer import ModelTrainer
from backend.shared.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training pipeline."""
    logger.info("=" * 70)
    logger.info("PHASE 3: TRAIN ML MODELS")
    logger.info("=" * 70)
    
    try:
        # Load configuration
        config = get_config()
        logger.info(f"Configuration loaded: {config.environment}")
        
        # Load and prepare data
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: Loading Data")
        logger.info("=" * 70)
        
        data_loader = DataLoader(config)
        dataset = data_loader.load_and_cache()
        
        logger.info(f"Dataset loaded:")
        logger.info(f"  - Train samples: {len(dataset.get_train_data()[0])}")
        logger.info(f"  - Val samples: {len(dataset.get_val_data()[0])}")
        logger.info(f"  - Test samples: {len(dataset.get_test_data()[0])}")
        logger.info(f"  - Features: {dataset.n_features}")
        
        X_train, y_train = dataset.get_train_data()
        X_val, y_val = dataset.get_val_data()
        X_test, y_test = dataset.get_test_data()
        
        # Initialize trainer
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: Initialize Agents")
        logger.info("=" * 70)
        
        trainer = ModelTrainer()
        logger.info(f"Initialized {len(trainer.agents)} agents:")
        for agent_name, agent in trainer.agents.items():
            logger.info(f"  - {agent_name}: {agent.__class__.__name__}")
        
        # Train all models
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: Train Models")
        logger.info("=" * 70)
        
        training_times = trainer.train_all(X_train, y_train)
        
        logger.info("Training complete:")
        for agent_name, elapsed in training_times.items():
            logger.info(f"  - {agent_name}: {elapsed:.2f}s")
        logger.info(f"  - Total: {sum(training_times.values()):.2f}s")
        
        # Evaluate on validation set
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: Evaluate on Validation Set")
        logger.info("=" * 70)
        
        val_results = trainer.evaluate_all(X_val, y_val, dataset_name='validation')
        
        logger.info("Validation Results:")
        logger.info(f"{'Agent':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}")
        logger.info("-" * 70)
        
        for agent_name, metrics in val_results.items():
            logger.info(
                f"{agent_name:<25} "
                f"{metrics['accuracy']:<12.4f} "
                f"{metrics['precision']:<12.4f} "
                f"{metrics['recall']:<12.4f} "
                f"{metrics['f1']:<12.4f}"
            )
        
        # Evaluate on test set
        logger.info("\n" + "=" * 70)
        logger.info("STEP 5: Evaluate on Test Set")
        logger.info("=" * 70)
        
        test_results = trainer.evaluate_all(X_test, y_test, dataset_name='test')
        
        logger.info("Test Results:")
        logger.info(f"{'Agent':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}")
        logger.info("-" * 70)
        
        for agent_name, metrics in test_results.items():
            logger.info(
                f"{agent_name:<25} "
                f"{metrics['accuracy']:<12.4f} "
                f"{metrics['precision']:<12.4f} "
                f"{metrics['recall']:<12.4f} "
                f"{metrics['f1']:<12.4f}"
            )
        
        # Get rankings
        logger.info("\n" + "=" * 70)
        logger.info("STEP 6: Agent Rankings by Test Accuracy")
        logger.info("=" * 70)
        
        rankings = trainer.get_agent_rankings('accuracy')
        for rank, (agent_name, score) in enumerate(rankings, 1):
            logger.info(f"  {rank}. {agent_name}: {score:.4f}")
        
        # Test ensemble predictions
        logger.info("\n" + "=" * 70)
        logger.info("STEP 7: Test Ensemble Predictions")
        logger.info("=" * 70)
        
        # Sample 5 test cases
        sample_size = min(5, len(X_test))
        for i in range(sample_size):
            consensus, conf, details = trainer.predict_ensemble(X_test[i])
            actual = y_test[i]
            
            logger.info(f"\nSample {i+1}:")
            logger.info(f"  Actual: {actual}")
            logger.info(f"  Consensus: {consensus} (confidence: {conf:.4f})")
            logger.info(f"  Individual predictions: {details['individual_predictions']}")
            logger.info(f"  Agreement: {details['agreement']:.2%}")
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 3 SUMMARY")
        logger.info("=" * 70)
        
        best_agent, best_score = rankings[0] if rankings else ("N/A", 0.0)
        logger.info(f"Best performing agent: {best_agent} ({best_score:.4f} accuracy)")
        logger.info(f"Total training time: {sum(training_times.values()):.2f}s")
        logger.info(f"Models ready for Phase 4 (Consensus Engine)")
        
        logger.info("\n✅ Phase 3 Complete - All models trained and evaluated")
        
        return trainer, val_results, test_results
        
    except Exception as e:
        logger.error(f"❌ Phase 3 Failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    trainer, val_results, test_results = main()
