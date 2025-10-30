"""
Claims Description Normalizer - Streamlit Application
AI-powered tool to extract structured data from unstructured insurance claim descriptions
"""

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Import custom modules
from prompts import build_prompt, GEMINI_CONFIG
from utils import (
    parse_gemini_response,
    extract_keywords_from_explanation,
    highlight_keywords_in_text,
    get_severity_color,
    get_confidence_color,
    get_confidence_percentage,
    validate_extracted_data,
    format_field_name,
    create_summary_stats
)
from database import (
    init_database,
    save_claim_to_history,
    get_all_history,
    get_history_by_id,
    delete_history_item,
    search_history,
    get_history_stats,
    clear_all_history
)

# Load environment variables
load_dotenv()

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="Claims Description Normalizer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .highlight-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000000;
        line-height: 1.6;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_gemini():
    """Initialize Gemini API with API key"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in environment variables!")
        st.stop()
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    return model


def process_claim(model, claim_text: str) -> dict:
    """
    Process claim description using Gemini API
    
    Args:
        model: Gemini model instance
        claim_text: Raw claim description
        
    Returns:
        Extracted structured data dictionary
    """
    try:
        # Build the prompt
        prompt = build_prompt(claim_text)
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(**GEMINI_CONFIG)
        )
        
        # Parse response
        extracted_data = parse_gemini_response(response.text)
        
        return extracted_data
    
    except Exception as e:
        return {
            "error": "API Error",
            "details": str(e)
        }


def display_results(claim_text: str, extracted_data: dict):
    """
    Display the extracted results in a beautiful format
    
    Args:
        claim_text: Original claim text
        extracted_data: Extracted structured data
    """
    
    # Check for errors
    if "error" in extracted_data:
        st.error(f"❌ {extracted_data['error']}")
        if "details" in extracted_data:
            st.error(f"Details: {extracted_data['details']}")
        if "raw_response" in extracted_data:
            with st.expander("Raw Response"):
                st.code(extracted_data['raw_response'])
        return
    
    # Validate data
    is_valid, missing_fields = validate_extracted_data(extracted_data)
    if not is_valid:
        st.warning(f"⚠️ Some fields are missing: {', '.join(missing_fields)}")
    
    # Display success message
    st.success("✅ Claim successfully normalized!")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "🔍 Detailed View", "💡 Explanation", "📝 JSON Output"])
    
    with tab1:
        st.subheader("Quick Summary")
        
        # Display key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            severity = extracted_data.get("severity", "Unknown")
            severity_color = get_severity_color(severity)
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #666; font-size: 14px; margin: 0;">Severity</p>
                    <p style="color: {severity_color}; font-size: 24px; font-weight: bold; margin: 5px 0;">{severity}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            loss_type = extracted_data.get("loss_type", "Unknown")
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #666; font-size: 14px; margin: 0;">Loss Type</p>
                    <p style="color: #1976D2; font-size: 24px; font-weight: bold; margin: 5px 0;">{loss_type}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            confidence = extracted_data.get("confidence", "Unknown")
            confidence_color = get_confidence_color(confidence)
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #666; font-size: 14px; margin: 0;">Confidence</p>
                    <p style="color: {confidence_color}; font-size: 24px; font-weight: bold; margin: 5px 0;">{confidence}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            estimated_loss = extracted_data.get("estimated_loss", "Not specified")
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #666; font-size: 14px; margin: 0;">Estimated Loss</p>
                    <p style="color: #388E3C; font-size: 24px; font-weight: bold; margin: 5px 0;">{estimated_loss}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Confidence progress bar
        st.markdown("### Confidence Level")
        confidence_pct = get_confidence_percentage(confidence)
        st.progress(confidence_pct / 100)
        st.caption(f"{confidence_pct}% confidence in extraction accuracy")
    
    with tab2:
        st.subheader("Detailed Extraction")
        
        # Display all fields in a nice format
        col1, col2 = st.columns(2)
        
        fields_to_display = [
            ("loss_type", "Loss Type"),
            ("severity", "Severity"),
            ("affected_assets", "Affected Assets"),
            ("estimated_loss", "Estimated Loss"),
            ("incident_date", "Incident Date"),
            ("location", "Location"),
            ("confidence", "Confidence Level")
        ]
        
        for idx, (field_key, field_label) in enumerate(fields_to_display):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                value = extracted_data.get(field_key, "Not available")
                st.markdown(f"**{field_label}:**")
                st.info(value)
    
    with tab3:
        st.subheader("AI Explanation & Keyword Highlighting")
        
        # Display explanation
        explanation = extracted_data.get("extraction_explanation", "No explanation provided")
        st.markdown("**Why the AI made these decisions:**")
        st.write(explanation)
        
        st.markdown("---")
        
        # Extract and highlight keywords
        st.markdown("**Highlighted Keywords in Original Text:**")
        keywords = extract_keywords_from_explanation(explanation)
        
        if keywords:
            st.caption(f"🔍 Found {len(keywords)} key phrases: {', '.join(keywords)}")
            highlighted_text = highlight_keywords_in_text(claim_text, keywords)
            st.markdown(f'<div class="highlight-box">{highlighted_text}</div>', unsafe_allow_html=True)
        else:
            st.info("No specific keywords were highlighted in the explanation.")
            st.write(claim_text)
    
    with tab4:
        st.subheader("JSON Output")
        st.caption("Copy this structured data for use in your systems")
        
        # Display formatted JSON
        json_output = json.dumps(extracted_data, indent=2, ensure_ascii=False)
        st.code(json_output, language="json")
        
        # Download button
        st.download_button(
            label="📥 Download JSON",
            data=json_output,
            file_name=f"claim_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def main():
    """Main application"""
    
    # Header
    st.title("📋 Claims Description Normalizer")
    st.markdown("""
        **AI-Powered Insurance Claim Analysis**  
        Transform unstructured claim descriptions into structured, actionable data using Google Gemini AI.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        # Quick stats
        try:
            stats = get_history_stats()
            total_claims = stats.get("total_claims", 0)
            st.metric("📊 Total Claims Processed", total_claims)
        except:
            st.metric("📊 Total Claims Processed", 0)
        
        st.markdown("---")
        
        # Navigation links
        st.subheader("🔗 Navigation")
        st.info("""
            📜 **History** - View all processed claims
            
            ℹ️ **About** - Learn more about this tool
        """)
        
        st.markdown("---")
        
        # Sample claims grouped dropdown
        st.subheader("📚 Load Sample Claim")
        
        # Define grouped samples
        sample_groups = {
            "🚗 Vehicle Claims": [
                ("Minor Car Accident", "Customer reported minor accident on rear bumper, scratches only, no injuries, estimated cost ₹7,000. Incident happened yesterday at parking lot near office."),
                ("Flood Damage", "Vehicle submerged during flood, engine not starting, electrical damage suspected. Major repairs needed."),
                ("Car Theft", "Vehicle stolen from residential parking area on Oct 28, 2025 around 3 AM. Honda Civic 2022 model, black color. Police report filed. Estimated value $25,000."),
                ("Multi-Vehicle Collision", "Involved in 3-car collision on Highway 101 on Oct 30 at 8:15 AM. Front end damage to vehicle, airbags deployed. Driver has minor injuries - whiplash. Other vehicles also damaged. Police attended scene. Estimate pending insurance adjuster inspection."),
            ],
            "🏠 Property Claims": [
                ("Kitchen Fire", "Fire reported in kitchen at 2:00 AM on Oct 15. Cabinets, microwave, and wall damaged. Customer estimates around $5000 damage. Fire department attended."),
                ("Water Leakage", "Customer called about water leakage from ceiling damaging furniture below. Not sure when it started, probably last week."),
                ("House Fire (Critical)", "Major house fire on Oct 29, 2025 at 11 PM on Maple Street. Entire second floor destroyed, first floor severely damaged by smoke and water from firefighting. Family evacuated safely. Total loss estimated over $200,000. Cause under investigation."),
                ("Pipe Burst", "Pipe burst in basement overnight, water flooded entire basement area. Carpet, drywall, and stored items damaged. Incident discovered this morning. Plumber called for emergency repair. No cost estimate yet."),
            ],
            "🌪️ Weather Claims": [
                ("Storm Damage", "Heavy storm last night caused tree branch to fall on vehicle roof. Windshield cracked, roof dented. No estimate yet. Happened at home driveway."),
                ("Hail Damage", "Vehicle damaged by hail storm yesterday evening. Multiple dents on hood and roof, rear windshield cracked. Car was parked outside during storm. Preliminary estimate around $8,000."),
            ],
            "👤 Other Claims": [
                ("Vandalism", "Customer reported vehicle vandalized with spray paint and broken side mirrors. Occurred somewhere between Oct 20-22 while parked on street. Estimated repair cost ₹15,000."),
                ("Slip and Fall", "Customer slipped on wet floor in shopping mall on Oct 30, 2025 around 2 PM. Injured right ankle, medical treatment required. Mall located at City Center. Medical bills approximately $2,500."),
            ],
        }
        
        # Create flat list for dropdown with group labels
        dropdown_options = ["-- Select a sample claim --"]
        sample_map = {}
        
        for group_name, samples in sample_groups.items():
            dropdown_options.append(group_name)
            for title, text in samples:
                option_label = f"  ↳ {title}"
                dropdown_options.append(option_label)
                sample_map[option_label] = text
        
        # Display dropdown
        selected_sample = st.selectbox(
            "Choose a sample:",
            dropdown_options,
            key="sample_selector",
            label_visibility="collapsed"
        )
        
        # Load sample when selected
        if selected_sample in sample_map:
            if st.button("Load This Sample", use_container_width=True):
                st.session_state.claim_input = sample_map[selected_sample]
                st.rerun()
        
        st.markdown("---")
        st.caption("Powered by Google Gemini 2.0 Flash")
    
    # Initialize Gemini
    model = initialize_gemini()
    
    # Main content area
    st.markdown("### Enter Claim Description")
    
    # Text area for input
    claim_input = st.text_area(
        "Paste or type the claim description below:",
        value=st.session_state.get("claim_input", ""),
        height=150,
        placeholder="Example: Customer reported minor accident on rear bumper, scratches only, no injuries, estimated cost ₹7,000...",
        key="claim_textarea"
    )
    
    # Update session state
    if claim_input:
        st.session_state.claim_input = claim_input
    
    # Process button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        process_button = st.button("🚀 Normalize Claim", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.claim_input = ""
        st.rerun()
    
    # Process claim
    if process_button:
        if not claim_input.strip():
            st.warning("⚠️ Please enter a claim description first!")
        else:
            with st.spinner("🤖 Processing claim with Gemini AI..."):
                extracted_data = process_claim(model, claim_input)
                
                # Save to history if successful (no errors)
                if "error" not in extracted_data:
                    try:
                        record_id = save_claim_to_history(claim_input, extracted_data)
                        st.toast(f"💾 Saved to history (ID: {record_id})", icon="✅")
                    except Exception as e:
                        st.warning(f"⚠️ Could not save to history: {str(e)}")
                
                # Display results
                st.markdown("---")
                display_results(claim_input, extracted_data)


if __name__ == "__main__":
    main()
