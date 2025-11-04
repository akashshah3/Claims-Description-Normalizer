"""
About Page - Information about the Claims Description Normalizer
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="About - Claims Normalizer",
    page_icon="ℹ️",
    layout="wide"
)

# Header
st.title("ℹ️ About Claims Description Normalizer")
st.markdown("**AI-Powered Insurance Claim Analysis Tool**")

st.markdown("---")

# Create tabs for organized information
tab1, tab2, tab3 = st.tabs(["📖 Overview", "🚀 How It Works", "💻 Technology"])

with tab1:
    st.header("📖 What This Tool Does")
    
    st.markdown("""
    Insurance companies receive hundreds of **unstructured claim descriptions** daily. 
    Claims adjusters and customers write them freely, making them inconsistent and hard to process. 
    This tool automatically extracts structured data from these descriptions using AI.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Input Example")
        st.code("""
Customer reported minor accident on 
rear bumper, scratches only, no injuries, 
estimated cost ₹7,000. Incident happened 
yesterday at parking lot near office.
        """, language=None)
    
    with col2:
        st.subheader("📤 Output Example")
        st.json({
            "loss_type": "Accident",
            "severity": "Low",
            "affected_assets": "Rear bumper (scratches)",
            "estimated_loss": "₹7,000",
            "incident_date": "Yesterday",
            "location": "Parking lot near office",
            "confidence": "High"
        })
    
    st.markdown("---")
    
    st.header("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - 🤖 **AI-Powered Extraction** - Uses Google Gemini 2.0 Flash
        - 📊 **Structured Output** - Clean JSON with 8 key fields
        - 💡 **Explainability** - AI explains its decisions
        - 🔍 **Keyword Highlighting** - See what influenced the AI
        """)
    
    with col2:
        st.markdown("""
        - 📈 **Confidence Scoring** - Visual confidence indicators
        - 📜 **History Tracking** - All claims saved automatically
        - 🎨 **Professional UI** - Clean, intuitive interface
        - 📥 **Export Results** - Download as JSON
        """)
    
    st.markdown("---")
    
    st.header("📊 Extracted Data Fields")
    
    field_descriptions = [
        ("loss_type", "Type of loss/incident", "Accident, Fire, Flood, Theft, Water Damage, Storm, Vandalism"),
        ("severity", "Damage severity level", "Low, Medium, High, Critical"),
        ("affected_assets", "What was damaged", '"Car bumper", "Kitchen cabinets", "Vehicle engine"'),
        ("estimated_loss", "Monetary loss estimate", '"₹7,000", "$5000", "Not specified"'),
        ("incident_date", "When it occurred", '"Yesterday", "Oct 15, 2:00 AM", "Last week"'),
        ("location", "Where it happened", '"Parking lot", "Kitchen", "Highway 101"'),
        ("confidence", "AI confidence level", "Low, Medium, High"),
        ("extraction_explanation", "AI reasoning", '"Classified as \'Fire\' due to keywords..."'),
    ]
    
    for field, description, examples in field_descriptions:
        with st.expander(f"**{field}** - {description}"):
            st.markdown(f"**Example values:** {examples}")

with tab2:
    st.header("🚀 How It Works")
    
    st.markdown("### The Processing Pipeline")
    
    # Visual workflow
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center;">
            <h3>1️⃣</h3>
            <p><strong>Input Claim</strong></p>
            <p style="font-size: 12px;">User enters unstructured text</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center;">
            <h3>2️⃣</h3>
            <p><strong>AI Processing</strong></p>
            <p style="font-size: 12px;">Gemini analyzes with few-shot prompts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center;">
            <h3>3️⃣</h3>
            <p><strong>Extraction</strong></p>
            <p style="font-size: 12px;">Structured JSON output</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center;">
            <h3>4️⃣</h3>
            <p><strong>Display & Save</strong></p>
            <p style="font-size: 12px;">Results shown + saved to DB</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 1. Prompt Engineering")
    st.markdown("""
    The system uses **few-shot prompting** to teach Gemini what to extract:
    - **System prompt** defines the AI's role as an insurance analyst
    - **4 example claims** demonstrate the desired format
    - **Clear instructions** for JSON structure with 8 specific fields
    """)
    
    st.markdown("### 2. AI Processing")
    st.markdown("""
    When you submit a claim:
    - Text is sent to **Gemini 2.0 Flash** with the engineered prompt
    - AI analyzes keywords, context, and patterns
    - Returns structured JSON with confidence levels
    """)
    
    st.markdown("### 3. Post-Processing")
    st.markdown("""
    The app enhances the output:
    - Extracts keywords from the AI's explanation
    - Highlights those keywords in the original text
    - Validates all required fields are present
    - Formats data for visual display
    """)
    
    st.markdown("### 4. Storage")
    st.markdown("""
    All successful claims are automatically saved to a local SQLite database:
    - View history anytime without re-processing
    - Search and filter past claims
    - Export data as needed
    """)

with tab3:
    st.header("💻 Technology Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Core Technologies")
        
        tech_stack = [
            ("🐍 Python", "3.8+", "Backend language"),
            ("🎈 Streamlit", "1.39.0", "Web framework"),
            ("🤖 Google Gemini", "2.0 Flash", "AI/LLM for NLP"),
            ("🗄️ SQLite", "Built-in", "Local database"),
        ]
        
        for tech, version, purpose in tech_stack:
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
                <strong>{tech}</strong> <span style="color: #666;">v{version}</span><br>
                <span style="font-size: 14px; color: #666;">{purpose}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Python Packages")
        
        packages = [
            ("streamlit", "1.39.0", "Web interface"),
            ("google-generativeai", "0.8.3", "Gemini API client"),
            ("python-dotenv", "1.0.1", "Environment variables"),
            ("pandas", "2.2.3", "Data manipulation"),
        ]
        
        for package, version, purpose in packages:
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
                <strong>{package}</strong> <span style="color: #666;">v{version}</span><br>
                <span style="font-size: 14px; color: #666;">{purpose}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.header("📁 Project Structure")
    
    st.code("""
Claims-Description-Normalizer/
├── app.py                    # Main Home page
├── pages/
│   ├── 1_📜_History.py      # Claims history viewer
│   └── 2_ℹ️_About.py        # This page
├── database.py               # SQLite operations
├── prompts.py                # Gemini prompt engineering
├── utils.py                  # Helper functions
├── requirements.txt          # Python dependencies
├── sample_claims.txt         # Sample data
├── .env                      # API keys (not in git)
├── .env.example              # Template
├── .gitignore                # Git ignore rules
└── claims_history.db         # SQLite database (auto-created)
    """, language="text")
    
    st.markdown("---")
    
    st.header("🔧 Configuration")
    
    st.markdown("### Gemini API Settings")
    st.code("""
GEMINI_CONFIG = {
    "temperature": 0.3,  # Lower = more consistent
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024,
}
    """, language="python")
    
    st.info("💡 **Tip:** Lower temperature (0.3) ensures consistent, factual outputs for insurance data extraction.")

# Footer section
st.markdown("---")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 👨🏻‍💻 Developers
    **Akash Shah**  
    [GitHub Profile](https://github.com/akashshah3)
    
    **Laxmi Khilnani**  
    [GitHub Profile](https://github.com/laxmikhilnani20)
    """)

with col2:
    st.markdown("""
    ### 📖 Documentation
    
    [View README](https://github.com/akashshah3/Claims-Description-Normalizer)
    
    [Report Issues](https://github.com/akashshah3/Claims-Description-Normalizer/issues)
    """)

with col3:
    st.markdown("""
    ### 📜 License
    
    MIT License
    
    Open source and free to use
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
    <h3>Made with ❤️ and AI</h3>
    <p>Powered by Google Gemini 2.0 Flash & Streamlit</p>
</div>
""", unsafe_allow_html=True)
