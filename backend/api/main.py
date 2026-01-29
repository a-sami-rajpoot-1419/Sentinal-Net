"""
Phase 4 API Server Startup Script
Run this to start the FastAPI server with consensus engine integration
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from backend.api.app import app
from backend.api.routes import include_routes
from backend.models.trainer import ModelTrainer
from backend.consensus.engine import ConsensusEngine
from backend.data.loader import DataLoader
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("Starting Sentinel-Net Consensus Engine...")
    
    try:
        # Load Phase 3 models
        logger.info("Loading Phase 3 models...")
        global model_trainer, consensus_engine, data_loader
        
        model_trainer = ModelTrainer()
        data_loader = DataLoader()
        
        # Initialize consensus engine
        logger.info("Initializing consensus engine...")
        consensus_engine = ConsensusEngine(
            agents=model_trainer.agents,
            weight_reward_correct=float(os.getenv("WEIGHT_REWARD_CORRECT", 1.05)),
            weight_penalty_wrong=float(os.getenv("WEIGHT_PENALTY_WRONG", 0.90)),
            weight_reward_minority=float(os.getenv("WEIGHT_REWARD_MINORITY", 1.15)),
            weight_penalty_both_wrong=float(os.getenv("WEIGHT_PENALTY_BOTH_WRONG", 0.85)),
        )
        
        # Make consensus engine available to routes
        from backend.api.routes import consensus, agents
        consensus.consensus_engine = consensus_engine
        consensus.model_trainer = model_trainer
        consensus.data_loader = data_loader
        agents.model_trainer = model_trainer
        
        logger.info("✓ Consensus engine ready")
        logger.info(f"✓ Loaded {len(consensus_engine.agents)} ML agents")
        logger.info(f"✓ API running at http://{os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', 8000)}")
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Sentinel-Net Consensus Engine...")


# Include all routes
include_routes(app)


def main():
    """Run the FastAPI server"""
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "backend.api.main:app",
        host=host,
        port=port,
        reload=os.getenv("API_ENV", "development") == "development",
        workers=int(os.getenv("WORKERS", 1)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()
