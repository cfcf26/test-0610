import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_performance
from utils.filters import render_sidebar_filters, apply_filters, empty_guard
from utils.metrics import format_krw, format_pct, calc_delta
from utils.styles import PLATFORM_COLORS, apply_layout, inject_css
from utils.charts import line_trend, scatter_bubble, heatmap_px

inject_css()
st.title("📈 종합 성과 대시보드")

df_raw = load_performance()

with st.spinner("데이터 불러오는 중..."):
    filters = render_sidebar_filters(df_raw, {
        "date_col": "날짜",
        "show_platform": True,
        "show_industry": True,
    })
    df = apply_filters(df_raw, filters)
    empty_guard(df)

# ── KPI 카드 ────────────────────────────────────────────
total_spend  = df["광고비(원)"].sum()
total_conv   = df["전환수"].sum()
avg_roas     = df["ROAS(%)"].mean()
avg_ctr      = df["CTR(%)"].mean()

# 전월 델타 계산
max_d = df["날짜"].max()
prev_mask = (df["날짜"] >= max_d - pd.Timedelta(days=60)) & (df["날짜"] < max_d - pd.Timedelta(days=30))
cur_mask  = df["날짜"] >= max_d - pd.Timedelta(days=30)
d_spend = calc_delta(df[cur_mask]["광고비(원)"].sum(), df[prev_mask]["광고비(원)"].sum())
d_conv  = calc_delta(df[cur_mask]["전환수"].sum(),   df[prev_mask]["전환수"].sum())
d_roas  = calc_delta(df[cur_mask]["ROAS(%)"].mean(), df[prev_mask]["ROAS(%)"].mean())
d_ctr   = calc_delta(df[cur_mask]["CTR(%)"].mean(),  df[prev_mask]["CTR(%)"].mean())

c1, c2, c3, c4 = st.columns(4)
c1.metric("총 광고비",  format_krw(total_spend), d_spend)
c2.metric("총 전환수",  f"{total_conv:,}건",      d_conv)
c3.metric("평균 ROAS", f"{avg_roas:.1f}%",        d_roas)
c4.metric("평균 CTR",  f"{avg_ctr:.2f}%",         d_ctr)

st.markdown("---")

# ── 월별 광고비 + ROAS 이중축 ────────────────────────────
st.subheader("월별 광고비 & ROAS 추이")
monthly = (
    df.groupby(df["날짜"].dt.to_period("M").astype(str))
    .agg(광고비=("광고비(원)", "sum"), ROAS=("ROAS(%)", "mean"))
    .reset_index()
    .rename(columns={"날짜": "연월"})
)

fig_dual = go.Figure()
fig_dual.add_trace(go.Bar(
    x=monthly["연월"], y=monthly["광고비"],
    name="광고비(원)", marker_color="#2563EB", yaxis="y1",
))
fig_dual.add_trace(go.Scatter(
    x=monthly["연월"], y=monthly["ROAS"],
    name="평균 ROAS(%)", line=dict(color="#F59E0B", width=2),
    mode="lines+markers", yaxis="y2",
))
fig_dual.update_layout(
    yaxis=dict(title="광고비(원)", gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
    yaxis2=dict(title="ROAS(%)", overlaying="y", side="right", gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F1F5F9")),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Malgun Gothic, sans-serif", color="#F1F5F9"),
    xaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
    barmode="group",
    height=350,
)
st.plotly_chart(fig_dual, use_container_width=True)

# ── 플랫폼별 성과 비교 ────────────────────────────────────
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("플랫폼별 노출·클릭·전환")
    plat_agg = (
        df.groupby("플랫폼")
        .agg(노출수=("노출수", "sum"), 클릭수=("클릭수", "sum"), 전환수=("전환수", "sum"))
        .reset_index()
    )
    plat_melt = plat_agg.melt(id_vars="플랫폼", value_vars=["노출수", "클릭수", "전환수"],
                               var_name="지표", value_name="값")
    fig_stack = px.bar(
        plat_melt, x="플랫폼", y="값", color="지표", barmode="group",
        color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B"],
    )
    apply_layout(fig_stack)
    fig_stack.update_layout(height=330)
    st.plotly_chart(fig_stack, use_container_width=True)

with col_right:
    st.subheader("플랫폼별 CTR vs CPC (버블크기=광고비)")
    bubble_df = (
        df.groupby("플랫폼")
        .agg(CTR=("CTR(%)", "mean"), CPC=("CPC(원)", "mean"), 광고비=("광고비(원)", "sum"))
        .reset_index()
    )
    fig_bubble = scatter_bubble(
        bubble_df, x="CPC", y="CTR", size="광고비", color="플랫폼",
        color_map=PLATFORM_COLORS, hover_name="플랫폼",
    )
    fig_bubble.update_layout(height=330)
    st.plotly_chart(fig_bubble, use_container_width=True)

# ── ROAS 랭킹 ─────────────────────────────────────────────
st.markdown("---")
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("플랫폼별 평균 ROAS 랭킹")
    roas_df = (
        df.groupby("플랫폼")["ROAS(%)"].mean().reset_index()
        .sort_values("ROAS(%)", ascending=True)
    )
    fig_roas = px.bar(
        roas_df, x="ROAS(%)", y="플랫폼", orientation="h",
        color="ROAS(%)", color_continuous_scale="Blues",
        text_auto=".1f",
    )
    apply_layout(fig_roas)
    fig_roas.update_layout(height=300, coloraxis_showscale=False)
    st.plotly_chart(fig_roas, use_container_width=True)

with col_r2:
    st.subheader("업종 × 광고목표 평균 ROAS")
    pivot = (
        df.groupby(["업종", "광고목표"])["ROAS(%)"].mean()
        .unstack(fill_value=0)
        .round(1)
    )
    fig_heat = heatmap_px(pivot, color_scale="Blues")
    fig_heat.update_layout(height=300)
    st.plotly_chart(fig_heat, use_container_width=True)

# ── 다운로드 ──────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 현재 데이터 CSV 다운로드",
    data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="overview_filtered.csv",
    mime="text/csv",
)
