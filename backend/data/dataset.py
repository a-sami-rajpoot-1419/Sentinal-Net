"""
Dataset Wrapper Module for Sentinel-Net

Provides Dataset class for easy access to split data.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import numpy as np
from typing import Optional, Tuple


class Dataset:
    """
    Wrapper for loaded dataset with convenient access methods.
    
    Attributes:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        X_test, y_test: Test data
        classes: Class names
        feature_names: Feature names from vectorizer
    """
    
    def __init__(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        classes: np.ndarray,
        feature_names: Optional[np.ndarray] = None
    ):
        """Initialize dataset."""
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.X_test = X_test
        self.y_test = y_test
        self.classes = classes
        self.feature_names = feature_names
    
    def get_train_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return training data."""
        return self.X_train, self.y_train
    
    def get_val_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return validation data."""
        return self.X_val, self.y_val
    
    def get_test_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return test data."""
        return self.X_test, self.y_test
    
    def get_all_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return concatenated train+val+test."""
        X = np.concatenate([self.X_train, self.X_val, self.X_test])
        y = np.concatenate([self.y_train, self.y_val, self.y_test])
        return X, y
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Shape of feature matrix."""
        return self.X_train.shape
    
    @property
    def n_classes(self) -> int:
        """Number of classes."""
        return len(self.classes)
    
    @property
    def n_features(self) -> int:
        """Number of features."""
        return self.X_train.shape[1]
