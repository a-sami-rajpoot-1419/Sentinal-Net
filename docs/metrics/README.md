# 📊 **Metrics & Key Performance Indicators**

Comprehensive guide to understanding Sentinel-Net's performance metrics.

---

## 🎯 **Core Metrics**

### 1. **Accuracy** (Most Important)

**Definition:** Percentage of predictions that are correct

$$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Predictions}} \times 100\%$$

**Example:**
```
Total predictions: 1000
Correct: 940
Incorrect: 60
Accuracy = 940/1000 = 94.0%
```

**Targets:**
- Individual models: 75-85%
- Sentinel-Net consensus: 92-97%
- Improvement: +15-20%

**Why it matters:** Directly impacts business outcomes

---

### 2. **Precision** (Avoid False Positives)

**Definition:** Of all messages classified as SPAM, what % were actually spam?

$$\text{Precision} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$$

**Example:**
```
System says 100 are SPAM
Actually spam: 94
Actually legitimate: 6

Precision = 94/100 = 94%
(6 innocent messages blocked - the cost of blocking spam)
```

**Targets:**
- High precision (>90%) = few innocent blocked
- Trade-off: May miss some actual spam

**When it matters:** Consumer email (users angry if blocked)

---

### 3. **Recall** (Catch All Spam)

**Definition:** Of all actual spam, what % did we catch?

$$\text{Recall} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$$

**Example:**
```
Total spam messages: 150
We caught: 138
We missed: 12

Recall = 138/150 = 92%
(12 spam messages got through)
```

**Targets:**
- High recall (>90%) = catch most spam
- Trade-off: May incorrectly block some legitimate

**When it matters:** Security/fraud (missing bad messages is costly)

---

### 4. **F1-Score** (Balanced Metric)

**Definition:** Harmonic mean of precision and recall

$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

**Example:**
```
Precision: 94%
Recall: 92%
F1 = 2 × (0.94 × 0.92) / (0.94 + 0.92) = 0.93 (93%)
```

**When to use:** When you care about both false positives AND false negatives

---

### 5. **Confidence Score** (System Certainty)

**Definition:** How confident is the system in its prediction (0-100%)?

**Example:**
```
Message: "Free prize!"
System prediction: SPAM
Confidence: 91.5%

Interpretation: The 4 models strongly agreed, high confidence
```

**Range:**
- **90-100%:** Very high confidence (all models agree)
- **70-90%:** High confidence (most models agree)
- **50-70%:** Moderate confidence (mixed opinions)
- **40-50%:** Low confidence (strong disagreement)

**Why it matters:** Low confidence = be skeptical of decision

---

## 📈 **Comparative Metrics**

### Improvement Ratio

**Definition:** How much better is consensus vs individual models?

$$\text{Improvement Ratio} = \frac{\text{Consensus Accuracy}}{\text{Average Individual Accuracy}}$$

**Example:**
```
Individual accuracies:
- Naive Bayes: 82%
- SVM: 78%
- Random Forest: 84%
- Logistic Regression: 76%
Average: 80%

Consensus accuracy: 94%

Improvement Ratio = 94 / 80 = 1.175x
(17.5% better than individual models)
```

**Target:** > 1.10x (at least 10% improvement)

---

### Head-to-Head Comparison

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Naive Bayes | 82% | 80% | 84% | 0.82 |
| SVM | 78% | 75% | 81% | 0.78 |
| Random Forest | 84% | 83% | 85% | 0.84 |
| Logistic Regression | 76% | 72% | 80% | 0.76 |
| **Sentinel-Net** | **94%** | **93%** | **95%** | **0.94** |

**Key insight:** Consensus beats every individual model

---

## 🎭 **Per-Model Metrics**

### Agent Performance Tracking

**What:** Track individual accuracy of each agent over time

```json
{
  "agent_nb": {
    "total_votes": 1000,
    "correct_votes": 820,
    "accuracy": 0.82,
    "current_weight": 0.95,
    "trend": "declining"
  },
  "agent_svm": {
    "total_votes": 1000,
    "correct_votes": 780,
    "accuracy": 0.78,
    "current_weight": 0.82,
    "trend": "stable"
  },
  "agent_rf": {
    "total_votes": 1000,
    "correct_votes": 840,
    "accuracy": 0.84,
    "current_weight": 1.12,
    "trend": "improving"
  },
  "agent_lr": {
    "total_votes": 1000,
    "correct_votes": 760,
    "accuracy": 0.76,
    "current_weight": 0.71,
    "trend": "declining"
  }
}
```

**Key insights:**
- Random Forest (RF) is best: 84% accuracy, weight 1.12
- Logistic Regression (LR) is worst: 76% accuracy, weight 0.71
- Weights automatically adjust based on performance

---

## ⚖️ **RWPV Reputation Metrics**

### Weight Evolution

**Definition:** How agent "trust scores" change over time

**Starting point:** All agents start with weight = 1.0

**Update rules:**
- Correct vote + correct consensus: weight × 1.05 (+5%)
- Wrong vote + correct consensus: weight × 0.90 (-10%)
- Correct vote + wrong consensus: weight × 1.15 (+15%)
- Wrong vote + wrong consensus: weight × 0.85 (-15%)

**Weight bounds:** Clamped to [0.1, 5.0]

**Example trajectory:**
```
Round 1:  Weight = 1.00 (start)
Round 2:  Weight = 1.00 × 1.05 = 1.05 (correct vote)
Round 3:  Weight = 1.05 × 0.90 = 0.945 (wrong vote)
Round 4:  Weight = 0.945 × 1.05 = 0.992 (correct vote)
Round 5:  Weight = 0.992 × 1.05 = 1.042 (correct vote)
...
Round 100: Weight = 1.12 (high performer)
```

---

### Byzantine Agent Detection

**What:** How well the system identifies and downweights bad agents

**Test setup:**
1. Inject faulty agent (gives wrong predictions)
2. Watch weight decline over time
3. Track how much influence it loses

**Example results:**
```
Faulty Agent (Byzantine):
- Rounds 1-50: Weight 1.0 → 0.62 (dropped 38%)
- Rounds 50-100: Weight 0.62 → 0.15 (limited influence)
- Rounds 100+: Weight capped at 0.1 (minimal impact)

Result: ✅ System successfully downweighted bad agent
```

**Goal:** Bad agents should have minimal influence after 100 rounds

---

## 📊 **Confusion Matrix**

**Visual breakdown of all prediction types:**

```
                 Predicted SPAM    Predicted HAM
Actual SPAM      TP: 945 (95%)    FN: 55 (5%)
Actual HAM       FP: 47 (5%)      TN: 953 (95%)
```

**Reading the matrix:**
- **TP (Top-left):** Spam correctly identified as spam ✓
- **FN (Top-right):** Spam missed (bad - false negative)
- **FP (Bottom-left):** Legitimate wrongly marked as spam (bad - false positive)
- **TN (Bottom-right):** Legitimate correctly identified as legitimate ✓

**Calculation:**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
         = (945 + 953) / (945 + 953 + 47 + 55)
         = 1898 / 2000
         = 94.9%
```

---

## 📉 **Confidence Calibration**

**Definition:** Is the system's confidence aligned with actual accuracy?

**Perfect calibration:** When system says 90% confident, it's correct 90% of the time

**Example - Well Calibrated:**
```
Confidence 90-100% → Actual accuracy 92%  ✓ (close to 95%)
Confidence 80-90%  → Actual accuracy 83%  ✓ (close to 85%)
Confidence 70-80%  → Actual accuracy 71%  ✓ (close to 75%)
```

**Overconfident (Bad):**
```
System says 90% confident → Actually only 78% correct ✗
```

**Underconfident (Wasteful):**
```
System says 70% confident → Actually 92% correct ✗
```

**Measurement:**
```
Calibration Error = Average(|confidence - actual_accuracy|)
Target: < 5%
```

---

## 🔍 **Error Analysis**

### Error Distribution

**Where do mistakes happen?**

```
Messages with "urgency" words (now, today, urgent):
- Spam detection rate: 96%
- False positive rate: 2%

Messages with multiple URLs:
- Spam detection rate: 98%
- False positive rate: 1%

Messages with unusual capitalization:
- Spam detection rate: 94%
- False positive rate: 3%
```

**Action:** Focus improvement on high error patterns

---

### Common Mistakes

**Type 1: False Positives (Legitimate marked as Spam)**
```
"Congratulations! Your order is here"
→ System says: SPAM (incorrect)
→ Reason: "Congratulations" + urgency triggers
→ Fix: Need more context awareness
```

**Type 2: False Negatives (Spam missed)**
```
"Hi, check out this great deal on flights"
→ System says: LEGITIMATE (incorrect)
→ Reason: Natural language tricks the system
→ Fix: Add more sophisticated features
```

---

## 📈 **Time-Series Metrics**

### Accuracy Over Time

Track accuracy as system processes more messages:

```
Round 1-100:      Accuracy = 91% (initial poor calibration)
Round 100-200:    Accuracy = 93% (agents learning)
Round 200-300:    Accuracy = 94% (stabilizing)
Round 300+:       Accuracy = 94% (converged)
```

**Interpretation:** System improves early, then stabilizes

### Weight Convergence

Track if agent weights stabilize:

```
Round 1-50:   Weights changing 5-10% per round
Round 50-100: Weights changing 1-2% per round
Round 100+:   Weights stable (< 1% change)
```

**Goal:** Weights should converge (not keep bouncing)

---

## 💾 **Metrics Storage & Export**

### In-Memory Tracking
```python
metrics = {
    "total_predictions": 1000,
    "correct_predictions": 940,
    "accuracy": 0.94,
    "per_agent_accuracy": {...},
    "agent_weights": {...},
    "confusion_matrix": {...}
}
```

### File Export

```json
{
  "timestamp": "2026-01-29T14:30:00Z",
  "experiment_id": "exp_001",
  "metrics": {
    "accuracy": 0.94,
    "precision": 0.93,
    "recall": 0.95,
    "f1_score": 0.94
  },
  "per_agent": {
    "agent_nb": {...},
    "agent_svm": {...},
    ...
  }
}
```

### Dashboard Visualization

See real-time metrics on the web dashboard:
- Line charts (accuracy over time)
- Bar charts (per-agent comparison)
- Gauge charts (current confidence)
- Heatmaps (confusion matrix)

---

## 🎯 **Success Criteria**

### Must Have
- [ ] Consensus accuracy ≥ 92%
- [ ] Improvement ratio ≥ 1.10x
- [ ] F1-score ≥ 0.90
- [ ] Inference time < 100ms

### Nice to Have
- [ ] Calibration error < 5%
- [ ] Byzantine resistance proven
- [ ] Weight convergence shown
- [ ] Per-agent accuracy tracked

### Stretch Goals
- [ ] Accuracy ≥ 96%
- [ ] Inference time < 50ms
- [ ] Real-time metrics dashboard
- [ ] Custom threshold optimization

---

## 📚 **Related Documentation**

- [Main README](../../README.md)
- [Developer Guide](../developer/README.md) - How to calculate metrics
- [Architecture Docs](../architecture/README.md) - Why these metrics
- [Experiment Results](../../outputs/reports/) - Actual data

---

**Last Updated:** January 29, 2026  
**Data Version:** Phase 5 Results (after experiments)
