def format_krw(value: float) -> str:
    if value >= 1_0000_0000:
        return f"{value / 1_0000_0000:.1f}억원"
    elif value >= 10_000:
        return f"{value / 10_000:.1f}만원"
    else:
        return f"{value:,.0f}원"


def format_number(value: float) -> str:
    if value >= 10_000:
        return f"{value / 10_000:.1f}만"
    return f"{value:,.0f}"


def format_pct(value: float) -> str:
    return f"{value:.2f}%"


def calc_delta(current: float, previous: float) -> str:
    if previous == 0:
        return None
    rate = (current - previous) / abs(previous) * 100
    sign = "+" if rate >= 0 else ""
    return f"{sign}{rate:.1f}%"


def calc_period_delta(df, value_col: str, date_col: str = "날짜"):
    """날짜 컬럼 기준 최근 30일 vs 이전 30일 델타 계산"""
    import pandas as pd
    if df.empty:
        return 0, 0, None
    max_date = df[date_col].max()
    split = max_date - pd.Timedelta(days=30)
    prev_split = split - pd.Timedelta(days=30)

    cur_val  = df[df[date_col] > split][value_col].sum()
    prev_val = df[(df[date_col] > prev_split) & (df[date_col] <= split)][value_col].sum()
    return cur_val, prev_val, calc_delta(cur_val, prev_val)
