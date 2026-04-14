import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set Page Config for Premium Look
st.set_page_config(
    page_title="لوحة تحكم المنافسات 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Premium Look & RTL Arabic Support
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans Arabic', 'Inter', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* KPI Cards */
    div.stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Titles */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-weight: 700 !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
    }

    /* Direction fix for metrics */
    [data-testid="stMetricValue"] {
        direction: ltr;
    }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data(ttl=600)
def load_data():
    try:
        with open('tenders_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"حدث خطأ في تحميل البيانات: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- Top Header ---
    st.markdown('<div class="main-header">لوحة تحكم منافسات عام 2026</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>تحديث تلقائي للمعلومات والبيانات التحليلية</p>", unsafe_allow_html=True)
    
    st.divider()

    # --- KPIs Row ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي المنافسات", len(df))
    with col2:
        top_org = df['org'].value_counts().index[0] if not df['org'].empty else "N/A"
        st.metric("أكثر الجهات طرحاً", top_org)
    with col3:
        ending_soon = len(df[df['days_left'] <= 7])
        st.metric("تنتهي خلال 7 أيام", ending_soon)
    with col4:
        total_cost = f"{df['cost'].sum():,.0f} ر.س"
        st.metric("إجمالي تكلفة الشروط", total_cost)

    st.divider()

    # --- Charts Row ---
    row2_col1, row2_col2 = st.columns([1, 1])
    
    with row2_col1:
        st.subheader("📊 توزيع المنافسات حسب الجهة")
        org_counts = df['org'].value_counts().head(10).reset_index()
        org_counts.columns = ['الجهة', 'العدد']
        fig_org = px.bar(org_counts, x='العدد', y='الجهة', orientation='h', 
                         template='plotly_dark', color='العدد', 
                         color_continuous_scale='Blues')
        fig_org.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_org, use_container_width=True)

    with row2_col2:
        st.subheader("🎯 توزيع المنافسات حسب المدينة")
        city_counts = df[df['city'] != "غير محدد"]['city'].value_counts().head(10).reset_index()
        city_counts.columns = ['المدينة', 'العدد']
        if not city_counts.empty:
            fig_city = px.pie(city_counts, values='العدد', names='المدينة', 
                             template='plotly_dark', hole=0.4, 
                             color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_city.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_city, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية للمدن حالياً")

    st.divider()

    # --- Recent Tenders & Table ---
    st.subheader("📋 قائمة المنافسات الأخيرة والمواعيد النهائية")
    
    # Simple search/filter
    search = st.text_input("🔍 ابحث في العناوين أو الجهات...", placeholder="اكتب للبحث...")
    
    filtered_df = df if not search else df[df['title'].str.contains(search) | df['org'].str.contains(search)]
    
    # Sort by deadline descending
    filtered_df = filtered_df.sort_values(by='days_left', ascending=True)

    # Clean display
    display_df = filtered_df[['title', 'org', 'city', 'deadline', 'days_left']]
    display_df.columns = ['العنوان', 'الجهة', 'المدينة', 'تاريخ التقديم', 'الأيام المتبقية']
    
    st.dataframe(display_df, use_container_width=True, height=400)

    # Refresh Button
    if st.button("🔄 تحديث البيانات الآن"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("⚠️ لا توجد بيانات متاحة. يرجى التأكد من تشغيل ملف sync_tenders.py أولاً.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #8b949e;'>تم التطوير بواسطة Antigravity AI | 2026</p>", unsafe_allow_html=True)
