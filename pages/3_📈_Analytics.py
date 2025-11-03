"""
Analytics Dashboard - Aggregate Insights from Processed Claims
Shows trends, distributions, and key metrics from the claim history
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database import get_analytics_data, get_all_history

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1.2em;
        color: #666;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📈 Analytics Dashboard")
st.markdown("### Aggregate Insights from Processed Claims")
st.markdown("---")

# Get analytics data
try:
    analytics = get_analytics_data()
    
    # Check if there's any data
    if analytics["total_claims"] == 0:
        st.warning("⚠️ No claims data available yet. Process some claims first to see analytics!")
        st.info("💡 Go to the main page to start processing claims.")
        st.stop()
    
    # Key Metrics Cards
    st.markdown("## 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Claims Processed",
            value=analytics["total_claims"],
            delta=None
        )
    
    with col2:
        # Most common severity
        if analytics["severity_distribution"]:
            most_common_severity = analytics["severity_distribution"][0]["severity"]
            st.metric(
                label="Most Common Severity",
                value=most_common_severity,
                delta=None
            )
        else:
            st.metric(label="Most Common Severity", value="N/A")
    
    with col3:
        # Most common loss type
        if analytics["loss_type_distribution"]:
            most_common_loss = analytics["loss_type_distribution"][0]["loss_type"]
            # Truncate if too long
            display_loss = most_common_loss[:20] + "..." if len(most_common_loss) > 20 else most_common_loss
            st.metric(
                label="Most Common Loss Type",
                value=display_loss,
                delta=None
            )
        else:
            st.metric(label="Most Common Loss Type", value="N/A")
    
    with col4:
        # High confidence percentage
        if analytics["confidence_distribution"]:
            high_conf = next((item["count"] for item in analytics["confidence_distribution"] if item["confidence"] == "High"), 0)
            high_conf_pct = round((high_conf / analytics["total_claims"]) * 100, 1)
            st.metric(
                label="High Confidence Claims",
                value=f"{high_conf_pct}%",
                delta=None
            )
        else:
            st.metric(label="High Confidence Claims", value="N/A")
    
    st.markdown("---")
    
    # Visualizations Row 1: Loss Type and Severity
    st.markdown("## 📉 Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Loss Type Distribution")
        if analytics["loss_type_distribution"]:
            # Prepare data for pie chart
            df_loss = pd.DataFrame(analytics["loss_type_distribution"])
            
            # Create pie chart
            fig_loss = px.pie(
                df_loss,
                values='count',
                names='loss_type',
                title='Claims by Loss Type',
                hole=0.3,  # Donut chart
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_loss.update_traces(textposition='inside', textinfo='percent+label')
            fig_loss.update_layout(
                showlegend=True,
                height=400,
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_loss, use_container_width=True)
        else:
            st.info("No loss type data available")
    
    with col2:
        st.markdown("### Severity Level Distribution")
        if analytics["severity_distribution"]:
            # Prepare data for bar chart
            df_severity = pd.DataFrame(analytics["severity_distribution"])
            
            # Define color mapping for severity
            severity_colors = {
                'Critical': '#d62728',
                'High': '#ff7f0e',
                'Medium': '#ffbb00',
                'Low': '#2ca02c',
                'Unknown': '#7f7f7f'
            }
            
            # Map colors
            df_severity['color'] = df_severity['severity'].map(severity_colors)
            
            # Create bar chart
            fig_severity = go.Figure(data=[
                go.Bar(
                    x=df_severity['severity'],
                    y=df_severity['count'],
                    marker_color=df_severity['color'],
                    text=df_severity['count'],
                    textposition='auto',
                )
            ])
            fig_severity.update_layout(
                title='Claims by Severity Level',
                xaxis_title='Severity',
                yaxis_title='Number of Claims',
                height=400,
                margin=dict(t=50, b=50, l=50, r=20),
                showlegend=False
            )
            st.plotly_chart(fig_severity, use_container_width=True)
        else:
            st.info("No severity data available")
    
    st.markdown("---")
    
    # Visualizations Row 2: Time Series and Confidence
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Claims Over Time")
        if analytics["claims_over_time"] and len(analytics["claims_over_time"]) > 0:
            # Prepare data for line chart
            df_time = pd.DataFrame(analytics["claims_over_time"])
            df_time['date'] = pd.to_datetime(df_time['date'])
            
            # Create line chart
            fig_time = px.line(
                df_time,
                x='date',
                y='count',
                title='Claims Processed by Date',
                markers=True,
                line_shape='spline'
            )
            fig_time.update_traces(line_color='#1f77b4', line_width=3)
            fig_time.update_layout(
                xaxis_title='Date',
                yaxis_title='Number of Claims',
                height=400,
                margin=dict(t=50, b=50, l=50, r=20),
                hovermode='x unified'
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Not enough time series data available yet")
    
    with col2:
        st.markdown("### Confidence Level Distribution")
        if analytics["confidence_distribution"]:
            # Prepare data for bar chart
            df_confidence = pd.DataFrame(analytics["confidence_distribution"])
            
            # Define color mapping for confidence
            confidence_colors = {
                'High': '#2ca02c',
                'Medium': '#ffbb00',
                'Low': '#ff7f0e',
                'Unknown': '#7f7f7f'
            }
            
            # Map colors
            df_confidence['color'] = df_confidence['confidence'].map(confidence_colors)
            
            # Create bar chart
            fig_confidence = go.Figure(data=[
                go.Bar(
                    x=df_confidence['confidence'],
                    y=df_confidence['count'],
                    marker_color=df_confidence['color'],
                    text=df_confidence['count'],
                    textposition='auto',
                )
            ])
            fig_confidence.update_layout(
                title='Claims by Confidence Level',
                xaxis_title='Confidence',
                yaxis_title='Number of Claims',
                height=400,
                margin=dict(t=50, b=50, l=50, r=20),
                showlegend=False
            )
            st.plotly_chart(fig_confidence, use_container_width=True)
        else:
            st.info("No confidence data available")
    
    st.markdown("---")
    
    # Advanced Analytics: Severity by Loss Type Heatmap
    st.markdown("## 🔥 Advanced Insights")
    
    if analytics["severity_by_loss_type"]:
        st.markdown("### Severity Distribution by Loss Type")
        
        # Prepare data for heatmap
        df_heatmap = pd.DataFrame(analytics["severity_by_loss_type"])
        
        # Pivot for heatmap
        pivot_df = df_heatmap.pivot_table(
            index='loss_type',
            columns='severity',
            values='count',
            fill_value=0
        )
        
        # Reorder columns for better visualization
        severity_order = ['Critical', 'High', 'Medium', 'Low', 'Unknown']
        existing_cols = [col for col in severity_order if col in pivot_df.columns]
        pivot_df = pivot_df[existing_cols]
        
        # Create heatmap
        fig_heatmap = px.imshow(
            pivot_df,
            labels=dict(x="Severity", y="Loss Type", color="Count"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig_heatmap.update_layout(
            title='Heatmap: Loss Type vs Severity',
            height=max(400, len(pivot_df) * 40),
            margin=dict(t=50, b=50, l=150, r=20)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Data Summary Section
    st.markdown("## 📋 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Date Range")
        if analytics["date_range"]["first_claim"] and analytics["date_range"]["last_claim"]:
            first_claim = datetime.fromisoformat(analytics["date_range"]["first_claim"].replace('Z', '+00:00'))
            last_claim = datetime.fromisoformat(analytics["date_range"]["last_claim"].replace('Z', '+00:00'))
            
            st.write(f"**First Claim:** {first_claim.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Last Claim:** {last_claim.strftime('%Y-%m-%d %H:%M')}")
            
            days_diff = (last_claim - first_claim).days
            st.write(f"**Time Period:** {days_diff} days")
        else:
            st.info("Date range not available")
    
    with col2:
        st.markdown("#### Loss Type Summary")
        if analytics["loss_type_distribution"]:
            st.write(f"**Total Loss Types:** {len(analytics['loss_type_distribution'])}")
            st.write("**Top 3 Loss Types:**")
            for i, item in enumerate(analytics["loss_type_distribution"][:3], 1):
                percentage = (item["count"] / analytics["total_claims"]) * 100
                st.write(f"{i}. {item['loss_type']} ({percentage:.1f}%)")
        else:
            st.info("Loss type summary not available")
    
    # Export Option
    st.markdown("---")
    st.markdown("### 💾 Export Analytics Data")
    
    if st.button("📥 Download Analytics Report (CSV)"):
        # Create a comprehensive CSV report
        all_history = get_all_history(limit=10000)
        df_export = pd.DataFrame(all_history)
        
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"claims_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        st.success("✅ Analytics report ready for download!")

except Exception as e:
    st.error(f"❌ Error loading analytics data: {str(e)}")
    st.info("Please ensure the database is properly initialized and contains data.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>📊 Analytics Dashboard | Claims Description Normalizer</p>
        <p>Powered by AI and Data Visualization</p>
    </div>
    """,
    unsafe_allow_html=True
)
