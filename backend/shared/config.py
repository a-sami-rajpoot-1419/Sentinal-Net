"""
Configuration Management Module

Centralized configuration for Sentinel-Net using Pydantic.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings


class Config(BaseSettings):
    """
    Application configuration.
    
    Loads from .env file with environment variable overrides.
    """
    
    # ===== DATABASE =====
    db_type: str = "local"  # Options: local, postgresql
    database_url: Optional[str] = None
    
    # ===== API CONFIGURATION =====
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"  # Options: development, staging, production
    
    # ===== LOGGING =====
    log_level: str = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_dir: str = "outputs/logs"
    max_log_size_mb: int = 100
    log_backup_count: int = 5
    
    # ===== DATA CONFIGURATION =====
    data_raw_dir: str = "data/raw"
    data_processed_dir: str = "data/processed"
    data_cache_dir: str = "data/cache"
    
    # ===== MODEL CONFIGURATION =====
    models_output_dir: str = "outputs/models"
    vectorizer_vocabulary_size: int = 1000
    
    # ===== EXPERIMENT CONFIGURATION =====
    simulation_rounds: int = 500
    test_set_size: float = 0.1
    validation_set_size: float = 0.1
    random_seed: int = 42
    
    # ===== CONSENSUS CONFIGURATION =====
    consensus_threshold: float = 0.5
    weight_reward_correct: float = 1.05
    weight_penalty_wrong: float = 0.90
    weight_reward_minority: float = 1.15
    weight_penalty_both_wrong: float = 0.85
    weight_min: float = 0.1
    weight_max: float = 5.0
    
    # ===== FRONTEND =====
    next_public_api_url: str = "http://localhost:8000"
    next_public_app_name: str = "Sentinel-Net"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get or create global configuration instance.
    
    Returns:
        Config: Application configuration
        
    Example:
        >>> config = get_config()
        >>> print(config.api_port)
        8000
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset global configuration (for testing)."""
    global _config
    _config = None


# Export config
config = get_config()
