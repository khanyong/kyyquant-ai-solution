# 키움 잔고 실시간 동기화 서비스

## 📌 개요

WebSocket을 사용하여 키움 모의투자 계좌의 잔고를 실시간으로 Supabase DB에 동기화하는 서비스입니다.

## 🏗️ 아키텍처

```
┌─────────────────┐
│  키움 WebSocket │
│   mockapi.      │
│  kiwoom.com     │
└────────┬────────┘
         │ 실시간 잔고 데이터 (주문 체결 시)
         ↓
┌─────────────────┐
│  WebSocket      │
│   Client        │
│ (kiwoom_        │
│  websocket.py)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Balance Sync   │
│   Service       │
│ (balance_sync_  │
│  service.py)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Supabase DB   │
│ - kw_portfolio  │
│ - kw_account_   │
│   balance       │
└─────────────────┘
```

## 📁 파일 구조

```
backend/
├── api/
│   └── kiwoom_websocket.py      # WebSocket 클라이언트
├── services/
│   └── balance_sync_service.py  # 동기화 서비스
├── run_balance_sync.py          # 실행 스크립트
└── requirements.txt             # 의존성 (websockets 추가됨)
```

## 🚀 사용 방법

### 1. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)

```env
# 키움 API 설정
KIWOOM_APP_KEY=your_app_key
KIWOOM_APP_SECRET=your_app_secret
KIWOOM_ACCOUNT_NO=8112-5100
KIWOOM_IS_DEMO=true

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 3. 서비스 실행

#### Windows (로컬 테스트)
```bash
python run_balance_sync.py
```

#### Docker (NAS 서버)
```bash
docker-compose up -d balance-sync
```

### 4. 로그 확인

```bash
# 실시간 로그
tail -f balance_sync.log

# 또는 Docker 로그
docker logs -f auto_stock_balance_sync
```

## 🔄 동작 방식

### 초기 연결
1. OAuth 2.0 토큰 발급 (REST API)
2. WebSocket 연결 (`wss://mockapi.kiwoom.com:10000`)
3. 잔고(04) 실시간 등록

### 실시간 업데이트
1. 주문 체결 시 키움 서버에서 잔고 데이터 자동 전송
2. WebSocket 클라이언트가 데이터 수신
3. `on_balance_update` 콜백 호출
4. 서비스가 DB 업데이트:
   - `kw_portfolio`: 종목별 보유 현황
   - `kw_account_balance`: 계좌 총액

### 자동 재연결
- 연결 끊김 시 10초 후 자동 재연결
- 재연결 시 잔고 재등록

## 📊 데이터 매핑

| WebSocket 필드 | 설명 | DB 필드 |
|---------------|------|---------|
| 9201 | 계좌번호 | account_number |
| 9001 | 종목코드 | stock_code |
| 302 | 종목명 | stock_name |
| 10 | 현재가 | current_price |
| 930 | 보유수량 | quantity |
| 931 | 매입단가 | average_price |
| 932 | 총매입가 | total_purchase_amount |
| 933 | 주문가능수량 | available_quantity |
| 8019 | 손익률 | profit_loss_rate |

## ⚠️ 주의사항

### 모의투자 제한
- REST API 잔고 조회는 모의투자 미지원
- WebSocket만 모의투자 지원
- 주문 체결이 있어야 잔고 데이터 수신 가능

### 실전투자 전환
- `KIWOOM_IS_DEMO=false`로 변경
- WebSocket URL이 자동으로 `wss://api.kiwoom.com:10000`로 전환
- 나머지 코드 수정 불필요

## 🧪 테스트

### 로컬 테스트
```bash
# 서비스 실행
python run_balance_sync.py

# 다른 터미널에서 주문 실행 (테스트용)
curl -X POST http://localhost:8000/api/order/buy \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"005930","quantity":1,"price":0,"order_type":"buy"}'

# 로그에서 잔고 업데이트 확인
```

### DB 확인
```sql
-- 최근 포트폴리오 확인
SELECT * FROM kw_portfolio
ORDER BY updated_at DESC
LIMIT 10;

-- 계좌 총액 확인
SELECT * FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 1;
```

## 🐛 트러블슈팅

### 연결 실패
```
[KiwoomWS] ❌ Connection failed: ...
```
→ API 키와 계좌번호 확인

### 토큰 발급 실패
```
토큰 발급 실패: App Key와 Secret Key 검증에 실패했습니다
```
→ 키움 API 키 재발급 또는 모의투자 계좌 활성화 확인

### 잔고 데이터 수신 안됨
```
[KiwoomWS] 📡 Listening for real-time data...
(아무 메시지 없음)
```
→ **정상입니다**. 주문 체결이 발생해야 데이터가 수신됩니다.
→ 테스트: 모의투자 HTS에서 소량 매수 후 확인

## 📝 TODO

- [ ] Health check 엔드포인트 추가
- [ ] Prometheus 메트릭 수집
- [ ] 연결 상태 UI에 표시
- [ ] 수동 잔고 조회 트리거 (초기 데이터)
