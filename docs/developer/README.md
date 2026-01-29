# 👨‍💻 **Developer Guide: Sentinel-Net**

Complete guide for developers building and extending Sentinel-Net.

---

## 📋 **Table of Contents**

1. [Setup & Installation](#setup--installation)
2. [Project Structure](#project-structure)
3. [Code Style & Standards](#code-style--standards)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Common Tasks](#common-tasks)
7. [Debugging](#debugging)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 **Setup & Installation**

### Step 1: Clone & Create Virtual Environment

```bash
cd c:\Sami\Sentinal-net

# Create Python virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 2: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import sklearn; print('✓ All dependencies installed')"
```

### Step 3: Setup Environment

```bash
# Copy example config
copy .env.example .env

# Edit .env if needed (defaults work for local dev)
# Most settings already configured for local JSON storage
```

### Step 4: Verify Setup

```bash
# Test backend imports
python -c "from backend.api import main; print('✓ Backend imports OK')"

# Test data pipeline
python -c "from backend.data.loader import DataLoader; print('✓ Data pipeline OK')"

# You're ready!
```

---

## 📁 **Project Structure**

### Backend Organization

```
backend/
├── api/                      # FastAPI application
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # Pydantic request/response schemas
│   ├── dependencies.py      # Dependency injection
│   ├── routes/
│   │   ├── predictions.py   # POST /api/v1/predict
│   │   ├── experiments.py   # POST /api/v1/experiment/run
│   │   ├── logs.py          # GET /api/v1/logs/{id}
│   │   └── metrics.py       # GET /api/v1/metrics/
│   └── tests/               # API tests
│
├── models/                   # ML Model Agents
│   ├── __init__.py
│   ├── base.py              # AgentBase abstract class (INTERFACE)
│   ├── naive_bayes.py       # Naive Bayes agent
│   ├── svm.py               # SVM agent
│   ├── random_forest.py     # Random Forest agent
│   ├── logistic_regression.py # LR agent
│   ├── trainer.py           # Model trainer orchestrator
│   └── tests/               # Model tests
│
├── consensus/               # RWPV Protocol
│   ├── __init__.py
│   ├── protocol.py          # Main RWPV consensus engine
│   ├── reputation.py        # Weight management system
│   ├── vote.py              # Vote dataclass
│   └── tests/               # Protocol tests
│
├── data/                    # Data Pipeline
│   ├── __init__.py
│   ├── preprocessor.py      # TF-IDF + feature engineering
│   ├── loader.py            # DataLoader with caching
│   ├── dataset.py           # Dataset wrapper
│   └── tests/               # Data tests
│
├── storage/                 # Database Abstraction
│   ├── __init__.py
│   ├── repository.py        # Abstract Repository interface
│   ├── json_storage.py      # JSON file implementation
│   ├── postgres.py          # PostgreSQL implementation (future)
│   └── tests/               # Storage tests
│
├── logging_analytics/       # Logging & Metrics
│   ├── __init__.py
│   ├── logger.py            # Structured logging
│   ├── analyzer.py          # Log analysis tools
│   └── metrics.py           # Metrics calculation
│
├── shared/                  # Shared Code
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   ├── types.py             # Shared TypedDicts/types
│   └── utils.py             # Utility functions
│
└── __init__.py
```

### Data Organization

```
data/
├── raw/                     # Original downloaded dataset
│   └── spam.csv            # SMS Spam Collection
│
├── processed/              # After preprocessing
│   ├── X_train.npy        # Training features
│   ├── y_train.npy        # Training labels
│   ├── X_val.npy          # Validation features
│   ├── y_val.npy          # Validation labels
│   ├── X_test.npy         # Test features
│   └── y_test.npy         # Test labels
│
└── cache/
    └── processed_data.pkl  # Cached preprocessor + split data
```

### Output Organization

```
outputs/
├── models/
│   ├── naive_bayes_model.pkl
│   ├── svm_model.pkl
│   ├── random_forest_model.pkl
│   ├── logistic_regression_model.pkl
│   └── tfidf_vectorizer.pkl
│
├── logs/
│   ├── api_2026-01-29.log
│   ├── experiment_2026-01-29.log
│   ├── predictions.jsonl
│   └── consensus_history.jsonl
│
├── reports/
│   ├── experiment_report_001.json
│   ├── accuracy_comparison.md
│   └── byzantine_test_results.json
│
└── plots/
    ├── accuracy_comparison.png
    ├── weight_evolution.png
    ├── confusion_matrices.png
    ├── confidence_calibration.png
    └── agent_performance.png
```

---

## 📐 **Code Style & Standards**

### Python Style

Follow **PEP 8** with these additions:

```python
# ✅ Good
def preprocess_text(text: str) -> str:
    """Clean and normalize text.
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned text string
    """
    text = text.lower()
    return text.strip()

class DataPreprocessor:
    """Handles text preprocessing and vectorization."""
    
    def __init__(self, vocab_size: int = 1000):
        """Initialize preprocessor.
        
        Args:
            vocab_size: Vocabulary size for TF-IDF
        """
        self.vocab_size = vocab_size

# ❌ Avoid
def prep(t):
    return t.lower()
```

### Type Hints

Always use type hints:

```python
from typing import Dict, List, Optional, Tuple

def train_model(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.1
) -> Tuple[Any, float]:
    """Train model and return accuracy."""
    pass
```

### Docstring Format

Use Google-style docstrings:

```python
def consensus_vote(
    votes: List[Vote],
    weights: Dict[str, float]
) -> ConsensusResult:
    """Calculate weighted consensus from agent votes.
    
    Implements Phase 2-3 of RWPV protocol. Aggregates votes
    using reputation-weighted majority voting.
    
    Args:
        votes: List of Vote objects from all agents
        weights: Current reputation weights for each agent
        
    Returns:
        ConsensusResult containing decision and reasoning
        
    Raises:
        ValueError: If votes list is empty
        
    Example:
        >>> result = consensus_vote(votes, weights)
        >>> print(result.decision)  # 'spam' or 'ham'
    """
    pass
```

### Imports Organization

```python
# Standard library
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Third-party
import numpy as np
import pandas as pd
from fastapi import FastAPI
from sklearn.naive_bayes import MultinomialNB

# Local imports
from backend.shared.config import get_config
from backend.data.preprocessor import DataPreprocessor
```

---

## 🔄 **Development Workflow**

### Starting a Feature

```bash
# 1. Create feature branch
git checkout -b feature/new-feature-name

# 2. Create new files if needed
# (Use templates in next section)

# 3. Edit and test locally
pytest backend/ -v

# 4. When satisfied, commit
git add .
git commit -m "Feature: Description of what you added"

# 5. Push when phase complete
git push origin feature/new-feature-name
```

### File Templates

#### New Model Agent Template

```python
# backend/models/[new_model].py
from typing import Dict, Tuple
import numpy as np
from .base import AgentBase

class NewModelAgent(AgentBase):
    """Agent using NewModel algorithm."""
    
    def __init__(self, agent_id: str = "agent_new"):
        """Initialize agent.
        
        Args:
            agent_id: Unique identifier for this agent
        """
        super().__init__(agent_id)
        self.model = None  # Initialize your model here
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model."""
        # Your training code
        pass
    
    def predict(
        self,
        X: np.ndarray,
        return_confidence: bool = True
    ) -> Tuple[int, float]:
        """Make prediction."""
        # Your prediction code
        pass
    
    def _generate_reasoning(
        self,
        X: np.ndarray,
        prediction: int
    ) -> Dict[str, any]:
        """Generate reasoning for decision."""
        # Your reasoning code
        pass
```

#### New API Route Template

```python
# backend/api/routes/new_route.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["new_route"])

class NewRequest(BaseModel):
    """Request model."""
    field1: str
    field2: int

class NewResponse(BaseModel):
    """Response model."""
    result: str
    status: str

@router.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest) -> NewResponse:
    """Endpoint description.
    
    Args:
        request: Request parameters
        
    Returns:
        NewResponse with results
    """
    try:
        # Your logic here
        return NewResponse(result="success", status="ok")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### New Test Template

```python
# backend/[module]/tests/test_something.py
import pytest
from backend.[module].something import SomeClass

class TestSomeClass:
    """Tests for SomeClass."""
    
    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return SomeClass()
    
    def test_initialization(self, instance):
        """Test initialization."""
        assert instance is not None
    
    def test_main_method(self, instance):
        """Test main functionality."""
        result = instance.some_method()
        assert result is not None
    
    def test_error_handling(self, instance):
        """Test error handling."""
        with pytest.raises(ValueError):
            instance.some_method(invalid_input)
```

---

## 🧪 **Testing**

### Running Tests

```bash
# Run all tests
pytest backend/ -v

# Run tests for specific module
pytest backend/models/tests/ -v

# Run with coverage report
pytest backend/ --cov=backend --cov-report=html

# Run specific test
pytest backend/models/tests/test_naive_bayes.py::TestNaiveBayesAgent::test_training -v

# Run tests that match pattern
pytest -k "test_preprocess" -v

# Run tests with print statements
pytest backend/ -v -s
```

### Test Coverage

Aim for **80%+ coverage** per module:

```bash
# Generate coverage report
pytest backend/ --cov=backend --cov-report=term-missing

# Output shows uncovered lines
# backend/models/naive_bayes.py  45%  (lines 23, 45, 67)
```

### Writing Good Tests

```python
import pytest
import numpy as np
from backend.data.preprocessor import DataPreprocessor

class TestDataPreprocessor:
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance."""
        return DataPreprocessor(vocab_size=100)
    
    @pytest.fixture
    def sample_text(self):
        """Sample SMS text."""
        return "Free entry in 2 a wkly comp to win FA Cup"
    
    def test_initialization(self, preprocessor):
        """Test preprocessor initializes correctly."""
        assert preprocessor.vocab_size == 100
        assert preprocessor.vectorizer is not None
    
    def test_lowercase_conversion(self, preprocessor, sample_text):
        """Test text is converted to lowercase."""
        cleaned = preprocessor.preprocess(sample_text)
        assert cleaned['text_clean'] == cleaned['text_clean'].lower()
    
    def test_special_char_removal(self, preprocessor):
        """Test special characters are removed."""
        text = "Hello!!!@@@##"
        result = preprocessor.preprocess(text)
        assert all(c.isalnum() or c.isspace() for c in result['text_clean'])
    
    def test_vectorization(self, preprocessor, sample_text):
        """Test TF-IDF vectorization."""
        corpus = [sample_text, "Another message"]
        vectors = preprocessor.fit_transform(corpus)
        assert vectors.shape == (2, 100)  # 2 documents, 100 vocab size
```

---

## 🛠️ **Common Tasks**

### Adding a New Model Agent

**Step-by-step:**

1. Create new file: `backend/models/[model_name].py`
2. Extend `AgentBase` class
3. Implement `train()`, `predict()`, `_generate_reasoning()`
4. Add to imports in `backend/models/__init__.py`
5. Add to trainer in `backend/models/trainer.py`
6. Write tests in `backend/models/tests/`
7. Test locally before committing

### Adding a New API Endpoint

**Step-by-step:**

1. Create route file: `backend/api/routes/[feature].py`
2. Define Pydantic models (request/response)
3. Write route handler with proper error handling
4. Add to router in `backend/api/main.py`
5. Add to OpenAPI tags
6. Document with docstrings
7. Test with `pytest` and `httpx`
8. Document in `docs/api/`

### Adding a New Metric

**Step-by-step:**

1. Add calculation method to `backend/logging_analytics/metrics.py`
2. Add corresponding logging in relevant module
3. Add endpoint to expose metric in `backend/api/routes/metrics.py`
4. Add visualization function to generate plots
5. Document in `docs/metrics/`

### Changing Configuration

**Step-by-step:**

1. Add new config variable to `.env.example`
2. Add to `backend/shared/config.py` with type hint
3. Add default value in config class
4. Use via `config = get_config()` in code
5. Document in [Configuration Docs](../../../.env.example)

---

## 🔍 **Debugging**

### Enable Debug Logging

```python
# In your code
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug(f"Debug message: {variable}")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Run Backend with Debug

```bash
cd backend
python -m uvicorn api.main:app --reload --log-level debug
```

### Use Python Debugger

```python
# Add breakpoint in code
breakpoint()  # Execution pauses here

# Then in interactive prompt:
# (Pdb) print(variable)
# (Pdb) continue
# (Pdb) exit()
```

### Check API Responses

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Free money!"}'

# Using Python
import requests
response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={"text": "Free money!"}
)
print(response.json())
```

### Inspect Model Predictions

```python
from backend.models.naive_bayes import NaiveBayesAgent
from backend.data.loader import DataLoader

# Load data
data = DataLoader().load_and_cache()
X_test = data['X_test'][:5]  # First 5 samples

# Test model
agent = NaiveBayesAgent()
agent.train(data['X_train'], data['y_train'])

for i, x in enumerate(X_test):
    pred, conf = agent.predict(x.reshape(1, -1))
    print(f"Sample {i}: pred={pred}, confidence={conf}")
```

---

## ❓ **Troubleshooting**

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
```bash
# Make sure you're running from project root
cd c:\Sami\Sentinal-net

# Add to Python path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from correct directory
python -m backend.api.main
```

### Virtual Environment Issues

**Problem:** `python: command not found`

**Solution:**
```bash
# Activate venv
venv\Scripts\activate

# Verify activation (should show (venv) prefix)
which python  # Should show path in venv

# If still not working, recreate
rm -r venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Data File Not Found

**Problem:** `FileNotFoundError: data/raw/spam.csv`

**Solution:**
```bash
# Data file should be in data/raw/
# If missing, follow Phase 2 instructions to download:
# 1. Download from UCI ML Repository
# 2. Place in data/raw/spam.csv
# 3. Run: python backend/data/loader.py

# Check if file exists
ls data/raw/spam.csv
```

### Port Already in Use

**Problem:** `OSError: [Errno 10048] Only one usage of each socket address`

**Solution:**
```bash
# Change port
python -m uvicorn api.main:app --port 8001

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID [PID] /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Dependency Conflicts

**Problem:** `pip install` fails with version conflicts

**Solution:**
```bash
# Update pip
python -m pip install --upgrade pip setuptools wheel

# Install requirements one by one
pip install numpy==1.26.4
pip install pandas==2.2.0
# ... etc

# Or clear cache
pip install --no-cache-dir -r requirements.txt
```

---

## 📚 **Additional Resources**

- [Main README](../../README.md)
- [Architecture Docs](../architecture/README.md)
- [API Reference](../api/README.md)
- [Metrics Documentation](../metrics/README.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [pytest Docs](https://docs.pytest.org/)
- [scikit-learn Docs](https://scikit-learn.org/)

---

**Happy coding! Ask questions in the code, submit feedback, and keep improving.**
