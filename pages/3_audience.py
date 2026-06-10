import streamlit as st
import plotly.express as px

from utils.data_loader import load_audience
from utils.filters import render_sidebar_filters, apply_filters, empty_guard
from utils.metrics import format_krw
from utils.styles import PLATFORM_COLORS, apply_layout, inject_css
from utils.charts import heatmap_px, donut_chart, scatter_bubble

inject_css()
st.title("👥 오디언스 분석")

df_raw = load_audience()

with st.spinner("데이터 불러오는 중..."):
    filters = render_sidebar_filters(df_raw, {
        "date_col": "날짜",
        "show_platform": True,
        "show_campaign": True,
    })
    df = apply_filters(df_raw, filters)
    empty_guard(df)

# ── KPI 카드 ────────────────────────────────────────────
avg_stay  = df["체류시간(초)"].mean()
avg_exit  = df["이탈률(%)"].mean()
new_ratio = (df["신규여부"] == "신규").mean() * 100
total_conv = df["전환수"].sum()
total_click = df["클릭수"].sum()
cvr = total_conv / total_click * 100 if total_click else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("평균 체류시간", f"{avg_stay:.0f}초")
c2.metric("평균 이탈률",  f"{avg_exit:.1f}%")
c3.metric("신규 유저 비율", f"{new_ratio:.1f}%")
c4.metric("전환율 (전환/클릭)", f"{cvr:.2f}%")

st.markdown("---")

# ── 연령대 × 성별 히트맵 ────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("연령대 × 성별 전환수")
    pivot_age = (
        df.groupby(["연령대", "성별"])["전환수"].sum()
        .unstack(fill_value=0)
    )
    age_order = ["18-24", "25-34", "35-44", "45-54", "55+"]
    pivot_age = pivot_age.reindex([a for a in age_order if a in pivot_age.index])
    fig_age = heatmap_px(pivot_age, color_scale="Blues")
    fig_age.update_layout(height=300)
    st.plotly_chart(fig_age, use_container_width=True)

with col_r:
    st.subheader("기기별 전환수")
    dev_df = df.groupby("기기")["전환수"].sum().reset_index()
    fig_dev = donut_chart(dev_df, names="기기", values="전환수",
                          color_map={"모바일": "#2563EB", "PC": "#10B981", "태블릿": "#F59E0B"})
    fig_dev.update_layout(height=300)
    st.plotly_chart(fig_dev, use_container_width=True)

# ── 관심사 × 연령대 히트맵 & 관심사 바 ────────────────────
st.markdown("---")
col_l2, col_r2 = st.columns([1.2, 0.8])

with col_l2:
    st.subheader("관심사 × 연령대 전환수")
    pivot_int = (
        df.groupby(["관심사", "연령대"])["전환수"].sum()
        .unstack(fill_value=0)
    )
    age_cols = [a for a in ["18-24", "25-34", "35-44", "45-54", "55+"] if a in pivot_int.columns]
    pivot_int = pivot_int[age_cols]
    fig_int = heatmap_px(pivot_int, color_scale="Blues")
    fig_int.update_layout(height=360)
    st.plotly_chart(fig_int, use_container_width=True)

with col_r2:
    st.subheader("관심사별 전환수 랭킹")
    int_df = (
        df.groupby("관심사")["전환수"].sum().reset_index()
        .sort_values("전환수", ascending=True)
    )
    fig_rank = px.bar(
        int_df, x="전환수", y="관심사", orientation="h",
        color="전환수", color_continuous_scale="Blues",
        text_auto=True,
    )
    apply_layout(fig_rank)
    fig_rank.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(fig_rank, use_container_width=True)

# ── 체류시간 vs 이탈률 산점도 ────────────────────────────
st.markdown("---")
st.subheader("지역별 체류시간 vs 이탈률 (버블크기=전환수)")
scatter_df = (
    df.groupby(["지역", "연령대"])
    .agg(체류시간=("체류시간(초)", "mean"),
         이탈률=("이탈률(%)", "mean"),
         전환수=("전환수", "sum"))
    .reset_index()
)
fig_scat = scatter_bubble(
    scatter_df, x="체류시간", y="이탈률", size="전환수",
    color="연령대", hover_name="지역",
)
fig_scat.update_layout(height=350)
st.plotly_chart(fig_scat, use_container_width=True)

# ── 신규 vs 재방문 ────────────────────────────────────────
st.markdown("---")
st.subheader("신규 vs 재방문 전환율 비교")
nv_df = (
    df.groupby("신규여부")
    .agg(전환수=("전환수", "sum"), 클릭수=("클릭수", "sum"))
    .reset_index()
)
nv_df["전환율(%)"] = nv_df["전환수"] / nv_df["클릭수"] * 100
fig_nv = px.bar(
    nv_df, x="신규여부", y="전환율(%)",
    color="신규여부",
    color_discrete_map={"신규": "#2563EB", "재방문": "#10B981"},
    text_auto=".2f",
)
apply_layout(fig_nv)
fig_nv.update_layout(height=280, showlegend=False)
st.plotly_chart(fig_nv, use_container_width=True)

# ── 다운로드 ──────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 현재 데이터 CSV 다운로드",
    data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="audience_filtered.csv",
    mime="text/csv",
)
