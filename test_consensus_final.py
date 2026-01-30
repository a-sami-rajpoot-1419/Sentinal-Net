#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sentinel-Net Consensus Engine

Tests:
1. Individual model predictions
2. Consensus predictions
3. Weight updates and reputation tracking
4. Full logging of all discussions and consensus decisions

Author: Sentinel-Net Team
Date: 2026-01-30
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Setup logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_consensus_results.log')
    ]
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.models.naive_bayes import NaiveBayesAgent
from backend.models.random_forest import RandomForestAgent
from backend.models.logistic_regression import LogisticRegressionAgent
from backend.models.svm import SVMAgent
from backend.consensus.engine import ConsensusEngine
from backend.data.loader import DataLoader


class TestConsensusEngine:
    """Comprehensive test suite for consensus engine"""
    
    def __init__(self):
        """Initialize test suite"""
        self.results = {
            'test_cases': [],
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'consensus_logs': []
        }
        logger.info("="*80)
        logger.info("SENTINEL-NET CONSENSUS ENGINE TEST SUITE")
        logger.info("="*80)
    
    def load_data(self):
        """Load preprocessed dataset"""
        logger.info("\n[SETUP] Loading dataset...")
        loader = DataLoader(
            cache_dir="data/cache",
            raw_dir="data/raw",
            processed_dir="data/processed"
        )
        data = loader.load_and_cache()
        logger.info(f"[OK] Dataset loaded: {data['X_train'].shape[0]} train samples")
        return data
    
    def load_trained_models(self) -> Dict:
        """Load trained models from pickle files"""
        logger.info("\n[SETUP] Loading trained models...")
        models_dir = Path("outputs/models")
        agents = {}
        
        for model_file in sorted(models_dir.glob("*_agent.pkl")):
            try:
                import pickle
                with open(model_file, 'rb') as f:
                    agent = pickle.load(f)
                
                agent_name = model_file.stem.replace('_agent', '')
                agents[agent_name] = agent
                
                status = "[OK] Trained" if agent.is_trained else "[??] Untrained"
                logger.info(f"  {agent_name:25s}: {status}")
                
            except Exception as e:
                logger.warning(f"  Failed to load {model_file.name}: {e}")
        
        logger.info(f"[OK] Loaded {len(agents)} agents")
        return agents
    
    def initialize_consensus_engine(self, agents: Dict) -> ConsensusEngine:
        """Initialize consensus engine with agents"""
        logger.info("\n[SETUP] Initializing consensus engine...")
        engine = ConsensusEngine(agents=agents)
        logger.info("[OK] Consensus engine initialized")
        logger.info(f"  Initial weights: {engine.get_weights()}")
        return engine
    
    def test_individual_predictions(self, agents: Dict, X_test: np.ndarray, y_test: np.ndarray):
        """Test individual model predictions"""
        logger.info("\n" + "="*80)
        logger.info("TEST 1: INDIVIDUAL MODEL PREDICTIONS")
        logger.info("="*80)
        
        # Use first 3 test samples
        for sample_idx in range(min(3, len(X_test))):
            X_sample = X_test[sample_idx:sample_idx+1]
            y_true = y_test[sample_idx]
            
            logger.info(f"\n[Sample {sample_idx+1}] True Label: {y_true} ({'SPAM' if y_true == 1 else 'HAM'})")
            logger.info("-" * 80)
            
            test_case = {
                'test_name': f'individual_prediction_{sample_idx}',
                'true_label': int(y_true),
                'sample_index': sample_idx,
                'predictions': {}
            }
            
            for agent_name, agent in agents.items():
                if not agent.is_trained:
                    logger.info(f"  {agent_name:25s}: [SKIP] (not trained)")
                    continue
                
                try:
                    prediction, confidence = agent.predict(X_sample)
                    prediction_label = 'SPAM' if prediction == 1 else 'HAM'
                    correct = "[OK]" if prediction == y_true else "[X]"
                    
                    logger.info(f"  {agent_name:25s}: {prediction_label:5s} (conf: {confidence:.4f}) {correct}")
                    
                    test_case['predictions'][agent_name] = {
                        'prediction': int(prediction),
                        'confidence': float(confidence),
                        'correct': prediction == y_true
                    }
                    
                except Exception as e:
                    logger.error(f"  {agent_name}: ERROR - {e}")
                    test_case['predictions'][agent_name] = {'error': str(e)}
            
            self.results['test_cases'].append(test_case)
            self.results['total_tests'] += 1
    
    def test_consensus_predictions(self, engine: ConsensusEngine, X_test: np.ndarray, y_test: np.ndarray):
        """Test consensus predictions"""
        logger.info("\n" + "="*80)
        logger.info("TEST 2: CONSENSUS PREDICTIONS")
        logger.info("="*80)
        
        for sample_idx in range(min(3, len(X_test))):
            X_sample = X_test[sample_idx:sample_idx+1]
            y_true = y_test[sample_idx]
            
            logger.info(f"\n[Sample {sample_idx+1}] True Label: {y_true} (consensus prediction)")
            logger.info("-" * 80)
            
            try:
                result = engine.predict(X_sample)
                
                consensus_label = 'SPAM' if result.predicted_class == 1 else 'HAM'
                correct = "[OK]" if result.predicted_class == y_true else "[X]"
                
                logger.info(f"\n  CONSENSUS PREDICTION: {consensus_label} (confidence: {result.confidence:.4f}) {correct}")
                logger.info(f"  Agreement Rate: {result.reasoning.get('agreement_rate', 0):.2%}")
                
                logger.info("\n  Individual Predictions:")
                for agent_name, (pred, conf) in result.agent_predictions.items():
                    pred_label = 'SPAM' if pred == 1 else 'HAM'
                    logger.info(f"    {agent_name:25s}: {pred_label} (conf: {conf:.4f})")
                
                logger.info(f"\n  Agent Weights (for consensus):")
                for agent_name, weight in result.weights.items():
                    logger.info(f"    {agent_name:25s}: {weight:.4f}")
                
                # Log reasoning
                if 'reasoning_details' in result.reasoning:
                    logger.info(f"\n  Consensus Reasoning:")
                    for detail in result.reasoning.get('reasoning_details', []):
                        logger.info(f"    - {detail}")
                
                test_case = {
                    'test_name': f'consensus_prediction_{sample_idx}',
                    'true_label': int(y_true),
                    'consensus': {
                        'prediction': int(result.predicted_class),
                        'confidence': float(result.confidence),
                        'correct': result.predicted_class == y_true,
                        'agreement_rate': float(result.reasoning.get('agreement_rate', 0)),
                        'individual_predictions': {
                            name: {'prediction': int(pred), 'confidence': float(conf)}
                            for name, (pred, conf) in result.agent_predictions.items()
                        }
                    }
                }
                
                self.results['test_cases'].append(test_case)
                self.results['total_tests'] += 1
                self.results['passed'] += 1
                
                # Log consensus discussion
                self.results['consensus_logs'].append({
                    'sample_index': sample_idx,
                    'true_label': int(y_true),
                    'consensus_prediction': int(result.predicted_class),
                    'reasoning': result.reasoning
                })
                
            except Exception as e:
                logger.error(f"ERROR in consensus prediction: {e}")
                self.results['total_tests'] += 1
                self.results['failed'] += 1
    
    def test_weight_updates(self, engine: ConsensusEngine, X_test: np.ndarray, y_test: np.ndarray):
        """Test weight updates based on feedback"""
        logger.info("\n" + "="*80)
        logger.info("TEST 3: WEIGHT UPDATES & REPUTATION TRACKING")
        logger.info("="*80)
        
        initial_weights = engine.get_weights()
        logger.info(f"\nInitial Weights:")
        for agent_name, weight in initial_weights.items():
            logger.info(f"  {agent_name:25s}: {weight:.6f}")
        
        # Make predictions and update weights
        for sample_idx in range(min(3, len(X_test))):
            X_sample = X_test[sample_idx:sample_idx+1]
            y_true = y_test[sample_idx]
            
            logger.info(f"\n[Sample {sample_idx+1}] Updating weights based on true label: {y_true}")
            
            try:
                result = engine.predict(X_sample)
                
                # Prepare predictions dict
                predictions = {
                    name: (pred, conf)
                    for name, (pred, conf) in result.agent_predictions.items()
                }
                
                # Update weights
                updated_weights = engine.update_weights_from_feedback(
                    true_label=y_true,
                    predictions=predictions
                )
                
                logger.info(f"\n  Weight Updates:")
                for agent_name, new_weight in updated_weights.items():
                    old_weight = initial_weights.get(agent_name, 1.0)
                    change = new_weight - old_weight
                    change_pct = (change / old_weight) * 100 if old_weight != 0 else 0
                    
                    change_symbol = "UP" if change > 0 else "DOWN" if change < 0 else "SAME"
                    logger.info(
                        f"    {agent_name:25s}: {old_weight:.6f} -> {new_weight:.6f} "
                        f"({change:+.6f}, {change_pct:+.2f}%) {change_symbol}"
                    )
                
                # Get reputations
                reputations = engine.get_all_reputations()
                logger.info(f"\n  Reputation Summary:")
                for agent_name, rep in reputations.items():
                    logger.info(
                        f"    {agent_name:25s}: "
                        f"Accuracy={rep['accuracy']:.4f}, "
                        f"Precision={rep.get('precision', 0.0):.4f}, "
                        f"Weight={rep['current_weight']:.6f}"
                    )
                
                # Update initial weights for next iteration
                initial_weights = updated_weights
                self.results['passed'] += 1
                
            except Exception as e:
                logger.error(f"ERROR in weight update: {e}")
                self.results['failed'] += 1
            
            self.results['total_tests'] += 1
    
    def test_batch_predictions(self, engine: ConsensusEngine, X_test: np.ndarray, y_test: np.ndarray):
        """Test batch predictions"""
        logger.info("\n" + "="*80)
        logger.info("TEST 4: BATCH PREDICTIONS")
        logger.info("="*80)
        
        X_batch = X_test[:5]
        y_batch = y_test[:5]
        
        logger.info(f"\nBatch size: {len(X_batch)} samples")
        
        try:
            results = engine.batch_predict(X_batch)
            
            logger.info(f"\nBatch Results:")
            correct_count = 0
            
            for i, result in enumerate(results):
                pred_label = 'SPAM' if result.predicted_class == 1 else 'HAM'
                true_label = 'SPAM' if y_batch[i] == 1 else 'HAM'
                correct = result.predicted_class == y_batch[i]
                if correct:
                    correct_count += 1
                
                symbol = "[OK]" if correct else "[X]"
                logger.info(
                    f"  [{i+1}] True: {true_label:5s}, "
                    f"Pred: {pred_label:5s}, "
                    f"Conf: {result.confidence:.4f} {symbol}"
                )
            
            accuracy = correct_count / len(results) if results else 0
            logger.info(f"\nBatch Accuracy: {correct_count}/{len(results)} ({accuracy:.1%})")
            
            self.results['total_tests'] += 1
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"ERROR in batch prediction: {e}")
            self.results['total_tests'] += 1
            self.results['failed'] += 1
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*80)
        logger.info("TEST SUMMARY")
        logger.info("="*80)
        
        logger.info(f"\nTotal Tests: {self.results['total_tests']}")
        logger.info(f"Passed: {self.results['passed']}")
        logger.info(f"Failed: {self.results['failed']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests']) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        
        logger.info(f"\nConsensus Decisions Logged: {len(self.results['consensus_logs'])}")
        
        # Save detailed results
        results_file = "test_consensus_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"\nDetailed results saved to: {results_file}")
        
        logger.info("\n" + "="*80)
        logger.info("TESTS COMPLETE")
        logger.info("="*80 + "\n")


def main():
    """Run all tests"""
    try:
        test_suite = TestConsensusEngine()
        
        # Load data
        data = test_suite.load_data()
        X_test = data['X_test']
        y_test = data['y_test']
        
        # Load models
        agents = test_suite.load_trained_models()
        
        if not agents:
            logger.error("No trained models found!")
            return 1
        
        # Initialize consensus engine
        engine = test_suite.initialize_consensus_engine(agents)
        
        # Run tests
        test_suite.test_individual_predictions(agents, X_test, y_test)
        test_suite.test_consensus_predictions(engine, X_test, y_test)
        test_suite.test_weight_updates(engine, X_test, y_test)
        test_suite.test_batch_predictions(engine, X_test, y_test)
        
        # Print summary
        test_suite.print_summary()
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
