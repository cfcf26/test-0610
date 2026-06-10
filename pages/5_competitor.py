import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_competitor
from utils.filters import render_sidebar_filters, apply_filters, empty_guard
from utils.styles import BRAND_COLORS, apply_layout, inject_css
from utils.charts import heatmap_px, radar_chart

inject_css()
st.title("🏆 경쟁사 벤치마크")

df_raw = load_competitor()

with st.spinner("데이터 불러오는 중..."):
    filters = render_sidebar_filters(df_raw, {
        "month_col": "연월_dt",
        "show_platform": True,
        "show_industry": True,
        "show_brand": True,
    })
    df = apply_filters(df_raw, filters)
    empty_guard(df)

# ── KPI 카드 (자사 기준) ────────────────────────────────
own = df[df["브랜드"] == "자사"]
own_sov    = own["공유오브보이스(%)"].mean() if not own.empty else 0
own_senti  = own["감성점수(긍정%)"].mean() if not own.empty else 0
own_ctr    = own["추정CTR(%)"].mean() if not own.empty else 0

c1, c2, c3 = st.columns(3)
c1.metric("자사 평균 SOV",    f"{own_sov:.1f}%")
c2.metric("자사 감성점수",    f"{own_senti:.1f}%")
c3.metric("자사 추정 CTR",   f"{own_ctr:.2f}%")

st.markdown("---")

# ── SOV 월별 추이 ────────────────────────────────────────
st.subheader("브랜드별 공유오브보이스(SOV) 추이")
sov_df = (
    df.groupby([df["연월_dt"].dt.strftime("%Y-%m"), "브랜드"])["공유오브보이스(%)"]
    .mean().reset_index()
    .rename(columns={"연월_dt": "연월"})
)
fig_sov = px.area(
    sov_df, x="연월", y="공유오브보이스(%)", color="브랜드",
    color_discrete_map=BRAND_COLORS,
)
apply_layout(fig_sov)
fig_sov.update_layout(height=320)
st.plotly_chart(fig_sov, use_container_width=True)

# ── 레이더 차트 + 감성점수 ──────────────────────────────────
st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("브랜드별 종합 역량 레이더")
    radar_agg = (
        df.groupby("브랜드")
        .agg(
            CTR=("추정CTR(%)", "mean"),
            전환율=("추정전환율(%)", "mean"),
            감성점수=("감성점수(긍정%)", "mean"),
            언급수=("브랜드언급수", "mean"),
            SOV=("공유오브보이스(%)", "mean"),
        )
        .reset_index()
    )
    # 정규화 (0~100)
    for col in ["CTR", "전환율", "감성점수", "언급수", "SOV"]:
        mn, mx = radar_agg[col].min(), radar_agg[col].max()
        radar_agg[col] = ((radar_agg[col] - mn) / (mx - mn + 1e-9) * 100).round(1)

    categories = ["CTR", "전환율", "감성점수", "언급수", "SOV"]
    traces = {row["브랜드"]: [row[c] for c in categories] for _, row in radar_agg.iterrows()}
    fig_radar = radar_chart(categories, traces, title="5개 지표 정규화 비교")
    fig_radar.update_layout(height=380)
    st.plotly_chart(fig_radar, use_container_width=True)

with col_r:
    st.subheader("월별 감성점수 추이")
    senti_df = (
        df.groupby([df["연월_dt"].dt.strftime("%Y-%m"), "브랜드"])["감성점수(긍정%)"]
        .mean().reset_index()
        .rename(columns={"연월_dt": "연월"})
    )
    fig_senti = px.line(
        senti_df, x="연월", y="감성점수(긍정%)", color="브랜드",
        color_discrete_map=BRAND_COLORS, markers=True,
    )
    apply_layout(fig_senti)
    fig_senti.update_layout(height=380)
    st.plotly_chart(fig_senti, use_container_width=True)

# ── 업종 × 브랜드 추정광고비 히트맵 ──────────────────────
st.markdown("---")
st.subheader("업종 × 브랜드 추정 광고비 (경쟁 강도)")
pivot_ind = (
    df.groupby(["업종", "브랜드"])["추정광고비(원)"].sum()
    .unstack(fill_value=0)
    .round(0)
)
fig_ind = heatmap_px(pivot_ind, color_scale="Reds")
fig_ind.update_layout(height=340)
st.plotly_chart(fig_ind, use_container_width=True)

# ── 플랫폼별 자사 vs 경쟁사 CTR ────────────────────────────
st.markdown("---")
st.subheader("플랫폼별 자사 vs 경쟁사 추정 CTR")
plat_brand = (
    df.groupby(["플랫폼", "브랜드"])["추정CTR(%)"].mean().reset_index()
)
fig_plat = px.bar(
    plat_brand, x="추정CTR(%)", y="플랫폼", color="브랜드",
    barmode="group", orientation="h",
    color_discrete_map=BRAND_COLORS,
)
apply_layout(fig_plat)
fig_plat.update_layout(height=320)
st.plotly_chart(fig_plat, use_container_width=True)

# ── 다운로드 ──────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 현재 데이터 CSV 다운로드",
    data=df.drop(columns=["연월_dt"]).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="competitor_filtered.csv",
    mime="text/csv",
)
