"""
Claims History Page - View and manage all processed claims
"""

import streamlit as st
import json
from datetime import datetime
from database import (
    get_all_history,
    get_history_by_id,
    delete_history_item,
    search_history,
    get_history_stats,
    clear_all_history,
    get_recommendations_by_claim_id,
    has_recommendations
)
from utils import (
    get_severity_color, 
    get_confidence_color,
    format_recommendations_compact,
    generate_recommendations
)

# Page configuration
st.set_page_config(
    page_title="History - Claims Normalizer",
    page_icon="📜",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .claim-item {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.2s;
    }
    .claim-item:hover {
        background-color: #f0f2f6;
        border-color: #1976D2;
    }
    .claim-item-selected {
        background-color: #e3f2fd;
        border-color: #1976D2;
    }
    .detail-panel {
        position: sticky;
        top: 20px;
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📜 Claim Processing History")
st.markdown("View, search, and manage all your processed claims")

# Get statistics
stats = get_history_stats()
total_claims = stats.get("total_claims", 0)

if total_claims == 0:
    st.info("📭 No history yet. Process your first claim on the Home page!")
    st.stop()

# Display statistics in cards
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Claims", total_claims)

with col2:
    severity_breakdown = stats.get("severity_breakdown", {})
    most_common = max(severity_breakdown.items(), key=lambda x: x[1])[0] if severity_breakdown else "N/A"
    st.metric("🔥 Most Common", most_common)

with col3:
    last_date = stats.get("last_claim_date", "N/A")
    if last_date and last_date != "N/A":
        try:
            dt = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
            last_date = dt.strftime("%b %d, %I:%M %p")
        except:
            pass
    st.metric("🕐 Last Processed", last_date)

with col4:
    high_severity = severity_breakdown.get("High", 0) + severity_breakdown.get("Critical", 0)
    st.metric("⚠️ High/Critical", high_severity)

st.markdown("---")

# Search and filter section
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    search_keyword = st.text_input("🔍 Search in claims", placeholder="Enter keyword...", key="search_input")

with col2:
    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All", "Low", "Medium", "High", "Critical"],
        key="severity_filter"
    )

with col3:
    confidence_filter = st.selectbox(
        "Filter by Confidence",
        ["All", "Low", "Medium", "High"],
        key="confidence_filter"
    )

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
        if st.session_state.get("confirm_clear", False):
            deleted = clear_all_history()
            st.success(f"✅ Deleted {deleted} records")
            st.session_state.confirm_clear = False
            st.session_state.pop("selected_claim_id", None)
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("⚠️ Click again to confirm")

# Get history with filters
if search_keyword or severity_filter != "All":
    history = search_history(
        keyword=search_keyword if search_keyword else None,
        severity=severity_filter if severity_filter != "All" else None,
        limit=100
    )
    # Additional filter by confidence (done client-side)
    if confidence_filter != "All":
        history = [h for h in history if h.get("confidence", "").lower() == confidence_filter.lower()]
else:
    history = get_all_history(limit=100)
    if confidence_filter != "All":
        history = [h for h in history if h.get("confidence", "").lower() == confidence_filter.lower()]

if not history:
    st.info("🔍 No claims found matching your filters.")
    st.stop()

# Pagination settings
ITEMS_PER_PAGE = 5

# Initialize pagination state
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# Calculate total pages
total_items = len(history)
total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE  # Ceiling division

# Ensure current page is valid
if st.session_state.current_page > total_pages:
    st.session_state.current_page = total_pages
if st.session_state.current_page < 1:
    st.session_state.current_page = 1

# Get current page items
start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
current_page_history = history[start_idx:end_idx]

# Display pagination info at top
st.markdown(f"**Showing {start_idx + 1}-{end_idx} of {total_items} claim(s)** | Page {st.session_state.current_page} of {total_pages}")
st.markdown("---")

# Initialize selected claim
if "selected_claim_id" not in st.session_state:
    st.session_state.selected_claim_id = current_page_history[0]["id"] if current_page_history else None

# Main layout: Left-Right Split
col_left, col_right = st.columns([4, 6])

# LEFT COLUMN: Claim List
with col_left:
    st.markdown("### 📋 Claims List")
    
    # Scrollable container for claims
    for record in current_page_history:
        claim_id = record["id"]
        is_selected = st.session_state.selected_claim_id == claim_id
        
        # Format timestamp
        timestamp = record.get("timestamp", "Unknown")
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            formatted_time = dt.strftime("%b %d, %I:%M %p")
        except:
            formatted_time = timestamp
        
        # Claim preview
        claim_preview = record.get("claim_text", "")[:80]
        if len(record.get("claim_text", "")) > 80:
            claim_preview += "..."
        
        # Severity
        severity = record.get("severity", "Unknown")
        severity_color = get_severity_color(severity)
        
        # Create claim item container
        container_class = "claim-item-selected" if is_selected else "claim-item"
        
        with st.container():
            col1, col2 = st.columns([7, 3])
            
            with col1:
                # Make the whole area clickable
                if st.button(
                    f"🕐 {formatted_time}",
                    key=f"select_{claim_id}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.selected_claim_id = claim_id
                    st.rerun()
                
                st.caption(claim_preview)
            
            with col2:
                st.markdown(f"""
                    <div style="text-align: center; margin-top: 8px;">
                        <span style="background-color: {severity_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                            {severity}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Pagination controls at bottom
    st.markdown("---")
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Previous", disabled=(st.session_state.current_page <= 1), use_container_width=True, type="secondary"):
            st.session_state.current_page -= 1
            st.rerun()
    with col_next:
        if st.button("Next ➡️", disabled=(st.session_state.current_page >= total_pages), use_container_width=True, type="secondary"):
            st.session_state.current_page += 1
            st.rerun()

# RIGHT COLUMN: Claim Details
with col_right:
    st.markdown("### 📄 Claim Details")
    
    # Get selected claim
    selected_claim = get_history_by_id(st.session_state.selected_claim_id)
    
    if selected_claim:
        # Create detail panel
        with st.container():
            # Timestamp
            timestamp = selected_claim.get("timestamp", "Unknown")
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                formatted_time = timestamp
            
            st.info(f"🕐 **Processed:** {formatted_time}")
            
            # Original Claim Text
            st.markdown("#### 📝 Original Claim Description")
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #1976D2; color: #000000; line-height: 1.6;">
                    {selected_claim.get("claim_text", "N/A")}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Extracted Data in a nice grid
            st.markdown("#### 🔍 Extracted Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Loss Type
                loss_type = selected_claim.get("loss_type", "Unknown")
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Loss Type</p>
                        <p style="font-size: 18px; font-weight: bold; margin: 5px 0; color: #1976D2;">{loss_type}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Severity
                severity = selected_claim.get("severity", "Unknown")
                severity_color = get_severity_color(severity)
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Severity</p>
                        <p style="font-size: 18px; font-weight: bold; margin: 5px 0; color: {severity_color};">{severity}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Affected Assets
                affected_assets = selected_claim.get("affected_assets", "Not specified")
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Affected Assets</p>
                        <p style="font-size: 16px; margin: 5px 0;">{affected_assets}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Estimated Loss
                estimated_loss = selected_claim.get("estimated_loss", "Not specified")
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Estimated Loss</p>
                        <p style="font-size: 18px; font-weight: bold; margin: 5px 0; color: #388E3C;">{estimated_loss}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Incident Date
                incident_date = selected_claim.get("incident_date", "Not specified")
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Incident Date</p>
                        <p style="font-size: 16px; margin: 5px 0;">{incident_date}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Location
                location = selected_claim.get("location", "Not specified")
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Location</p>
                        <p style="font-size: 16px; margin: 5px 0;">{location}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Confidence
                confidence = selected_claim.get("confidence", "Unknown")
                confidence_color = get_confidence_color(confidence)
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Confidence Level</p>
                        <p style="font-size: 18px; font-weight: bold; margin: 5px 0; color: {confidence_color};">{confidence}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AI Explanation
            st.markdown("#### 💡 AI Explanation")
            explanation = selected_claim.get("extraction_explanation", "No explanation available")
            st.write(explanation)
            
            st.markdown("---")
            
            # AI Recommendations Section
            st.markdown("#### 🤖 AI Recommendations")
            
            # Initialize session state for recommendations expansion
            if f"show_recommendations_{selected_claim['id']}" not in st.session_state:
                st.session_state[f"show_recommendations_{selected_claim['id']}"] = False
            
            # Button to toggle recommendations
            if st.button(
                "🔍 View Recommendations" if not st.session_state[f"show_recommendations_{selected_claim['id']}"] else "🔼 Hide Recommendations",
                key=f"toggle_rec_{selected_claim['id']}",
                type="secondary",
                use_container_width=True
            ):
                st.session_state[f"show_recommendations_{selected_claim['id']}"] = not st.session_state[f"show_recommendations_{selected_claim['id']}"]
                st.rerun()
            
            # Display recommendations when expanded
            if st.session_state[f"show_recommendations_{selected_claim['id']}"]:
                with st.spinner("Loading recommendations..."):
                    # Check if recommendations exist in database
                    if has_recommendations(selected_claim['id']):
                        # Load from database
                        recommendations = get_recommendations_by_claim_id(selected_claim['id'])
                        
                        if recommendations:
                            # Format and display
                            recommendations_html = format_recommendations_compact(recommendations)
                            st.markdown(recommendations_html, unsafe_allow_html=True)
                        else:
                            st.info("No recommendations found for this claim.")
                    else:
                        # Show message for old claims
                        st.warning("⚠️ Recommendations are not available for claims processed before this feature was added. Only newly processed claims will have AI-powered recommendations.")
            
            st.markdown("---")
            
            # Action Buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download JSON
                extracted_data = {
                    "loss_type": selected_claim.get("loss_type"),
                    "severity": selected_claim.get("severity"),
                    "affected_assets": selected_claim.get("affected_assets"),
                    "estimated_loss": selected_claim.get("estimated_loss"),
                    "incident_date": selected_claim.get("incident_date"),
                    "location": selected_claim.get("location"),
                    "confidence": selected_claim.get("confidence"),
                    "extraction_explanation": selected_claim.get("extraction_explanation")
                }
                json_output = json.dumps(extracted_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_output,
                    file_name=f"claim_{selected_claim['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # Delete button
                if st.button("🗑️ Delete This Claim", type="secondary", use_container_width=True):
                    if st.session_state.get(f"confirm_delete_{selected_claim['id']}", False):
                        delete_history_item(selected_claim['id'])
                        st.success("✅ Claim deleted!")
                        st.session_state.pop(f"confirm_delete_{selected_claim['id']}", None)
                        st.session_state.pop("selected_claim_id", None)
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{selected_claim['id']}"] = True
                        st.warning("⚠️ Click again to confirm deletion")
            
            with col3:
                # Export all button
                if st.button("📊 Export All CSV", use_container_width=True):
                    st.info("CSV export feature coming soon!")
    
    else:
        st.error("❌ Claim not found")

# Footer
st.markdown("---")
st.caption(f"📊 Total: {total_claims} claims | 🔍 Showing: {len(history)} claims")
