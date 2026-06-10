import streamlit as st
from utils.styles import inject_css

st.set_page_config(
    page_title="마케팅 인사이트 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

pages = [
    st.Page("pages/1_overview.py",    title="종합 성과",      icon="📈"),
    st.Page("pages/2_campaign.py",    title="캠페인 예산",    icon="💰"),
    st.Page("pages/3_audience.py",    title="오디언스 분석",  icon="👥"),
    st.Page("pages/4_creative.py",    title="소재 성과",      icon="🎨"),
    st.Page("pages/5_competitor.py",  title="경쟁사 벤치마크", icon="🏆"),
    st.Page("pages/6_region.py",      title="지역별 유입",    icon="🗺️"),
    st.Page("pages/7_ai_chat.py",     title="AI 데이터 대화", icon="🤖"),
]

with st.sidebar:
    st.markdown("# 📊 마케팅 인사이트")
    st.markdown("---")

pg = st.navigation(pages)
pg.run()
