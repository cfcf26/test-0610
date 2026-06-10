import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame, config: dict) -> dict:
    """
    config keys:
      date_col      : str  — 날짜 컬럼명 (None이면 날짜 필터 생략)
      month_col     : str  — 연월_dt 컬럼명 (None이면 생략)
      show_platform : bool
      show_campaign : bool
      show_industry : bool
      show_status   : bool — 캠페인상태
      show_brand    : bool — 브랜드(경쟁사)
      show_region   : bool — 광역시도
    """
    filters = {}

    with st.sidebar:
        st.markdown("## 필터")

        # 날짜 범위
        date_col = config.get("date_col")
        if date_col and date_col in df.columns:
            min_d = df[date_col].min().date()
            max_d = df[date_col].max().date()
            date_range = st.date_input(
                "기간",
                value=(min_d, max_d),
                min_value=min_d,
                max_value=max_d,
            )
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                filters["date_range"] = date_range
            else:
                filters["date_range"] = (min_d, max_d)

        # 연월 범위
        month_col = config.get("month_col")
        if month_col and month_col in df.columns:
            months = sorted(df[month_col].dt.strftime("%Y-%m").unique())
            selected = st.select_slider("연월 범위", options=months, value=(months[0], months[-1]))
            filters["month_range"] = selected

        # 플랫폼
        if config.get("show_platform") and "플랫폼" in df.columns:
            opts = sorted(df["플랫폼"].unique())
            sel = st.multiselect("플랫폼", opts, default=opts)
            filters["platforms"] = sel

        # 캠페인
        if config.get("show_campaign") and "캠페인명" in df.columns:
            opts = sorted(df["캠페인명"].unique())
            sel = st.multiselect("캠페인", opts, default=opts)
            filters["campaigns"] = sel

        # 업종
        if config.get("show_industry") and "업종" in df.columns:
            opts = sorted(df["업종"].unique())
            sel = st.multiselect("업종", opts, default=opts)
            filters["industries"] = sel

        # 캠페인 상태
        if config.get("show_status") and "캠페인상태" in df.columns:
            opts = sorted(df["캠페인상태"].unique())
            sel = st.multiselect("캠페인 상태", opts, default=opts)
            filters["statuses"] = sel

        # 브랜드
        if config.get("show_brand") and "브랜드" in df.columns:
            opts = sorted(df["브랜드"].unique())
            sel = st.multiselect("브랜드", opts, default=opts)
            filters["brands"] = sel

        # 광역시도
        if config.get("show_region") and "광역시도" in df.columns:
            opts = sorted(df["광역시도"].unique())
            sel = st.multiselect("광역시도", opts, default=opts)
            filters["regions"] = sel

    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    result = df.copy()

    if "date_range" in filters:
        s, e = filters["date_range"]
        result = result[result["날짜"].between(pd.Timestamp(s), pd.Timestamp(e))]

    if "month_range" in filters:
        s, e = filters["month_range"]
        result = result[
            (result["연월_dt"].dt.strftime("%Y-%m") >= s) &
            (result["연월_dt"].dt.strftime("%Y-%m") <= e)
        ]

    if "platforms" in filters and filters["platforms"]:
        result = result[result["플랫폼"].isin(filters["platforms"])]

    if "campaigns" in filters and filters["campaigns"]:
        result = result[result["캠페인명"].isin(filters["campaigns"])]

    if "industries" in filters and filters["industries"]:
        result = result[result["업종"].isin(filters["industries"])]

    if "statuses" in filters and filters["statuses"]:
        result = result[result["캠페인상태"].isin(filters["statuses"])]

    if "brands" in filters and filters["brands"]:
        result = result[result["브랜드"].isin(filters["brands"])]

    if "regions" in filters and filters["regions"]:
        result = result[result["광역시도"].isin(filters["regions"])]

    return result


def empty_guard(df: pd.DataFrame):
    if df.empty:
        st.warning("선택한 조건에 맞는 데이터가 없습니다. 필터를 조정해 주세요.")
        st.stop()
