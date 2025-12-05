# Claims Description Normalizer - Final Implementation Plan

## 🎯 Problem Statement
Build an NLP pipeline that transforms unstructured insurance claim descriptions into structured data fields.

**Input:** `claim_text` (raw, emotional, varied formatting)

**Output:** Structured fields:
- `category` (Auto, Home)
- `incident_type` 
- `affected_item` (damage summary)
- `severity` (Minor, Moderate, Major, Total Loss)
- `sentiment` (Panicked, Frustrated, Confused, Apologetic, Formal, Minimalist)
- `date_of_loss`
- `location`

**Dataset:** 1447 labeled samples with all target fields

---

## 🔧 Implementation Decisions

**Development Environment:**
- Platform: Kaggle Jupyter Notebook
- Hardware: GPU enabled from start
- Dataset: Uploaded to Kaggle

**Workflow:**
- Phase-by-phase implementation
- Test each phase before proceeding
- Wait for confirmation before moving to next phase

**Deliverables per Phase:**
- Self-contained notebook with inline results
- Exported model files (.pkl, .pt) for Streamlit deployment
- Dense summary at end of each phase

---

## 📋 Implementation Roadmap

### **Phase 1: Exploratory Data Analysis & Data Prep**

**Why:** Understanding data distribution prevents model bias and identifies preprocessing needs.

**Actions:**
1. Analyze class distribution for each target field
   - Check for imbalanced classes (may need stratified sampling)
   - Visualize category, severity, sentiment distributions
2. Text statistics
   - Length distribution of `claim_text`
   - Common patterns, keywords per category
3. Data quality checks
   - Missing values
   - Duplicates
   - Outliers (extremely short/long claims)
4. Train/validation/test split (70/15/15 or 80/20)
   - Use stratified split to maintain class distributions

**Tools:** pandas, matplotlib, seaborn

---

### **Phase 2: Baseline Model (Quick Validation)**

**Why:** Establish performance baseline before investing in complex models.

**Approach:** Traditional ML (from AGENTS.md)
- **Classification:** TF-IDF + Logistic Regression/Random Forest
- **Extraction:** Regex patterns for `date_of_loss`, `location`

**Implementation:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier

# One model for all classification fields
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)

model = MultiOutputClassifier(LogisticRegression())
model.fit(X_train_tfidf, y_train[['category', 'severity', 'sentiment', 'incident_type']])
```

**Expected Results:** 60-75% accuracy (acceptable baseline)

---

### **Phase 3: Advanced Classification Model**

**Why:** Transformers understand context better than TF-IDF (from both documents).

**Recommended Approach:** Fine-tuned Transformer (from plan2.md)

#### **Option A: Separate Models (RECOMMENDED)**
Train individual models for each field:
- **Reasoning:** Simpler to debug, faster to train, easier to update one field independently
- **Models:** 5 separate BERT/DistilBERT classifiers

#### **Option B: Multi-Head Model**
Single BERT with multiple classification heads:
- **Reasoning:** More efficient inference, shared representations
- **Trade-off:** More complex to implement and debug

**Implementation Strategy:**
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer

# Example for 'category' field
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(df['category'].unique())
)

# Tokenize
train_encodings = tokenizer(X_train.tolist(), truncation=True, padding=True)

# Train using Hugging Face Trainer
trainer = Trainer(model=model, ...)
trainer.train()
```

**Target Metrics:** 85-90% accuracy on classification fields

---

### **Phase 4: Information Extraction (NER for Entities)**

**Why:** Better extraction of location, dates, and affected_item details (from AGENTS.md).

**Two-Pronged Strategy:**

#### **4A: Named Entity Recognition**
- **Tool:** SpaCy or BERT-Token-Classification
- **Target Fields:** `location`, `date_of_loss`, `affected_item`
- **Method:** Either:
  - Fine-tune SpaCy NER on custom labels
  - Or use weak supervision to auto-generate span annotations from existing labels

```python
import spacy
from spacy.training import Example

# Create training data with entity spans
TRAIN_DATA = [
    ("My car was damaged on June 16th in South Josephton, AK", 
     {"entities": [(23, 33, "DATE"), (37, 56, "LOCATION")]})
]

nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")
ner.add_label("DATE")
ner.add_label("LOCATION")
ner.add_label("ITEM")
```

#### **4B: Generative Summarization for affected_item**
- **Tool:** T5 or BART (from AGENTS.md)
- **Purpose:** Generate concise damage summaries
- **Input:** Full claim_text
- **Output:** Short description (e.g., "Driver was looking at GPS and missed a critical road sign")

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
affected_item_summary = summarizer(claim_text, max_length=50, min_length=10)
```

---

### **Phase 5: LLM-Based Fallback (Optional Enhancement)**

**Why:** Handle edge cases and improve robustness (from plan2.md).

**Use Case:** When confidence scores from Phase 3/4 are low (<70%), query an LLM.

**Recommended Models:**
- Open-source: Llama-3-8B, Mistral-7B (can run locally)
- API: GPT-4.1, Claude (if budget allows)

**Prompt Template:**
```python
prompt = f"""
Extract the following fields from this insurance claim description.
Return ONLY valid JSON.

Fields to extract:
- category: Auto or Home
- incident_type: brief classification
- affected_item: what was damaged
- severity: Minor, Moderate, Major, or Total Loss
- sentiment: Panicked, Frustrated, Confused, Apologetic, Formal, or Minimalist
- date_of_loss: YYYY-MM-DD format
- location: city, state

Claim: {claim_text}

JSON:
"""
```

**Cost Control:** Only use for <10% of claims (low-confidence cases)

---

### **Phase 6: Evaluation & Metrics**

**Classification Tasks:**
- Accuracy per field
- F1-score (macro/weighted)
- Confusion matrix
- Classification report

**Extraction Tasks:**
- Exact match accuracy (date, location)
- Token-level F1 (for NER spans)
- ROUGE/BLEU scores (for affected_item summaries)

**Business Metrics:**
- End-to-end accuracy (all fields correct)
- Processing time per claim
- Manual review rate reduction

```python
from sklearn.metrics import classification_report, confusion_matrix

# Per-field evaluation
for field in ['category', 'severity', 'sentiment', 'incident_type']:
    print(f"\n{field} Performance:")
    print(classification_report(y_test[field], predictions[field]))
```

---

### **Phase 7: Deployment**

**Recommended Stack:**
- **Backend:** FastAPI (REST API)
- **Frontend:** Streamlit (quick demo) or React (production)
- **Model Serving:** 
  - Hugging Face Inference API
  - Or self-hosted with TorchServe/TensorFlow Serving

**Deployment Flow:**
```
User Input (claim_text)
    ↓
API Endpoint (/predict)
    ↓
Model Ensemble (Classification + NER + Summarization)
    ↓
Return JSON with all structured fields
    ↓
Display in UI
```

**Streamlit Example:**
```python
import streamlit as st

st.title("Claims Description Normalizer")
claim_text = st.text_area("Enter claim description:")

if st.button("Analyze"):
    results = predict_pipeline(claim_text)
    st.json(results)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Category", results['category'])
        st.metric("Severity", results['severity'])
    with col2:
        st.metric("Sentiment", results['sentiment'])
        st.metric("Date of Loss", results['date_of_loss'])
```

---

## 🏆 Final Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Input: claim_text                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌──────────────────┐                 ┌──────────────────┐
│  Classification  │                 │    Extraction    │
│   (BERT/DistilBERT)                │   (NER + T5/BART) │
├──────────────────┤                 ├──────────────────┤
│ • category       │                 │ • location       │
│ • severity       │                 │ • date_of_loss   │
│ • sentiment      │                 │ • affected_item  │
│ • incident_type  │                 │   (summary)      │
└──────────────────┘                 └──────────────────┘
        ↓                                       ↓
        └───────────────────┬───────────────────┘
                            ↓
                  ┌──────────────────┐
                  │  LLM Fallback    │
                  │ (Low Confidence) │
                  └──────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │   Structured Output (All Fields)      │
        └───────────────────────────────────────┘
```

---

## 📊 Timeline Estimate

| Phase | Duration | Priority |
|-------|----------|----------|
| 1. EDA | 2-3 days | HIGH |
| 2. Baseline | 1-2 days | HIGH |
| 3. Transformer Classification | 1 week | HIGH |
| 4. NER + Summarization | 1 week | MEDIUM |
| 5. LLM Fallback | 2-3 days | LOW |
| 6. Evaluation | 2 days | HIGH |
| 7. Deployment | 3-5 days | MEDIUM |

**Total:** 3-4 weeks for full production system

---

## 🎯 Reasoning for Choices

### **From AGENTS.md:**
✅ **Transformers over TF-IDF** - Better context understanding
✅ **NER for entity extraction** - More precise than regex
✅ **T5/BART for summarization** - Generates natural affected_item descriptions

### **From plan2.md:**
✅ **6-step pipeline structure** - Systematic and comprehensive
✅ **EDA first** - Prevents wasted effort on wrong approach
✅ **Separate models per field** - Easier to implement and maintain
✅ **Multiple approach comparison** - Flexibility based on results
✅ **Streamlit deployment** - Fast prototyping and demo

### **Rejected:**
❌ Multi-head single model (initially) - More complex, harder to debug
❌ Pure LLM approach - Too expensive, not deterministic enough
❌ Pure regex extraction - Too brittle for varied text formats

---

## 🚀 Getting Started

**Next Immediate Steps:**
1. Run EDA on `final_training_data.csv`
2. Create train/test splits
3. Build baseline TF-IDF model
4. Set up Hugging Face transformers environment
5. Fine-tune first classifier (category - simplest field)

**Ready to begin implementation?**
