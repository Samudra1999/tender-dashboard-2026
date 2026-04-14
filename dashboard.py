import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# PAGE CONFIG - Premium Setting
st.set_page_config(
    page_title="Corporate Tender Intelligence 2026",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM THEME & PREMIUM UI/UX
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Premium Header */
    .dashboard-header {
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    .dashboard-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    /* KPI CARDS */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px !important;
        border-radius: 18px !important;
        border-left: 5px solid #38bdf8 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        color: #38bdf8;
        padding-bottom: 20px;
    }

    /* Dataframe Styling */
    .stDataFrame {
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# LOAD DATA
@st.cache_data(ttl=300)
def load_data():
    try:
        with open('tenders_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- Sidebar Filters ---
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Analytics Filters</div>', unsafe_allow_html=True)
        search = st.text_input("🔍 Search Tenders", placeholder="E.g. Infrastructure...")
        
        st.divider()
        
        cities = ["All"] + sorted(df['city'].unique().tolist())
        selected_city = st.selectbox("📍 Filter by City", cities)
        
        orgs = ["All"] + sorted(df['org'].unique().tolist())
        selected_org = st.multiselect("🏢 Filter by Organization", orgs, default=["All"])
        
        st.divider()
        
        st.markdown("**Urgency Level**")
        min_days = st.slider("Min Days Left", 0, 100, 0)

    # --- Header ---
    st.markdown("""
        <div class="dashboard-header">
            <div class="dashboard-title">Tender Intelligence Portal</div>
            <div style="color: #94a3b8; font-size: 1.1rem; letter-spacing: 1px;">
                Strategic Analysis & Monitoring Platform | Q2 2026
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Filtering Logic
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False) | filtered_df['org'].str.contains(search, case=False)]
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    if "All" not in selected_org:
        filtered_df = filtered_df[filtered_df['org'].isin(selected_org)]
    filtered_df = filtered_df[filtered_df['days_left'] >= min_days]

    # --- KPI Section ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Tenders", len(filtered_df))
    with kpi2:
        val = filtered_df['cost'].sum()
        st.metric("Total Document Fees", f"${val:,.0f}" if val > 0 else "N/A")
    with kpi3:
        top_city = filtered_df['city'].value_counts().idxmax() if not filtered_df.empty else "N/A"
        st.metric("Primary Market", top_city)
    with kpi4:
        critical = len(filtered_df[filtered_df['days_left'] <= 5])
        st.metric("Critical Deadlines", critical)

    st.divider()

    # --- Analytics Charts ---
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
        st.markdown("### 🏢 Top Organizations by Tender Volume")
        org_data = filtered_df['org'].value_counts().head(12).reset_index()
        org_data.columns = ['Organization', 'Count']
        fig_org = px.bar(org_data, x='Count', y='Organization', orientation='h',
                         color='Count', color_continuous_scale='Blues',
                         template='plotly_dark')
        fig_org.update_layout(yaxis={'categoryorder':'total ascending'}, 
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_org, use_container_width=True)

    with chart_col2:
        st.markdown("### 📍 Geographic Concentration")
        city_data = filtered_df[filtered_df['city'] != 'Not Specified']['city'].value_counts().head(8).reset_index()
        city_data.columns = ['City', 'Count']
        fig_city = px.pie(city_data, values='Count', names='City', hole=0.5,
                          color_discrete_sequence=px.colors.sequential.PuBuGn_r,
                          template='plotly_dark')
        fig_city.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_city, use_container_width=True)

    st.divider()

    # --- Timeline Analytics ---
    st.markdown("### ⏳ Deadline Submission Timeline")
    timeline_df = filtered_df[filtered_df['days_left'] <= 60].sort_values('deadline')
    if not timeline_df.empty:
        fig_timeline = px.line(timeline_df, x='deadline', y='days_left', 
                               hover_data=['title', 'org'],
                               markers=True, template='plotly_dark')
        fig_timeline.update_traces(line_color='#38bdf8', marker_size=10)
        fig_timeline.update_layout(xaxis_title="Closing Date", yaxis_title="Days Remaining",
                                   plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_timeline, use_container_width=True)

    st.divider()

    # --- Data Explorer ---
    st.markdown("### 🔍 Strategic Resource Explorer")
    
    # Color code urgency in the table if possible, otherwise use clean formatting
    display_df = filtered_df[['title', 'org', 'city', 'deadline', 'days_left']].copy()
    display_df.columns = ['Tender Title', 'Organization', 'Location', 'Closing Date', 'Days Left']
    
    st.dataframe(display_df.sort_values('Days Left'), use_container_width=True, height=500)

    # Final Actions
    col_f1, col_f2 = st.columns([1, 4])
    with col_f1:
        if st.button("🔄 Sync Live Data"):
            st.cache_data.clear()
            st.rerun()
else:
    st.error("Data connectivity issue. Please ensure 'tenders_data.json' is present.")

# Footer
st.markdown("<p style='text-align: center; color: #64748b; padding-top: 50px;'>Proprietary Strategic Intelligence Dashboard | Confidental</p>", unsafe_allow_html=True)
