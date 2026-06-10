import streamlit as st

PLATFORM_COLORS = {
    "Instagram": "#E1306C",
    "Facebook":  "#1877F2",
    "TikTok":    "#69C9D0",
    "YouTube":   "#FF0000",
    "Naver":     "#03C75A",
    "KakaoTalk": "#FEE500",
}

BRAND_COLORS = {
    "자사":    "#2563EB",
    "경쟁사A": "#64748B",
    "경쟁사B": "#94A3B8",
    "경쟁사C": "#475569",
    "경쟁사D": "#334155",
}

PLOTLY_FONT = dict(family="Malgun Gothic, sans-serif", color="#F1F5F9")

PLOTLY_LAYOUT = dict(
    font=PLOTLY_FONT,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=list(PLATFORM_COLORS.values()),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F1F5F9")),
    xaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
    yaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
)


def apply_layout(fig, title=""):
    fig.update_layout(**PLOTLY_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(color="#F1F5F9", size=14)))
    return fig


def inject_css():
    st.markdown("""
    <style>
    /* 메트릭 카드 스타일 */
    [data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-size: 0.85rem;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #F1F5F9 !important;
        font-size: 1.6rem;
        font-weight: 700;
    }
    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    /* 데이터프레임 */
    .stDataFrame { border-radius: 8px; }
    /* 구분선 */
    hr { border-color: #1E293B; }
    </style>
    """, unsafe_allow_html=True)
