# Samsung Stock Fluctuation Monitor | 삼성전자 주가 변동 자동 모니터링

> **Type:** Automated Daily Email Report | **유형:** 자동化 일일 이메일 리포트
> **Schedule:** Daily 8:00 AM KST | **스케줄:** 매일 오전 8시 (한국 시간)
> **Data Source:** Yahoo Finance (`005930.KS`) | **데이터 출처:** 야후 파이낸스

---

## Purpose | 프로젝트 목적

**EN:**
In early 2026, Samsung Electronics entered a period of heightened volatility driven by global trade tensions, AI semiconductor demand shifts, and macroeconomic uncertainty. The goal of this project is to answer one daily question without manually checking charts:

> *"Is Samsung's recent price movement within the normal statistical range — or has something changed?"*

Instead of building a dashboard that requires active monitoring, this project delivers a fully automated email report every morning, so you can make an informed decision from your inbox.

**KR:**
2026년 초 삼성전자는 글로벌 무역 긴장, AI 반도체 수요 변화, 거시경제 불확실성으로 격변기에 진입했습니다. 이 프로젝트의 목표는 매일 차트를 확인하지 않고도 하나의 질문에 답하는 것입니다:

> *"최근 삼성전자의 주가 움직임이 통계적 정상 범위 안에 있는가, 아니면 무언가 달라졌는가?"*

직접 모니터링이 필요한 대시보드 대신, 매일 아침 자동으로 이메일 리포트를 수신하여 메일함에서 바로 판단할 수 있습니다.

---

## System Architecture | 시스템 구조

```
Yahoo Finance API
      ↓
samsung_analysis.py  (분석 + 이메일 생성)
      ↓
GitHub Actions  (매일 오전 8시 KST 자동 실행)
      ↓
Gmail SMTP  →  📧 다니엘님의 메일함
```

| Component | Tool | Role | 역할 |
|-----------|------|------|------|
| Data Source | `yfinance` | Pull daily Samsung & US chip stock prices | 삼성전자·미국 반도체 주가 수집 |
| Analysis | Python / pandas | Statistical anomaly detection | 통계 기반 이상 탐지 |
| Automation | GitHub Actions | Daily cron schedule | 매일 자동 실행 |
| Delivery | Gmail SMTP | Email the result | 이메일 발송 |

---

## Analysis Logic | 분석 로직

**EN:**
- Baseline statistics (mean & standard deviation) calculated from Samsung's 2026 YTD daily returns
- **Normal range:** Mean ± 2σ
- **Anomaly:** Any single-day return outside this range
- **7-day signal:** If the 7-day average return exits the normal range → `[ALERT]`
- **30-day trend:** Weekly anomaly count breakdown over the last 6 weeks
- **Correlation:** Samsung vs NVIDIA & Micron (global chip sync coefficient)

**KR:**
- 2026년 연초 이후 삼성전자 일일 수익률로 기준 통계(평균·표준편차) 산출
- **정상 범위:** 평균 ± 2σ
- **비정상:** 해당 범위를 벗어나는 단일 거래일
- **7일 신호:** 7일 평균 수익률이 정상 범위를 이탈할 경우 → `[비정상 발생]`
- **30일 추이:** 최근 6주 주별 비정상 발생 횟수
- **동기화 계수:** 삼성전자 vs 엔비디아·마이크론 상관관계

---

## Email Report Sample | 이메일 리포트 예시

**Subject | 제목:**
- `[안정적] 삼성전자 분석 리포트 - 2026-04-10`
- `[비정상 발생] 삼성전자 분석 리포트 - 2026-04-10`

**Body | 본문:**
```
=================================================================
    [ 삼성전자 주간 분석 리포트 (2026년 격변기 기준) - 2026-04-10 ]
=================================================================
2026년 평균 변화율       : 0.0821%
2026년 표준편차(σ)       : 1.4532%
삼성전자 ±2σ 정상 범위  : -2.8243% ~ 2.9885%
삼성전자 최근 7일 평균   : 0.3214%
삼성전자 최근 7일 결과  : 정상  [안정적]
-----------------------------------------------------------------
삼성전자 최근 30일 비정상 총 횟수 : 3회
[주별 비정상 발생 분포 (최근 6주)]
 - 03월 10일 ~ 03월 14일 : 1회
 - 03월 17일 ~ 03월 21일 : 0회
 ...
-----------------------------------------------------------------
엔비디아 최근 7일 평균    : 1.2045%
마이크론 최근 7일 평균    : 0.8821%
삼성전자 vs 엔비디아 동기화 계수 : 0.61
삼성전자 vs 마이크론 동기화 계수 : 0.54
```

---

## Setup Guide | 설정 방법

### 1. Gmail App Password | Gmail 앱 비밀번호 발급
1. [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) 접속
2. 앱 이름 입력 (예: `samsung-report`) → **만들기**
3. 16자리 비밀번호 복사 (창 닫으면 재확인 불가)

### 2. GitHub Secrets | GitHub 시크릿 등록
`Repository → Settings → Secrets and variables → Actions → New repository secret`

| Secret Name | Description | 설명 |
|-------------|-------------|------|
| `GMAIL_ADDRESS` | Sender Gmail address | 발신 Gmail 주소 |
| `GMAIL_APP_PW` | 16-digit app password | 앱 비밀번호 16자리 |
| `RECEIVER_EMAIL` | Recipient email address | 수신 이메일 주소 |

### 3. Manual Test | 수동 테스트
`GitHub → Actions 탭 → Daily Samsung Stock Report → Run workflow`

---

## Key Insight | 주요 인사이트

**EN:**
- **No dashboard needed:** A single subject-line tag (`[ALERT]` / `[STABLE]`) eliminates the need to open any app on stable days
- **Alert fatigue prevention:** The 7-day average signal filters out daily noise — only sustained deviations trigger an alert
- **Zero server cost:** GitHub Actions runs entirely on GitHub's infrastructure at no cost
- **Peer context:** NVIDIA and Micron correlation coefficients reveal whether Samsung's moves are global semiconductor trends or Samsung-specific events

**KR:**
- **대시보드 불필요:** 이메일 제목 태그(`[비정상 발생]` / `[안정적]`) 하나로 안정적인 날엔 앱을 열 필요가 없음
- **경고 피로 방지:** 7일 평균 신호가 일별 노이즈를 필터링 — 지속적인 이탈 시에만 경고 발생
- **서버 비용 제로:** GitHub Actions는 GitHub 인프라에서 무료로 실행
- **비교 맥락 제공:** 엔비디아·마이크론 동기화 계수로 삼성 움직임이 글로벌 반도체 트렌드인지 삼성 고유 이슈인지 판별 가능

---

## Files | 파일 구성

```
samsung stock Fluctuations/
  ├── .github/
  │     └── workflows/
  │           └── daily_report.yml   # GitHub Actions 스케줄 설정
  ├── samsung_analysis.py            # 분석 + 이메일 발송 스크립트
  ├── samsung_result.png             # 분석 차트 이미지
  ├── .gitignore                     # 민감 파일 업로드 방지
  └── README.md
```
