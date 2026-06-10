import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

os.makedirs("c:/pj2/data", exist_ok=True)

np.random.seed(42)
random.seed(42)

# ─── 공통 설정 ───────────────────────────────────────────
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 31)
N_DAYS     = (END_DATE - START_DATE).days + 1
dates      = [START_DATE + timedelta(days=i) for i in range(N_DAYS)]

PLATFORMS   = ["Instagram", "Facebook", "TikTok", "YouTube", "Naver", "KakaoTalk"]
OBJECTIVES  = ["인지도", "트래픽", "전환", "리드수집", "앱설치", "동영상조회"]
AD_FORMATS  = ["이미지", "동영상", "카드뉴스", "스토리", "릴스", "배너"]
INDUSTRIES  = ["뷰티/화장품", "패션/의류", "식품/음료", "전자기기", "여행", "교육", "금융", "게임"]
REGIONS     = ["서울", "경기", "부산", "인천", "대구", "대전", "광주", "제주"]
AGE_GROUPS  = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS     = ["남성", "여성", "전체"]
CAMPAIGNS   = [f"캠페인_{chr(65+i)}" for i in range(20)]   # 캠페인_A ~ 캠페인_T

platform_ctr_base = {
    "Instagram": 0.022, "Facebook": 0.018, "TikTok": 0.031,
    "YouTube": 0.009,   "Naver": 0.015,    "KakaoTalk": 0.020,
}
platform_cvr_base = {
    "Instagram": 0.028, "Facebook": 0.032, "TikTok": 0.019,
    "YouTube": 0.011,   "Naver": 0.041,    "KakaoTalk": 0.035,
}

# ══════════════════════════════════════════════════════════
# 1. SNS 광고 성과 데이터 (메인, 5 000행)
# ══════════════════════════════════════════════════════════
print("생성 중: 01_sns_ad_performance.csv")
rows = 5_000
df_perf = pd.DataFrame({
    "날짜":       np.random.choice(dates, rows),
    "플랫폼":     np.random.choice(PLATFORMS, rows),
    "캠페인명":   np.random.choice(CAMPAIGNS, rows),
    "광고목표":   np.random.choice(OBJECTIVES, rows),
    "광고형식":   np.random.choice(AD_FORMATS, rows),
    "업종":       np.random.choice(INDUSTRIES, rows),
    "지역":       np.random.choice(REGIONS, rows),
    "연령대":     np.random.choice(AGE_GROUPS, rows),
    "성별":       np.random.choice(GENDERS, rows),
})
df_perf["광고비(원)"]  = np.random.randint(50_000, 5_000_000, rows)
df_perf["노출수"]     = (df_perf["광고비(원)"] * np.random.uniform(0.5, 2.0, rows)).astype(int)
df_perf["도달수"]     = (df_perf["노출수"] * np.random.uniform(0.6, 0.95, rows)).astype(int)
ctr_arr              = [platform_ctr_base[p] * np.random.uniform(0.5, 1.8) for p in df_perf["플랫폼"]]
df_perf["클릭수"]     = (df_perf["노출수"] * np.array(ctr_arr)).astype(int).clip(1)
df_perf["CTR(%)"]    = (df_perf["클릭수"] / df_perf["노출수"] * 100).round(2)
df_perf["CPC(원)"]   = (df_perf["광고비(원)"] / df_perf["클릭수"]).round(0).astype(int)
df_perf["CPM(원)"]   = (df_perf["광고비(원)"] / df_perf["노출수"] * 1000).round(0).astype(int)
cvr_arr              = [platform_cvr_base[p] * np.random.uniform(0.4, 2.0) for p in df_perf["플랫폼"]]
df_perf["전환수"]     = (df_perf["클릭수"] * np.array(cvr_arr)).astype(int).clip(0)
df_perf["전환가치(원)"] = df_perf["전환수"] * np.random.randint(5_000, 150_000, rows)
df_perf["ROAS(%)"]   = (df_perf["전환가치(원)"] / df_perf["광고비(원)"] * 100).round(1)
df_perf["좋아요"]     = (df_perf["도달수"] * np.random.uniform(0.01, 0.08, rows)).astype(int)
df_perf["댓글"]      = (df_perf["좋아요"] * np.random.uniform(0.03, 0.15, rows)).astype(int)
df_perf["공유"]      = (df_perf["좋아요"] * np.random.uniform(0.02, 0.10, rows)).astype(int)
df_perf["저장"]      = (df_perf["좋아요"] * np.random.uniform(0.05, 0.20, rows)).astype(int)
df_perf["날짜"] = pd.to_datetime(df_perf["날짜"]).dt.strftime("%Y-%m-%d")
df_perf.sort_values("날짜", inplace=True)
df_perf.to_csv("c:/pj2/data/01_sns_ad_performance.csv", index=False, encoding="utf-8-sig")
print(f"  → {len(df_perf):,}행 저장 완료")

# ══════════════════════════════════════════════════════════
# 2. 캠페인별 예산 및 목표 대비 실적 (500행)
# ══════════════════════════════════════════════════════════
print("생성 중: 02_campaign_budget.csv")
rows2 = 500
months = pd.date_range("2023-01", "2024-12", freq="MS")
df_budget = pd.DataFrame({
    "연월":       np.random.choice([m.strftime("%Y-%m") for m in months], rows2),
    "캠페인명":   np.random.choice(CAMPAIGNS, rows2),
    "플랫폼":     np.random.choice(PLATFORMS, rows2),
    "업종":       np.random.choice(INDUSTRIES, rows2),
})
df_budget["배정예산(원)"]  = np.random.randint(500_000, 30_000_000, rows2)
df_budget["집행예산(원)"]  = (df_budget["배정예산(원)"] * np.random.uniform(0.7, 1.05, rows2)).astype(int)
df_budget["예산소진율(%)"] = (df_budget["집행예산(원)"] / df_budget["배정예산(원)"] * 100).round(1)
df_budget["목표전환수"]    = np.random.randint(50, 2_000, rows2)
df_budget["실제전환수"]    = (df_budget["목표전환수"] * np.random.uniform(0.5, 1.4, rows2)).astype(int)
df_budget["목표달성률(%)"] = (df_budget["실제전환수"] / df_budget["목표전환수"] * 100).round(1)
df_budget["목표CPA(원)"]  = np.random.randint(3_000, 50_000, rows2)
df_budget["실제CPA(원)"]  = (df_budget["집행예산(원)"] / df_budget["실제전환수"].clip(1)).round(0).astype(int)
df_budget["캠페인상태"]    = np.random.choice(["진행중", "종료", "일시중지"], rows2, p=[0.5, 0.3, 0.2])
df_budget.sort_values("연월", inplace=True)
df_budget.to_csv("c:/pj2/data/02_campaign_budget.csv", index=False, encoding="utf-8-sig")
print(f"  → {len(df_budget):,}행 저장 완료")

# ══════════════════════════════════════════════════════════
# 3. 타겟 오디언스 분석 데이터 (3 000행)
# ══════════════════════════════════════════════════════════
print("생성 중: 03_audience_analysis.csv")
rows3 = 3_000
INTERESTS = ["패션", "음식", "여행", "운동/헬스", "게임", "뷰티", "육아", "재테크", "자동차", "반려동물"]
DEVICES   = ["모바일", "PC", "태블릿"]
df_aud = pd.DataFrame({
    "날짜":       np.random.choice([d.strftime("%Y-%m-%d") for d in dates], rows3),
    "플랫폼":     np.random.choice(PLATFORMS, rows3),
    "캠페인명":   np.random.choice(CAMPAIGNS, rows3),
    "연령대":     np.random.choice(AGE_GROUPS, rows3),
    "성별":       np.random.choice(["남성", "여성"], rows3),
    "지역":       np.random.choice(REGIONS, rows3),
    "관심사":     np.random.choice(INTERESTS, rows3),
    "기기":       np.random.choice(DEVICES, rows3, p=[0.65, 0.28, 0.07]),
    "신규여부":   np.random.choice(["신규", "재방문"], rows3, p=[0.4, 0.6]),
})
df_aud["노출수"]        = np.random.randint(100, 50_000, rows3)
df_aud["클릭수"]        = (df_aud["노출수"] * np.random.uniform(0.005, 0.06, rows3)).astype(int).clip(1)
df_aud["전환수"]        = (df_aud["클릭수"] * np.random.uniform(0.01, 0.12, rows3)).astype(int).clip(0)
df_aud["광고비(원)"]    = np.random.randint(10_000, 1_000_000, rows3)
df_aud["체류시간(초)"]  = np.random.randint(5, 300, rows3)
df_aud["페이지뷰"]      = (df_aud["클릭수"] * np.random.uniform(1.0, 4.5, rows3)).astype(int)
df_aud["이탈률(%)"]     = np.random.uniform(20, 85, rows3).round(1)
df_aud.sort_values("날짜", inplace=True)
df_aud.to_csv("c:/pj2/data/03_audience_analysis.csv", index=False, encoding="utf-8-sig")
print(f"  → {len(df_aud):,}행 저장 완료")

# ══════════════════════════════════════════════════════════
# 4. 크리에이티브(소재) 성과 데이터 (2 000행)
# ══════════════════════════════════════════════════════════
print("생성 중: 04_creative_performance.csv")
rows4 = 2_000
COPY_TYPES  = ["혜택강조형", "감성소구형", "정보제공형", "유머형", "긴급성강조형"]
COLOR_TONES = ["밝음", "어두움", "파스텔", "비비드", "모노톤"]
df_cre = pd.DataFrame({
    "날짜":       np.random.choice([d.strftime("%Y-%m-%d") for d in dates], rows4),
    "캠페인명":   np.random.choice(CAMPAIGNS, rows4),
    "플랫폼":     np.random.choice(PLATFORMS, rows4),
    "광고형식":   np.random.choice(AD_FORMATS, rows4),
    "소재유형":   np.random.choice(COPY_TYPES, rows4),
    "색감":       np.random.choice(COLOR_TONES, rows4),
    "해시태그수": np.random.randint(0, 15, rows4),
    "텍스트길이":  np.random.randint(10, 300, rows4),
})
df_cre["동영상길이(초)"] = np.where(
    df_cre["광고형식"].isin(["동영상", "릴스"]),
    np.random.randint(6, 120, rows4), 0
)
df_cre["노출수"]       = np.random.randint(500, 200_000, rows4)
df_cre["클릭수"]       = (df_cre["노출수"] * np.random.uniform(0.005, 0.07, rows4)).astype(int).clip(1)
df_cre["CTR(%)"]      = (df_cre["클릭수"] / df_cre["노출수"] * 100).round(2)
df_cre["좋아요"]       = (df_cre["노출수"] * np.random.uniform(0.005, 0.06, rows4)).astype(int)
df_cre["공유"]         = (df_cre["좋아요"] * np.random.uniform(0.02, 0.12, rows4)).astype(int)
df_cre["광고비(원)"]   = np.random.randint(30_000, 3_000_000, rows4)
df_cre["전환수"]       = (df_cre["클릭수"] * np.random.uniform(0.01, 0.10, rows4)).astype(int).clip(0)
df_cre["소재평점"]     = np.random.uniform(1, 10, rows4).round(1)
df_cre["A/B그룹"]     = np.random.choice(["A", "B", "C"], rows4)
df_cre.sort_values("날짜", inplace=True)
df_cre.to_csv("c:/pj2/data/04_creative_performance.csv", index=False, encoding="utf-8-sig")
print(f"  → {len(df_cre):,}행 저장 완료")

# ══════════════════════════════════════════════════════════
# 5. 경쟁사 벤치마크 데이터 (1 200행)
# ══════════════════════════════════════════════════════════
print("생성 중: 05_competitor_benchmark.csv")
rows5 = 1_200
COMPETITORS = ["자사", "경쟁사A", "경쟁사B", "경쟁사C", "경쟁사D"]
df_bm = pd.DataFrame({
    "연월":       np.random.choice([m.strftime("%Y-%m") for m in months], rows5),
    "업종":       np.random.choice(INDUSTRIES, rows5),
    "플랫폼":     np.random.choice(PLATFORMS, rows5),
    "브랜드":     np.random.choice(COMPETITORS, rows5),
})
df_bm["추정노출수"]      = np.random.randint(10_000, 5_000_000, rows5)
df_bm["추정광고비(원)"]  = np.random.randint(1_000_000, 500_000_000, rows5)
df_bm["추정CTR(%)"]     = np.random.uniform(0.5, 5.0, rows5).round(2)
df_bm["추정전환율(%)"]   = np.random.uniform(0.5, 8.0, rows5).round(2)
df_bm["브랜드언급수"]    = np.random.randint(100, 50_000, rows5)
df_bm["감성점수(긍정%)"] = np.random.uniform(40, 95, rows5).round(1)
df_bm["광고소재수"]      = np.random.randint(1, 50, rows5)
df_bm["공유오브보이스(%)"] = np.random.uniform(1, 40, rows5).round(1)
df_bm.sort_values("연월", inplace=True)
df_bm.to_csv("c:/pj2/data/05_competitor_benchmark.csv", index=False, encoding="utf-8-sig")
print(f"  → {len(df_bm):,}행 저장 완료")

# ══════════════════════════════════════════════════════════
# 완료 요약
# ══════════════════════════════════════════════════════════
total = rows + rows2 + rows3 + rows4 + rows5
print(f"\n✅ 총 {total:,}행 · 5개 파일 생성 완료 → c:/pj2/data/")
for f in sorted(os.listdir("c:/pj2/data")):
    size = os.path.getsize(f"c:/pj2/data/{f}") / 1024
    print(f"  {f}  ({size:.0f} KB)")
