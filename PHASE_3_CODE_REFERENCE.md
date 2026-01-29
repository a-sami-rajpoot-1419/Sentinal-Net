# Phase 3 Code Reference Card

## Quick API Reference

### AgentBase (Interface)

```python
from backend.models.base import AgentBase

# All agents implement this interface:

class MyAgent(AgentBase):
    def __init__(self, agent_id: str = "my_agent"):
        super().__init__(agent_id)
        self.model = MyMLModel()
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model."""
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray, return_confidence: bool = True) -> Tuple[int, float]:
        """Get prediction and confidence."""
        prediction = self.model.predict(X)[0]
        confidence = self.model.predict_proba(X).max()
        return int(prediction), float(confidence)
    
    def _generate_reasoning(self, X, prediction, confidence) -> Dict:
        """Explain the prediction."""
        return {
            'reasoning': '...',
            'key_features': [...],
            'model_explanation': '...'
        }

# Properties
agent.weight                    # Reputation weight (mutable)
agent.total_votes              # Total predictions made
agent.correct_votes            # Number correct
agent.accuracy                 # correct_votes / total_votes

# Methods
agent.update_accuracy(True)    # Update vote stats
agent.get_prediction_with_reasoning(X)  # Full output dict
```

### NaiveBayesAgent

```python
from backend.models.naive_bayes import NaiveBayesAgent

agent = NaiveBayesAgent("agent_nb")  # Default ID: "agent_nb"
agent.train(X_train, y_train)
prediction, confidence = agent.predict(X_test)
result = agent.get_prediction_with_reasoning(X_test)
```

### SVMAgent

```python
from backend.models.svm import SVMAgent

agent = SVMAgent("agent_svm")  # Default ID: "agent_svm"
agent.train(X_train, y_train)
prediction, confidence = agent.predict(X_test)

# Reasoning includes decision_distance
result = agent.get_prediction_with_reasoning(X_test)
print(result['reasoning'])  # Includes "Decision boundary distance"
```

### RandomForestAgent

```python
from backend.models.random_forest import RandomForestAgent

agent = RandomForestAgent("agent_rf")  # Default ID: "agent_rf"
agent.train(X_train, y_train)
prediction, confidence = agent.predict(X_test)

# Reasoning includes top feature importances
result = agent.get_prediction_with_reasoning(X_test)
print(result['key_features'])  # Top 5 important features
```

### LogisticRegressionAgent

```python
from backend.models.logistic_regression import LogisticRegressionAgent

agent = LogisticRegressionAgent("agent_lr")  # Default ID: "agent_lr"
agent.train(X_train, y_train)
prediction, confidence = agent.predict(X_test)

# Reasoning includes feature coefficients
result = agent.get_prediction_with_reasoning(X_test)
print(result['reasoning'])  # Mentions top positive/negative features
```

### ModelTrainer (Orchestrator)

```python
from backend.models.trainer import ModelTrainer
from backend.data.loader import DataLoader

# Initialize
trainer = ModelTrainer()  # Manages all 4 agents

# Train all agents
results = trainer.train_all(
    X_train, y_train,  # Training data
    X_val, y_val       # Validation data (optional)
)
# Returns: {
#     'naive_bayes': {'train_accuracy': 0.92, 'val_accuracy': 0.91, 'training_time': 0.1},
#     'svm': {...},
#     'random_forest': {...},
#     'logistic_regression': {...},
#     'total_training_time': 4.5
# }

# Get predictions from all agents
predictions = trainer.predict_all(X_sample)  # X_sample shape: (1, 1004)
# Returns: {
#     'naive_bayes': (1, 0.87),
#     'svm': (1, 0.93),
#     'random_forest': (1, 0.95),
#     'logistic_regression': (1, 0.89)
# }

# Get full predictions with reasoning
pred_with_reasoning = trainer.get_predictions_with_reasoning(X_sample)
# Returns list of 4 dicts with agent_id, prediction, confidence, reasoning, weight

# Weight management
weights = trainer.get_agent_weights()
# Returns: {'naive_bayes': 1.0, 'svm': 1.0, 'random_forest': 1.0, 'logistic_regression': 1.0}

trainer.update_agent_weights('svm', 1.5)  # Update SVM weight to 1.5

# Access individual agents
trainer.agents['naive_bayes']    # Get specific agent
trainer.agents['svm']
trainer.agents['random_forest']
trainer.agents['logistic_regression']
```

## Complete Workflow Example

```python
import numpy as np
from backend.models.trainer import ModelTrainer
from backend.data.loader import DataLoader

# Step 1: Load data from Phase 2
loader = DataLoader()
data = loader.load_and_cache()
X_train, y_train = data['X_train'], data['y_train']
X_val, y_val = data['X_val'], data['y_val']
X_test, y_test = data['X_test'], data['y_test']

# Step 2: Initialize trainer
trainer = ModelTrainer()

# Step 3: Train all agents
print("Training...")
results = trainer.train_all(X_train, y_train, X_val, y_val)
for agent, metrics in results.items():
    if agent != 'total_training_time':
        print(f"{agent}: train={metrics['train_accuracy']:.3f}, val={metrics['val_accuracy']:.3f}")

# Step 4: Make predictions
print("\nPredicting on test set...")
correct = 0
for i in range(len(X_test)):
    X_sample = X_test[i:i+1]
    y_true = y_test[i]
    
    # Get all agent predictions
    all_preds = trainer.predict_all(X_sample)
    
    # Simple majority voting (Phase 4 will do weighted voting)
    votes = [pred[0] for pred in all_preds.values()]
    final_pred = max(set(votes), key=votes.count)
    
    if final_pred == y_true:
        correct += 1

accuracy = correct / len(X_test)
print(f"\nTest Accuracy: {accuracy:.1%}")

# Step 5: Get reasoning for sample
print("\nSample predictions with reasoning:")
X_sample = X_test[0:1]
pred_dicts = trainer.get_predictions_with_reasoning(X_sample)
for pred in pred_dicts:
    print(f"\n{pred['agent_id']}:")
    print(f"  Prediction: {pred['prediction']}")
    print(f"  Confidence: {pred['confidence']:.1%}")
    print(f"  Reasoning: {pred['reasoning']}")
    print(f"  Weight: {pred['weight']:.2f}")
```

## Common Patterns

### Pattern 1: Train Single Agent
```python
from backend.models.naive_bayes import NaiveBayesAgent

agent = NaiveBayesAgent()
agent.train(X_train, y_train)

# Evaluate
correct = sum(1 for i in range(len(y_test)) 
              if agent.predict(X_test[i:i+1])[0] == y_test[i])
accuracy = correct / len(y_test)
print(f"Accuracy: {accuracy:.1%}")
```

### Pattern 2: Compare All Agents
```python
from backend.models.trainer import ModelTrainer

trainer = ModelTrainer()
trainer.train_all(X_train, y_train, X_val, y_val)

# Evaluate all agents
for agent_name, agent in trainer.agents.items():
    correct = sum(1 for i in range(len(y_test))
                  if agent.predict(X_test[i:i+1])[0] == y_test[i])
    accuracy = correct / len(y_test)
    print(f"{agent_name}: {accuracy:.1%}")
```

### Pattern 3: Get Reasoning
```python
pred_dict = agent.get_prediction_with_reasoning(X_sample)

print(f"Agent: {pred_dict['agent_id']}")
print(f"Prediction: {pred_dict['prediction']} (ham=0, spam=1)")
print(f"Confidence: {pred_dict['confidence']:.1%}")
print(f"Reasoning: {pred_dict['reasoning']}")
print(f"Key Features: {pred_dict['key_features']}")
print(f"Weight: {pred_dict['weight']:.3f}")
```

### Pattern 4: Update Weights (Phase 4 Preview)
```python
# Reward good agent
trainer.update_agent_weights('svm', trainer.agents['svm'].weight * 1.05)

# Penalize bad agent
trainer.update_agent_weights('nb', trainer.agents['nb'].weight * 0.90)

# Check new weights
print(trainer.get_agent_weights())
```

## Input/Output Specifications

### Input
```python
X: np.ndarray
  - Shape: (n_samples, 1004)
  - Type: float32 or float64
  - Range: [0.0, 1.0] (normalized by TF-IDF)

y: np.ndarray
  - Shape: (n_samples,)
  - Type: int (0 or 1)
  - Values: 0 = ham (legitimate), 1 = spam
```

### Output (Single Prediction)
```python
prediction: int
  - Value: 0 or 1

confidence: float
  - Range: [0.0, 1.0]
  - Meaning: Probability of prediction being correct
```

### Output (With Reasoning)
```python
{
    'agent_id': str,              # e.g., 'agent_nb'
    'prediction': int,            # 0 or 1
    'confidence': float,          # 0.0 to 1.0
    'reasoning': str,             # Explanation text
    'key_features': List[str],   # Important feature names
    'weight': float               # Reputation weight
}
```

## Error Handling

```python
try:
    agent = NaiveBayesAgent()
    agent.train(X_train, y_train)
    pred, conf = agent.predict(X_test)
except Exception as e:
    print(f"Error: {e}")
    # Common errors:
    # - ValueError: X must be 2D array
    # - TypeError: y must be 1D array
    # - RuntimeError: model not trained yet
```

## Testing Patterns

```python
# Test agent training
def test_agent_training():
    agent = NaiveBayesAgent()
    assert agent.model is not None
    
    X_train = np.random.rand(100, 1004)
    y_train = np.random.randint(0, 2, 100)
    agent.train(X_train, y_train)
    
    assert agent.model.n_features_in_ == 1004

# Test predictions
def test_agent_predictions():
    agent = RandomForestAgent()
    X_train = np.random.rand(100, 1004)
    y_train = np.random.randint(0, 2, 100)
    agent.train(X_train, y_train)
    
    X_test = np.random.rand(5, 1004)
    for i in range(5):
        pred, conf = agent.predict(X_test[i:i+1])
        assert isinstance(pred, (int, np.integer))
        assert 0.0 <= conf <= 1.0

# Test reasoning
def test_reasoning():
    agent = SVMAgent()
    X_train = np.random.rand(100, 1004)
    y_train = np.random.randint(0, 2, 100)
    agent.train(X_train, y_train)
    
    X_test = np.random.rand(1, 1004)
    pred, conf = agent.predict(X_test)
    reasoning = agent._generate_reasoning(X_test, pred, conf)
    
    assert 'reasoning' in reasoning
    assert 'key_features' in reasoning
    assert isinstance(reasoning['reasoning'], str)
```

## Debugging Tips

### Agent not training
```python
# Check if data is correct shape
print(f"X shape: {X_train.shape}")  # Should be (n, 1004)
print(f"y shape: {y_train.shape}")  # Should be (n,)

# Check if classes exist
print(f"Unique classes: {np.unique(y_train)}")  # Should be [0, 1]
```

### Low accuracy
```python
# Check if data is preprocessed
print(f"Feature range: {X_train.min():.3f} to {X_train.max():.3f}")
# Should be normalized (mostly 0-1)

# Check class distribution
print(f"Class distribution: {np.bincount(y_train)}")
# Should be reasonably balanced (or at least known)
```

### Prediction always same class
```python
# Check model training
print(f"Model trained: {agent.model is not None}")

# Check prediction variance
for i in range(10):
    pred, conf = agent.predict(X_test[i:i+1])
    print(f"{i}: pred={pred}, conf={conf:.1%}")
# Should see variation, not all same
```

## Performance Tips

```python
# Use batch predictions instead of single
predictions = trainer.predict_all(X_test)  # Fast

# Instead of
for i in range(len(X_test)):
    pred = trainer.predict_all(X_test[i:i+1])  # Slower

# Pre-allocate trainer once
trainer = ModelTrainer()
trainer.train_all(X_train, y_train)
# Reuse for many predictions (don't retrain)

# If memory limited
# - Use RandomForest with fewer trees (n_estimators=50)
# - Use smaller feature dimension in Phase 2
```

## Summary

**4 Agents**: NaiveBayes, SVM, RandomForest, LogisticRegression
**Interface**: AgentBase (train, predict, reasoning)
**Orchestrator**: ModelTrainer (manage all agents)
**Input**: 1004-dim vectors
**Output**: (int prediction, float confidence) + reasoning
**Ready for**: Phase 4 consensus engine

See: `PHASE_3_README.md` for full documentation
