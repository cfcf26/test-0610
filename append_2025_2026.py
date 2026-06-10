import pandas as pd
import numpy as np
import os

np.random.seed(99)

START_DATE = "2025-01-01"
END_DATE   = "2026-06-10"   # 오늘까지
dates_new  = pd.date_range(START_DATE, END_DATE)

PLATFORMS   = ["Instagram", "Facebook", "TikTok", "YouTube", "Naver", "KakaoTalk"]
OBJECTIVES  = ["인지도", "트래픽", "전환", "리드수집", "앱설치", "동영상조회"]
AD_FORMATS  = ["이미지", "동영상", "카드뉴스", "스토리", "릴스", "배너"]
INDUSTRIES  = ["뷰티/화장품", "패션/의류", "식품/음료", "전자기기", "여행", "교육", "금융", "게임"]
REGIONS     = ["서울", "경기", "부산", "인천", "대구", "대전", "광주", "제주"]
AGE_GROUPS  = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS     = ["남성", "여성", "전체"]
CAMPAIGNS   = [f"캠페인_{chr(65+i)}" for i in range(20)]

# 25~26년 플랫폼 트렌드: TikTok/릴스 성장, Facebook 하락
platform_ctr_base = {
    "Instagram": 0.026, "Facebook": 0.015, "TikTok": 0.038,
    "YouTube": 0.011,   "Naver": 0.016,    "KakaoTalk": 0.021,
}
platform_cvr_base = {
    "Instagram": 0.031, "Facebook": 0.029, "TikTok": 0.023,
    "YouTube": 0.013,   "Naver": 0.043,    "KakaoTalk": 0.036,
}

DATA_DIR = "c:/pj2/data"

# ── 1. SNS 광고 성과 (+3 000행) ──────────────────────────
print("추가 중: 01_sns_ad_performance.csv")
r = 3_000
df = pd.DataFrame({
    "날짜":     pd.to_datetime(np.random.choice(dates_new, r)).strftime("%Y-%m-%d"),
    "플랫폼":   np.random.choice(PLATFORMS, r),
    "캠페인명": np.random.choice(CAMPAIGNS, r),
    "광고목표": np.random.choice(OBJECTIVES, r),
    "광고형식": np.random.choice(AD_FORMATS, r),
    "업종":     np.random.choice(INDUSTRIES, r),
    "지역":     np.random.choice(REGIONS, r),
    "연령대":   np.random.choice(AGE_GROUPS, r),
    "성별":     np.random.choice(GENDERS, r),
})
# 26년 광고비 소폭 상승 반영
df["광고비(원)"]    = np.random.randint(60_000, 6_000_000, r)
df["노출수"]        = (df["광고비(원)"] * np.random.uniform(0.5, 2.2, r)).astype(int)
df["도달수"]        = (df["노출수"] * np.random.uniform(0.6, 0.95, r)).astype(int)
ctr = [platform_ctr_base[p] * np.random.uniform(0.5, 1.8) for p in df["플랫폼"]]
df["클릭수"]        = (df["노출수"] * np.array(ctr)).astype(int).clip(1)
df["CTR(%)"]       = (df["클릭수"] / df["노출수"] * 100).round(2)
df["CPC(원)"]      = (df["광고비(원)"] / df["클릭수"]).round(0).astype(int)
df["CPM(원)"]      = (df["광고비(원)"] / df["노출수"] * 1000).round(0).astype(int)
cvr = [platform_cvr_base[p] * np.random.uniform(0.4, 2.0) for p in df["플랫폼"]]
df["전환수"]        = (df["클릭수"] * np.array(cvr)).astype(int).clip(0)
df["전환가치(원)"]  = df["전환수"] * np.random.randint(5_000, 180_000, r)
df["ROAS(%)"]      = (df["전환가치(원)"] / df["광고비(원)"] * 100).round(1)
df["좋아요"]        = (df["도달수"] * np.random.uniform(0.01, 0.09, r)).astype(int)
df["댓글"]          = (df["좋아요"] * np.random.uniform(0.03, 0.15, r)).astype(int)
df["공유"]          = (df["좋아요"] * np.random.uniform(0.02, 0.10, r)).astype(int)
df["저장"]          = (df["좋아요"] * np.random.uniform(0.05, 0.22, r)).astype(int)

orig = pd.read_csv(f"{DATA_DIR}/01_sns_ad_performance.csv", encoding="utf-8-sig")
orig = orig[orig["날짜"] < "2025-01-01"]  # 기존 2025+ 데이터 제거 (멱등성)
merged = pd.concat([orig, df], ignore_index=True).sort_values("날짜")
merged.to_csv(f"{DATA_DIR}/01_sns_ad_performance.csv", index=False, encoding="utf-8-sig")
print(f"  → 기존 {len(orig):,}행 + 추가 {r:,}행 = 총 {len(merged):,}행")

# ── 2. 캠페인 예산 (+300행) ──────────────────────────────
print("추가 중: 02_campaign_budget.csv")
r2 = 300
months_new = pd.date_range("2025-01", "2026-06", freq="MS")
df2 = pd.DataFrame({
    "연월":     np.random.choice([m.strftime("%Y-%m") for m in months_new], r2),
    "캠페인명": np.random.choice(CAMPAIGNS, r2),
    "플랫폼":   np.random.choice(PLATFORMS, r2),
    "업종":     np.random.choice(INDUSTRIES, r2),
})
df2["배정예산(원)"]   = np.random.randint(700_000, 40_000_000, r2)
df2["집행예산(원)"]   = (df2["배정예산(원)"] * np.random.uniform(0.7, 1.05, r2)).astype(int)
df2["예산소진율(%)"]  = (df2["집행예산(원)"] / df2["배정예산(원)"] * 100).round(1)
df2["목표전환수"]     = np.random.randint(50, 2_500, r2)
df2["실제전환수"]     = (df2["목표전환수"] * np.random.uniform(0.5, 1.5, r2)).astype(int)
df2["목표달성률(%)"]  = (df2["실제전환수"] / df2["목표전환수"] * 100).round(1)
df2["목표CPA(원)"]   = np.random.randint(3_000, 55_000, r2)
df2["실제CPA(원)"]   = (df2["집행예산(원)"] / df2["실제전환수"].clip(1)).round(0).astype(int)
df2["캠페인상태"]     = np.random.choice(["진행중", "종료", "일시중지"], r2, p=[0.6, 0.25, 0.15])

orig2 = pd.read_csv(f"{DATA_DIR}/02_campaign_budget.csv", encoding="utf-8-sig")
orig2 = orig2[orig2["연월"] < "2025-01"]
merged2 = pd.concat([orig2, df2], ignore_index=True).sort_values("연월")
merged2.to_csv(f"{DATA_DIR}/02_campaign_budget.csv", index=False, encoding="utf-8-sig")
print(f"  → 기존 {len(orig2):,}행 + 추가 {r2:,}행 = 총 {len(merged2):,}행")

# ── 3. 오디언스 분석 (+2 000행) ─────────────────────────
print("추가 중: 03_audience_analysis.csv")
r3 = 2_000
INTERESTS = ["패션", "음식", "여행", "운동/헬스", "게임", "뷰티", "육아", "재테크", "자동차", "반려동물"]
DEVICES   = ["모바일", "PC", "태블릿"]
df3 = pd.DataFrame({
    "날짜":     pd.to_datetime(np.random.choice(dates_new, r3)).strftime("%Y-%m-%d"),
    "플랫폼":   np.random.choice(PLATFORMS, r3),
    "캠페인명": np.random.choice(CAMPAIGNS, r3),
    "연령대":   np.random.choice(AGE_GROUPS, r3),
    "성별":     np.random.choice(["남성", "여성"], r3),
    "지역":     np.random.choice(REGIONS, r3),
    "관심사":   np.random.choice(INTERESTS, r3),
    "기기":     np.random.choice(DEVICES, r3, p=[0.70, 0.24, 0.06]),  # 모바일 비중 증가
    "신규여부": np.random.choice(["신규", "재방문"], r3, p=[0.38, 0.62]),
})
df3["노출수"]       = np.random.randint(100, 60_000, r3)
df3["클릭수"]       = (df3["노출수"] * np.random.uniform(0.005, 0.07, r3)).astype(int).clip(1)
df3["전환수"]       = (df3["클릭수"] * np.random.uniform(0.01, 0.13, r3)).astype(int).clip(0)
df3["광고비(원)"]   = np.random.randint(10_000, 1_200_000, r3)
df3["체류시간(초)"] = np.random.randint(5, 320, r3)
df3["페이지뷰"]     = (df3["클릭수"] * np.random.uniform(1.0, 5.0, r3)).astype(int)
df3["이탈률(%)"]    = np.random.uniform(18, 83, r3).round(1)

orig3 = pd.read_csv(f"{DATA_DIR}/03_audience_analysis.csv", encoding="utf-8-sig")
orig3 = orig3[orig3["날짜"] < "2025-01-01"]
merged3 = pd.concat([orig3, df3], ignore_index=True).sort_values("날짜")
merged3.to_csv(f"{DATA_DIR}/03_audience_analysis.csv", index=False, encoding="utf-8-sig")
print(f"  → 기존 {len(orig3):,}행 + 추가 {r3:,}행 = 총 {len(merged3):,}행")

# ── 4. 크리에이티브 성과 (+1 500행) ─────────────────────
print("추가 중: 04_creative_performance.csv")
r4 = 1_500
COPY_TYPES  = ["혜택강조형", "감성소구형", "정보제공형", "유머형", "긴급성강조형"]
COLOR_TONES = ["밝음", "어두움", "파스텔", "비비드", "모노톤"]
df4 = pd.DataFrame({
    "날짜":     pd.to_datetime(np.random.choice(dates_new, r4)).strftime("%Y-%m-%d"),
    "캠페인명": np.random.choice(CAMPAIGNS, r4),
    "플랫폼":   np.random.choice(PLATFORMS, r4),
    "광고형식": np.random.choice(AD_FORMATS, r4),
    "소재유형": np.random.choice(COPY_TYPES, r4),
    "색감":     np.random.choice(COLOR_TONES, r4),
    "해시태그수": np.random.randint(0, 20, r4),
    "텍스트길이": np.random.randint(10, 300, r4),
})
df4["동영상길이(초)"] = np.where(
    df4["광고형식"].isin(["동영상", "릴스"]),
    np.random.randint(6, 90, r4), 0   # 숏폼 트렌드 반영 (최대 90초)
)
df4["노출수"]      = np.random.randint(500, 250_000, r4)
df4["클릭수"]      = (df4["노출수"] * np.random.uniform(0.005, 0.08, r4)).astype(int).clip(1)
df4["CTR(%)"]     = (df4["클릭수"] / df4["노출수"] * 100).round(2)
df4["좋아요"]      = (df4["노출수"] * np.random.uniform(0.005, 0.07, r4)).astype(int)
df4["공유"]        = (df4["좋아요"] * np.random.uniform(0.02, 0.13, r4)).astype(int)
df4["광고비(원)"]  = np.random.randint(30_000, 4_000_000, r4)
df4["전환수"]      = (df4["클릭수"] * np.random.uniform(0.01, 0.12, r4)).astype(int).clip(0)
df4["소재평점"]    = np.random.uniform(1, 10, r4).round(1)
df4["A/B그룹"]    = np.random.choice(["A", "B", "C"], r4)

orig4 = pd.read_csv(f"{DATA_DIR}/04_creative_performance.csv", encoding="utf-8-sig")
orig4 = orig4[orig4["날짜"] < "2025-01-01"]
merged4 = pd.concat([orig4, df4], ignore_index=True).sort_values("날짜")
merged4.to_csv(f"{DATA_DIR}/04_creative_performance.csv", index=False, encoding="utf-8-sig")
print(f"  → 기존 {len(orig4):,}행 + 추가 {r4:,}행 = 총 {len(merged4):,}행")

# ── 5. 경쟁사 벤치마크 (+600행) ─────────────────────────
print("추가 중: 05_competitor_benchmark.csv")
r5 = 600
COMPETITORS = ["자사", "경쟁사A", "경쟁사B", "경쟁사C", "경쟁사D"]
df5 = pd.DataFrame({
    "연월":   np.random.choice([m.strftime("%Y-%m") for m in months_new], r5),
    "업종":   np.random.choice(INDUSTRIES, r5),
    "플랫폼": np.random.choice(PLATFORMS, r5),
    "브랜드": np.random.choice(COMPETITORS, r5),
})
df5["추정노출수"]       = np.random.randint(10_000, 7_000_000, r5)
df5["추정광고비(원)"]   = np.random.randint(1_000_000, 600_000_000, r5)
df5["추정CTR(%)"]      = np.random.uniform(0.5, 6.0, r5).round(2)
df5["추정전환율(%)"]    = np.random.uniform(0.5, 9.0, r5).round(2)
df5["브랜드언급수"]     = np.random.randint(100, 70_000, r5)
df5["감성점수(긍정%)"]  = np.random.uniform(40, 97, r5).round(1)
df5["광고소재수"]       = np.random.randint(1, 60, r5)
df5["공유오브보이스(%)"] = np.random.uniform(1, 45, r5).round(1)

orig5 = pd.read_csv(f"{DATA_DIR}/05_competitor_benchmark.csv", encoding="utf-8-sig")
orig5 = orig5[orig5["연월"] < "2025-01"]
merged5 = pd.concat([orig5, df5], ignore_index=True).sort_values("연월")
merged5.to_csv(f"{DATA_DIR}/05_competitor_benchmark.csv", index=False, encoding="utf-8-sig")
print(f"  → 기존 {len(orig5):,}행 + 추가 {r5:,}행 = 총 {len(merged5):,}행")

# ── 6. 접속 지역 데이터 (신규 파일, 4 000행 / 2023~2026) ──
print("생성 중: 06_access_region.csv")
r6 = 4_000
all_dates = pd.date_range("2023-01-01", "2026-06-10")
CITIES = {
    "서울":  ["강남구","서초구","마포구","종로구","송파구","강서구","노원구","영등포구"],
    "경기":  ["수원시","성남시","고양시","용인시","부천시","안산시","화성시","남양주시"],
    "부산":  ["해운대구","수영구","사상구","북구","동래구"],
    "인천":  ["연수구","남동구","부평구","서구"],
    "대구":  ["수성구","달서구","중구","북구"],
    "대전":  ["유성구","서구","중구"],
    "광주":  ["서구","북구","광산구"],
    "제주":  ["제주시","서귀포시"],
}
DEVICES_NEW   = ["모바일", "PC", "태블릿"]
OS_LIST       = ["Android", "iOS", "Windows", "macOS"]
BROWSER_LIST  = ["Chrome", "Safari", "Samsung Internet", "Edge", "Naver앱"]
CHANNEL_LIST  = ["SNS광고", "검색광고", "자연검색", "직접접속", "이메일", "추천링크"]

region_rows = []
for _ in range(r6):
    region = np.random.choice(REGIONS)
    city   = np.random.choice(CITIES[region])
    region_rows.append({"광역시도": region, "시군구": city})

df6 = pd.DataFrame(region_rows)
df6["날짜"]        = pd.to_datetime(np.random.choice(all_dates, r6)).strftime("%Y-%m-%d")
df6["플랫폼"]      = np.random.choice(PLATFORMS, r6)
df6["캠페인명"]    = np.random.choice(CAMPAIGNS, r6)
df6["유입채널"]    = np.random.choice(CHANNEL_LIST, r6, p=[0.35,0.25,0.18,0.10,0.07,0.05])
df6["기기"]        = np.random.choice(DEVICES_NEW, r6, p=[0.68, 0.25, 0.07])
df6["OS"]          = np.random.choice(OS_LIST, r6, p=[0.42, 0.30, 0.20, 0.08])
df6["브라우저"]    = np.random.choice(BROWSER_LIST, r6, p=[0.40,0.25,0.15,0.12,0.08])
df6["세션수"]      = np.random.randint(10, 5_000, r6)
df6["사용자수"]    = (df6["세션수"] * np.random.uniform(0.6, 0.95, r6)).astype(int).clip(1)
df6["페이지뷰"]    = (df6["세션수"] * np.random.uniform(1.5, 6.0, r6)).astype(int)
df6["평균체류(초)"] = np.random.randint(10, 400, r6)
df6["이탈률(%)"]   = np.random.uniform(15, 88, r6).round(1)
df6["전환수"]      = (df6["사용자수"] * np.random.uniform(0.005, 0.12, r6)).astype(int).clip(0)
df6["광고비(원)"]  = np.random.randint(5_000, 2_000_000, r6)
df6.sort_values("날짜", inplace=True)
df6.to_csv(f"{DATA_DIR}/06_access_region.csv", index=False, encoding="utf-8-sig")
print(f"  → {len(df6):,}행 저장 완료")

# ── 완료 요약 ────────────────────────────────────────────
total_added = r + r2 + r3 + r4 + r5
print(f"\n총 {total_added:,}행 추가 완료 (2025-01-01 ~ 2026-06-10)")
print(f"{'파일명':<40} {'크기(KB)':>8}")
print("-" * 50)
for f in sorted(os.listdir(DATA_DIR)):
    size = os.path.getsize(f"{DATA_DIR}/{f}") / 1024
    print(f"  {f:<38} {size:>7.0f} KB")
