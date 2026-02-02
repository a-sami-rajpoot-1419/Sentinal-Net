"""
Consensus Prediction Endpoints
Phase 7: Updated to use model loading and consensus engine from app
Phase 8: Database integration for logging and persistence
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any
import numpy as np
import uuid
from datetime import datetime
from backend.consensus.engine import ConsensusEngine, ConsensusResult
from backend.shared.exceptions_v2 import ConsensusException
from backend.database import get_db

router = APIRouter(prefix="/consensus", tags=["consensus"])


class PredictionRequest(BaseModel):
    """Request model for single prediction"""
    features: List[float] = Field(..., description="Feature vector (1004 dimensions)")


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    features: List[List[float]] = Field(..., description="Batch of feature vectors")


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    predicted_class: int
    confidence: float
    agent_predictions: Dict[str, Dict[str, Any]]
    weights: Dict[str, float]
    reasoning: Dict[str, Any]


class WeightUpdateRequest(BaseModel):
    """Request to update agent weights based on feedback"""
    true_label: int
    predictions: Dict[str, List[Any]]  # {agent_name: [class, confidence]}


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Get consensus prediction for a single sample
    
    Args:
        request: PredictionRequest with feature vector
        
    Returns:
        PredictionResponse with consensus result
    """
    try:
        # Import inside function to avoid circular imports
        from backend.api.app import get_consensus_engine
        
        # Get consensus engine (initialized on startup)
        consensus_engine = get_consensus_engine()
        
        # Convert to numpy array
        X = np.array(request.features).reshape(1, -1)
        
        if X.shape[1] != 1004:
            raise ValueError(f"Expected 1004 features, got {X.shape[1]}")
        
        # Get consensus prediction
        result: ConsensusResult = consensus_engine.predict(X)
        
        return PredictionResponse(
            predicted_class=result.predicted_class,
            confidence=result.confidence,
            agent_predictions={
                name: {
                    "class": int(pred[0]),
                    "confidence": float(pred[1]),
                }
                for name, pred in result.agent_predictions.items()
            },
            weights={name: float(w) for name, w in result.weights.items()},
            reasoning=result.reasoning,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConsensusException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/batch-predict")
async def batch_predict(request: BatchPredictionRequest) -> Dict[str, Any]:
    """
    Get consensus predictions for multiple samples
    
    Args:
        request: BatchPredictionRequest with feature vectors
        
    Returns:
        Dictionary with predictions, statistics, and consensus metrics
    """
    try:
        # Import inside function to avoid circular imports
        from backend.api.app import get_consensus_engine
        
        # Get consensus engine (initialized on startup)
        consensus_engine = get_consensus_engine()
        
        # Convert to numpy array
        X = np.array(request.features)
        
        if X.shape[1] != 1004:
            raise ValueError(f"Expected 1004 features, got {X.shape[1]}")
        
        # Get batch predictions
        results = consensus_engine.batch_predict(X)
        
        # Aggregate statistics
        predictions_list = [
            {
                "predicted_class": r.predicted_class,
                "confidence": float(r.confidence),
                "agent_predictions": {
                    name: {"class": int(pred[0]), "confidence": float(pred[1])}
                    for name, pred in r.agent_predictions.items()
                },
            }
            for r in results
        ]
        
        # Calculate aggregate statistics
        confidences = [r.confidence for r in results]
        predicted_classes = [r.predicted_class for r in results]
        
        return {
            "total_predictions": len(results),
            "predictions": predictions_list,
            "statistics": {
                "mean_confidence": float(np.mean(confidences)),
                "std_confidence": float(np.std(confidences)),
                "min_confidence": float(np.min(confidences)),
                "max_confidence": float(np.max(confidences)),
                "class_distribution": {
                    int(c): int(predicted_classes.count(c))
                    for c in set(predicted_classes)
                },
            },
            "weights": consensus_engine.get_weights(),
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConsensusException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@router.post("/update-weights")
async def update_weights(request: WeightUpdateRequest) -> Dict[str, Any]:
    """
    Update agent weights based on prediction feedback (RWPV mechanism)
    
    Args:
        request: WeightUpdateRequest with true label and predictions
        
    Returns:
        Dictionary with updated weights and reputation metrics
    """
    # Import inside function to avoid circular imports
    from backend.api.app import get_consensus_engine
    
    consensus_engine = get_consensus_engine()
    if not consensus_engine:
        raise HTTPException(status_code=503, detail="Consensus engine not initialized")
    
    try:
        # Parse predictions
        predictions = {
            agent_name: (int(pred[0]), float(pred[1]))
            for agent_name, pred in request.predictions.items()
        }
        
        # Update weights
        updated_weights = consensus_engine.update_weights_from_feedback(
            true_label=request.true_label,
            predictions=predictions,
        )
        
        # Get updated reputations
        reputations = consensus_engine.get_all_reputations()
        
        return {
            "success": True,
            "updated_weights": {name: float(w) for name, w in updated_weights.items()},
            "reputations": reputations,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConsensusException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weight update error: {str(e)}")


@router.get("/weights")
async def get_weights() -> Dict[str, float]:
    """Get current agent weights"""
    from backend.api.app import get_consensus_engine
    consensus_engine = get_consensus_engine()
    if not consensus_engine:
        raise HTTPException(status_code=503, detail="Consensus engine not initialized")
    
    return {name: float(w) for name, w in consensus_engine.get_weights().items()}


@router.get("/reputations")
async def get_reputations() -> Dict[str, Any]:
    """Get reputation statistics for all agents"""
    from backend.api.app import get_consensus_engine
    consensus_engine = get_consensus_engine()
    if not consensus_engine:
        raise HTTPException(status_code=503, detail="Consensus engine not initialized")
    
    return consensus_engine.get_all_reputations()


@router.get("/reputation/{agent_name}")
async def get_agent_reputation(agent_name: str) -> Dict[str, Any]:
    """Get agent reputation stats."""
    from backend.api.app import get_consensus_engine
    ce = get_consensus_engine()
    if not ce:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    try:
        return ce.get_agent_reputation(agent_name)
    except ConsensusException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reset-weights")
async def reset_weights() -> Dict[str, Any]:
    """Reset all agent weights to 1.0"""
    from backend.api.app import get_consensus_engine
    consensus_engine = get_consensus_engine()
    if not consensus_engine:
        raise HTTPException(status_code=503, detail="Consensus engine not initialized")
    
    try:
        consensus_engine.reset_weights()
        return {
            "success": True,
            "message": "Weights reset to 1.0",
            "weights": consensus_engine.get_weights(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prediction-history")
async def get_prediction_history(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent prediction history"""
    from backend.api.app import get_consensus_engine
    consensus_engine = get_consensus_engine()
    if not consensus_engine:
        raise HTTPException(status_code=503, detail="Consensus engine not initialized")
    
    history = consensus_engine.get_prediction_history()
    return history[-limit:]
