import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_creative
from utils.filters import render_sidebar_filters, apply_filters, empty_guard
from utils.styles import apply_layout, inject_css
from utils.charts import heatmap_px, scatter_bubble

inject_css()
st.title("🎨 소재 성과 분석")

df_raw = load_creative()

with st.spinner("데이터 불러오는 중..."):
    filters = render_sidebar_filters(df_raw, {
        "date_col": "날짜",
        "show_platform": True,
        "show_campaign": True,
    })
    df = apply_filters(df_raw, filters)
    empty_guard(df)

# ── KPI 카드 ────────────────────────────────────────────
best_type = df.groupby("소재유형")["CTR(%)"].mean().idxmax()
avg_score = df["소재평점"].mean()
best_format = df.groupby("광고형식")["전환수"].sum().idxmax()

c1, c2, c3 = st.columns(3)
c1.metric("최고 CTR 소재유형", best_type)
c2.metric("평균 소재 평점",    f"{avg_score:.1f} / 10")
c3.metric("최고 전환 광고형식", best_format)

st.markdown("---")

# ── A/B 테스트 결과 ────────────────────────────────────────
st.subheader("A/B/C 그룹 성과 비교")
ab_df = (
    df.groupby("A/B그룹")
    .agg(CTR=("CTR(%)", "mean"), 전환수=("전환수", "sum"), 광고비=("광고비(원)", "sum"))
    .reset_index()
)
ab_melt = ab_df.melt(id_vars="A/B그룹", value_vars=["CTR", "전환수"],
                      var_name="지표", value_name="값")

col_ab1, col_ab2 = st.columns(2)
with col_ab1:
    fig_ab_ctr = px.bar(
        ab_df, x="A/B그룹", y="CTR",
        color="A/B그룹", color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B"],
        text_auto=".2f", title="그룹별 평균 CTR(%)",
    )
    apply_layout(fig_ab_ctr)
    fig_ab_ctr.update_layout(height=280, showlegend=False)
    st.plotly_chart(fig_ab_ctr, use_container_width=True)

with col_ab2:
    fig_ab_conv = px.bar(
        ab_df, x="A/B그룹", y="전환수",
        color="A/B그룹", color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B"],
        text_auto=True, title="그룹별 총 전환수",
    )
    apply_layout(fig_ab_conv)
    fig_ab_conv.update_layout(height=280, showlegend=False)
    st.plotly_chart(fig_ab_conv, use_container_width=True)

# ── 소재 속성별 성과 ────────────────────────────────────────
st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("소재유형별 CTR & 전환수")
    type_df = (
        df.groupby("소재유형")
        .agg(CTR=("CTR(%)", "mean"), 전환수=("전환수", "sum"))
        .reset_index()
        .sort_values("CTR", ascending=False)
    )
    fig_type = go.Figure()
    fig_type.add_trace(go.Bar(
        x=type_df["소재유형"], y=type_df["CTR"],
        name="평균 CTR(%)", marker_color="#2563EB", yaxis="y1",
    ))
    fig_type.add_trace(go.Scatter(
        x=type_df["소재유형"], y=type_df["전환수"],
        name="전환수", line=dict(color="#F59E0B"), mode="lines+markers", yaxis="y2",
    ))
    fig_type.update_layout(
        yaxis=dict(title="CTR(%)", gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
        yaxis2=dict(title="전환수", overlaying="y", side="right", tickfont=dict(color="#94A3B8")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Malgun Gothic, sans-serif", color="#F1F5F9"),
        xaxis=dict(tickfont=dict(color="#94A3B8")),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F1F5F9")),
        height=320,
    )
    st.plotly_chart(fig_type, use_container_width=True)

with col_r:
    st.subheader("색감별 CTR 분포")
    fig_box = px.box(
        df, x="색감", y="CTR(%)",
        color="색감",
        color_discrete_sequence=["#2563EB", "#E1306C", "#F59E0B", "#10B981", "#8B5CF6"],
    )
    apply_layout(fig_box)
    fig_box.update_layout(height=320, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ── 플랫폼 × 광고형식 히트맵 ────────────────────────────────
st.markdown("---")
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("플랫폼 × 광고형식 평균 CTR")
    pivot_fmt = (
        df.groupby(["플랫폼", "광고형식"])["CTR(%)"].mean()
        .unstack(fill_value=0)
        .round(2)
    )
    fig_fmt = heatmap_px(pivot_fmt, color_scale="Blues")
    fig_fmt.update_layout(height=330)
    st.plotly_chart(fig_fmt, use_container_width=True)

with col_r2:
    st.subheader("소재평점 vs 실제 CTR")
    fig_sc = scatter_bubble(
        df, x="소재평점", y="CTR(%)", size="전환수",
        color="소재유형", hover_name="캠페인명",
        title="평점이 높을수록 CTR도 높은가?",
    )
    fig_sc.update_layout(height=330)
    st.plotly_chart(fig_sc, use_container_width=True)

# ── 상관관계 히트맵 ────────────────────────────────────────
st.markdown("---")
st.subheader("소재 속성 vs 성과 상관관계")
corr_cols = ["해시태그수", "텍스트길이", "동영상길이(초)", "소재평점", "CTR(%)", "전환수"]
corr_df = df[corr_cols].corr().round(2)
fig_corr = heatmap_px(corr_df, color_scale="RdBu")
fig_corr.update_layout(height=350)
st.plotly_chart(fig_corr, use_container_width=True)

# ── 다운로드 ──────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 현재 데이터 CSV 다운로드",
    data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    file_name="creative_filtered.csv",
    mime="text/csv",
)
