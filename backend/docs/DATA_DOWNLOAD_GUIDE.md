# 키움증권 실시간 데이터 다운로드 가이드

## 🚀 빠른 시작

### 1. API 키 설정
Supabase의 `user_api_keys` 테이블에 키움증권 API 정보를 저장하세요:
- `KIWOOM_APP_KEY`: 앱 키
- `KIWOOM_APP_SECRET`: 앱 시크릿
- `KIWOOM_ACCOUNT_NO`: 계좌번호

### 2. 데이터 다운로드 실행

#### 방법 A: REST API 사용 (권장 - 모든 환경)
```bash
# NAS/Linux/Windows 모든 환경에서 가능
cd backend/rest_api

# 특정 종목만 다운로드
python download_stock_data_rest.py --codes 005930,000660,035720

# 상위 N개 종목 다운로드
python download_stock_data_rest.py --limit 50

# 전체 종목 다운로드 (시간 오래 걸림)
python download_stock_data_rest.py --all

# 기본: 상위 30개 종목
python download_stock_data_rest.py
```

#### 방법 B: OpenAPI+ 직접 연결 (Windows 전용)
```bash
# Windows + 32비트 Python 환경 필요
cd backend/data_collectors
python collect_kiwoom_data.py
```

## 📊 데이터 수집 스크립트

### 1. 전체 종목 다운로드
```python
# backend/data_collectors/download_complete_data.py
python download_complete_data.py
```
- 코스피/코스닥 전체 종목
- 10년치 일봉 데이터
- 재무지표 포함

### 2. 특정 종목 다운로드
```python
# backend/data_collectors/collect_kiwoom_data.py
python collect_kiwoom_data.py --codes 005930,000660,035720
```
- 삼성전자, SK하이닉스, 카카오 등 지정 종목만

### 3. 실시간 현재가 업데이트
```python
# backend/rest_api/update_current_prices.py
python update_current_prices.py
```

## 🔄 백테스트 데이터 흐름

```
1. 키움 REST API/OpenAPI+
   ↓
2. 데이터 수집 스크립트
   ↓
3. Supabase 저장 (kw_price_daily, kw_financial_ratio)
   ↓
4. NAS 백테스트 엔진이 Supabase에서 로드
   ↓
5. 백테스트 실행
```

## 📝 데이터 테이블 구조

### kw_price_daily (일봉 데이터)
- stock_code: 종목코드
- trade_date: 거래일
- open, high, low, close: OHLC
- volume: 거래량

### kw_financial_ratio (재무지표)
- stock_code: 종목코드
- per, pbr, roe: 밸류에이션 지표
- eps, bps: 주당 지표
- dividend_yield: 배당수익률

## ⚙️ 환경 설정

### .env 파일 예시
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# 키움증권 (Supabase user_api_keys 테이블에서 관리)
# KIWOOM_APP_KEY, KIWOOM_APP_SECRET은 DB에서 동적 로드
```

## 🐳 NAS Docker 환경

### 데이터 수집 컨테이너 실행
```bash
docker run -d \
  --name kiwoom-collector \
  -e SUPABASE_URL=$SUPABASE_URL \
  -e SUPABASE_KEY=$SUPABASE_KEY \
  kiwoom-bridge:latest \
  python collect_data_scheduler.py
```

## 📅 자동화 스케줄

### 일일 데이터 수집 (cron)
```cron
# 매일 오후 4시 장 마감 후 데이터 수집
0 16 * * 1-5 cd /app && python download_daily_data.py

# 매주 토요일 전체 데이터 검증 및 보정
0 10 * * 6 cd /app && python validate_and_fix_data.py
```

## 🔍 데이터 확인

### Supabase에서 데이터 확인
```sql
-- 최근 다운로드된 데이터 확인
SELECT stock_code, MAX(trade_date) as latest_date, COUNT(*) as days
FROM kw_price_daily
GROUP BY stock_code
ORDER BY latest_date DESC
LIMIT 10;

-- 특정 종목 데이터 확인
SELECT * FROM kw_price_daily
WHERE stock_code = '005930'
ORDER BY trade_date DESC
LIMIT 30;
```

## 🔄 기존 데이터와의 관계

### Upsert 방식 (INSERT + UPDATE)
모든 데이터는 **upsert** 방식으로 저장됩니다:

| 테이블 | Primary Key | 동작 |
|--------|------------|------|
| `kw_stock_master` | stock_code | 종목 정보 업데이트 |
| `kw_price_daily` | stock_code + trade_date | 해당 날짜 가격 업데이트 |
| `kw_price_current` | stock_code | 최신 현재가로 갱신 |

### 실제 동작 예시
```sql
-- 2024-01-15 삼성전자 데이터가 이미 있는 경우
-- 새로운 다운로드시 해당 데이터를 덮어씀
INSERT INTO kw_price_daily (stock_code, trade_date, close, ...)
VALUES ('005930', '2024-01-15', 75000, ...)
ON CONFLICT (stock_code, trade_date)
DO UPDATE SET close = 75000, ...;
```

### 데이터 관리 전략
1. **증분 업데이트**: 매일 장 마감 후 최신 데이터만 추가
2. **전체 갱신**: 주기적으로 전체 데이터 재다운로드로 정합성 확보
3. **중복 방지**: Primary Key로 자동 중복 제거

## ❗ 주의사항

1. **API 호출 제한**: 키움 API는 초당 5회 제한이 있으므로 적절한 딜레이 필요
2. **32비트 Python**: OpenAPI+ 직접 연결시 반드시 32비트 Python 필요
3. **거래시간**: 장중에는 데이터 수집 자제 (부하 방지)
4. **데이터 정합성**: 수집 후 반드시 데이터 검증 스크립트 실행
5. **기존 데이터**: Upsert로 자동 업데이트되므로 별도 삭제 불필요

## 📞 문제 해결

### Mock 데이터만 나오는 경우
1. Supabase 연결 확인
2. API 키 설정 확인
3. 데이터 수집 스크립트 실행
4. 테이블에 데이터 존재 확인

### 데이터 수집 실패시
1. 키움 API 키 유효성 확인
2. 네트워크 연결 상태 확인
3. Python 환경 (32bit) 확인
4. 로그 파일 확인 (`logs/collector.log`)