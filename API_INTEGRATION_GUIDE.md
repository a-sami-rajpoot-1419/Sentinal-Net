# API Integration Guide for Enhanced UI

## Overview

This guide explains how to integrate the backend API with the new enhanced UI features.

---

## 1. Response Format Requirements

The API must return predictions in the following format for the UI to work correctly:

### Complete Response Example

```json
{
  "prediction_id": "pred_6f7a9c2b_20240115_103045",
  "classification": "SPAM",
  "confidence": 0.883,
  "agent_votes": {
    "Naive Bayes": {
      "prediction": "SPAM",
      "confidence": 0.92,
      "vote": 1
    },
    "Random Forest": {
      "prediction": "SPAM",
      "confidence": 0.88,
      "vote": 1
    },
    "Logistic Regression": {
      "prediction": "SPAM",
      "confidence": 0.85,
      "vote": 1
    },
    "SVM": null
  },
  "reasoning": {
    "vote_distribution": "3-0 consensus for SPAM",
    "confidence_level": "High confidence ensemble decision",
    "dominant_signals": [
      "Free entry offer",
      "Lottery/prize keywords",
      "SMS shortening patterns",
      "Urgency tactics"
    ],
    "weighted_score_spam": 0.883,
    "weighted_score_ham": 0.117
  },
  "communication_log": {
    "timestamp": "2024-01-15T10:30:45.123Z",
    "request_id": "req_8f2d1a9e",
    "processing_time_ms": 45,
    "models_used": ["Naive Bayes", "Random Forest", "Logistic Regression"],
    "consensus_algorithm": "RWPV",
    "cache_hit": false
  },
  "weights_at_prediction": {
    "Naive Bayes": 0.88,
    "Random Forest": 0.85,
    "Logistic Regression": 0.82,
    "SVM": null
  },
  "text": "Free entry in 2 a wkly comp to win FA Cup tickets 2005...",
  "metadata": {
    "text_length": 87,
    "has_links": false,
    "has_numbers": true,
    "language_detected": "en"
  }
}
```

---

## 2. Field Descriptions

### Required Fields

| Field                   | Type   | Description                  | Example                        |
| ----------------------- | ------ | ---------------------------- | ------------------------------ |
| `prediction_id`         | string | Unique prediction identifier | `"pred_6f7a9c2b_..."`          |
| `classification`        | string | Final classification result  | `"SPAM"` or `"HAM"`            |
| `confidence`            | number | Overall confidence (0-1)     | `0.883`                        |
| `agent_votes`           | object | Individual model predictions | See structure below            |
| `reasoning`             | object | Explanation of decision      | See structure below            |
| `communication_log`     | object | Metadata about prediction    | See structure below            |
| `weights_at_prediction` | object | Model reputation weights     | `{ "Naive Bayes": 0.88, ... }` |
| `text`                  | string | Original SMS text            | `"User's input SMS..."`        |

### agent_votes Structure

```json
{
  "Model Name": {
    "prediction": "SPAM" | "HAM",
    "confidence": 0.0-1.0,
    "vote": 0 | 1
  }
  // or null if model not available
}
```

**Note:** Each model can be present, null (not evaluated), or have 0-3 models available:

```json
// Example with mixed availability
{
  "Naive Bayes": { "prediction": "SPAM", "confidence": 0.92, "vote": 1 },
  "Random Forest": { "prediction": "SPAM", "confidence": 0.88, "vote": 1 },
  "Logistic Regression": null,
  "SVM": null
}
```

### reasoning Structure

```json
{
  "vote_distribution": "3-0 consensus for SPAM", // Human-readable vote breakdown
  "confidence_level": "High confidence ensemble decision",
  "dominant_signals": ["Signal 1", "Signal 2", "Signal 3"],
  "weighted_score_spam": 0.883,
  "weighted_score_ham": 0.117
}
```

### communication_log Structure

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z", // ISO 8601 format
  "request_id": "req_8f2d1a9e",
  "processing_time_ms": 45,
  "models_used": ["Naive Bayes", "Random Forest", "Logistic Regression"],
  "consensus_algorithm": "RWPV",
  "cache_hit": false
}
```

---

## 3. Minimal Valid Response

If you want to start simple, here's the minimum required:

```json
{
  "prediction_id": "pred_123",
  "classification": "SPAM",
  "confidence": 0.88,
  "agent_votes": {
    "Naive Bayes": { "prediction": "SPAM", "confidence": 0.92 },
    "Random Forest": { "prediction": "HAM", "confidence": 0.45 }
  },
  "reasoning": {
    "vote_distribution": "Majority vote SPAM",
    "confidence_level": "Medium"
  },
  "communication_log": {
    "processing_time_ms": 45,
    "models_used": ["Naive Bayes", "Random Forest"]
  },
  "weights_at_prediction": {
    "Naive Bayes": 0.88,
    "Random Forest": 0.85
  },
  "text": "Original SMS text here"
}
```

---

## 4. Integration Steps

### Step 1: Update API Endpoint

In your backend (FastAPI example):

```python
from fastapi import FastAPI
from datetime import datetime
from typing import Optional, Dict, Any

app = FastAPI()

@app.post("/classify/text")
async def classify_text(text: str) -> Dict[str, Any]:
    # Your existing classification logic
    predictions = run_models(text)

    # Format response for UI
    return {
        "prediction_id": generate_prediction_id(),
        "classification": predictions["final_decision"],
        "confidence": predictions["confidence"],
        "agent_votes": format_agent_votes(predictions),
        "reasoning": format_reasoning(predictions),
        "communication_log": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "processing_time_ms": predictions["time_ms"],
            "models_used": predictions["models_used"],
            "consensus_algorithm": "RWPV"
        },
        "weights_at_prediction": predictions["weights"],
        "text": text
    }
```

### Step 2: Test with curl

```bash
curl -X POST http://localhost:8000/classify/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Free entry in 2 a wkly comp to win FA Cup tickets"}'
```

### Step 3: Update Frontend Component

The `PredictionTester.tsx` component expects this format. When API returns data:

```typescript
const handleSubmit = async () => {
  const response = await fetch("/api/classify", {
    method: "POST",
    body: JSON.stringify({ text: inputText }),
  });

  const result = await response.json();

  // Set result and show enhanced display
  setResult(result);
  setShowResult(true);
};
```

### Step 4: Verify in Frontend

The `EnhancedPredictionDisplay` component will automatically display:

- Classification badge (RED/GREEN)
- Individual predictions
- Performance metrics
- Weight visualization
- Communication logs

---

## 5. Optional: PDF Generation

If you want PDF downloads to work, implement:

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

@app.get("/pdf/overview")
async def get_overview_pdf():
    """Generate PDF of overview page"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add content to PDF
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Sentinel-Net System Overview", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5-Minute Quick Start", styles['Heading2']))
    # ... more content

    doc.build(elements)
    return StreamingResponse(
        BytesIO(buffer.getvalue()),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=overview.pdf"}
    )
```

Then update frontend buttons to call `/pdf/{page_name}`.

---

## 6. Error Handling

The UI expects errors in this format:

```json
{
  "error": "Invalid input",
  "message": "Text must be between 1-500 characters",
  "code": "INVALID_INPUT"
}
```

Handle in frontend:

```typescript
try {
  const response = await fetch("/api/classify", {
    method: "POST",
    body: JSON.stringify({ text: inputText }),
  });

  if (!response.ok) {
    const error = await response.json();
    setError(error.message);
    return;
  }

  const result = await response.json();
  setResult(result);
  setShowResult(true);
} catch (err) {
  setError("Failed to classify text");
}
```

---

## 7. Testing Scenarios

### Test Case 1: SPAM Classification

**Input:**

```json
{
  "text": "Congratulations! You've won a FREE IPHONE! Click here: http://bit.ly/xxx"
}
```

**Expected Response:**

```json
{
  "classification": "SPAM",
  "confidence": 0.95,
  "agent_votes": {
    "Naive Bayes": { "prediction": "SPAM", "confidence": 0.98 },
    "Random Forest": { "prediction": "SPAM", "confidence": 0.93 }
  }
}
```

### Test Case 2: HAM Classification

**Input:**

```json
{
  "text": "Hi! Just confirming our meeting tomorrow at 2pm. See you then!"
}
```

**Expected Response:**

```json
{
  "classification": "HAM",
  "confidence": 0.97,
  "agent_votes": {
    "Naive Bayes": { "prediction": "HAM", "confidence": 0.99 },
    "Random Forest": { "prediction": "HAM", "confidence": 0.95 }
  }
}
```

### Test Case 3: Borderline Case

**Input:**

```json
{
  "text": "Limited time offer on electronics. High quality products. Call 1-800-123-4567"
}
```

**Expected Response:**

```json
{
  "classification": "SPAM",
  "confidence": 0.62,
  "agent_votes": {
    "Naive Bayes": { "prediction": "SPAM", "confidence": 0.75 },
    "Random Forest": { "prediction": "HAM", "confidence": 0.55 }
  }
}
```

---

## 8. Performance Considerations

### Response Time

The UI expects:

- **Ideal:** < 100ms response time
- **Acceptable:** < 500ms response time
- **Maximum:** < 2000ms (show loading spinner)

### Caching

For frequently tested phrases:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def classify_text_cached(text: str):
    return classify_text(text)
```

### Batch Processing

For multiple SMS:

```python
@app.post("/classify/batch")
async def classify_batch(texts: List[str]):
    results = [classify_text(text) for text in texts]
    return {"predictions": results}
```

---

## 9. Documentation for Different Audiences

Each audience gets different documentation:

| Audience          | Doc Page             | Content                             |
| ----------------- | -------------------- | ----------------------------------- |
| **End Users**     | `/docs/users`        | How to use, privacy, FAQs           |
| **Developers**    | `/docs/developers`   | API reference, setup, code examples |
| **Researchers**   | `/docs/researchers`  | Benchmarks, ML models, datasets     |
| **Business**      | `/docs/business`     | ROI, market analysis, roadmap       |
| **System Admins** | `/docs/architecture` | System design, deployment, security |
| **New Users**     | `/docs/overview`     | 5-minute quick start                |

---

## 10. Deployment Checklist

- [ ] API returns all required fields
- [ ] Response format matches specification
- [ ] Error messages are clear and formatted correctly
- [ ] Response times < 500ms for typical SMS
- [ ] All model names match exactly (case-sensitive)
- [ ] Confidence values are 0-1 range
- [ ] Timestamps are ISO 8601 format
- [ ] Processing time is measured in milliseconds
- [ ] PDF endpoints functional (if implemented)
- [ ] CORS headers set correctly for frontend access

---

## Example Complete Workflow

```
USER INPUT
    ↓
[SMS text]
    ↓
POST /classify/text
    ↓
BACKEND PROCESSING
├─ Text preprocessing
├─ Run 3-4 ML models
├─ Calculate consensus (RWPV)
└─ Format response
    ↓
JSON RESPONSE
    ↓
FRONTEND DISPLAY
├─ Show RED/GREEN badge
├─ Expandable sections
├─ Performance metrics
└─ Weight visualization
    ↓
USER SEES RESULTS
```

---

For questions or issues, refer to:

- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- Individual doc pages at `/docs/*`

---

Last Updated: 2024-01-15
