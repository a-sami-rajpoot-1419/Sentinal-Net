"""
Unit Tests for Data Preprocessing Module

Tests the DataPreprocessor class and preprocessing functions.

Author: Sentinel-Net Team
Date: 2026-01-29
"""

import pytest
import numpy as np
from backend.data.preprocessor import DataPreprocessor, preprocess_batch


class TestDataPreprocessor:
    """Test suite for DataPreprocessor class."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance."""
        return DataPreprocessor(vocab_size=100)
    
    @pytest.fixture
    def sample_texts(self):
        """Sample SMS messages for testing."""
        return [
            "FREE MONEY!!! Click now!!!",
            "Hi John, your appointment is confirmed",
            "Prize winner! You won $1,000,000",
            "Hi, just checking in with you"
        ]
    
    def test_initialization(self, preprocessor):
        """Test preprocessor initializes correctly."""
        assert preprocessor.vocab_size == 100
        assert preprocessor.vectorizer is not None
    
    def test_lowercase_conversion(self, preprocessor):
        """Test text is converted to lowercase."""
        result = preprocessor.preprocess("HELLO WORLD")
        assert result['text_clean'] == result['text_clean'].lower()
        assert "HELLO" not in result['text_clean']
    
    def test_url_removal(self, preprocessor):
        """Test URLs are removed."""
        text = "Check this out https://example.com now"
        result = preprocessor.preprocess(text)
        assert "https" not in result['text_clean']
        assert "example" not in result['text_clean']
        assert result['url_count'] == 1
    
    def test_special_char_removal(self, preprocessor):
        """Test special characters are removed."""
        text = "Hello!!!@@@###World$$$"
        result = preprocessor.preprocess(text)
        assert all(c.isalnum() or c.isspace() for c in result['text_clean'])
        assert "!" not in result['text_clean']
        assert "@" not in result['text_clean']
    
    def test_whitespace_normalization(self, preprocessor):
        """Test extra whitespace is normalized."""
        text = "Hello    world    test"
        result = preprocessor.preprocess(text)
        assert "    " not in result['text_clean']
        assert result['text_clean'] == "hello world test"
    
    def test_feature_extraction(self, preprocessor):
        """Test feature extraction."""
        text = "Hello world"
        result = preprocessor.preprocess(text)
        
        assert result['char_count'] >= 0
        assert result['word_count'] >= 0
        assert result['url_count'] >= 0
        assert 0 <= result['special_char_ratio'] <= 1
    
    def test_char_count(self, preprocessor):
        """Test character count calculation."""
        text = "hello"
        result = preprocessor.preprocess(text)
        assert result['char_count'] == 5
    
    def test_word_count(self, preprocessor):
        """Test word count calculation."""
        text = "hello world test"
        result = preprocessor.preprocess(text)
        assert result['word_count'] == 3
    
    def test_url_count(self, preprocessor):
        """Test URL count."""
        text = "Check www.example.com and https://test.com"
        result = preprocessor.preprocess(text)
        assert result['url_count'] == 2
    
    def test_special_char_ratio(self, preprocessor):
        """Test special character ratio calculation."""
        text = "Hello!!!"
        result = preprocessor.preprocess(text)
        assert result['special_char_ratio'] > 0
        assert result['special_char_ratio'] < 1
    
    def test_fit_transform(self, preprocessor, sample_texts):
        """Test TF-IDF fit and transform."""
        vectors = preprocessor.fit_transform(sample_texts)
        
        assert vectors.shape == (len(sample_texts), 100)
        assert vectors.dtype == np.float64
        assert np.all(vectors >= 0)  # TF-IDF values are non-negative
    
    def test_transform_after_fit(self, preprocessor, sample_texts):
        """Test transform after fitting."""
        preprocessor.fit_transform(sample_texts)
        
        new_texts = ["hello world", "test message"]
        vectors = preprocessor.transform(new_texts)
        
        assert vectors.shape == (2, 100)
    
    def test_transform_without_fit(self, preprocessor):
        """Test transform raises error without fit."""
        with pytest.raises(ValueError):
            preprocessor.transform(["hello"])
    
    def test_feature_names(self, preprocessor, sample_texts):
        """Test feature names are extracted."""
        preprocessor.fit_transform(sample_texts)
        
        assert preprocessor.feature_names is not None
        assert len(preprocessor.feature_names) > 0
    
    def test_combined_feature_vector(self, preprocessor):
        """Test combined feature vector creation."""
        tfidf = np.random.rand(100)
        combined = preprocessor.create_feature_vector(
            tfidf_vector=tfidf,
            char_count=50,
            word_count=10,
            url_count=2,
            special_char_ratio=0.1
        )
        
        # TF-IDF (100) + engineered (4) = 104
        assert combined.shape == (104,)
    
    def test_get_top_features(self, preprocessor, sample_texts):
        """Test top features extraction."""
        preprocessor.fit_transform(sample_texts)
        
        top = preprocessor.get_top_features(n=5)
        
        assert 'top_features' in top
        assert 'low_features' in top
        assert len(top['top_features']) <= 5
        assert len(top['low_features']) <= 5


class TestPreprocessBatch:
    """Test batch preprocessing function."""
    
    def test_batch_preprocessing(self):
        """Test batch preprocessing."""
        texts = ["Hello world", "TEST message"]
        cleaned, features = preprocess_batch(texts)
        
        assert len(cleaned) == 2
        assert len(features) == 2
        assert all(isinstance(f, dict) for f in features)
    
    def test_batch_with_preprocessor(self):
        """Test batch preprocessing with provided preprocessor."""
        preprocessor = DataPreprocessor()
        texts = ["Hello world", "TEST message"]
        cleaned, features = preprocess_batch(texts, preprocessor)
        
        assert len(cleaned) == 2
        assert len(features) == 2


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance."""
        return DataPreprocessor()
    
    def test_empty_string(self, preprocessor):
        """Test handling empty string."""
        result = preprocessor.preprocess("")
        assert result['text_clean'] == ""
        assert result['word_count'] == 0
    
    def test_only_special_chars(self, preprocessor):
        """Test text with only special characters."""
        result = preprocessor.preprocess("!!!@@@###$$$")
        assert result['text_clean'] == ""
        assert result['special_char_ratio'] == 1.0
    
    def test_very_long_text(self, preprocessor):
        """Test very long text."""
        text = "hello " * 1000
        result = preprocessor.preprocess(text)
        assert result['word_count'] == 1000
    
    def test_unicode_text(self, preprocessor):
        """Test unicode characters."""
        text = "Hello 世界 مرحبا"
        result = preprocessor.preprocess(text)
        # Unicode should be removed as non-alphanumeric
        assert "世界" not in result['text_clean']
    
    def test_numbers_preserved(self, preprocessor):
        """Test numbers are preserved."""
        text = "You won 1000000 dollars"
        result = preprocessor.preprocess(text)
        assert "1000000" in result['text_clean']
