# Claims Description Normalizer - Deployment Package

## 📋 Package Contents

### Model Files (5):
- baseline_tfidf_vectorizer.pkl - TF-IDF vectorizer (fitted on training data)
- baseline_model_category.pkl - Category classifier (97.59% accuracy)
- baseline_model_severity.pkl - Severity classifier (78.28% accuracy)
- baseline_model_sentiment.pkl - Sentiment classifier (91.38% accuracy)
- baseline_model_incident_type.pkl - Incident type classifier (64.48% accuracy)

### Extraction Functions:
- extraction_functions.py - Date, location, and affected_item extraction functions

### Metadata Files:
- baseline_metrics.json - Performance metrics for classification models
- extraction_metrics.json - Performance metrics for extraction
- deployment_info.json - Complete system information
- README.md - This file

## 🚀 Quick Start

### Install Dependencies:
```bash
pip install streamlit pandas numpy scikit-learn python-dateutil spacy transformers torch
python -m spacy download en_core_web_sm
```

### Load Models:
```python
import joblib
import pandas as pd

# Load vectorizer and models
vectorizer = joblib.load('baseline_tfidf_vectorizer.pkl')
models = {
    'category': joblib.load('baseline_model_category.pkl'),
    'severity': joblib.load('baseline_model_severity.pkl'),
    'sentiment': joblib.load('baseline_model_sentiment.pkl'),
    'incident_type': joblib.load('baseline_model_incident_type.pkl')
}

# Load extraction functions
from extraction_functions import extract_date, extract_location, extract_affected_item
```

### Make Predictions:
```python
def predict_all_fields(claim_text):
    # Vectorize
    text_tfidf = vectorizer.transform([claim_text])
    
    # Classify
    predictions = {
        'category': models['category'].predict(text_tfidf)[0],
        'severity': models['severity'].predict(text_tfidf)[0],
        'sentiment': models['sentiment'].predict(text_tfidf)[0],
        'incident_type': models['incident_type'].predict(text_tfidf)[0],
        'date_of_loss': extract_date(claim_text),
        'location': extract_location(claim_text),
        'affected_item': extract_affected_item(claim_text)
    }
    return predictions

# Test
claim = "My car was damaged on June 16th in South Josephton, AK when another driver crashed into me"
result = predict_all_fields(claim)
print(result)
```

## 📊 Model Performance

### Classification (Average: 82.93%):
- Category: 97.59%
- Severity: 78.28%
- Sentiment: 91.38%
- Incident Type: 64.48% (183 classes)

### Extraction:
- Date: 36.9% extraction rate
- Location: 29.3% extraction rate
- Affected Item: 100% extraction rate

## 🎯 Streamlit Deployment

Create `app.py`:
```python
import streamlit as st
import joblib
from extraction_functions import extract_date, extract_location, extract_affected_item

# Load models
@st.cache_resource
def load_models():
    vectorizer = joblib.load('baseline_tfidf_vectorizer.pkl')
    models = {
        'category': joblib.load('baseline_model_category.pkl'),
        'severity': joblib.load('baseline_model_severity.pkl'),
        'sentiment': joblib.load('baseline_model_sentiment.pkl'),
        'incident_type': joblib.load('baseline_model_incident_type.pkl')
    }
    return vectorizer, models

vectorizer, models = load_models()

st.title("🔍 Claims Description Normalizer")
claim_text = st.text_area("Enter claim description:", height=150)

if st.button("Analyze Claim"):
    # Make predictions
    text_tfidf = vectorizer.transform([claim_text])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Category", models['category'].predict(text_tfidf)[0])
        st.metric("Severity", models['severity'].predict(text_tfidf)[0])
        st.metric("Sentiment", models['sentiment'].predict(text_tfidf)[0])
    
    with col2:
        st.metric("Date", extract_date(claim_text) or "Not found")
        st.metric("Location", extract_location(claim_text) or "Not found")
    
    st.write("**Incident Type:**", models['incident_type'].predict(text_tfidf)[0])
    st.write("**Affected Item:**", extract_affected_item(claim_text))
```

Run with: `streamlit run app.py`

## 📝 Notes
- Models were trained on 1447 insurance claim samples
- Best performance on Auto and Home insurance categories
- Extraction functions use regex + SpaCy for structured fields
- Total system processes 7 fields from unstructured text

## 🔗 Links
- Repository: [Claims-Description-Normalizer]
- Streamlit Cloud: Deploy directly from GitHub
