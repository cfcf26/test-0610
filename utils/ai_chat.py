"""Gemini API 기반 대시보드 AI 대화 헬퍼."""
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from utils.data_loader import (
    load_performance,
    load_budget,
    load_audience,
    load_creative,
    load_competitor,
    load_region,
)

load_dotenv()


def get_api_key() -> str | None:
    """.env 의 GEMINI_API_KEY 또는 Streamlit secrets 에서 키를 읽는다."""
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip() and "여기에" not in key:
        return key.strip()
    # 배포 환경 대비: st.secrets 도 지원
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"


@st.cache_data(ttl=3600, show_spinner=False)
def build_data_context() -> str:
    """대시보드 데이터셋들을 집계해 모델에 줄 텍스트 컨텍스트를 만든다.

    원본 행을 그대로 넣으면 토큰이 폭발하므로, 핵심 지표를 집계한 요약만 전달한다.
    """
    parts: list[str] = []

    # 1. 광고 성과
    try:
        perf = load_performance()
        d0, d1 = perf["날짜"].min().date(), perf["날짜"].max().date()
        parts.append(
            "[광고 성과 (01_sns_ad_performance)]\n"
            f"- 기간: {d0} ~ {d1}, 총 {len(perf):,}행\n"
            f"- 총 광고비: {perf['광고비(원)'].sum():,.0f}원, "
            f"총 전환수: {perf['전환수'].sum():,.0f}, "
            f"평균 ROAS: {perf['ROAS(%)'].mean():.1f}%, "
            f"평균 CTR: {perf['CTR(%)'].mean():.2f}%\n"
            "- 플랫폼별 광고비/ROAS:\n"
            + perf.groupby("플랫폼").agg(
                광고비=("광고비(원)", "sum"),
                전환수=("전환수", "sum"),
                평균ROAS=("ROAS(%)", "mean"),
                평균CTR=("CTR(%)", "mean"),
            ).round(1).to_string()
        )
    except Exception as e:
        parts.append(f"[광고 성과] 로드 실패: {e}")

    # 2. 캠페인 예산
    try:
        bud = load_budget()
        parts.append(
            "\n[캠페인 예산 (02_campaign_budget)]\n"
            f"- 총 배정예산: {bud['배정예산(원)'].sum():,.0f}원, "
            f"총 집행예산: {bud['집행예산(원)'].sum():,.0f}원, "
            f"평균 예산소진율: {bud['예산소진율(%)'].mean():.1f}%, "
            f"평균 목표달성률: {bud['목표달성률(%)'].mean():.1f}%\n"
            "- 캠페인 상태 분포: "
            + bud["캠페인상태"].value_counts().to_dict().__str__()
        )
    except Exception as e:
        parts.append(f"[캠페인 예산] 로드 실패: {e}")

    # 3. 오디언스
    try:
        aud = load_audience()
        parts.append(
            "\n[오디언스 분석 (03_audience_analysis)]\n"
            "- 연령대별 전환수:\n"
            + aud.groupby("연령대")["전환수"].sum().sort_values(ascending=False).to_string()
            + "\n- 기기별 전환수: "
            + aud.groupby("기기")["전환수"].sum().to_dict().__str__()
            + f"\n- 평균 이탈률: {aud['이탈률(%)'].mean():.1f}%, "
            f"평균 체류시간: {aud['체류시간(초)'].mean():.0f}초"
        )
    except Exception as e:
        parts.append(f"[오디언스] 로드 실패: {e}")

    # 4. 소재 성과
    try:
        cre = load_creative()
        parts.append(
            "\n[소재 성과 (04_creative_performance)]\n"
            "- 소재유형별 평균 CTR / 평점:\n"
            + cre.groupby("소재유형").agg(
                평균CTR=("CTR(%)", "mean"),
                평균소재평점=("소재평점", "mean"),
                전환수=("전환수", "sum"),
            ).round(2).to_string()
        )
    except Exception as e:
        parts.append(f"[소재 성과] 로드 실패: {e}")

    # 5. 경쟁사 벤치마크
    try:
        comp = load_competitor()
        parts.append(
            "\n[경쟁사 벤치마크 (05_competitor_benchmark)]\n"
            "- 브랜드별 평균 추정 CTR / 공유오브보이스(SOV):\n"
            + comp.groupby("브랜드").agg(
                평균추정CTR=("추정CTR(%)", "mean"),
                평균SOV=("공유오브보이스(%)", "mean"),
                평균감성점수=("감성점수(긍정%)", "mean"),
            ).round(2).to_string()
        )
    except Exception as e:
        parts.append(f"[경쟁사] 로드 실패: {e}")

    # 6. 지역별 유입
    try:
        reg = load_region()
        parts.append(
            "\n[지역별 유입 (06_access_region)]\n"
            "- 광역시도별 세션수 TOP10:\n"
            + reg.groupby("광역시도")["세션수"].sum().sort_values(ascending=False).head(10).to_string()
            + "\n- 유입채널별 전환수: "
            + reg.groupby("유입채널")["전환수"].sum().to_dict().__str__()
        )
    except Exception as e:
        parts.append(f"[지역] 로드 실패: {e}")

    return "\n".join(parts)


SYSTEM_PROMPT = """당신은 마케팅 인사이트 대시보드의 AI 분석 어시스턴트입니다.
아래 제공되는 '대시보드 데이터 요약'을 근거로 사용자의 질문에 한국어로 답하세요.

규칙:
- 반드시 제공된 데이터 요약에 근거해 답하고, 수치를 인용할 때는 구체적인 숫자를 제시하세요.
- 데이터에 없는 내용은 추측하지 말고 "제공된 데이터로는 확인할 수 없습니다"라고 답하세요.
- 마케터가 실무에 활용할 수 있도록 간결하고 실행 가능한 인사이트를 제시하세요.
- 표나 목록이 가독성에 도움이 되면 적극 활용하세요.

[대시보드 데이터 요약]
{context}
"""


def ask_gemini(question: str, history: list[dict]) -> str:
    """질문과 이전 대화 기록을 받아 Gemini 응답 텍스트를 반환한다."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY가 설정되지 않았습니다. .env 파일에 키를 입력하세요."
        )

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    context = build_data_context()
    model = genai.GenerativeModel(
        get_model_name(),
        system_instruction=SYSTEM_PROMPT.format(context=context),
    )

    # 이전 대화(현재 질문 제외)를 Gemini 형식으로 변환
    gemini_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=gemini_history)
    resp = chat.send_message(question)
    return resp.text
