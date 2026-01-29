"""
Custom Exceptions for Sentinel-Net

Defines exception hierarchy for the application.

Author: Sentinel-Net Team
Date: 2026-01-29
"""


class SentinelException(Exception):
    """Base exception for Sentinel-Net."""
    pass


class DataPreprocessingError(SentinelException):
    """Raised when data preprocessing fails."""
    pass


class DataLoadingError(SentinelException):
    """Raised when data loading fails."""
    pass


class ModelTrainingError(SentinelException):
    """Raised when model training fails."""
    pass


class ModelPredictionError(SentinelException):
    """Raised when model prediction fails."""
    pass


class ConsensusError(SentinelException):
    """Raised when consensus calculation fails."""
    pass


class ValidationError(SentinelException):
    """Raised when validation fails."""
    pass


class ConfigurationError(SentinelException):
    """Raised when configuration is invalid."""
    pass


class StorageError(SentinelException):
    """Raised when storage operations fail."""
    pass
