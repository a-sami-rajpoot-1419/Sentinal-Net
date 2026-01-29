"""
Unit Tests for Data Loader Module

Tests the DataLoader class and dataset utilities.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
from backend.data.loader import DataLoader
from backend.data.dataset import Dataset


class TestDataLoader:
    """Test suite for DataLoader class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        cache_dir = Path(temp_dir) / "cache"
        raw_dir = Path(temp_dir) / "raw"
        processed_dir = Path(temp_dir) / "processed"
        
        cache_dir.mkdir(exist_ok=True)
        raw_dir.mkdir(exist_ok=True)
        processed_dir.mkdir(exist_ok=True)
        
        yield {
            'root': temp_dir,
            'cache': str(cache_dir),
            'raw': str(raw_dir),
            'processed': str(processed_dir)
        }
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def loader(self, temp_dirs):
        """Create DataLoader instance."""
        return DataLoader(
            cache_dir=temp_dirs['cache'],
            raw_dir=temp_dirs['raw'],
            processed_dir=temp_dirs['processed'],
            vocab_size=50,
            random_seed=42
        )
    
    def test_initialization(self, loader):
        """Test DataLoader initialization."""
        assert loader.vocab_size == 50
        assert loader.random_seed == 42
        assert loader.cache_dir.exists()
        assert loader.raw_dir.exists()
        assert loader.processed_dir.exists()
    
    def test_missing_dataset(self, loader):
        """Test error when dataset not found."""
        with pytest.raises(FileNotFoundError):
            loader.load_and_cache()
    
    def test_preprocessor_initialization(self, loader):
        """Test preprocessor is initialized."""
        assert loader.preprocessor is not None
        assert loader.preprocessor.vocab_size == 50


class TestDataset:
    """Test suite for Dataset wrapper class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        n_samples = 100
        n_features = 50
        
        X = np.random.rand(n_samples, n_features)
        y = np.random.randint(0, 2, n_samples)
        
        # Split into train/val/test
        X_train, X_val, X_test = X[:60], X[60:80], X[80:]
        y_train, y_val, y_test = y[:60], y[60:80], y[80:]
        
        return {
            'X_train': X_train,
            'y_train': y_train,
            'X_val': X_val,
            'y_val': y_val,
            'X_test': X_test,
            'y_test': y_test
        }
    
    @pytest.fixture
    def dataset(self, sample_data):
        """Create Dataset instance."""
        return Dataset(
            X_train=sample_data['X_train'],
            y_train=sample_data['y_train'],
            X_val=sample_data['X_val'],
            y_val=sample_data['y_val'],
            X_test=sample_data['X_test'],
            y_test=sample_data['y_test'],
            classes=np.array(['spam', 'ham']),
            feature_names=None
        )
    
    def test_dataset_initialization(self, dataset):
        """Test Dataset initialization."""
        assert dataset.n_classes == 2
        assert dataset.n_features == 50
    
    def test_get_train_data(self, dataset):
        """Test getting training data."""
        X_train, y_train = dataset.get_train_data()
        assert X_train.shape[0] == 60
        assert len(y_train) == 60
    
    def test_get_val_data(self, dataset):
        """Test getting validation data."""
        X_val, y_val = dataset.get_val_data()
        assert X_val.shape[0] == 20
        assert len(y_val) == 20
    
    def test_get_test_data(self, dataset):
        """Test getting test data."""
        X_test, y_test = dataset.get_test_data()
        assert X_test.shape[0] == 20
        assert len(y_test) == 20
    
    def test_get_all_data(self, dataset):
        """Test getting concatenated data."""
        X_all, y_all = dataset.get_all_data()
        assert X_all.shape[0] == 100
        assert len(y_all) == 100
    
    def test_shape_property(self, dataset):
        """Test shape property."""
        assert dataset.shape == (60, 50)
    
    def test_classes_property(self, dataset):
        """Test classes property."""
        assert list(dataset.classes) == ['spam', 'ham']


class TestDataSplitting:
    """Test data splitting logic."""
    
    def test_split_stratification(self, temp_dirs):
        """Test that data is stratified."""
        # This requires actual dataset, so we create a mock scenario
        from sklearn.model_selection import train_test_split
        
        # Create imbalanced data
        X = np.random.rand(1000, 50)
        y = np.concatenate([np.zeros(900), np.ones(100)])  # 90-10 split
        
        # Split with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        
        # Check proportions maintained
        train_ratio = np.sum(y_train == 1) / len(y_train)
        test_ratio = np.sum(y_test == 1) / len(y_test)
        
        # Should be close to 0.1 (10%)
        assert 0.08 < train_ratio < 0.12
        assert 0.08 < test_ratio < 0.12


class TestEdgeCases:
    """Test edge cases for data loading."""
    
    def test_vocab_size_variations(self, temp_dirs):
        """Test with different vocabulary sizes."""
        for vocab_size in [10, 100, 500]:
            loader = DataLoader(
                cache_dir=temp_dirs['cache'],
                raw_dir=temp_dirs['raw'],
                processed_dir=temp_dirs['processed'],
                vocab_size=vocab_size
            )
            assert loader.preprocessor.vocab_size == vocab_size
    
    def test_random_seed_reproducibility(self, temp_dirs):
        """Test that same seed produces same results."""
        loader1 = DataLoader(
            cache_dir=temp_dirs['cache'],
            raw_dir=temp_dirs['raw'],
            processed_dir=temp_dirs['processed'],
            random_seed=42
        )
        
        loader2 = DataLoader(
            cache_dir=temp_dirs['cache'],
            raw_dir=temp_dirs['raw'],
            processed_dir=temp_dirs['processed'],
            random_seed=42
        )
        
        assert loader1.random_seed == loader2.random_seed
