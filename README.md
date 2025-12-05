# 🔍 Claims Description Normalizer

> **Transform unstructured insurance claim descriptions into structured data fields using AI/ML**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent system that extracts **7 structured fields** from unstructured insurance claim text with **82.93% average accuracy**.

---

## 🎯 What It Does

Converts messy claim descriptions like this:

> *"My car was severely damaged on June 16th in South Josephton, AK when another driver ran a red light and crashed into my passenger side."*

Into structured data:

```json
{
  "category": "Auto",
  "severity": "Major",
  "sentiment": "Formal",
  "incident_type": "Rear-end collision",
  "date_of_loss": "2024-06-16",
  "location": "South Josephton, AK",
  "affected_item": "Car passenger side door and wheel"
}
```

---

## ✨ Features

- 🤖 **4 Classification Models** - Category, Severity, Sentiment, Incident Type
- 📅 **Smart Date Extraction** - Multiple date formats supported
- 📍 **Location Detection** - City, State extraction with US validation
- 🎯 **Affected Item Summarization** - Automatic damage description
- ⚡ **Fast Processing** - < 1 second per claim
- 🎨 **Interactive UI** - Beautiful Streamlit interface
- 📊 **Confidence Scores** - Know how certain the predictions are
- 💾 **JSON Export** - Download structured results

---

## 📊 Model Performance

| Field | Accuracy | Method |
|-------|----------|--------|
| **Category** | 97.59% | TF-IDF + Logistic Regression |
| **Sentiment** | 91.38% | TF-IDF + Logistic Regression |
| **Severity** | 78.28% | TF-IDF + Logistic Regression |
| **Incident Type** | 64.48% | TF-IDF + Logistic Regression (183 classes!) |
| **Date of Loss** | 36.9% extraction rate | Regex + dateutil |
| **Location** | 29.3% extraction rate | SpaCy NER + Regex |
| **Affected Item** | 100% extraction rate | Keyword extraction |

**Overall System Accuracy:** 82.93%

**Training Data:** 1,447 insurance claims across 6 categories (Auto, Home, Health, Cyber, Travel, Liability)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/akashshah3/Claims-Description-Normalizer.git
   cd Claims-Description-Normalizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser:**
   - Local: http://localhost:8501
   - The app should automatically open in your default browser

---

## 🎮 Usage

### Web Interface

1. Launch the app with `streamlit run app.py`
2. Choose an example claim or enter your own
3. Click **"Analyze Claim"**
4. View extracted fields and download JSON

### Python API

```python
import joblib
from claims_normalizer_models.extraction_functions import (
    extract_date, extract_location, extract_affected_item
)

# Load models
vectorizer = joblib.load('claims_normalizer_models/baseline_tfidf_vectorizer.pkl')
models = {
    'category': joblib.load('claims_normalizer_models/baseline_model_category.pkl'),
    'severity': joblib.load('claims_normalizer_models/baseline_model_severity.pkl'),
    'sentiment': joblib.load('claims_normalizer_models/baseline_model_sentiment.pkl'),
    'incident_type': joblib.load('claims_normalizer_models/baseline_model_incident_type.pkl')
}

# Make predictions
claim_text = "Your claim description here..."
text_tfidf = vectorizer.transform([claim_text])

result = {
    'category': models['category'].predict(text_tfidf)[0],
    'severity': models['severity'].predict(text_tfidf)[0],
    'sentiment': models['sentiment'].predict(text_tfidf)[0],
    'incident_type': models['incident_type'].predict(text_tfidf)[0],
    'date_of_loss': extract_date(claim_text),
    'location': extract_location(claim_text),
    'affected_item': extract_affected_item(claim_text)
}

print(result)
```

---

## 📁 Project Structure

```
Claims-Description-Normalizer/
│
├── app.py                          # Streamlit web application
├── requirements.txt                # Python dependencies
├── model.ipynb                     # Model training notebook (Kaggle)
├── final_training_data.csv         # Training dataset (1,447 samples)
├── AGENTS.md                       # Implementation plan & decisions
│
├── claims_normalizer_models/       # Trained models & functions
│   ├── baseline_tfidf_vectorizer.pkl
│   ├── baseline_model_category.pkl
│   ├── baseline_model_severity.pkl
│   ├── baseline_model_sentiment.pkl
│   ├── baseline_model_incident_type.pkl
│   ├── extraction_functions.py
│   ├── baseline_metrics.json
│   ├── extraction_metrics.json
│   └── deployment_info.json
│
└── README.md                       # You are here!
```

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **ML Framework:** scikit-learn
- **Text Processing:** TF-IDF Vectorization
- **Classification:** Logistic Regression (MultiOutput)
- **Extraction:** Regex + python-dateutil + SpaCy patterns
- **Development:** Jupyter Notebook (Kaggle with GPU)

---

## 🎓 Model Details

### Classification Pipeline

1. **Text Vectorization:** TF-IDF (5,000 features, unigrams + bigrams)
2. **Algorithm:** Logistic Regression with L-BFGS solver
3. **Training:** Separate model per field (4 total)
4. **Dataset Split:** 60% train, 20% validation, 20% test

### Why Not Transformers?

We tested DistilBERT but found that **baseline TF-IDF models outperformed** transformers:
- **TF-IDF:** 82.93% average accuracy
- **DistilBERT:** 60.48% average accuracy

**Reason:** Dataset too small (867 training samples, 183 incident types = 4.7 samples/class average). Transformers need 100+ samples per class for effective fine-tuning.

**Lesson:** Traditional ML can outperform deep learning on small, diverse datasets.

---

## 📈 Supported Categories & Fields

### Categories (6)
- Auto
- Home
- Health
- Cyber
- Travel
- Liability

### Severity Levels (8)
- Minor
- Moderate
- Major
- High
- Low
- Medium
- Critical
- Total Loss

### Sentiment Types (7)
- Formal
- Neutral
- Frustrated
- Confused
- Apologetic
- Panicked
- Minimalist

### Incident Types
**183 unique types** including:
- Collision types (Rear-end, Side-swipe, Head-on, etc.)
- Property damage (Fire, Flood, Theft, Vandalism, etc.)
- Health incidents (Injury, Surgery, Emergency, etc.)
- And many more...

---

## 🎯 Use Cases

- **Insurance Claims Processing** - Automate data entry
- **Claims Triage** - Prioritize by severity
- **Fraud Detection** - Analyze sentiment patterns
- **Data Analytics** - Extract insights from unstructured text
- **Customer Service** - Route claims to correct departments
- **Report Generation** - Create structured summaries

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your repository
4. Deploy!

Your app will be live at: `https://your-username-claims-normalizer.streamlit.app`

### Local Production

```bash
# Install dependencies
pip install -r requirements.txt

# Run with production settings
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 🔬 Training & Development

The models were trained on Kaggle with GPU support. See `model.ipynb` for the complete pipeline:

**Phase 1:** EDA & Data Preparation
**Phase 2:** Baseline TF-IDF Models
**Phase 3:** Transformer Investigation (rejected)
**Phase 4:** Information Extraction (NER + Summarization)

### Retrain Models

```python
# Load dataset
df = pd.read_csv('final_training_data.csv')

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(...)

# Vectorize
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)

# Train
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Save
joblib.dump(model, 'model.pkl')
```

---

## 📝 TODO / Future Improvements

- [ ] Add data augmentation for minority classes
- [ ] Implement active learning for continuous improvement
- [ ] Add multi-language support
- [ ] Create REST API endpoint
- [ ] Add batch processing capability
- [ ] Implement A/B testing framework
- [ ] Add model versioning and monitoring
- [ ] Create mobile-responsive UI
- [ ] Add user authentication
- [ ] Implement caching for common queries

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Akash Shah**
- GitHub: [@akashshah3](https://github.com/akashshah3)
- Repository: [Claims-Description-Normalizer](https://github.com/akashshah3/Claims-Description-Normalizer)

---

## 🙏 Acknowledgments

- Dataset inspired by real-world insurance claims scenarios
- Built with amazing open-source tools: scikit-learn, Streamlit, pandas
- Developed on Kaggle with GPU support
- Special thanks to the ML community for best practices

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/akashshah3/Claims-Description-Normalizer/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ using Python, Streamlit, and Machine Learning**

[⬆ Back to Top](#-claims-description-normalizer)

</div>
