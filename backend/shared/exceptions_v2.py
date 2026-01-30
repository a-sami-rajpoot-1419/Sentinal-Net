"""
Custom Exceptions - Sentinel-Net

Defines custom exception classes for error handling.

Author: Sentinel-Net Team
Date: 2026-01-29
"""


class SentinelNetException(Exception):
    """Base exception for all Sentinel-Net errors."""
    pass


class DataException(SentinelNetException):
    """Base exception for data-related errors."""
    pass


class DataLoadingError(DataException):
    """Raised when data loading fails."""
    pass


class DataPreprocessingError(DataException):
    """Raised when data preprocessing fails."""
    pass


class DataValidationError(DataException):
    """Raised when data validation fails."""
    pass


class ModelException(SentinelNetException):
    """Base exception for model-related errors."""
    pass


class ModelTrainingError(ModelException):
    """Raised when model training fails."""
    pass


class ModelPredictionError(ModelException):
    """Raised when prediction fails."""
    pass


class AgentException(ModelException):
    """Raised when agent-related operations fail."""
    pass


class ConsensusException(SentinelNetException):
    """Base exception for consensus-related errors."""
    pass


class ConsensusVotingError(ConsensusException):
    """Raised when consensus voting fails."""
    pass


class ReputationError(ConsensusException):
    """Raised when reputation management fails."""
    pass


class WeightUpdateError(ReputationError):
    """Raised when weight update fails."""
    pass


class ConfigException(SentinelNetException):
    """Raised when configuration is invalid."""
    pass


class DatabaseException(SentinelNetException):
    """Base exception for database-related errors."""
    pass


# Alias for compatibility
DatabaseError = DatabaseException
