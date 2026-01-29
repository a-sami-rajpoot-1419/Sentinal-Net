# 🏗️ **Architecture Decision Records (ADRs)**

Technical decisions and design patterns used in Sentinel-Net.

---

## ADR-001: RWPV Protocol Over Traditional Consensus

### Decision
Use custom **Reputation-Weighted Proposer-Voter (RWPV)** protocol instead of traditional consensus mechanisms (BFT, PoS).

### Rationale
- **BFT:** Designed for Byzantine resilience in distributed systems, overkill for local ML models
- **PoS:** Designed for financial transactions, not semantic correctness
- **RWPV:** Optimized for AI agents, tracks accuracy not stake

### Implementation
- Phase-based consensus (collect → aggregate → decide → update)
- Reputation = historical accuracy (not financial stake)
- Weights automatically adjust based on correctness

### Trade-offs
| Aspect | RWPV | BFT | PoS |
|--------|------|-----|-----|
| Semantic correctness | ✅ Optimized | ❌ Generic | ❌ Generic |
| Byzantine resistance | ✅ Tested | ✅ Proven | ✅ Proven |
| Complexity | ✅ Simple | ❌ Complex | ❌ Complex |
| Scalability | ✅ O(n) | ❌ O(n²) | ✅ O(n) |

---

## ADR-002: Agent Diversity Strategy

### Decision
Use 4 fundamentally different ML models instead of ensemble of same type.

### Models Chosen
1. **Naive Bayes:** Probabilistic (fast, interpretable)
2. **SVM:** Geometric (boundary-based)
3. **Random Forest:** Ensemble (decision trees)
4. **Logistic Regression:** Linear (baseline)

### Rationale
- **Diversity:** Different failure modes
- **Speed:** Each trains in < 5 seconds
- **Interpretability:** All are explainable
- **Proof-of-Concept:** Classic methods before scaling to LLMs

### Future Extensions
- Phase 10+: Add deep learning models (LLaMA, Mistral)
- Allow plugging in external models (OpenAI, Anthropic)
- Scale to 10+ diverse agents

### Trade-off
✅ **Proven:** 94%+ accuracy  
❌ **Not state-of-the-art:** ~5% lower than single fine-tuned BERT  
✅ **Worth it:** Explainability + reliability matter more

---

## ADR-003: Local-First Data Storage

### Decision
Store all data locally (JSON files) with PostgreSQL as optional upgrade.

### Architecture
```
Phase 1-6: JSON files (data/processed/, outputs/logs/)
Phase 7+: PostgreSQL (Supabase) optional, with JSON fallback
```

### Rationale
- **MVP:** JSON works fine for <100k predictions
- **Free:** No database cost during development
- **Portable:** Can run anywhere, no setup
- **Migration path:** Easy to add PostgreSQL later (repository pattern)

### Implementation
- Abstract repository pattern in `storage/repository.py`
- Concrete implementations: `json_storage.py`, `postgres.py`
- Switch via `.env` config: `DB_TYPE=local` or `DB_TYPE=postgresql`

### When to Upgrade
- When > 100k predictions logged
- When you need real-time queries across millions
- When deploying to multi-server setup

---

## ADR-004: FastAPI + TailwindCSS Stack

### Decision
Use **FastAPI** (backend) + **Next.js** (frontend) instead of alternatives.

### Why FastAPI?
- ✅ **Async:** Built-in async/await (fast)
- ✅ **Type hints:** Automatic validation + documentation
- ✅ **Modern:** Latest Python features
- ✅ **OpenAPI:** Auto-generated API docs

### Why NOT Django?
- ❌ Too heavyweight for microservice
- ❌ Slower due to synchronous design
- ❌ Overkill for this use case

### Why Next.js + TailwindCSS?
- ✅ **React:** Rich interactive UI
- ✅ **Server rendering:** Fast initial load
- ✅ **File-based routes:** Simple structure
- ✅ **TailwindCSS:** Utility-first styling (fast)

### Why NOT Next.js 13 App Router?
- Using Pages Router for simplicity and stability
- App Router is newer, Pages is battle-tested

---

## ADR-005: Test Coverage Requirements

### Decision
Minimum **80% code coverage** for each module.

### Structure
```
backend/[module]/tests/test_*.py  # Unit tests
api/tests/test_routes.py          # Integration tests
```

### Tools
- **pytest:** Test runner
- **pytest-cov:** Coverage reporting
- **httpx:** HTTP client for API tests

### Rationale
- 80% catches most bugs (diminishing returns beyond)
- 100% coverage = wasted time on trivial tests
- Focus on critical paths and error cases

### Enforcement
```bash
# Before committing
pytest backend/ --cov=backend --cov-report=term-missing
# Must see: Coverage total: >= 80%
```

---

## ADR-006: Logging Strategy

### Decision
Use **structured JSON logging** instead of traditional log files.

### Format
```json
{
  "timestamp": "2026-01-29T14:30:00Z",
  "level": "INFO",
  "module": "api.routes.predictions",
  "message": "Prediction completed",
  "problem_id": "uuid-123",
  "decision": "spam",
  "confidence": 0.925,
  "processing_time_ms": 95
}
```

### Rationale
- **Queryable:** Can search by any field
- **Parseable:** Easy to analyze with code
- **Scalable:** Works with any logging backend
- **Secure:** No plaintext passwords in logs

### Storage
- **Development:** `outputs/logs/api_YYYY-MM-DD.log`
- **Production:** ClickHouse (or similar)

### Log Retention
- Keep 30 days locally
- Archive to S3 (future)

---

## ADR-007: Configuration Management

### Decision
Use `.env` file + `config.py` class for all configuration.

### Pattern
```python
# .env file
DB_TYPE=local
LOG_LEVEL=INFO
CONSENSUS_THRESHOLD=0.5

# backend/shared/config.py
from pydantic import BaseSettings

class Config(BaseSettings):
    db_type: str = "local"
    log_level: str = "INFO"
    consensus_threshold: float = 0.5
    
    class Config:
        env_file = ".env"

# In your code
from backend.shared.config import get_config
config = get_config()
print(config.db_type)  # "local"
```

### Rationale
- **No hardcoding:** All config externalized
- **Type-safe:** Pydantic validates types
- **Environment-aware:** Different configs for dev/prod

---

## ADR-008: Error Handling Strategy

### Decision
Use custom exception classes + clear HTTP status codes.

### Exception Hierarchy
```python
# backend/shared/exceptions.py
class SentinelException(Exception):
    """Base exception"""
    pass

class DataPreprocessingError(SentinelException):
    """Data pipeline errors"""
    pass

class ConsensusError(SentinelException):
    """RWPV protocol errors"""
    pass

class ModelError(SentinelException):
    """Model training/prediction errors"""
    pass
```

### HTTP Status Codes
- `400 Bad Request`: Invalid input
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing failure
- `503 Service Unavailable`: Temporary failure

### Example
```python
@router.post("/predict")
async def predict(request: PredictionRequest):
    try:
        # Process
        return result
    except DataPreprocessingError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid text: {str(e)}"
        )
    except ConsensusError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Consensus failed: {str(e)}"
        )
```

---

## ADR-009: Agent Interface Design

### Decision
Use abstract base class (`AgentBase`) for all models.

### Interface
```python
from abc import ABC, abstractmethod

class AgentBase(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.weight = 1.0
        self.model = None
    
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray, return_confidence: bool = True) -> Tuple[int, float]:
        pass
    
    @abstractmethod
    def _generate_reasoning(self, X: np.ndarray, prediction: int) -> Dict:
        pass
```

### Rationale
- **Extensible:** Easy to add new agents
- **Consistent:** All agents have same interface
- **Testable:** Can mock agents in tests
- **Future-proof:** Can add LLM agents later

### How to Add New Agent
1. Create `backend/models/new_model.py`
2. Extend `AgentBase`
3. Implement 3 abstract methods
4. Add to `AgentPool` in consensus engine

---

## ADR-010: Visualization Strategy

### Decision
Generate **multiple plot types** (not repeated visualizations).

### Plot Types (Phase 5+)
| Plot | Purpose | Library |
|------|---------|---------|
| Line chart | Accuracy over time | Matplotlib |
| Bar chart | Per-agent comparison | Plotly |
| Heatmap | Confusion matrix | Seaborn |
| Gauge chart | Current confidence | Plotly |
| Scatter plot | Weight vs accuracy | Matplotlib |

### Storage
- `outputs/plots/*.png` - Static plots
- Dashboard endpoints - Interactive plots

### Rationale
- **Variety:** Different plots show different insights
- **Accessible:** PNG files for reports
- **Interactive:** Web dashboards for exploration

---

## ADR-011: Testing Pyramid

### Decision
Follow standard testing pyramid: Unit > Integration > E2E

### Structure
```
Tests:
├── Unit tests (70%)         - Test individual functions
├── Integration tests (20%)   - Test module interactions
└── E2E tests (10%)          - Test full workflows
```

### Test Organization
```
backend/[module]/tests/
├── test_unit_*.py           - Unit tests
├── test_integration_*.py     - Integration tests
└── conftest.py              - Shared fixtures
```

### Example
```python
# test_unit_preprocessor.py
def test_lowercase_conversion():
    """Unit: Single function"""
    result = preprocess("HELLO")
    assert result.lower() == "hello"

# test_integration_data_pipeline.py
def test_full_preprocessing_pipeline():
    """Integration: Multiple functions"""
    data = DataLoader().load_and_cache()
    assert len(data) > 0

# api/tests/test_routes.py
def test_predict_endpoint():
    """E2E: Full API request"""
    response = client.post("/api/v1/predict", json={"text": "..."})
    assert response.status_code == 200
```

---

## ADR-012: Documentation Requirements

### Decision
Maintain 4 documentation tiers for different audiences.

### Tiers
1. **Developer** (`docs/developer/`) - Code patterns, setup, debugging
2. **Stakeholder** (`docs/stakeholder/`) - ROI, metrics, business value
3. **Visitor** (`docs/visitor/`) - User guide, features, how to use
4. **Metrics** (`docs/metrics/`) - Performance analysis, benchmarks

### Rule
Every public function/class needs:
- Google-style docstring
- Type hints
- Example usage (if complex)
- Related documentation link

---

## ADR-013: Git Workflow

### Decision
Push to GitHub after each major phase completion.

### Commit Pattern
```bash
git commit -m "Phase X: [Description]"

# Examples:
# Phase 2: Data pipeline complete - preprocessing, caching, unit tests
# Phase 3: All 4 models trained and benchmarked
# Phase 4: RWPV consensus engine with reputation system
```

### Rationale
- Clear history of progress
- Easy to rollback if needed
- Stakeholder transparency
- Code review opportunities

---

## ADR-014: Modular Design Principles

### Decision
Ensure every component can be swapped/upgraded independently.

### Key Principles

**1. Dependency Injection**
```python
# ❌ BAD: Hardcoded dependency
class Consensus:
    def __init__(self):
        self.preprocessor = DataPreprocessor()

# ✅ GOOD: Injected dependency
class Consensus:
    def __init__(self, preprocessor: DataPreprocessor):
        self.preprocessor = preprocessor
```

**2. Abstract Interfaces**
```python
# Repository pattern - can swap implementations
class RepositoryBase(ABC):
    @abstractmethod
    def save(self, data): pass

class JSONRepository(RepositoryBase):
    def save(self, data): ...

class PostgresRepository(RepositoryBase):
    def save(self, data): ...
```

**3. Configuration over Hardcoding**
```python
# ✅ GOOD
weights = {
    "reward_correct": config.weight_reward_correct,
    "penalty_wrong": config.weight_penalty_wrong,
}

# ❌ BAD
weights = {
    "reward_correct": 1.05,
    "penalty_wrong": 0.90,
}
```

### Benefits
- Easy to test (mock dependencies)
- Easy to upgrade (swap implementations)
- Easy to scale (add new agents, databases, etc.)
- Future-proof design

---

## Decision Log

| ADR | Topic | Date | Status |
|-----|-------|------|--------|
| 001 | RWPV Protocol | 2026-01-29 | ✅ Implemented |
| 002 | Agent Diversity | 2026-01-29 | ✅ Implemented |
| 003 | Local-First Storage | 2026-01-29 | ✅ Implemented |
| 004 | Tech Stack | 2026-01-29 | ✅ Implemented |
| 005 | Testing | 2026-01-29 | ✅ Implemented |
| 006 | Logging | 2026-01-29 | ⏳ Phase 8 |
| 007 | Configuration | 2026-01-29 | ⏳ Phase 1 |
| 008 | Error Handling | 2026-01-29 | ⏳ Phase 6 |
| 009 | Agent Interface | 2026-01-29 | ⏳ Phase 3 |
| 010 | Visualization | 2026-01-29 | ⏳ Phase 5 |
| 011 | Testing Pyramid | 2026-01-29 | ✅ Implemented |
| 012 | Documentation | 2026-01-29 | ✅ Implemented |
| 013 | Git Workflow | 2026-01-29 | ✅ Implemented |
| 014 | Modularity | 2026-01-29 | ✅ Implemented |

---

**For questions about architectural decisions, refer to this document.**
