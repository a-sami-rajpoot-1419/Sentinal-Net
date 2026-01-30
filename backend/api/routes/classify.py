"""
Text Classification Endpoints with Database Logging
SMS Spam Classification with Consensus Engine
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import logging

from backend.data_preprocessing import DataPreprocessor
from backend.consensus.engine import ConsensusEngine
from backend.shared.exceptions_v2 import ConsensusException
from backend.database import get_db
from backend.api.app import get_consensus_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/classify", tags=["text-classification"])


class ClassifyRequest(BaseModel):
    """Request model for text classification"""
    text: str = Field(..., description="Text to classify (SMS message)")
    ground_truth: Optional[int] = Field(None, description="Optional: 0=ham, 1=spam for feedback")


class ClassifyResponse(BaseModel):
    """Response model for text classification"""
    prediction_id: str
    text: str
    classification: str  # "SPAM" or "HAM"
    confidence: float
    agent_votes: Dict[str, Dict[str, Any]]
    reasoning: Dict[str, Any]
    timestamp: str


class BatchClassifyRequest(BaseModel):
    """Request for batch classification"""
    texts: List[str] = Field(..., description="List of SMS messages")


@router.post("/text", response_model=ClassifyResponse)
async def classify_text(
    request: ClassifyRequest,
    background_tasks: BackgroundTasks,
) -> ClassifyResponse:
    """
    Classify a text message as SPAM or HAM using consensus voting
    
    Args:
        request: ClassifyRequest with text and optional ground truth
        background_tasks: FastAPI background tasks for async database logging
        
    Returns:
        ClassifyResponse with consensus classification
    """
    try:
        # Generate prediction ID
        prediction_id = str(uuid.uuid4())
        
        # Initialize preprocessor and consensus engine
        preprocessor = DataPreprocessor()
        consensus_engine = get_consensus_engine()
        
        if not consensus_engine:
            raise HTTPException(status_code=503, detail="Consensus engine not initialized")
        
        # Preprocess text
        processed = preprocessor.preprocess(request.text)
        text_clean = processed['text_clean']
        
        # Vectorize
        X = preprocessor.vectorizer.transform([text_clean]).toarray()
        
        # Get consensus prediction
        result = consensus_engine.predict(X)
        
        # Map prediction to label
        classification = "SPAM" if result.predicted_class == 1 else "HAM"
        
        # Format agent votes
        agent_votes = {}
        for agent_name, (prediction, confidence) in result.agent_predictions.items():
            agent_votes[agent_name] = {
                "prediction": "SPAM" if prediction == 1 else "HAM",
                "confidence": float(confidence),
                "weight": float(result.weights.get(agent_name, 1.0)),
            }
        
        # Log to database asynchronously
        background_tasks.add_task(
            _log_prediction_to_db,
            prediction_id=prediction_id,
            text_raw=request.text,
            text_clean=text_clean,
            classification=result.predicted_class,
            confidence=result.confidence,
            agent_votes=result.agent_predictions,
            agent_weights=result.weights,
            ground_truth=request.ground_truth,
        )
        
        return ClassifyResponse(
            prediction_id=prediction_id,
            text=request.text,
            classification=classification,
            confidence=float(result.confidence),
            agent_votes=agent_votes,
            reasoning=result.reasoning,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except ValueError as e:
        logger.error(f"Preprocessing error: {e}")
        raise HTTPException(status_code=400, detail=f"Text processing error: {str(e)}")
    except ConsensusException as e:
        logger.error(f"Consensus error: {e}")
        raise HTTPException(status_code=422, detail=f"Consensus error: {str(e)}")
    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.post("/batch-text")
async def classify_batch(
    request: BatchClassifyRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Classify multiple text messages in batch
    
    Args:
        request: BatchClassifyRequest with list of texts
        background_tasks: For async logging
        
    Returns:
        Dictionary with predictions and aggregate statistics
    """
    try:
        preprocessor = DataPreprocessor()
        consensus_engine = get_consensus_engine()
        
        if not consensus_engine:
            raise HTTPException(status_code=503, detail="Consensus engine not initialized")
        
        results = []
        predictions_data = []
        
        for text in request.texts:
            prediction_id = str(uuid.uuid4())
            
            try:
                # Preprocess and vectorize
                processed = preprocessor.preprocess(text)
                X = preprocessor.vectorizer.transform([processed['text_clean']]).toarray()
                
                # Get prediction
                result = consensus_engine.predict(X)
                classification = "SPAM" if result.predicted_class == 1 else "HAM"
                
                results.append({
                    "prediction_id": prediction_id,
                    "text": text,
                    "classification": classification,
                    "confidence": float(result.confidence),
                })
                
                predictions_data.append({
                    "prediction_id": prediction_id,
                    "text_clean": processed['text_clean'],
                    "classification": result.predicted_class,
                    "confidence": result.confidence,
                })
            
            except Exception as e:
                logger.error(f"Error processing text: {e}")
                results.append({
                    "prediction_id": prediction_id,
                    "text": text,
                    "error": str(e),
                })
        
        # Aggregate statistics
        successful_predictions = [r for r in results if "error" not in r]
        spam_count = sum(1 for r in successful_predictions if r["classification"] == "SPAM")
        ham_count = sum(1 for r in successful_predictions if r["classification"] == "HAM")
        
        confidences = [r["confidence"] for r in successful_predictions]
        
        # Log batch to database
        background_tasks.add_task(
            _log_batch_to_db,
            predictions_data=predictions_data,
        )
        
        return {
            "total_texts": len(request.texts),
            "successful": len(successful_predictions),
            "failed": len(results) - len(successful_predictions),
            "predictions": results,
            "statistics": {
                "spam_count": spam_count,
                "ham_count": ham_count,
                "mean_confidence": float(sum(confidences) / len(confidences)) if confidences else 0,
                "min_confidence": float(min(confidences)) if confidences else 0,
                "max_confidence": float(max(confidences)) if confidences else 0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    except ConsensusException as e:
        logger.error(f"Batch consensus error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Batch classification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prediction/{prediction_id}")
async def get_prediction_details(prediction_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific prediction"""
    try:
        db = get_db()
        prediction = db.get_prediction(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Get votes for this prediction
        votes = db.get_problem_votes(prediction_id)
        
        return {
            "prediction_id": prediction_id,
            "text": prediction.get("text_raw"),
            "classification": "SPAM" if prediction.get("consensus_decision") == 1 else "HAM",
            "confidence": prediction.get("consensus_confidence"),
            "votes": votes,
            "created_at": prediction.get("created_at"),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_predictions(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent predictions"""
    try:
        db = get_db()
        predictions = db.get_recent_predictions(limit=limit)
        
        return [
            {
                "prediction_id": str(p.get("problem_id")),
                "text": p.get("text_raw"),
                "classification": "SPAM" if p.get("consensus_decision") == 1 else "HAM",
                "confidence": p.get("consensus_confidence"),
                "created_at": p.get("created_at"),
            }
            for p in predictions
        ]
    
    except Exception as e:
        logger.error(f"Error retrieving predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== HELPER FUNCTIONS FOR BACKGROUND TASKS =====

def _log_prediction_to_db(
    prediction_id: str,
    text_raw: str,
    text_clean: str,
    classification: int,
    confidence: float,
    agent_votes: Dict[str, tuple],
    agent_weights: Dict[str, float],
    ground_truth: Optional[int] = None,
):
    """Log a single prediction to database"""
    try:
        db = get_db()
        
        # Log the prediction
        db.log_prediction(
            problem_id=prediction_id,
            text_raw=text_raw,
            text_clean=text_clean,
            consensus_decision=classification,
            consensus_confidence=confidence,
            ground_truth=ground_truth,
        )
        
        # Log individual votes
        for agent_name, (prediction, agent_confidence) in agent_votes.items():
            db.log_vote(
                problem_id=prediction_id,
                agent_id=agent_name,
                prediction=int(prediction),
                confidence=float(agent_confidence),
                weight_at_time=float(agent_weights.get(agent_name, 1.0)),
                reasoning={
                    "agent": agent_name,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                is_correct=None if ground_truth is None else (int(prediction) == ground_truth),
            )
        
        logger.info(f"✓ Prediction {prediction_id} logged to database")
    
    except Exception as e:
        logger.error(f"Error logging prediction to database: {e}")


def _log_batch_to_db(predictions_data: List[Dict[str, Any]]):
    """Log batch predictions to database"""
    try:
        db = get_db()
        
        for pred in predictions_data:
            db.log_prediction(
                problem_id=pred["prediction_id"],
                text_raw="",
                text_clean=pred["text_clean"],
                consensus_decision=int(pred["classification"]),
                consensus_confidence=pred["confidence"],
            )
        
        logger.info(f"✓ Batch of {len(predictions_data)} predictions logged to database")
    
    except Exception as e:
        logger.error(f"Error logging batch to database: {e}")
