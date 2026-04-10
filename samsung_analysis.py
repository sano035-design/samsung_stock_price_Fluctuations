import yfinance as yf
import pandas as pd
from datetime import datetime
import smtplib
import os
from email.mime.text import MIMEText

# =============================================================
# 1. 데이터 가져오기
# =============================================================
samsung_ticker = "005930.KS"
us_tickers = ["NVDA", "MU"]

print("2026년 최신 데이터를 기반으로 분석 중입니다...")
samsung_data = yf.download(samsung_ticker, start="2026-01-01", auto_adjust=False)['Adj Close'].squeeze()
us_data = yf.download(us_tickers, start="2026-01-01", auto_adjust=False)['Adj Close']

# =============================================================
# 2. 시장별 독립 변동률 계산
# =============================================================
samsung_ret = samsung_data.pct_change().dropna()
nvda_ret = us_data["NVDA"].pct_change().dropna()
mu_ret = us_data["MU"].pct_change().dropna()

# =============================================================
# 3. 2026년 기준 삼성전자 통계 분석
# =============================================================
overall_avg = float(samsung_ret.mean())
overall_std = float(samsung_ret.std())
upper_limit = overall_avg + (2 * overall_std)
lower_limit = overall_avg - (2 * overall_std)

# 최근 30거래일 데이터 추출
history_30 = samsung_ret.tail(30)
anomalies = history_30[(history_30 > upper_limit) | (history_30 < lower_limit)]

# =============================================================
# 4. 주별(Weekly) 비정상 발생 횟수 계산 (30거래일 → 6주차)
# =============================================================
weekly_summary = []
for i in range(0, 30, 5):
    start_idx = 30 - (i + 5)
    end_idx = 30 - i
    week_data = history_30.iloc[start_idx:end_idx]
    start_date = week_data.index[0]
    end_date = week_data.index[-1]
    week_anomalies = anomalies[(anomalies.index >= start_date) & (anomalies.index <= end_date)]
    count = len(week_anomalies)
    weekly_summary.append(f"{start_date.strftime('%m월 %d일')} ~ {end_date.strftime('%m월 %d일')} : {count}회")

# =============================================================
# 5. 타 종목 분석 및 동기화 계수
# =============================================================
recent_7_samsung = float(samsung_ret.tail(7).mean())
recent_7_nvda = float(nvda_ret.tail(7).mean())
recent_7_mu = float(mu_ret.tail(7).mean())

combined_ret = pd.concat([samsung_ret, nvda_ret, mu_ret], axis=1).dropna()
corr_nvda = float(combined_ret.iloc[:, 0].corr(combined_ret.iloc[:, 1]))
corr_mu = float(combined_ret.iloc[:, 0].corr(combined_ret.iloc[:, 2]))

# =============================================================
# 6. 상태 판단 (이메일 제목 태깅용)
# =============================================================
samsung_status = "비정상" if (recent_7_samsung > upper_limit or recent_7_samsung < lower_limit) else "정상"
status_tag = "[비정상 발생]" if samsung_status == "비정상" else "[안정적]"

# =============================================================
# 7. 리포트 문자열 생성 (콘솔 출력 + 이메일 공용)
# =============================================================
sep = "=" * 65
thin = "-" * 65
today = datetime.now().strftime('%Y-%m-%d')

lines = [
    sep,
    f"    [ 삼성전자 주간 분석 리포트 (2026년 격변기 기준) - {today} ]",
    sep,
    f"2026년 평균 변화율       : {overall_avg:.4%}",
    f"2026년 표준편차(σ)       : {overall_std:.4%}",
    f"삼성전자 ±2σ 정상 범위  : {lower_limit:.4%} ~ {upper_limit:.4%}",
    f"삼성전자 최근 7일 평균   : {recent_7_samsung:.4%}",
    f"삼성전자 최근 7일 결과  : {samsung_status}  {status_tag}",
    thin,
    f"삼성전자 최근 30일 비정상 총 횟수 : {len(anomalies)}회",
    "[주별 비정상 발생 분포 (최근 6주)]",
]
for line in reversed(weekly_summary):
    lines.append(f" - {line}")

lines += [
    thin,
    f"엔비디아 최근 7일 평균    : {recent_7_nvda:.4%}",
    f"마이크론 최근 7일 평균    : {recent_7_mu:.4%}",
    f"삼성전자 vs 엔비디아 동기화 계수 : {corr_nvda:.2f}",
    f"삼성전자 vs 마이크론 동기화 계수 : {corr_mu:.2f}",
    thin,
    "분석가 조언 :",
]
if len(anomalies) >= 20:
    lines.append(" ⚠️  경고: 비정상이 압도적으로 많습니다. 주가가 정상 범주를 이탈 중입니다.")
else:
    lines.append(" ✅  정보: 2026년 변동성에 적응 중입니다. 주별 횟수 추이를 확인하세요.")
lines.append(sep)

report_text = "\n".join(lines)

# 콘솔 출력
print("\n" + report_text + "\n")

# =============================================================
# 8. 이메일 발송
# =============================================================
def send_email(subject: str, content: str) -> None:
    """
    Gmail SMTP를 통해 분석 리포트를 발송합니다.
    GitHub Secrets 또는 로컬 환경 변수에 아래 두 값이 설정되어 있어야 합니다:
      GMAIL_ADDRESS  : 발신 Gmail 주소
      GMAIL_APP_PW   : Gmail 앱 비밀번호 (16자리)
    RECEIVER_EMAIL 환경 변수가 없으면 발신 주소로 자기 자신에게 발송합니다.
    """
    sender = os.environ.get("GMAIL_ADDRESS", "")
    password = os.environ.get("GMAIL_APP_PW", "")
    receiver = os.environ.get("RECEIVER_EMAIL", sender)

    if not sender or not password:
        print("⚠️  이메일 환경 변수(GMAIL_ADDRESS / GMAIL_APP_PW)가 설정되지 않아 메일을 건너뜁니다.")
        return

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"✅  이메일 발송 완료 → {receiver}")
    except Exception as e:
        print(f"❌  이메일 발송 실패: {e}")
        raise


email_subject = f"{status_tag} 삼성전자 분석 리포트 - {today}"
send_email(email_subject, report_text)