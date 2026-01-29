"""
pytest configuration and shared fixtures.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pytest
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture
def test_data_dir():
    """Provide test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    from backend.shared.config import reset_config
    reset_config()
    yield
    reset_config()
