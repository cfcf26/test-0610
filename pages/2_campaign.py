import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_budget
from utils.filters import render_sidebar_filters, apply_filters, empty_guard
from utils.metrics import format_krw, calc_delta
from utils.styles import PLATFORM_COLORS, apply_layout, inject_css
from utils.charts import scatter_bubble

inject_css()
st.title("💰 캠페인 예산 분석")

df_raw = load_budget()

with st.spinner("데이터 불러오는 중..."):
    filters = render_sidebar_filters(df_raw, {
        "month_col": "연월_dt",
        "show_platform": True,
        "show_campaign": True,
        "show_status": True,
    })
    df = apply_filters(df_raw, filters)
    empty_guard(df)

# ── KPI 카드 ────────────────────────────────────────────
avg_util    = df["예산소진율(%)"].mean()
achieved    = (df["목표달성률(%)"] >= 100).sum()
total_camp  = len(df["캠페인명"].unique())
avg_cpa     = df["실제CPA(원)"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("평균 예산 소진율", f"{avg_util:.1f}%")
c2.metric("목표 달성 캠페인", f"{achieved}건", f"전체 {total_camp}개 중")
c3.metric("평균 실제 CPA",   format_krw(avg_cpa))

st.markdown("---")

# ── 캠페인 현황 테이블 ────────────────────────────────────
st.subheader("캠페인별 예산 집행 현황")

tbl = (
    df.groupby(["캠페인명", "플랫폼", "캠페인상태"])
    .agg(
        배정예산=("배정예산(원)", "sum"),
        집행예산=("집행예산(원)", "sum"),
        예산소진율=("예산소진율(%)", "mean"),
        목표달성률=("목표달성률(%)", "mean"),
        실제CPA=("실제CPA(원)", "mean"),
    )
    .reset_index()
    .sort_values("목표달성률", ascending=False)
)

def color_achievement(val):
    if val >= 100:
        return "background-color: #14532d; color: #86efac"
    elif val >= 70:
        return "background-color: #713f12; color: #fde68a"
    else:
        return "background-color: #450a0a; color: #fca5a5"

styled = (
    tbl.style
    .applymap(color_achievement, subset=["목표달성률"])
    .format({
        "배정예산": "{:,.0f}원",
        "집행예산": "{:,.0f}원",
        "예산소진율": "{:.1f}%",
        "목표달성률": "{:.1f}%",
        "실제CPA": "{:,.0f}원",
    })
    .background_gradient(subset=["예산소진율"], cmap="Blues")
)
st.dataframe(styled, use_container_width=True, height=300)

st.markdown("---")

# ── CPA 비교 + 버블차트 ────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("목표 CPA vs 실제 CPA")
    cpa_df = (
        df.groupby("캠페인명")
        .agg(목표CPA=("목표CPA(원)", "mean"), 실제CPA=("실제CPA(원)", "mean"))
        .reset_index()
        .sort_values("실제CPA")
        .head(15)
    )
    cpa_melt = cpa_df.melt(id_vars="캠페인명", value_vars=["목표CPA", "실제CPA"],
                            var_name="구분", value_name="CPA")
    fig_cpa = px.bar(
        cpa_melt, x="CPA", y="캠페인명", color="구분", orientation="h",
        barmode="group",
        color_discrete_map={"목표CPA": "#2563EB", "실제CPA": "#F59E0B"},
    )
    apply_layout(fig_cpa)
    fig_cpa.update_layout(height=380)
    st.plotly_chart(fig_cpa, use_container_width=True)

with col_r:
    st.subheader("집행예산 × 목표달성률 × 전환수")
    bub_df = (
        df.groupby(["캠페인명", "플랫폼"])
        .agg(집행예산=("집행예산(원)", "sum"),
             목표달성률=("목표달성률(%)", "mean"),
             전환수=("실제전환수", "sum"))
        .reset_index()
    )
    fig_bub = scatter_bubble(
        bub_df, x="집행예산", y="목표달성률",
        size="전환수", color="플랫폼",
        color_map=PLATFORM_COLORS, hover_name="캠페인명",
        title="저효율 캠페인 식별",
    )
    fig_bub.update_layout(height=380)
    fig_bub.add_hline(y=100, line_dash="dash", line_color="#10B981",
                      annotation_text="목표 달성선", annotation_font_color="#10B981")
    st.plotly_chart(fig_bub, use_container_width=True)

# ── 월별 목표달성률 추이 ────────────────────────────────────
st.markdown("---")
st.subheader("월별 평균 목표달성률 추이")
trend_df = (
    df.groupby(df["연월_dt"].dt.strftime("%Y-%m"))["목표달성률(%)"]
    .mean().reset_index()
    .rename(columns={"연월_dt": "연월", "목표달성률(%)": "목표달성률"})
)
fig_trend = px.line(trend_df, x="연월", y="목표달성률", markers=True,
                    color_discrete_sequence=["#2563EB"])
fig_trend.add_hline(y=100, line_dash="dash", line_color="#10B981",
                    annotation_text="100% 기준선", annotation_font_color="#10B981")
apply_layout(fig_trend)
fig_trend.update_layout(height=280)
st.plotly_chart(fig_trend, use_container_width=True)

# ── 다운로드 ──────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 현재 데이터 CSV 다운로드",
    data=df.drop(columns=["연월_dt"]).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="campaign_filtered.csv",
    mime="text/csv",
)
