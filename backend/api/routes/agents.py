"""
Agent and Model Management Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from backend.models.trainer import ModelTrainer
from backend.shared.exceptions_v2 import ConsensusError

router = APIRouter(prefix="/agents", tags=["agents"])

# Global instances
model_trainer: Optional[ModelTrainer] = None


class AgentInfoResponse(BaseModel):
    """Response model for agent information"""
    agent_name: str
    model_type: str
    accuracy: float
    weight: float
    is_trained: bool


@router.get("/list")
async def list_agents() -> Dict[str, Any]:
    """List all available agents and their status"""
    if not model_trainer:
        raise HTTPException(status_code=503, detail="Model trainer not initialized")
    
    try:
        agents_info = {}
        for agent_name, agent in model_trainer.agents.items():
            agents_info[agent_name] = {
                "agent_name": agent_name,
                "model_type": agent.__class__.__name__,
                "accuracy": float(agent.accuracy) if hasattr(agent, 'accuracy') else 0.0,
                "is_trained": agent.is_trained if hasattr(agent, 'is_trained') else False,
            }
        
        return {
            "total_agents": len(agents_info),
            "agents": agents_info,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")


@router.get("/{agent_name}")
async def get_agent_info(agent_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific agent"""
    if not model_trainer:
        raise HTTPException(status_code=503, detail="Model trainer not initialized")
    
    try:
        if agent_name not in model_trainer.agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = model_trainer.agents[agent_name]
        
        return {
            "agent_name": agent_name,
            "model_type": agent.__class__.__name__,
            "accuracy": float(agent.accuracy) if hasattr(agent, 'accuracy') else 0.0,
            "weight": float(model_trainer.get_agent_weights().get(agent_name, 1.0)),
            "is_trained": agent.is_trained if hasattr(agent, 'is_trained') else False,
            "confidence": float(agent.confidence) if hasattr(agent, 'confidence') else 0.0,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving agent info: {str(e)}")


@router.get("/performance/comparison")
async def compare_agent_performance() -> Dict[str, Any]:
    """Compare performance metrics across all agents"""
    if not model_trainer:
        raise HTTPException(status_code=503, detail="Model trainer not initialized")
    
    try:
        comparison = {
            "agents": {},
            "best_agent": None,
            "average_accuracy": 0.0,
        }
        
        accuracies = []
        for agent_name, agent in model_trainer.agents.items():
            accuracy = float(agent.accuracy) if hasattr(agent, 'accuracy') else 0.0
            accuracies.append(accuracy)
            
            comparison["agents"][agent_name] = {
                "accuracy": accuracy,
                "weight": float(model_trainer.get_agent_weights().get(agent_name, 1.0)),
                "model_type": agent.__class__.__name__,
            }
        
        if accuracies:
            best_agent = max(comparison["agents"].items(), key=lambda x: x[1]["accuracy"])
            comparison["best_agent"] = {
                "name": best_agent[0],
                "accuracy": best_agent[1]["accuracy"],
            }
            comparison["average_accuracy"] = sum(accuracies) / len(accuracies)
        
        return comparison
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing agents: {str(e)}")
