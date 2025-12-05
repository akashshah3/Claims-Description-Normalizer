import streamlit as st
import joblib
import pandas as pd
import sys
import os

# Add the models directory to path
models_dir = os.path.join(os.path.dirname(__file__), 'claims_normalizer_models')
sys.path.insert(0, models_dir)

from extraction_functions import extract_date, extract_location, extract_affected_item

# Page config
st.set_page_config(
    page_title="Claims Description Normalizer",
    page_icon="🔍",
    layout="wide"
)

# Load models (cached for performance)
@st.cache_resource
def load_models():
    """Load all trained models"""
    try:
        vectorizer = joblib.load(os.path.join(models_dir, 'baseline_tfidf_vectorizer.pkl'))
        models = {
            'category': joblib.load(os.path.join(models_dir, 'baseline_model_category.pkl')),
            'severity': joblib.load(os.path.join(models_dir, 'baseline_model_severity.pkl')),
            'sentiment': joblib.load(os.path.join(models_dir, 'baseline_model_sentiment.pkl')),
            'incident_type': joblib.load(os.path.join(models_dir, 'baseline_model_incident_type.pkl'))
        }
        return vectorizer, models
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

# Load models
vectorizer, models = load_models()
models_loaded = vectorizer is not None and models is not None

# App header
st.title("🔍 Claims Description Normalizer")
st.markdown("""
Transform unstructured insurance claim descriptions into structured data fields.
Enter a claim description below to extract key information automatically.
""")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This app uses ML models to extract:
    - **Category** (Auto, Home, etc.)
    - **Severity** (Minor, Moderate, Major, etc.)
    - **Sentiment** (Formal, Frustrated, etc.)
    - **Incident Type** (specific classification)
    - **Date of Loss** (when it happened)
    - **Location** (where it happened)
    - **Affected Item** (what was damaged)
    """)
    
    st.header("📊 Performance")
    st.metric("Avg Accuracy", "82.93%")
    st.metric("Fields Extracted", "7")
    st.metric("Processing Time", "< 1 sec")
    
    st.markdown("---")
    st.markdown("**🎯 Model Details:**")
    st.markdown("""
    - **Algorithm:** TF-IDF + Logistic Regression
    - **Training Data:** 1,447 claims
    - **Categories:** Auto, Home, Health, Cyber, Travel, Liability
    """)

# Main content
if models_loaded:
    # Input section
    st.header("📝 Enter Claim Description")
    
    # Example claims for demo
    examples = {
        "Auto Accident": "My car was severely damaged on June 16th in South Josephton, AK when another driver ran a red light and crashed into my passenger side. The entire right side needs repair including the door and wheel.",
        "Home Damage": "Heavy rain caused my garden wall to collapse. There's now a security risk and the wall needs rebuilding urgently. This happened last Tuesday at my home in Portland, OR.",
        "Bicycle Theft": "My bicycle was stolen from the garage on May 5th, 2024. The lock was cut and the bike was worth $800. Police report filed in Seattle, WA.",
        "Health Emergency": "I had an emergency appendicitis surgery on November 20th at Portland General Hospital. The surgery was successful but I'm facing high medical bills.",
        "Home Fire": "Kitchen fire on December 1st damaged cabinets and appliances. Fire started from unattended stove. Total damage estimated at $15,000.",
    }
    
    example_choice = st.selectbox("Or select an example:", ["Custom"] + list(examples.keys()))
    
    if example_choice != "Custom":
        default_text = examples[example_choice]
    else:
        default_text = ""
    
    claim_text = st.text_area(
        "Claim Description:",
        value=default_text,
        height=150,
        placeholder="Enter the insurance claim description here... Be specific about what happened, when, and where."
    )
    
    # Analyze button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        analyze_button = st.button("🔍 Analyze Claim", type="primary", use_container_width=True)
    with col_btn2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if analyze_button:
        if claim_text.strip():
            with st.spinner("Analyzing claim..."):
                try:
                    # Vectorize input
                    text_tfidf = vectorizer.transform([claim_text])
                    
                    # Make predictions
                    category = models['category'].predict(text_tfidf)[0]
                    severity = models['severity'].predict(text_tfidf)[0]
                    sentiment = models['sentiment'].predict(text_tfidf)[0]
                    incident_type = models['incident_type'].predict(text_tfidf)[0]
                    
                    # Extract additional fields
                    date_loss = extract_date(claim_text)
                    location = extract_location(claim_text)
                    affected = extract_affected_item(claim_text)
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    
                    st.header("📊 Extracted Fields")
                    
                    # Create 3 columns for better layout
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📂 Category", category)
                        st.metric("⚠️ Severity", severity)
                        
                    with col2:
                        st.metric("💭 Sentiment", sentiment)
                        st.metric("📅 Date of Loss", date_loss or "Not found")
                        
                    with col3:
                        st.metric("📍 Location", location or "Not found")
                    
                    # Incident type and affected item in full width
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**🔖 Incident Type:**")
                        st.info(incident_type)
                    
                    with col_b:
                        st.markdown("**🎯 Affected Item:**")
                        st.info(affected if affected else "Not extracted")
                    
                    # Show structured output
                    st.markdown("---")
                    with st.expander("📋 View Structured Output (JSON)", expanded=False):
                        output_dict = {
                            "category": category,
                            "severity": severity,
                            "sentiment": sentiment,
                            "incident_type": incident_type,
                            "date_of_loss": date_loss,
                            "location": location,
                            "affected_item": affected
                        }
                        
                        st.json(output_dict)
                        
                        # Download option
                        import json
                        json_str = json.dumps(output_dict, indent=2)
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json_str,
                            file_name="claim_analysis.json",
                            mime="application/json"
                        )
                    
                    # Show prediction confidence (if available)
                    with st.expander("📈 Model Confidence Scores", expanded=False):
                        st.markdown("**Classification Probabilities:**")
                        
                        # Get probabilities for each model
                        proba_cols = st.columns(4)
                        
                        with proba_cols[0]:
                            cat_proba = models['category'].predict_proba(text_tfidf)[0]
                            max_proba = max(cat_proba)
                            st.metric("Category", f"{max_proba*100:.1f}%")
                        
                        with proba_cols[1]:
                            sev_proba = models['severity'].predict_proba(text_tfidf)[0]
                            max_proba = max(sev_proba)
                            st.metric("Severity", f"{max_proba*100:.1f}%")
                        
                        with proba_cols[2]:
                            sent_proba = models['sentiment'].predict_proba(text_tfidf)[0]
                            max_proba = max(sent_proba)
                            st.metric("Sentiment", f"{max_proba*100:.1f}%")
                        
                        with proba_cols[3]:
                            inc_proba = models['incident_type'].predict_proba(text_tfidf)[0]
                            max_proba = max(inc_proba)
                            st.metric("Incident Type", f"{max_proba*100:.1f}%")
                    
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                    with st.expander("📋 Error Details"):
                        st.exception(e)
        else:
            st.warning("⚠️ Please enter a claim description")
else:
    st.error("❌ Failed to load models. Please check that all model files are in the 'claims_normalizer_models' directory.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Claims Description Normalizer</strong></p>
    <p>Built with Streamlit | Models: TF-IDF + Logistic Regression + Rule-based Extraction</p>
    <p>Average Accuracy: 82.93% | Processing Time: < 1 second</p>
</div>
""", unsafe_allow_html=True)
