import streamlit as st
import plotly.express as px

from utils.data_loader import load_region
from utils.filters import render_sidebar_filters, apply_filters, empty_guard
from utils.styles import PLATFORM_COLORS, apply_layout, inject_css
from utils.charts import donut_chart

inject_css()
st.title("🗺️ 지역별 유입 분석")

df_raw = load_region()

with st.spinner("데이터 불러오는 중..."):
    filters = render_sidebar_filters(df_raw, {
        "date_col": "날짜",
        "show_platform": True,
        "show_campaign": True,
        "show_region": True,
    })
    df = apply_filters(df_raw, filters)
    empty_guard(df)

# ── KPI 카드 ────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("총 세션수",     f"{df['세션수'].sum():,}")
c2.metric("총 전환수",     f"{df['전환수'].sum():,}")
c3.metric("평균 이탈률",   f"{df['이탈률(%)'].mean():.1f}%")
c4.metric("평균 체류시간", f"{df['평균체류(초)'].mean():.0f}초")

st.markdown("---")

# ── 광역시도별 성과 바 랭킹 ────────────────────────────────
metric_choice = st.radio(
    "표시 지표",
    ["전환수", "세션수", "광고비(원)"],
    horizontal=True,
)

region_agg = (
    df.groupby("광역시도")
    .agg(전환수=("전환수", "sum"),
         세션수=("세션수", "sum"),
         광고비=("광고비(원)", "sum"),
         이탈률=("이탈률(%)", "mean"),
         체류시간=("평균체류(초)", "mean"))
    .reset_index()
    .rename(columns={"광고비": "광고비(원)"})
    .sort_values(metric_choice, ascending=True)
)

fig_reg = px.bar(
    region_agg, x=metric_choice, y="광역시도",
    orientation="h",
    color=metric_choice, color_continuous_scale="Blues",
    text_auto=True,
    title=f"광역시도별 {metric_choice}",
)
apply_layout(fig_reg)
fig_reg.update_layout(height=350, coloraxis_showscale=False)
st.plotly_chart(fig_reg, use_container_width=True)

# ── 유입채널 파이 + 기기/OS 트리맵 ────────────────────────
st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("유입채널별 전환수")
    ch_df = df.groupby("유입채널")["전환수"].sum().reset_index()
    fig_ch = donut_chart(ch_df, names="유입채널", values="전환수")
    fig_ch.update_layout(height=320)
    st.plotly_chart(fig_ch, use_container_width=True)

with col_r:
    st.subheader("기기 / OS 세션 트리맵")
    tree_df = (
        df.groupby(["기기", "OS"])["세션수"].sum().reset_index()
    )
    fig_tree = px.treemap(
        tree_df, path=["기기", "OS"], values="세션수",
        color="세션수", color_continuous_scale="Blues",
    )
    fig_tree.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Malgun Gothic, sans-serif", color="#F1F5F9"),
        height=320,
    )
    st.plotly_chart(fig_tree, use_container_width=True)

# ── 브라우저별 세션 ────────────────────────────────────────
st.markdown("---")
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("브라우저별 세션수")
    brow_df = df.groupby("브라우저")["세션수"].sum().reset_index().sort_values("세션수", ascending=False)
    fig_brow = px.bar(
        brow_df, x="브라우저", y="세션수",
        color="세션수", color_continuous_scale="Blues",
        text_auto=True,
    )
    apply_layout(fig_brow)
    fig_brow.update_layout(height=300, coloraxis_showscale=False)
    st.plotly_chart(fig_brow, use_container_width=True)

with col_r2:
    st.subheader("유입채널별 이탈률 비교")
    exit_df = df.groupby("유입채널")["이탈률(%)"].mean().reset_index().sort_values("이탈률(%)")
    fig_exit = px.bar(
        exit_df, x="이탈률(%)", y="유입채널", orientation="h",
        color="이탈률(%)", color_continuous_scale="Reds",
        text_auto=".1f",
    )
    apply_layout(fig_exit)
    fig_exit.update_layout(height=300, coloraxis_showscale=False)
    st.plotly_chart(fig_exit, use_container_width=True)

# ── 시군구 드릴다운 ────────────────────────────────────────
st.markdown("---")
st.subheader("시군구 드릴다운")
selected_region = st.selectbox("광역시도 선택", sorted(df["광역시도"].unique()))
drill = (
    df[df["광역시도"] == selected_region]
    .groupby("시군구")
    .agg(세션수=("세션수", "sum"),
         사용자수=("사용자수", "sum"),
         전환수=("전환수", "sum"),
         광고비=("광고비(원)", "sum"),
         평균체류=("평균체류(초)", "mean"),
         이탈률=("이탈률(%)", "mean"))
    .reset_index()
    .sort_values("전환수", ascending=False)
)
st.dataframe(
    drill.style.format({
        "광고비": "{:,.0f}원",
        "평균체류": "{:.0f}초",
        "이탈률": "{:.1f}%",
    }).background_gradient(subset=["전환수"], cmap="Blues"),
    use_container_width=True,
    height=280,
)

# ── 다운로드 ──────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 현재 데이터 CSV 다운로드",
    data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="region_filtered.csv",
    mime="text/csv",
)
