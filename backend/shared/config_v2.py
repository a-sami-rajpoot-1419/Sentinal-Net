"""
Configuration Module - Sentinel-Net

Centralized configuration management using Pydantic.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

from pydantic import BaseSettings
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """
    Application configuration.
    
    Loads from .env file with sensible defaults.
    """
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    raw_data_dir: Path = data_dir / "raw"
    cache_dir: Path = data_dir / "cache"
    models_dir: Path = project_root / "backend" / "models"
    
    # Data Pipeline (Phase 2)
    raw_data_file: str = "spam.csv"
    test_size: float = 0.1
    val_size: float = 0.1
    random_state: int = 42
    
    # ML Models (Phase 3)
    tf_idf_max_features: int = 1000
    num_agents: int = 4
    
    # Consensus (Phase 4)
    consensus_threshold: float = 0.5
    weight_update_correct: float = 1.05
    weight_update_incorrect: float = 0.90
    weight_update_minority_correct: float = 1.15
    weight_update_both_wrong: float = 0.85
    
    # Database (Phase 7)
    database_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **data):
        """Initialize and create required directories."""
        super().__init__(**data)
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create required directories if they don't exist."""
        for dir_path in [self.data_dir, self.raw_data_dir, self.cache_dir, self.models_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")


# Global config instance
_config = None


def get_config() -> Config:
    """
    Get global config instance.
    
    Returns:
        Config: Application configuration
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config) -> None:
    """
    Set global config instance.
    
    Args:
        config (Config): New configuration
    """
    global _config
    _config = config
