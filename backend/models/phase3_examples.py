"""
Phase 3 Complete Example - Sentinel-Net

Demonstrates full Phase 3 workflow with detailed output.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import numpy as np
from backend.models.trainer import ModelTrainer
from backend.models.naive_bayes import NaiveBayesAgent
from backend.models.svm import SVMAgent
from backend.models.random_forest import RandomForestAgent
from backend.models.logistic_regression import LogisticRegressionAgent


def example_basic_agent_usage():
    """Basic example: Train single agent and predict."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Agent Usage")
    print("=" * 80)
    
    # Generate synthetic data
    np.random.seed(42)
    X_train = np.random.rand(100, 1004)
    y_train = np.random.randint(0, 2, 100)
    X_test = np.random.rand(10, 1004)
    
    # Create and train agent
    agent = NaiveBayesAgent("my_nb_agent")
    print(f"\nCreated: {agent}")
    
    agent.train(X_train, y_train)
    print(f"Trained on {X_train.shape[0]} samples")
    
    # Make predictions
    for i in range(3):
        X_sample = X_test[i:i+1]
        prediction, confidence = agent.predict(X_sample)
        print(f"Sample {i}: Prediction={prediction}, Confidence={confidence:.1%}")
    
    print()


def example_agent_with_reasoning():
    """Example: Get predictions with reasoning."""
    print("=" * 80)
    print("EXAMPLE 2: Predictions with Reasoning")
    print("=" * 80)
    
    np.random.seed(42)
    X_train = np.random.rand(100, 1004)
    y_train = np.random.randint(0, 2, 100)
    X_test = np.random.rand(5, 1004)
    
    # Try different agents
    agents = [
        NaiveBayesAgent("nb"),
        SVMAgent("svm"),
        RandomForestAgent("rf"),
        LogisticRegressionAgent("lr")
    ]
    
    # Train all
    for agent in agents:
        agent.train(X_train, y_train)
    
    # Get predictions with reasoning for first test sample
    X_sample = X_test[0:1]
    
    print(f"\nPredictions for sample with full reasoning:")
    print("-" * 80)
    
    for agent in agents:
        result = agent.get_prediction_with_reasoning(X_sample)
        print(f"\n{result['agent_id']}:")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Weight: {result['weight']:.2f}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"  Key Features: {result['key_features'][:3]}...")  # First 3
    
    print()


def example_model_trainer():
    """Example: Use ModelTrainer to manage all agents."""
    print("=" * 80)
    print("EXAMPLE 3: ModelTrainer - Managing All Agents")
    print("=" * 80)
    
    np.random.seed(42)
    X_train = np.random.rand(200, 1004)
    y_train = np.random.randint(0, 2, 200)
    X_val = np.random.rand(50, 1004)
    y_val = np.random.randint(0, 2, 50)
    X_test = np.random.rand(10, 1004)
    y_test = np.random.randint(0, 2, 10)
    
    # Initialize trainer
    trainer = ModelTrainer()
    print(f"\nInitialized trainer with {len(trainer.agents)} agents")
    
    # Train all agents
    print("\nTraining all agents...")
    results = trainer.train_all(X_train, y_train, X_val, y_val)
    
    print("\nTraining Results:")
    print("-" * 80)
    for agent_name, metrics in results.items():
        if agent_name == 'total_training_time':
            print(f"Total training time: {metrics:.2f}s")
        else:
            print(f"{agent_name:20s} | "
                  f"Train Acc: {metrics['train_accuracy']:.3f} | "
                  f"Val Acc: {metrics['val_accuracy']:.3f} | "
                  f"Time: {metrics['training_time']:.2f}s")
    
    # Check agent weights
    print(f"\nAgent Weights (for Phase 4 reputation system):")
    for agent_name, weight in trainer.get_agent_weights().items():
        print(f"  {agent_name}: {weight:.2f}")
    
    print()


def example_batch_predictions():
    """Example: Get predictions from all agents for multiple samples."""
    print("=" * 80)
    print("EXAMPLE 4: Batch Predictions from All Agents")
    print("=" * 80)
    
    np.random.seed(42)
    X_train = np.random.rand(100, 1004)
    y_train = np.random.randint(0, 2, 100)
    X_test = np.random.rand(5, 1004)
    y_test = np.random.randint(0, 2, 5)
    
    trainer = ModelTrainer()
    trainer.train_all(X_train, y_train)
    
    print(f"\nBatch predictions for {len(y_test)} test samples:")
    print("-" * 80)
    
    for i in range(len(y_test)):
        X_sample = X_test[i:i+1]
        y_true = y_test[i]
        
        # Get all predictions
        predictions = trainer.predict_all(X_sample)
        
        # Show results
        print(f"\nSample {i} (True label: {y_true}):")
        for agent_name, (pred, conf) in predictions.items():
            match = "✓" if pred == y_true else "✗"
            print(f"  {match} {agent_name:20s}: Pred={pred}, Conf={conf:.1%}")
    
    print()


def example_weight_management():
    """Example: Update and manage agent weights."""
    print("=" * 80)
    print("EXAMPLE 5: Agent Weight Management (Phase 4 Preview)")
    print("=" * 80)
    
    trainer = ModelTrainer()
    
    print("\nInitial weights:")
    weights = trainer.get_agent_weights()
    for agent_name, weight in weights.items():
        print(f"  {agent_name}: {weight:.2f}")
    
    # Simulate weight updates based on performance
    print("\nSimulating Phase 4 weight updates...")
    print("-" * 80)
    
    # Reward best agent (SVM)
    trainer.update_agent_weights('svm', 1.1)
    print("✓ Rewarded SVM (correct prediction)")
    
    # Penalize worst agent (NB)
    trainer.update_agent_weights('naive_bayes', 0.95)
    print("✗ Penalized Naive Bayes (incorrect prediction)")
    
    # Bonus for minority correct
    trainer.update_agent_weights('logistic_regression', 1.15)
    print("☆ Bonus for Logistic Regression (minority correct)")
    
    print("\nUpdated weights:")
    weights = trainer.get_agent_weights()
    for agent_name, weight in weights.items():
        print(f"  {agent_name}: {weight:.2f}")
    
    print()


def example_comparison_all_agents():
    """Example: Compare all agent types side-by-side."""
    print("=" * 80)
    print("EXAMPLE 6: Agent Comparison")
    print("=" * 80)
    
    np.random.seed(42)
    X_train = np.random.rand(150, 1004)
    y_train = np.random.randint(0, 2, 150)
    X_val = np.random.rand(50, 1004)
    y_val = np.random.randint(0, 2, 50)
    
    agents = {
        'Naive Bayes': NaiveBayesAgent(),
        'SVM': SVMAgent(),
        'Random Forest': RandomForestAgent(),
        'Logistic Regression': LogisticRegressionAgent()
    }
    
    print("\nTraining and evaluating all agents...")
    print("-" * 80)
    
    results = []
    for agent_name, agent in agents.items():
        # Train
        agent.train(X_train, y_train)
        
        # Evaluate
        correct = sum(1 for i in range(len(y_val)) 
                     if agent.predict(X_val[i:i+1])[0] == y_val[i])
        accuracy = correct / len(y_val)
        
        results.append((agent_name, accuracy))
        print(f"{agent_name:20s}: {accuracy:.1%}")
    
    # Rank
    print("\nRanking:")
    print("-" * 80)
    for rank, (agent_name, accuracy) in enumerate(sorted(results, 
                                                         key=lambda x: x[1], 
                                                         reverse=True), 1):
        print(f"{rank}. {agent_name:20s}: {accuracy:.1%}")
    
    print()


def main():
    """Run all examples."""
    example_basic_agent_usage()
    example_agent_with_reasoning()
    example_model_trainer()
    example_batch_predictions()
    example_weight_management()
    example_comparison_all_agents()
    
    print("=" * 80)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 80)
    print("\nNext: Phase 4 - RWPV Consensus Engine")
    print("See PHASE_4_BLUEPRINT.py for implementation guide")


if __name__ == "__main__":
    main()
