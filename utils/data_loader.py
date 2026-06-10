import pandas as pd
import streamlit as st

DATA_DIR = "data"


@st.cache_data(ttl=3600)
def load_performance() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/01_sns_ad_performance.csv", encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df


@st.cache_data(ttl=3600)
def load_budget() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/02_campaign_budget.csv", encoding="utf-8-sig")
    df["연월_dt"] = pd.to_datetime(df["연월"], format="%Y-%m")
    return df


@st.cache_data(ttl=3600)
def load_audience() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/03_audience_analysis.csv", encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df


@st.cache_data(ttl=3600)
def load_creative() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/04_creative_performance.csv", encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df


@st.cache_data(ttl=3600)
def load_competitor() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/05_competitor_benchmark.csv", encoding="utf-8-sig")
    df["연월_dt"] = pd.to_datetime(df["연월"], format="%Y-%m")
    return df


@st.cache_data(ttl=3600)
def load_region() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/06_access_region.csv", encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df
