"""
Model Loader - Load or initialize trained ML agents

Handles loading pre-trained models from disk or initializing fresh agents.
Supports both pickle-based serialization and direct instantiation.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pickle
import os
from pathlib import Path
from typing import Dict, Optional
import logging

from .base import AgentBase
from .naive_bayes import NaiveBayesAgent
from .svm import SVMAgent
from .random_forest import RandomForestAgent
from .logistic_regression import LogisticRegressionAgent

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Loads pre-trained ML agents or initializes fresh ones.
    
    Supports two modes:
    1. Load from pickle files (if models have been trained and serialized)
    2. Initialize fresh untrained agents (for development)
    """
    
    # Default model directory
    DEFAULT_MODEL_DIR = Path(__file__).parent.parent.parent / "outputs" / "models"
    
    # Model file names (when pickled)
    MODEL_FILENAMES = {
        'naive_bayes': 'naive_bayes_agent.pkl',
        'svm': 'svm_agent.pkl',
        'random_forest': 'random_forest_agent.pkl',
        'logistic_regression': 'logistic_regression_agent.pkl',
    }
    
    # Agent ID to class mapping
    AGENT_CLASSES = {
        'naive_bayes': NaiveBayesAgent,
        'svm': SVMAgent,
        'random_forest': RandomForestAgent,
        'logistic_regression': LogisticRegressionAgent,
    }
    
    # Agent ID to class ID mapping (for initialization)
    AGENT_IDS = {
        'naive_bayes': 'agent_nb',
        'svm': 'agent_svm',
        'random_forest': 'agent_rf',
        'logistic_regression': 'agent_lr',
    }
    
    @classmethod
    def load_models(
        cls,
        model_dir: Optional[Path] = None,
        allow_uninitialized: bool = True
    ) -> Dict[str, AgentBase]:
        """
        Load pre-trained models from disk or initialize fresh ones.
        
        Priority:
        1. Try to load pickled models from disk
        2. If files don't exist and allow_uninitialized=True, initialize fresh agents
        3. Otherwise raise error
        
        Args:
            model_dir (Path, optional): Directory containing pickled models.
                                       Defaults to outputs/models/
            allow_uninitialized (bool): If True, initialize fresh agents if
                                       pickled versions don't exist.
                                       If False, raise error.
        
        Returns:
            Dict[str, AgentBase]: Dictionary of loaded/initialized agents
            
        Raises:
            FileNotFoundError: If model files not found and allow_uninitialized=False
            Exception: If loading fails (corruption, incompatible pickle, etc.)
        """
        if model_dir is None:
            model_dir = cls.DEFAULT_MODEL_DIR
        
        model_dir = Path(model_dir)
        agents = {}
        
        for agent_name, agent_class in cls.AGENT_CLASSES.items():
            agent_id = cls.AGENT_IDS[agent_name]
            model_file = model_dir / cls.MODEL_FILENAMES[agent_name]
            
            # Try to load from disk
            if model_file.exists():
                try:
                    logger.info(f"Loading {agent_name} from {model_file}")
                    with open(model_file, 'rb') as f:
                        agent = pickle.load(f)
                    
                    # Verify it's the right type
                    if not isinstance(agent, agent_class):
                        raise TypeError(
                            f"Loaded agent for {agent_name} is not a {agent_class.__name__}"
                        )
                    
                    agents[agent_name] = agent
                    logger.info(f"✓ {agent_name} loaded successfully (trained: {agent.is_trained})")
                    
                except FileNotFoundError:
                    logger.warning(f"{agent_name} model file not found: {model_file}")
                    if allow_uninitialized:
                        logger.info(f"Initializing fresh {agent_name} agent")
                        agents[agent_name] = agent_class(agent_id)
                    else:
                        raise
                        
                except Exception as e:
                    logger.error(f"Failed to load {agent_name}: {str(e)}")
                    if allow_uninitialized:
                        logger.info(f"Initializing fresh {agent_name} agent (load failed)")
                        agents[agent_name] = agent_class(agent_id)
                    else:
                        raise
            else:
                # File doesn't exist
                if allow_uninitialized:
                    logger.info(f"Model file not found, initializing fresh {agent_name} agent")
                    agents[agent_name] = agent_class(agent_id)
                else:
                    raise FileNotFoundError(
                        f"Model file not found: {model_file}\n"
                        f"Please train models first or set allow_uninitialized=True"
                    )
        
        logger.info(f"✓ Loaded {len(agents)} agents total")
        return agents
    
    @classmethod
    def save_models(
        cls,
        agents: Dict[str, AgentBase],
        model_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Save trained agents to disk as pickle files.
        
        Args:
            agents (Dict[str, AgentBase]): Dictionary of agents to save
            model_dir (Path, optional): Directory to save models.
                                       Defaults to outputs/models/
        
        Returns:
            Dict[str, Path]: Mapping of agent_name -> saved file path
            
        Raises:
            ValueError: If any agent is not trained
            IOError: If write fails
        """
        if model_dir is None:
            model_dir = cls.DEFAULT_MODEL_DIR
        
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = {}
        
        for agent_name, agent in agents.items():
            if not agent.is_trained:
                raise ValueError(f"Cannot save {agent_name}: agent is not trained")
            
            file_path = model_dir / cls.MODEL_FILENAMES[agent_name]
            
            try:
                logger.info(f"Saving {agent_name} to {file_path}")
                with open(file_path, 'wb') as f:
                    pickle.dump(agent, f, protocol=pickle.HIGHEST_PROTOCOL)
                saved_paths[agent_name] = file_path
                logger.info(f"✓ {agent_name} saved successfully")
            except Exception as e:
                logger.error(f"Failed to save {agent_name}: {str(e)}")
                raise
        
        logger.info(f"✓ Saved {len(saved_paths)} agents total")
        return saved_paths
    
    @classmethod
    def initialize_fresh(cls) -> Dict[str, AgentBase]:
        """
        Initialize fresh, untrained agents (for development/testing).
        
        Returns:
            Dict[str, AgentBase]: Dictionary of initialized but untrained agents
        """
        logger.info("Initializing fresh agents...")
        agents = {}
        
        for agent_name, agent_class in cls.AGENT_CLASSES.items():
            agent_id = cls.AGENT_IDS[agent_name]
            agents[agent_name] = agent_class(agent_id)
        
        logger.info(f"✓ Initialized {len(agents)} fresh agents")
        return agents
