# Backend API 엔드포인트 가이드

자동매매 시스템 Backend API 명세서입니다.

## 기본 정보

- **Base URL**: `http://localhost:8001`
- **Content-Type**: `application/json`
- **인증**: 없음 (내부 네트워크 전용)

---

## 📍 Market API

시장 데이터 조회 API

### GET /api/market/price/{stock_code}

현재가 조회

**Parameters:**
- `stock_code` (path, required): 종목 코드 (예: 005930)

**Response:**
```json
{
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "current_price": 71000,
  "change_amount": 1000,
  "change_rate": 1.43,
  "volume": 15234567,
  "high": 71500,
  "low": 70000,
  "open_price": 70500,
  "prev_close": 70000,
  "timestamp": "2024-10-05T14:30:00",
  "market_status": "open"
}
```

**Example:**
```bash
curl http://localhost:8001/api/market/price/005930
```

---

### POST /api/market/prices

복수 종목 현재가 조회

**Request Body:**
```json
{
  "stock_codes": ["005930", "000660", "035720"]
}
```

**Response:**
```json
[
  {
    "stock_code": "005930",
    "current_price": 71000,
    ...
  },
  {
    "stock_code": "000660",
    "current_price": 42500,
    ...
  }
]
```

**Example:**
```bash
curl -X POST http://localhost:8001/api/market/prices \
  -H "Content-Type: application/json" \
  -d '{"stock_codes": ["005930", "000660"]}'
```

---

### GET /api/market/historical/{stock_code}

과거 데이터 조회 (기술적 지표 계산용)

**Parameters:**
- `stock_code` (path, required): 종목 코드
- `interval` (query, optional): 시간 간격 (기본: 1d)
  - `1d`: 일봉
- `limit` (query, optional): 데이터 개수 (기본: 100, 최대: 1000)
- `start_date` (query, optional): 시작일 (YYYY-MM-DD)
- `end_date` (query, optional): 종료일 (YYYY-MM-DD)

**Response:**
```json
{
  "stock_code": "005930",
  "interval": "1d",
  "count": 100,
  "data": [
    {
      "date": "2024-01-02",
      "open": 70000,
      "high": 71000,
      "low": 69500,
      "close": 70500,
      "volume": 12345678
    },
    ...
  ]
}
```

**Example:**
```bash
# 최근 100일 데이터
curl "http://localhost:8001/api/market/historical/005930?limit=100"

# 날짜 범위 지정
curl "http://localhost:8001/api/market/historical/005930?start_date=2024-01-01&end_date=2024-12-31"
```

---

### GET /api/market/candles/{stock_code}

차트용 캔들 데이터

**Parameters:**
- `stock_code` (path, required): 종목 코드
- `count` (query, optional): 캔들 개수 (기본: 100, 최대: 500)

**Response:**
```json
{
  "stock_code": "005930",
  "count": 100,
  "candles": [
    {
      "time": "2024-01-02",
      "open": 70000,
      "high": 71000,
      "low": 69500,
      "close": 70500,
      "volume": 12345678
    },
    ...
  ]
}
```

---

### GET /api/market/market-status

시장 상태 확인

**Response:**
```json
{
  "is_open": true,
  "is_weekend": false,
  "current_time": "2024-10-05T14:30:00",
  "market_open_time": "2024-10-05T09:00:00",
  "market_close_time": "2024-10-05T15:30:00",
  "next_event": "close",
  "next_event_time": "2024-10-05T15:30:00",
  "time_to_next_event_minutes": 60
}
```

**Example:**
```bash
curl http://localhost:8001/api/market/market-status
```

---

## 📍 Strategy API

전략 실행 및 신호 생성 API

### POST /api/strategy/check-signal

**매매 신호 확인 (n8n에서 호출)**

Supabase에서 전략을 로드하고, 과거 데이터 기반으로 기술적 지표를 계산하여 매매 신호를 생성합니다.

**Request Body:**
```json
{
  "strategy_id": "uuid-strategy-id",
  "stock_code": "005930",
  "current_price": 71000  // 선택사항
}
```

**Response:**
```json
{
  "strategy_id": "uuid-strategy-id",
  "strategy_name": "RSI 과매도 전략",
  "stock_code": "005930",
  "stock_name": null,
  "signal_type": "BUY",  // BUY | SELL | HOLD
  "signal_strength": 0.85,  // 0.0 ~ 1.0
  "current_price": 71000,
  "indicators": {
    "rsi": 28.5,
    "macd": -1.2,
    "bb_upper": 75000,
    "bb_middle": 71000,
    "bb_lower": 67000
  },
  "entry_conditions_met": {
    "rsi": true,
    "macd": false
  },
  "exit_conditions_met": {
    "stop_loss": false,
    "profit_target": false
  },
  "timestamp": "2024-10-05T14:30:00",
  "debug_info": {
    "data_points": 100,
    "latest_date": "2024-10-05"
  }
}
```

**프로세스:**

1. Supabase `strategies` 테이블에서 전략 조회
2. Supabase `stock_prices`에서 과거 데이터 조회 (필요한 만큼)
3. `indicators.calculator`로 지표 계산 (RSI, MACD 등)
4. 진입 조건 평가 (모든 조건 충족 시 BUY)
5. 청산 조건 평가 (하나라도 충족 시 SELL)
6. 신호 반환

**Example:**
```bash
curl -X POST http://localhost:8001/api/strategy/check-signal \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "123e4567-e89b-12d3-a456-426614174000",
    "stock_code": "005930"
  }'
```

**에러:**
```json
{
  "detail": "Strategy 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

### POST /api/strategy/batch-check

배치 신호 확인 (여러 종목 동시 처리)

**Request Body:**
```json
{
  "strategy_id": "uuid-strategy-id",
  "stock_codes": ["005930", "000660", "035720"]
}
```

**Response:**
```json
[
  {
    "strategy_id": "uuid-strategy-id",
    "stock_code": "005930",
    "signal_type": "BUY",
    ...
  },
  {
    "strategy_id": "uuid-strategy-id",
    "stock_code": "000660",
    "signal_type": "HOLD",
    ...
  }
]
```

---

### POST /api/strategy/check-position-exit

**포지션 청산 확인 (손절/익절)**

활성 포지션의 청산 조건을 확인합니다.

**Request Body:**
```json
{
  "position_id": "uuid-position-id",
  "stock_code": "005930",
  "entry_price": 70000,
  "current_quantity": 10,
  "strategy_id": "uuid-strategy-id"
}
```

**Response:**
```json
{
  "position_id": "uuid-position-id",
  "should_exit": true,
  "exit_type": "stop_loss",  // stop_loss | profit_target | trailing_stop | strategy_signal | none
  "exit_percentage": 1.0,  // 청산 비율 (0.2 = 20%, 1.0 = 100%)
  "exit_quantity": 10,
  "current_price": 66500,
  "entry_price": 70000,
  "profit_loss": -35000,
  "profit_loss_rate": -0.05,
  "reason": "Stop loss triggered: -5.00% <= -5.00%"
}
```

**청산 조건 우선순위:**

1. **손절 (stop_loss)**: 수익률이 설정값 이하
2. **익절 (profit_target)**: 수익률이 목표값 이상 (단계별)
3. **Trailing Stop**: 고점 대비 하락률
4. **전략 신호 (strategy_signal)**: 청산 조건 충족

**단계별 익절 예시:**

```json
// 전략 설정
{
  "exit": {
    "profit_target": {
      "enabled": true,
      "targets": [
        {"rate": 0.03, "percentage": 0.2},  // 3% 수익 시 20% 매도
        {"rate": 0.05, "percentage": 0.3},  // 5% 수익 시 30% 매도
        {"rate": 0.10, "percentage": 1.0}   // 10% 수익 시 전량 매도
      ]
    }
  }
}

// API 응답 (3% 달성 시)
{
  "should_exit": true,
  "exit_type": "profit_target",
  "exit_percentage": 0.2,  // 20% 매도
  "exit_quantity": 2,      // 10주 중 2주
  ...
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/api/strategy/check-position-exit \
  -H "Content-Type: application/json" \
  -d '{
    "position_id": "uuid-here",
    "stock_code": "005930",
    "entry_price": 70000,
    "current_quantity": 10,
    "strategy_id": "uuid-strategy-id"
  }'
```

---

### GET /api/strategy/evaluate/{strategy_id}

전략 성과 평가

**Parameters:**
- `strategy_id` (path, required): 전략 ID

**Response:**
```json
{
  "strategy_id": "uuid-strategy-id",
  "total_trades": 25,
  "buy_orders": 15,
  "sell_orders": 10,
  "latest_trade": "2024-10-05T14:30:00"
}
```

**Example:**
```bash
curl http://localhost:8001/api/strategy/evaluate/123e4567-e89b-12d3-a456-426614174000
```

---

## 📍 Backtest API

백테스트 API (기존)

### GET /api/backtest/version

백테스트 API 버전 확인

**Response:**
```json
{
  "version": "3.1.0",
  "features": [
    "staged_trading",
    "sell_conditions",
    "multi_strategy",
    "real_time_data",
    "preflight_validation",
    "version_tracking"
  ]
}
```

---

## 📍 Health & Status

### GET /

루트 엔드포인트 (헬스체크)

**Response:**
```json
{
  "status": "running",
  "version": "3.0.0",
  "build_time": "2024-10-05T12:00:00",
  "endpoints": {
    "backtest": "/api/backtest",
    "market": "/api/market",
    "strategy": "/api/strategy",
    "docs": "/docs"
  }
}
```

---

### GET /health

헬스체크

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-05T14:30:00"
}
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파라미터 오류) |
| 404 | 리소스 없음 (전략/종목 없음) |
| 500 | 서버 에러 (계산 실패, DB 연결 실패) |

**에러 응답 형식:**
```json
{
  "detail": "Strategy 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

## n8n 워크플로우 사용 예시

### 메인 자동매매 워크플로우

```javascript
// n8n HTTP Request 노드
{
  "method": "POST",
  "url": "{{$env.BACKEND_URL}}/api/strategy/check-signal",
  "body": {
    "strategy_id": "{{$json.strategy_id}}",
    "stock_code": "{{$json.stock_code}}"
  }
}

// 응답
{
  "signal_type": "BUY",
  "signal_strength": 0.85,
  "current_price": 71000,
  ...
}

// IF 노드로 신호 체크
if ($json.signal_type === "BUY" && $json.signal_strength > 0.5) {
  // 주문 실행 노드로 이동
}
```

### 포지션 모니터링 워크플로우

```javascript
// n8n HTTP Request 노드
{
  "method": "POST",
  "url": "{{$env.BACKEND_URL}}/api/strategy/check-position-exit",
  "body": {
    "position_id": "{{$json.id}}",
    "stock_code": "{{$json.stock_code}}",
    "entry_price": {{$json.entry_price}},
    "current_quantity": {{$json.current_quantity}},
    "strategy_id": "{{$json.strategy_id}}"
  }
}

// 응답
{
  "should_exit": true,
  "exit_type": "stop_loss",
  "exit_quantity": 10,
  ...
}

// IF 노드로 청산 필요 확인
if ($json.should_exit === true) {
  // 매도 주문 실행
}
```

---

## 개발 가이드

### 로컬 테스트

```bash
# Backend 서버 실행
cd backend
python main.py

# 다른 터미널에서 테스트
curl http://localhost:8001/health

# 신호 확인 테스트
curl -X POST http://localhost:8001/api/strategy/check-signal \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "your-uuid",
    "stock_code": "005930"
  }'
```

### API 문서

FastAPI 자동 생성 문서:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## 참고

- [REAL_TRADING_DEPLOYMENT.md](REAL_TRADING_DEPLOYMENT.md) - 배포 가이드
- [MASTER_ROADMAP.md](../MASTER_ROADMAP.md) - 프로젝트 로드맵
