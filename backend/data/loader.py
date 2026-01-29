"""
Data Loader Module for Sentinel-Net

Handles downloading, loading, preprocessing, and caching of SMS dataset.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from .preprocessor import DataPreprocessor

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Load and preprocess SMS Spam Collection dataset.
    
    Features:
    - Automatic download from UCI if not present
    - Caching with pickle for fast reloading
    - Train/validation/test split (80/10/10)
    - Complete preprocessing pipeline
    
    Attributes:
        cache_dir (str): Directory for cached data
        raw_dir (str): Directory for raw data
        processed_dir (str): Directory for processed data
        preprocessor (DataPreprocessor): Text preprocessor instance
    """
    
    # UCI ML Repository URL for SMS Spam Collection
    DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
    
    def __init__(
        self,
        cache_dir: str = "data/cache",
        raw_dir: str = "data/raw",
        processed_dir: str = "data/processed",
        vocab_size: int = 1000,
        random_seed: int = 42
    ):
        """
        Initialize DataLoader.
        
        Args:
            cache_dir (str): Directory for cached preprocessed data
            raw_dir (str): Directory for raw dataset
            processed_dir (str): Directory for processed numpy arrays
            vocab_size (int): Vocabulary size for TF-IDF
            random_seed (int): Random seed for reproducibility
        """
        self.cache_dir = Path(cache_dir)
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.vocab_size = vocab_size
        self.random_seed = random_seed
        self.preprocessor = DataPreprocessor(vocab_size=vocab_size)
        
        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DataLoader initialized with seed={random_seed}")
    
    def _download_dataset(self) -> str:
        """
        Download SMS Spam Collection from UCI ML Repository.
        
        Returns:
            str: Path to downloaded CSV file
            
        Note:
            The dataset should be manually downloaded and placed in data/raw/
            as the UCI website requires special handling.
        """
        csv_path = self.raw_dir / "spam.csv"
        
        if csv_path.exists():
            logger.info(f"Dataset already exists at {csv_path}")
            return str(csv_path)
        
        logger.warning(
            "Dataset not found. Please manually download from:\n"
            "https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection\n"
            "Extract and place 'smsspamcollection' file in data/raw/\n"
            "Then rename to 'spam.csv'"
        )
        
        return None
    
    def load_and_cache(self) -> Dict[str, np.ndarray]:
        """
        Load, preprocess, and cache dataset.
        
        Uses cache if available, otherwise:
        1. Downloads/loads raw CSV
        2. Preprocesses all texts
        3. Fits TF-IDF vectorizer
        4. Splits into train/val/test (80/10/10)
        5. Saves cache for future use
        
        Returns:
            Dict containing:
            - 'X_train': Training features
            - 'y_train': Training labels
            - 'X_val': Validation features
            - 'y_val': Validation labels
            - 'X_test': Test features
            - 'y_test': Test labels
            - 'feature_names': Feature names from TF-IDF
            - 'label_encoder': Fitted label encoder
            
        Raises:
            FileNotFoundError: If dataset file not found
        """
        cache_path = self.cache_dir / "processed_data.pkl"
        
        # Return cached data if available
        if cache_path.exists():
            logger.info(f"Loading cached data from {cache_path}")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        
        logger.info("No cache found. Processing dataset...")
        
        # Load raw CSV
        csv_path = self.raw_dir / "spam.csv"
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {csv_path}. "
                "Please download SMS Spam Collection from UCI ML Repository:\n"
                "https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection"
            )
        
        logger.info(f"Loading dataset from {csv_path}")
        df = pd.read_csv(csv_path, encoding='latin-1')
        
        # Handle different column names (dataset has varied formats)
        if len(df.columns) >= 2:
            label_col = df.columns[0]
            text_col = df.columns[1]
        else:
            raise ValueError("Dataset must have at least 2 columns")
        
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Unique labels: {df[label_col].unique()}")
        
        # Preprocess texts
        logger.info("Preprocessing texts...")
        texts_raw = df[text_col].values.astype(str)
        cleaned_texts = []
        
        for i, text in enumerate(texts_raw):
            if i % 1000 == 0:
                logger.info(f"Processed {i}/{len(texts_raw)} messages")
            result = self.preprocessor.preprocess(text)
            cleaned_texts.append(result['text_clean'])
        
        # Fit TF-IDF
        logger.info("Fitting TF-IDF vectorizer...")
        X = self.preprocessor.fit_transform(cleaned_texts)
        logger.info(f"TF-IDF shape: {X.shape}")
        
        # Encode labels
        le = LabelEncoder()
        y = le.fit_transform(df[label_col].values)
        logger.info(f"Classes: {le.classes_} -> {np.unique(y)}")
        
        # Split data (80% train, 10% val, 10% test)
        logger.info("Splitting dataset (80/10/10)...")
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=0.2,
            random_state=self.random_seed,
            stratify=y
        )
        
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=0.5,
            random_state=self.random_seed,
            stratify=y_temp
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Val set: {X_val.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Create data dict
        data = {
            'X_train': X_train,
            'y_train': y_train,
            'X_val': X_val,
            'y_val': y_val,
            'X_test': X_test,
            'y_test': y_test,
            'feature_names': self.preprocessor.feature_names,
            'label_encoder': le,
            'vocab_size': self.vocab_size,
            'classes': le.classes_
        }
        
        # Save cache
        logger.info(f"Saving cache to {cache_path}")
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info("Dataset loaded and cached successfully!")
        return data
    
    def get_dataset_statistics(self) -> Dict:
        """
        Load dataset and generate statistics.
        
        Returns:
            Dict containing dataset statistics
        """
        logger.info("Generating dataset statistics...")
        
        data = self.load_and_cache()
        le = data['label_encoder']
        
        # Count per class
        train_counts = pd.Series(data['y_train']).value_counts()
        val_counts = pd.Series(data['y_val']).value_counts()
        test_counts = pd.Series(data['y_test']).value_counts()
        
        stats = {
            'total_samples': len(data['y_train']) + len(data['y_val']) + len(data['y_test']),
            'train_samples': len(data['y_train']),
            'val_samples': len(data['y_val']),
            'test_samples': len(data['y_test']),
            'features': data['X_train'].shape[1],
            'classes': list(le.classes_),
            'train_distribution': {
                str(le.classes_[i]): int(train_counts.get(i, 0))
                for i in range(len(le.classes_))
            },
            'val_distribution': {
                str(le.classes_[i]): int(val_counts.get(i, 0))
                for i in range(len(le.classes_))
            },
            'test_distribution': {
                str(le.classes_[i]): int(test_counts.get(i, 0))
                for i in range(len(le.classes_))
            },
            'vocabulary_size': data['vocab_size'],
            'random_seed': self.random_seed
        }
        
        return stats
    
    def print_statistics(self) -> None:
        """Print formatted dataset statistics."""
        stats = self.get_dataset_statistics()
        
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        print(f"\nTotal samples: {stats['total_samples']}")
        print(f"Train: {stats['train_samples']} samples")
        print(f"Val:   {stats['val_samples']} samples")
        print(f"Test:  {stats['test_samples']} samples")
        print(f"\nFeatures: {stats['features']}")
        print(f"Classes: {stats['classes']}")
        print(f"Vocabulary Size: {stats['vocabulary_size']}")
        
        print(f"\nTrain distribution:")
        for cls, count in stats['train_distribution'].items():
            pct = (count / stats['train_samples']) * 100
            print(f"  {cls}: {count} ({pct:.1f}%)")
        
        print(f"\nVal distribution:")
        for cls, count in stats['val_distribution'].items():
            pct = (count / stats['val_samples']) * 100
            print(f"  {cls}: {count} ({pct:.1f}%)")
        
        print(f"\nTest distribution:")
        for cls, count in stats['test_distribution'].items():
            pct = (count / stats['test_samples']) * 100
            print(f"  {cls}: {count} ({pct:.1f}%)")
        
        print("\n" + "="*60 + "\n")
