"""
Data Preprocessing Module for Sentinel-Net

Handles text preprocessing, TF-IDF vectorization, and feature engineering
for SMS spam classification.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Text preprocessing and feature engineering for SMS messages.
    
    Applies multiple preprocessing steps:
    1. Lowercase conversion
    2. URL removal
    3. Special character removal
    4. Extra whitespace normalization
    5. TF-IDF vectorization
    6. Feature engineering (char count, word count, URL count, special char ratio)
    
    Attributes:
        vocab_size (int): Vocabulary size for TF-IDF (default: 1000)
        vectorizer (TfidfVectorizer): Fitted TF-IDF vectorizer
        feature_names (List[str]): Feature names from vectorizer
    """
    
    def __init__(self, vocab_size: int = 1000):
        """
        Initialize the preprocessor.
        
        Args:
            vocab_size (int): Maximum number of features for TF-IDF.
                            Default: 1000
        """
        self.vocab_size = vocab_size
        self.vectorizer = TfidfVectorizer(
            max_features=vocab_size,
            ngram_range=(1, 2),  # Unigrams + bigrams
            min_df=2,            # Ignore terms appearing in < 2 documents
            max_df=0.95,         # Ignore terms appearing in > 95% of documents
            lowercase=True,
            stop_words='english'
        )
        self.feature_names = None
        logger.info(f"DataPreprocessor initialized with vocab_size={vocab_size}")
    
    def preprocess(self, text: str) -> Dict[str, any]:
        """
        Clean and preprocess a single SMS message.
        
        Steps:
        1. Convert to lowercase
        2. Remove URLs
        3. Remove special characters (keep alphanumeric + spaces)
        4. Remove extra whitespace
        5. Extract engineered features
        
        Args:
            text (str): Raw SMS message text
            
        Returns:
            Dict containing:
                - 'text_raw': Original text
                - 'text_clean': Cleaned text
                - 'char_count': Number of characters
                - 'word_count': Number of words
                - 'url_count': Number of URLs
                - 'special_char_ratio': Ratio of special characters
        
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> result = preprocessor.preprocess("FREE MONEY!!! Click now")
            >>> print(result['text_clean'])
            'free money click now'
        """
        # Step 1: Lowercase
        text_clean = text.lower()
        
        # Step 2: Count URLs before removal
        url_count = len(re.findall(r'http\S+|www\S+', text_clean))
        text_clean = re.sub(r'http\S+|www\S+', '', text_clean)
        
        # Step 3: Remove special characters (keep alphanumeric + spaces)
        text_clean = re.sub(r'[^a-z0-9\s]', '', text_clean)
        
        # Step 4: Remove extra whitespace
        text_clean = ' '.join(text_clean.split())
        
        # Step 5: Extract features
        char_count = len(text_clean)
        word_count = len(text_clean.split())
        
        # Calculate special character ratio from original text
        original_special = len(re.findall(r'[^a-zA-Z0-9\s]', text))
        special_char_ratio = original_special / max(len(text), 1)
        
        return {
            'text_raw': text,
            'text_clean': text_clean,
            'char_count': char_count,
            'word_count': word_count,
            'url_count': url_count,
            'special_char_ratio': special_char_ratio
        }
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit TF-IDF vectorizer and transform texts.
        
        Args:
            texts (List[str]): List of cleaned text strings
            
        Returns:
            np.ndarray: TF-IDF matrix of shape (n_samples, vocab_size)
                       Dense array for easier processing
            
        Example:
            >>> texts = ["hello world", "goodbye world"]
            >>> vectors = preprocessor.fit_transform(texts)
            >>> print(vectors.shape)  # (2, vocab_size)
        """
        logger.info(f"Fitting TF-IDF vectorizer on {len(texts)} documents")
        vectors = self.vectorizer.fit_transform(texts).toarray()
        self.feature_names = self.vectorizer.get_feature_names_out()
        logger.info(f"TF-IDF vocabulary size: {len(self.feature_names)}")
        return vectors
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts using fitted vectorizer.
        
        Args:
            texts (List[str]): List of cleaned text strings
            
        Returns:
            np.ndarray: TF-IDF matrix of shape (n_samples, vocab_size)
            
        Raises:
            ValueError: If vectorizer is not fitted yet
        """
        if self.vectorizer is None or self.feature_names is None:
            raise ValueError("Vectorizer not fitted. Call fit_transform first.")
        
        return self.vectorizer.transform(texts).toarray()
    
    def create_feature_vector(
        self,
        tfidf_vector: np.ndarray,
        char_count: int,
        word_count: int,
        url_count: int,
        special_char_ratio: float
    ) -> np.ndarray:
        """
        Combine TF-IDF vector with engineered features.
        
        Creates a feature vector combining:
        - TF-IDF (1000 dimensions)
        - Char count (normalized)
        - Word count (normalized)
        - URL count
        - Special char ratio
        
        Args:
            tfidf_vector (np.ndarray): TF-IDF vector
            char_count (int): Character count
            word_count (int): Word count
            url_count (int): URL count
            special_char_ratio (float): Special character ratio
            
        Returns:
            np.ndarray: Combined feature vector (1004 dimensions)
        """
        # Normalize counts (assuming max reasonable values)
        normalized_char = char_count / 200  # Typical SMS: 160 chars
        normalized_word = word_count / 50   # Typical SMS: ~30 words
        
        engineered = np.array([
            normalized_char,
            normalized_word,
            url_count,
            special_char_ratio
        ])
        
        # Combine TF-IDF (1000) + engineered (4) = 1004 dimensions
        combined = np.concatenate([tfidf_vector, engineered])
        return combined
    
    def get_top_features(
        self,
        n: int = 20,
        class_weight: Optional[np.ndarray] = None
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top TF-IDF features overall or per class.
        
        Args:
            n (int): Number of top features to return
            class_weight (Optional[np.ndarray]): Weights for classes
                                               (for weighted feature importance)
            
        Returns:
            Dict mapping feature names to importance scores
            
        Example:
            >>> top_features = preprocessor.get_top_features(n=20)
        """
        if self.feature_names is None:
            raise ValueError("Vectorizer not fitted yet")
        
        feature_scores = {}
        for idx, name in enumerate(self.feature_names):
            feature_scores[name] = self.vectorizer.idf_[idx]
        
        # Sort by IDF score
        sorted_features = sorted(
            feature_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'top_features': sorted_features[:n],
            'low_features': sorted_features[-n:]
        }


def preprocess_batch(
    texts: List[str],
    preprocessor: Optional[DataPreprocessor] = None
) -> Tuple[List[str], List[Dict]]:
    """
    Preprocess a batch of SMS messages.
    
    Args:
        texts (List[str]): List of raw SMS messages
        preprocessor (Optional[DataPreprocessor]): Preprocessor instance
                                                  (creates new if None)
    
    Returns:
        Tuple of:
        - List of cleaned texts
        - List of feature dictionaries
    """
    if preprocessor is None:
        preprocessor = DataPreprocessor()
    
    cleaned_texts = []
    features_list = []
    
    for text in texts:
        features = preprocessor.preprocess(text)
        cleaned_texts.append(features['text_clean'])
        features_list.append(features)
    
    return cleaned_texts, features_list
