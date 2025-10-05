# 일별 가격 데이터 업데이트 현황

## 현재 상태

### 데이터 상태
- **테이블**: `kw_price_daily`
- **최신 데이터**: 2025-09-12까지
- **데이터 갭**: 2025-09-13 ~ 현재 (약 23일)
- **업데이트 필요**: 즉시

### 구현 완료 사항
✅ 일별 가격 업데이트 스크립트 생성 (`backend/update_daily_prices.py`)
✅ 키움 REST API 클라이언트 통합
✅ 환경 변수 기반 API URL 설정
✅ Supabase upsert 기능 (중복 방지)

## 현재 문제

### API 연결 문제
1. **Mock API** (`https://mockapi.kiwoom.com`):
   - 토큰 발급: ✅ 성공
   - 현재가 조회: ❌ 500 Error (장 마감 후)
   - 일봉 조회: ❌ 500 Error (엔드포인트 미지원 가능성)

2. **Real API** (`https://openapi.kiwoom.com:9443`):
   - 연결: ❌ Timeout (네트워크/방화벽 문제)
   - 한국 IP 또는 VPN 필요 가능성

### 시간 제약
- 현재 시간: 19:00+ (장 마감 후)
- 장 운영 시간: 09:00 - 15:30 KST
- API는 장 운영 시간에만 정상 작동 가능

## 해결 방안

### 즉시 실행 (장 시작 전 또는 장 중)
```bash
# 1. 단일 종목 테스트
cd backend
python update_daily_prices.py --stock 005930 --days 100

# 2. 여러 종목 업데이트
python update_daily_prices.py --stock 005930,000660,035720 --days 100

# 3. 모든 활성 전략 종목 업데이트
python update_daily_prices.py --all --days 100
```

### 자동화 방안 (권장)

#### 방법 1: Windows 작업 스케줄러
```powershell
# 매일 오전 8:50 (장 시작 전) 실행
schtasks /create /tn "KiwoomDailyUpdate" /tr "D:\Dev\auto_stock\backend\update_daily_prices.py --all" /sc daily /st 08:50
```

#### 방법 2: N8N 워크플로우
```json
{
  "name": "Daily Price Update",
  "nodes": [
    {
      "type": "Schedule Trigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "value": "50 8 * * 1-5"}]
        }
      }
    },
    {
      "type": "Execute Command",
      "parameters": {
        "command": "python D:\\Dev\\auto_stock\\backend\\update_daily_prices.py --all --days 100"
      }
    }
  ]
}
```

#### 방법 3: Python 스케줄러
```python
# scheduler.py
import schedule
import time
import subprocess

def update_daily_prices():
    subprocess.run([
        "python",
        "D:\\Dev\\auto_stock\\backend\\update_daily_prices.py",
        "--all",
        "--days", "100"
    ])

# 매일 오전 8:50 실행
schedule.every().day.at("08:50").do(update_daily_prices)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 스크립트 사용법

### 기본 사용법
```bash
# 환경 변수 확인
set | findstr KIWOOM

# 스크립트 실행 (단일 종목)
cd D:\Dev\auto_stock\backend
python update_daily_prices.py --stock 005930

# 여러 종목
python update_daily_prices.py --stock 005930,000660,035720

# 모든 활성 전략 종목
python update_daily_prices.py --all

# 기간 지정 (기본: 100일)
python update_daily_prices.py --all --days 200
```

### 옵션 설명
- `--stock CODE`: 단일 종목 코드 (예: 005930)
- `--stock CODE1,CODE2,...`: 여러 종목 (쉼표로 구분)
- `--all`: 모든 활성 전략의 종목
- `--days N`: 조회 기간 (기본: 100일)

## 데이터 검증

### 업데이트 후 확인
```sql
-- 최신 데이터 확인
SELECT stock_code, MAX(trade_date) as latest_date
FROM kw_price_daily
GROUP BY stock_code
ORDER BY stock_code;

-- 특정 종목 최근 데이터
SELECT *
FROM kw_price_daily
WHERE stock_code = '005930'
ORDER BY trade_date DESC
LIMIT 10;

-- 데이터 갭 확인
SELECT stock_code,
       MIN(trade_date) as oldest,
       MAX(trade_date) as latest,
       COUNT(*) as record_count
FROM kw_price_daily
GROUP BY stock_code;
```

## 주의 사항

1. **API 호출 제한**
   - 키움 API: 초당 5회, 분당 100회 제한
   - 스크립트는 자동으로 딜레이 적용 (200ms)

2. **네트워크 요구사항**
   - `openapi.kiwoom.com:9443` 접근 가능해야 함
   - 방화벽/VPN 설정 확인 필요

3. **장 운영 시간**
   - 평일 09:00 - 15:30 KST
   - 장 마감 후에는 일부 API 동작 안 할 수 있음

4. **데이터 품질**
   - 휴장일(공휴일, 주말)은 데이터 없음
   - 상장폐지 종목은 오류 발생 가능

## 다음 단계

1. ✅ 스크립트 생성 완료
2. ⏳ 장 시작 시간에 수동 실행하여 테스트
3. ⏳ 자동화 스케줄 설정 (N8N 또는 작업 스케줄러)
4. ⏳ 데이터 검증 및 모니터링 설정

## 관련 파일

- 스크립트: `backend/update_daily_prices.py`
- API 클라이언트: `backend/api/kiwoom_client.py`
- 환경 설정: `.env`
- 테이블: Supabase `kw_price_daily`

---

**작성일**: 2025-10-05 19:00
**상태**: 장 시작 시간 테스트 대기 중
