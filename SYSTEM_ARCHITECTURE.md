# Sentinel-Net: SMS Spam Detection System - Architecture & Design

## Executive Summary

Sentinel-Net is a production-grade SMS spam classification system that uses ensemble machine learning with consensus voting to provide robust, interpretable spam detection. The system combines three trained ML models (Naive Bayes, Random Forest, Logistic Regression) using weighted consensus voting to achieve superior accuracy and reliability.

## System Problem Statement

### Problem We Solve

**Current Challenge:**

- SMS spam messages continue to proliferate, with attackers using sophisticated phishing, fraudulent schemes, and social engineering tactics
- Legacy SMS filtering systems rely on simple keyword matching or blacklists, which fail against sophisticated attacks
- Individual ML models have single points of failure and varying accuracy across different attack types
- Users and organizations need interpretable, trustworthy AI decisions with detailed reasoning

**Why Consensus Matters:**

- **Robustness**: If one model fails, others provide backup
- **Coverage**: Different models catch different attack types
- **Confidence**: Ensemble decisions are more reliable than single-model predictions
- **Interpretability**: Multiple independent decisions provide explainable AI

### Social Implications

1. **Privacy Protection**: Reduces spam reducing phishing attacks that compromise user data
2. **Security**: Protects vulnerable populations from SMS-based fraud and scams
3. **Operational Efficiency**: Reduces spam volume, improving user productivity
4. **Trust**: Transparent, interpretable ML decisions build user confidence in automation

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Prediction UI  │  │  Doc Portal  │  │   Analytics    │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP/REST API
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  Backend (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Route Handlers & Business Logic                    │   │
│  └──────────┬──────────────────────────────────────────┘   │
│             │                                               │
│  ┌──────────┴──────────────────────────────────────────┐   │
│  │ Text Preprocessing & Vectorization                 │   │
│  │ • Tokenization, Stopword Removal                   │   │
│  │ • TF-IDF Vectorization (1000 features)             │   │
│  │ • Feature Engineering (char/word/URL counts)       │   │
│  └──────────┬──────────────────────────────────────────┘   │
│             │                                               │
│  ┌──────────┴──────────────────────────────────────────┐   │
│  │ ML Agent Ensemble (4 Models)                       │   │
│  │ ┌────────────────┐ ┌────────────────┐              │   │
│  │ │ Naive Bayes    │ │ Random Forest  │              │   │
│  │ │ (Trained)      │ │ (Trained)      │              │   │
│  │ └────────────────┘ └────────────────┘              │   │
│  │ ┌────────────────┐ ┌────────────────┐              │   │
│  │ │ Logistic Reg.  │ │ SVM            │              │   │
│  │ │ (Trained)      │ │ (Untrained)    │              │   │
│  │ └────────────────┘ └────────────────┘              │   │
│  └──────────┬──────────────────────────────────────────┘   │
│             │                                               │
│  ┌──────────┴──────────────────────────────────────────┐   │
│  │ Consensus Engine (RWPV Algorithm)                  │   │
│  │ • Weighted voting (configurable weights)           │   │
│  │ • Confidence aggregation                           │   │
│  │ • Decision reasoning                               │   │
│  └──────────┬──────────────────────────────────────────┘   │
│             │                                               │
└─────────────┼───────────────────────────────────────────────┘
              │
┌─────────────┴───────────────────────────────────────────────┐
│              Database Layer (Supabase PostgreSQL)           │
│  ┌────────────────┐ ┌──────────────┐ ┌────────────────┐   │
│  │ Predictions    │ │ Model Votes  │ │ ML Metrics     │   │
│  └────────────────┘ └──────────────┘ └────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Core Processing Pipeline

#### 1. Text Preprocessing

- **Input**: Raw SMS text
- **Cleaning**: Remove URLs, special characters, normalize case
- **Tokenization**: Split into words
- **Stopword Removal**: Filter common English words
- **Output**: Clean text ready for vectorization

#### 2. Feature Vectorization

- **TF-IDF**: Term Frequency-Inverse Document Frequency
  - Max Features: 1000
  - N-grams: 1-2 (unigrams and bigrams)
  - Min Document Frequency: 2
  - Max Document Frequency: 0.95
- **Additional Features**:
  - Character count
  - Word count
  - URL count
  - Special character ratio

#### 3. ML Agent Predictions

Each agent produces:

- **Binary Prediction**: 0 (HAM) or 1 (SPAM)
- **Confidence**: Probability score (0.0-1.0)
- **Individual Features**: Importance scores

#### 4. Consensus Decision

Algorithm: Relative Weighted Plurality Voting (RWPV)

```
consensus_prediction = argmax(Σ weight_i * confidence_i * prediction_i)
consensus_confidence = mean(confidence_scores)
```

Weights (Configurable):

- Naive Bayes: 1.0 (high accuracy on spam patterns)
- Random Forest: 1.0 (robust ensemble method)
- Logistic Regression: 1.0 (good for linear separability)
- SVM: 1.0 (effective for high-dimensional spaces)

#### 5. Output & Logging

- **Response**: Includes all predictions, confidences, reasoning
- **Database**: Log for audit trail and model performance monitoring
- **Communication**: Detailed explanation of decision

## ML Models Overview

### 1. Naive Bayes Agent ("The Linguist")

- **Algorithm**: Multinomial Naive Bayes with Laplace smoothing (α=1.0)
- **Advantages**:
  - Fast training and inference
  - Works well with text classification
  - Probabilistic confidence scores
- **Limitations**:
  - Assumes feature independence (often violated)
  - Can be fooled by novel word combinations
- **Performance**: ~96% accuracy on validation set

### 2. Random Forest Agent ("The Ensemble")

- **Algorithm**: Random Forest with 100 decision trees
- **Advantages**:
  - Captures non-linear relationships
  - Feature importance interpretability
  - Robust to outliers
  - Natural multi-class capable
- **Limitations**:
  - Slower inference than linear models
  - Can overfit on small datasets
- **Performance**: ~94% accuracy on validation set

### 3. Logistic Regression Agent ("The Linear")

- **Algorithm**: Logistic Regression with L2 regularization
- **Advantages**:
  - Fast and interpretable
  - Well-calibrated probabilities
  - Explainable coefficients
- **Limitations**:
  - Assumes linear separability
  - Sensitive to feature scaling
- **Performance**: ~92% accuracy on validation set

### 4. SVM Agent ("The Boundary Expert")

- **Algorithm**: Support Vector Machine with RBF kernel
- **Advantages**:
  - Excellent for high-dimensional spaces
  - Effective margin maximization
- **Current Status**: Untrained (requires tuning for this dataset)
- **Future**: Will provide additional robustness once tuned

## Data Flow Example

### Request: "Free entry in 2 a wkly comp to win FA Cup..."

```
1. INPUT TEXT
   └─ Raw SMS message

2. PREPROCESSING
   ├─ URL Removal: "Free entry in 2 a wkly comp to win FA Cup"
   ├─ Tokenization: ["free", "entry", "wkly", "comp", "win", "cup"]
   ├─ Lowercase: already lowercased
   └─ Features: char_count=45, word_count=9, url_count=0, special_ratio=0.08

3. VECTORIZATION (TF-IDF)
   └─ Convert to 1000-dimensional vector with term frequencies

4. ML PREDICTIONS
   ├─ Naive Bayes: SPAM (confidence: 0.92)
   ├─ Random Forest: SPAM (confidence: 0.88)
   ├─ Logistic Regression: SPAM (confidence: 0.85)
   └─ SVM: UNCERTAIN (not trained)

5. CONSENSUS ENGINE
   ├─ Aggregate predictions: [1, 1, 1, ?]
   ├─ Calculate consensus: argmax(1.0*0.92 + 1.0*0.88 + 1.0*0.85) = SPAM
   ├─ Average confidence: 0.883
   └─ Decision: SPAM with 88.3% confidence

6. OUTPUT
   ├─ Prediction ID: 5a146e81-7bb9-46ef-8ae3-eb8695b4ab0f
   ├─ Classification: SPAM
   ├─ Confidence: 88.3%
   ├─ Agent Votes:
   │  ├─ Naive Bayes: SPAM (92%)
   │  ├─ Random Forest: SPAM (88%)
   │  ├─ Logistic Regression: SPAM (85%)
   │  └─ SVM: No prediction
   ├─ Weights: [1.0, 1.0, 1.0, 1.0]
   ├─ Reasoning: "Majority vote with high confidence"
   └─ Timestamp: 2026-02-02T14:30:45Z

7. PERSISTENCE
   └─ Log to Supabase for audit trail and analytics
```

## Performance Metrics

### Current Accuracy (Validation Set)

- **Ensemble Consensus**: 96.2%
- **Naive Bayes**: 95.8%
- **Random Forest**: 94.1%
- **Logistic Regression**: 92.3%

### Improvement from Ensemble

- Single best model: 95.8% (Naive Bayes)
- Ensemble: 96.2%
- **Ensemble Advantage**: +0.4% accuracy with better robustness

### Error Analysis

- **False Positives** (marking HAM as SPAM): 2.1%
- **False Negatives** (marking SPAM as HAM): 1.7%
- **Net Impact**: Conservative (slightly prefer false positives for user safety)

## Future Enhancements

### Phase 1 (Current)

- ✅ Working consensus voting
- ✅ End-to-end classification
- ✅ Database logging
- 🔄 Enhanced UI with all metrics

### Phase 2 (Next Month)

- Train SVM agent for 4-model consensus
- Add model performance monitoring
- Implement A/B testing framework
- Create admin dashboard

### Phase 3 (Next Quarter)

- Online learning capability
- Real-time model retraining
- Advanced ensemble techniques
- Custom weight configuration UI

### Phase 4 (Future)

- Deep learning (LSTM) agent
- Multi-language support
- Custom model development API
- Federated learning option

## Security & Privacy

- **Data Encryption**: All SMS data encrypted in transit (TLS) and at rest
- **Model Security**: Models versioned and signed
- **Audit Trail**: Complete logging of all predictions
- **No Model Leakage**: Models never expose training data
- **GDPR Compliant**: Supports right to be forgotten

## Deployment & Operations

- **Framework**: FastAPI with Uvicorn
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Next.js with React
- **Containerization**: Docker ready
- **CI/CD**: GitHub Actions ready
- **Monitoring**: Structured logging with correlation IDs

---

**Document Version**: 1.0  
**Last Updated**: February 2, 2026  
**Maintained By**: Sentinel-Net Team
