import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# PAGE CONFIGURATION & AGGRESSIVE THEME INJECTION
# ==============================================================================
st.set_page_config(
    page_title="NexGen Tender Analytics",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Reset & Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    h1, h2, h3, h4, h5 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.5px;
    }

    /* Core Application Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 70%, #000000 100%);
        background-attachment: fixed;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background: rgba(2, 6, 23, 0.7) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .css-1544g2n {
        padding-top: 2rem !important;
    }

    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Premium Header */
    .premium-header {
        text-align: center;
        padding: 40px 0;
        margin-bottom: 30px;
        position: relative;
    }
    .premium-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #38bdf8, transparent);
    }
    .premium-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        text-shadow: 0 0 40px rgba(56, 189, 248, 0.2);
    }
    .premium-subtitle {
        color: #94a3b8;
        font-weight: 300;
        font-size: 1.1rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Custom Animated HTML KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 40px;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 25px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .kpi-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.2);
    }
    /* Glowing orb behind card text */
    .kpi-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 2.4rem;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        line-height: 1.1;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #10b981; /* Default green for positive indication */
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .kpi-subtext.urgent {
        color: #ef4444; /* Red for urgent */
    }

    /* Section Titles */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        color: #f1f5f9;
        font-weight: 600;
        margin: 30px 0 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-title i {
        color: #38bdf8;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA PIPELINE
# ==============================================================================
@st.cache_data(ttl=300)
def load_data():
    try:
        with open('tenders_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        # Proper Datetime Parsing
        df['pub_date'] = pd.to_datetime(df['pub_date'], errors='coerce')
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df['pub_month'] = df['pub_date'].dt.to_period('M').astype(str)
        
        # Sanitization
        df['area'] = df['area'].replace('', 'Unspecified')
        df['activity'] = df['activity'].replace('', 'Unspecified')
        df['org'] = df['org'].replace('', 'Unspecified')
        df['value'] = df['value'].fillna(0)
        df['days_left'] = df['days_left'].fillna(0).astype(int)
        
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("Data pipeline disconnected. Please verify tenders_data.json.")
    st.stop()

# ==============================================================================
# INTELLIGENT EXPERT SLICERS (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8; font-family: Space Grotesk;'>Control Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:14px;'>Global Data Slicers</p><hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    search_q = st.text_input("🔍 Neural Search", placeholder="Keywords, IDs, etc...")
    st.markdown("<br>", unsafe_allow_html=True)
    
    status_options = sorted(df['status'].unique())
    selected_status = st.multiselect("Pipeline Status", status_options, default=status_options)
    
    org_options = sorted([x for x in df['org'].unique() if x != 'Unspecified'])
    selected_orgs = st.multiselect("Issuing Authority", org_options)
    
    area_options = sorted([x for x in df['area'].unique() if x != 'Unspecified'])
    selected_areas = st.multiselect("Geographic Zone", area_options)
    
    type_options = sorted([x for x in df['type'].unique() if x != 'Unspecified'])
    selected_types = st.multiselect("Contract Modality", type_options)

# FILTERING EXECUTION
f_df = df.copy()
if search_q:
    f_df = f_df[
        f_df['title'].str.contains(search_q, case=False, na=False) |
        f_df['org'].str.contains(search_q, case=False, na=False) |
        f_df['ref'].str.contains(search_q, case=False, na=False)
    ]
if selected_status:
    f_df = f_df[f_df['status'].isin(selected_status)]
if selected_orgs:
    f_df = f_df[f_df['org'].isin(selected_orgs)]
if selected_areas:
    f_df = f_df[f_df['area'].isin(selected_areas)]
if selected_types:
    f_df = f_df[f_df['type'].isin(selected_types)]

# ==============================================================================
# DASHBOARD RENDERING
# ==============================================================================

# MAIN HEADER
st.markdown("""
<div class="premium-header">
    <div class="premium-title">NexGen Market Intelligence</div>
    <div class="premium-subtitle">Automated Institutional Procurement Analytics • Live Feed</div>
</div>
""", unsafe_allow_html=True)

# METRICS CALCULATIONS
total_vol = len(f_df)
total_value = f_df['value'].sum()
active_count = len(f_df[f_df['status'].str.contains('Certified|Active', case=False, na=False)])
urgent_count = len(f_df[(f_df['days_left'] <= 7) & (f_df['days_left'] >= 0)])

# Value formatting
if total_value > 1e9:
    val_disp = f"SAR {total_value/1e9:.2f}B"
elif total_value > 1e6:
    val_disp = f"SAR {total_value/1e6:.1f}M"
else:
    val_disp = "SAR 0.0M" # or calculate average if true data is missing

# HTML INJECTION FOR WOW-FACTOR KPIs
kpi_html = f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-title">Total Opportunities</div>
        <div class="kpi-value">{total_vol:,}</div>
        <div class="kpi-subtext"><span>●</span> Sliced Dataset Matrix</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Total Contract Value</div>
        <div class="kpi-value" style="color:#818cf8;">{val_disp}</div>
        <div class="kpi-subtext" style="color:#818cf8;"><span>▲</span> Estimated Target Cap</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Active Market Status</div>
        <div class="kpi-value" style="color:#10b981;">{active_count:,}</div>
        <div class="kpi-subtext"><span>✔</span> Certified & Available</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Urgent Action Required</div>
        <div class="kpi-value" style="color:#ef4444;">{urgent_count:,}</div>
        <div class="kpi-subtext urgent"><span>⚠</span> Closing in < 7 Days</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# PLOTLY MASTER CONFIG
plt_config = {
    'displayModeBar': False,
    'scrollZoom': False
}
layout_args = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#cbd5e1'),
    margin=dict(l=20, r=20, t=40, b=20),
)

# ==============================================================================
# VISUAL ANALYTICS - TIER 1
# ==============================================================================
col1, col2 = st.columns([6, 4])

with col1:
    st.markdown('<div class="section-title">📊 Temporal Demand Mapping</div>', unsafe_allow_html=True)
    trend_df = f_df.groupby('pub_month').size().reset_index(name='Density')
    trend_df = trend_df[trend_df['pub_month'] != 'NaT'].sort_values('pub_month')
    
    if not trend_df.empty:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_df['pub_month'], y=trend_df['Density'],
            mode='lines+markers',
            line=dict(color='#38bdf8', width=3),
            marker=dict(size=8, color='#0ea5e9', line=dict(width=2, color='#f8fafc')),
            fill='tozeroy',
            fillcolor='rgba(56, 189, 248, 0.15)',
            hoverinfo='text',
            text=[f"Month: {x}<br>Tenders: {y}" for x, y in zip(trend_df['pub_month'], trend_df['Density'])]
        ))
        fig_trend.update_layout(**layout_args, hovermode="x unified", xaxis_title="", yaxis_title="Volume")
        fig_trend.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        fig_trend.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        st.plotly_chart(fig_trend, use_container_width=True, config=plt_config)

with col2:
    st.markdown('<div class="section-title">⏱️ Portfolio Lifecycle (Days Left)</div>', unsafe_allow_html=True)
    # create bins for days_left
    bins = [-9999, -1, 7, 30, 9999]
    labels = ['Expired', 'Critical (0-7)', 'Active (8-30)', 'Long Term (30+)']
    f_df['Lifecycle'] = pd.cut(f_df['days_left'], bins=bins, labels=labels)
    urg_df = f_df['Lifecycle'].value_counts().reset_index()
    urg_df.columns = ['Status', 'Count']
    
    colors = {'Expired': '#475569', 'Critical (0-7)': '#ef4444', 'Active (8-30)': '#10b981', 'Long Term (30+)': '#38bdf8'}
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=urg_df['Status'], values=urg_df['Count'], hole=0.75,
        marker=dict(colors=[colors.get(x, '#cbd5e1') for x in urg_df['Status']],
                    line=dict(color='#0f172a', width=4)),
        textinfo='label+percent', textposition='outside'
    )])
    fig_donut.update_layout(**layout_args, showlegend=False,
                            annotations=[dict(text=str(sum(urg_df['Count'])), x=0.5, y=0.5, 
                                            font_size=40, font_family='Space Grotesk', showarrow=False)])
    st.plotly_chart(fig_donut, use_container_width=True, config=plt_config)


# ==============================================================================
# VISUAL ANALYTICS - TIER 2
# ==============================================================================
col3, col4 = st.columns([5, 5])

with col3:
    st.markdown('<div class="section-title">🏛️ Top Institutional Entities</div>', unsafe_allow_html=True)
    org_df = f_df[f_df['org'] != 'Unspecified']['org'].value_counts().head(8).reset_index()
    org_df.columns = ['Entity', 'Volume']
    
    if not org_df.empty:
        fig_bar = go.Figure(go.Bar(
            x=org_df['Volume'], y=org_df['Entity'], orientation='h',
            marker=dict(
                color=org_df['Volume'],
                colorscale=['#1e293b', '#38bdf8', '#818cf8'],
                line=dict(color='rgba(255,255,255,0.1)', width=1)
            )
        ))
        fig_bar.update_layout(**layout_args, yaxis={'categoryorder':'total ascending'})
        fig_bar.update_layout(margin=dict(l=10, r=20, t=10, b=20))
        st.plotly_chart(fig_bar, use_container_width=True, config=plt_config)

with col4:
    st.markdown('<div class="section-title">🌐 Multi-Dimensional Matrix (Region → Sector)</div>', unsafe_allow_html=True)
    sun_df = f_df[(f_df['area'] != 'Unspecified') & (f_df['activity'] != 'Unspecified')].copy()
    
    if not sun_df.empty:
        fig_sun = px.sunburst(sun_df, path=['area', 'activity'], 
                              color_discrete_sequence=px.colors.sequential.Agaln)
        fig_sun.update_layout(**layout_args)
        fig_sun.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        fig_sun.update_traces(hovertemplate='<b>%{label}</b><br>Volume: %{value}<extra></extra>', textinfo='label')
        st.plotly_chart(fig_sun, use_container_width=True, config=plt_config)


st.markdown("<br><hr style='border:1px solid rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)

# ==============================================================================
# PREMIUM MISSION CONTROL DATA GRID
# ==============================================================================
st.markdown('<div class="section-title">🔬 Deep Inspection Grid</div>', unsafe_allow_html=True)

st.markdown("""
<style>
/* Customizing the Streamlit dataframe wrapping */
div[data-testid="stDataFrame"] {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 12px;
    padding: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

view_cols = ['ref', 'title', 'org', 'status', 'deadline', 'days_left', 'activity', 'area']
rename_map = {
    'ref': 'ID / Ref', 'title': 'Tender Description', 'org': 'Authority',
    'status': 'Status Phase', 'deadline': 'Final Deadline', 
    'days_left': 'T-Minus (Days)', 'activity': 'Sector', 'area': 'Locale'
}

grid_df = f_df[view_cols].copy().rename(columns=rename_map)
grid_df['T-Minus (Days)'] = grid_df['T-Minus (Days)'].astype(int)
grid_df = grid_df.sort_values(by=['T-Minus (Days)', 'Final Deadline'], ascending=[True, False])

# Render with conditional logic in pandas styling for an incredible look
def stylize_status(row):
    days = row['T-Minus (Days)']
    if 0 <= days <= 7:
        return ['color: #111827; background-color: #ef4444; font-weight:700'] * len(row)
    elif 8 <= days <= 15:
        return ['color: #fef08a; background-color: rgba(234, 179, 8, 0.15);'] * len(row)
    return [''] * len(row)

styled_grid = grid_df.style.apply(stylize_status, axis=1)

st.dataframe(
    styled_grid, 
    use_container_width=True, 
    height=450,
    hide_index=True,
    column_config={
        "Tender Description": st.column_config.TextColumn(width="large"),
        "T-Minus (Days)": st.column_config.ProgressColumn(
            format="%d",
            min_value=0,
            max_value=30,
        )
    }
)
