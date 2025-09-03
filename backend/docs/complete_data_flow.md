# 🔄 완전한 데이터 흐름 및 저장 구조

## 1️⃣ **사용자가 전략 생성**

### 순서:
1. 사용자가 웹/앱에서 전략 설정 입력
2. Frontend → Backend API 호출
3. Backend → Supabase 저장

### 저장 위치: `strategies_v2` 테이블

```sql
INSERT INTO strategies_v2 (
    -- 기본 정보
    name,           -- '나의 모멘텀 전략'
    version,        -- '1.0.0'
    description,    -- '상승 모멘텀 포착 전략'
    author,         -- '홍길동'
    strategy_type,  -- 'momentum'
    timeframe,      -- '1d' (일봉)
    universe,       -- ['005930', '000660', '035720'] (종목 코드 배열)
    
    -- 상태
    is_active,      -- true
    is_test_mode,   -- false (실거래)
    auto_trade_enabled, -- true (자동매매 활성화)
    
    -- 전략 설정 (JSON)
    indicators,     -- JSON 형식 (아래 상세)
    entry_conditions, -- JSON 형식 (아래 상세)
    exit_conditions,  -- JSON 형식 (아래 상세)
    risk_management,  -- JSON 형식 (아래 상세)
    
    -- 전략 코드
    strategy_code,  -- Python 코드 문자열
    
    -- 메타데이터
    user_id,        -- 'uuid-1234-5678'
    created_at,     -- '2024-01-01 09:00:00'
    updated_at      -- '2024-01-01 09:00:00'
) VALUES (...)
```

### 📦 **indicators 컬럼 (JSONB)**
```json
{
  "rsi_enabled": true,
  "rsi_period": 14,
  "rsi_oversold": 30,
  "rsi_overbought": 70,
  "macd_enabled": true,
  "macd_fast": 12,
  "macd_slow": 26,
  "macd_signal": 9,
  "bb_enabled": true,
  "bb_period": 20,
  "bb_std_dev": 2,
  "volume_enabled": true,
  "volume_ratio_threshold": 1.5
}
```

### 📦 **entry_conditions 컬럼 (JSONB)**
```json
{
  "use_trend_confirmation": true,
  "buy_signals_required": 3,
  "buy_rsi_max": 65,
  "min_volume_ratio": 1.5,
  "time_filter_enabled": true,
  "allowed_hours": [9, 10, 11, 13, 14],
  "avoid_gap": true,
  "max_spread_percent": 0.5
}
```

### 📦 **exit_conditions 컬럼 (JSONB)**
```json
{
  "stop_loss_enabled": true,
  "stop_loss_percent": 3.0,
  "take_profit_enabled": true,
  "take_profit_percent": 10.0,
  "trailing_stop_enabled": true,
  "trailing_stop_percent": 2.0,
  "max_holding_days": 30,
  "exit_on_signal_reverse": true
}
```

### 📦 **risk_management 컬럼 (JSONB)**
```json
{
  "position_sizing_method": "fixed_percent",
  "fixed_position_percent": 10.0,
  "max_positions": 3,
  "daily_loss_limit": 2.0,
  "daily_trade_limit": 5,
  "volatility_filter": true,
  "max_volatility": 0.03
}
```

---

## 2️⃣ **사용자 API 인증 정보 저장**

### 저장 위치: `user_api_credentials` 테이블

```sql
INSERT INTO user_api_credentials (
    user_id,        -- 'uuid-1234-5678'
    api_key,        -- 'PSED...' (한투 앱키)
    api_secret,     -- '7Zz5...' (암호화 저장)
    account_no,     -- '12345678-01' (암호화 저장)
    is_demo,        -- false (실거래)
    api_url,        -- 'https://openapi.koreainvestment.com:9443'
    is_active,      -- true
    created_at      -- '2024-01-01 09:00:00'
) VALUES (...)
```

---

## 3️⃣ **클라우드 실행자가 전략 실행 (매분 체크)**

### 실행 순서:
```python
# cloud_executor.py 실행 흐름

1. 시장 개장 체크 (09:00 - 15:30)
   ↓
2. 활성 전략 조회
   SELECT * FROM strategies_v2 
   WHERE is_active = true 
   AND auto_trade_enabled = true
   ↓
3. 각 전략별 시장 데이터 수집
   - 한투 API 호출 (사용자 API 키 사용)
   - universe의 각 종목 현재가 조회
   ↓
4. 전략 코드 실행
   - strategy_code 컬럼의 Python 코드 실행
   - indicators 설정값 적용
   - entry_conditions 체크
   ↓
5. 신호 생성
   {'type': 'buy', 'stock_code': '005930', 'price': 70000, 'quantity': 10}
```

---

## 4️⃣ **신호 저장**

### 저장 위치: `signals` 테이블

```sql
INSERT INTO signals (
    stock_code,     -- '005930'
    signal_type,    -- 'buy'
    strategy,       -- 'momentum'
    strength,       -- 0.85 (신호 강도)
    price,          -- 70000
    timestamp,      -- '2024-01-01 09:15:00'
    executed,       -- false (아직 미실행)
    notes,          -- 'RSI=45, MACD 골든크로스, 거래량 급증'
    user_id,        -- 'uuid-1234-5678'
    strategy_id     -- 123 (strategies_v2.id)
) VALUES (...)
```

---

## 5️⃣ **리스크 체크**

### 체크 항목:
```python
# 1. 일일 거래 횟수 체크
SELECT COUNT(*) FROM orders 
WHERE user_id = ? 
AND DATE(created_at) = TODAY()

# 2. 보유 종목 수 체크
SELECT COUNT(*) FROM portfolio 
WHERE user_id = ? 
AND quantity > 0

# 3. 일일 손실 한도 체크
SELECT SUM(profit_loss) FROM orders 
WHERE user_id = ? 
AND DATE(executed_at) = TODAY()
```

---

## 6️⃣ **주문 실행 및 저장**

### 저장 위치: `orders` 테이블

```sql
INSERT INTO orders (
    order_id,       -- '2024010100001' (한투 주문번호)
    stock_code,     -- '005930'
    stock_name,     -- '삼성전자'
    order_type,     -- 'buy'
    quantity,       -- 10
    price,          -- 70000
    order_method,   -- 'limit' (지정가)
    status,         -- 'pending' → 'executed'
    executed_price, -- 70000 (체결가)
    executed_quantity, -- 10 (체결 수량)
    created_at,     -- '2024-01-01 09:15:30'
    executed_at,    -- '2024-01-01 09:15:35'
    strategy,       -- 'momentum'
    strategy_id,    -- 123
    user_id,        -- 'uuid-1234-5678'
    notes           -- '모멘텀 전략 자동 매수'
) VALUES (...)
```

---

## 7️⃣ **포트폴리오 업데이트**

### 저장 위치: `portfolio` 테이블

```sql
-- 신규 매수 시
INSERT INTO portfolio (
    stock_code,     -- '005930'
    stock_name,     -- '삼성전자'
    quantity,       -- 10
    avg_price,      -- 70000
    current_price,  -- 70500
    profit_loss,    -- 5000
    profit_loss_rate, -- 0.71
    last_updated,   -- '2024-01-01 09:20:00'
    user_id         -- 'uuid-1234-5678'
) VALUES (...)

-- 기존 보유 시 UPDATE
UPDATE portfolio 
SET quantity = quantity + 10,
    avg_price = (old_qty * old_avg + 10 * 70000) / new_qty
WHERE stock_code = '005930' AND user_id = ?
```

---

## 8️⃣ **실행 로그 저장**

### 저장 위치: `strategy_execution_logs` 테이블

```sql
INSERT INTO strategy_execution_logs (
    strategy_id,    -- 123
    execution_time, -- '2024-01-01 09:15:00'
    
    -- 시장 데이터 스냅샷 (JSON)
    market_data,    -- {"005930": {"price": 70000, "volume": 1000000}}
    
    -- 지표 값 (JSON)
    indicator_values, -- {"rsi": 45, "macd": 0.5, "volume_ratio": 1.8}
    
    -- 조건 체크 결과 (JSON)
    entry_conditions_met, -- {"trend_ok": true, "volume_ok": true}
    exit_conditions_met,  -- {"stop_loss": false, "take_profit": false}
    risk_checks_passed,   -- {"daily_limit": true, "position_size": true}
    
    -- 결과
    signal_generated, -- 'buy'
    signal_strength,  -- 0.85
    action_taken,     -- 'order_placed'
    action_reason,    -- '모든 조건 충족'
    order_placed,     -- true
    order_details     -- {"order_id": "2024010100001", "qty": 10}
) VALUES (...)
```

---

## 9️⃣ **가격 데이터 저장 (실시간)**

### 저장 위치: `price_data` 테이블

```sql
INSERT INTO price_data (
    stock_code,     -- '005930'
    timestamp,      -- '2024-01-01 09:15:00'
    open,           -- 69500
    high,           -- 70500
    low,            -- 69000
    close,          -- 70000
    volume          -- 1234567
) VALUES (...)
ON CONFLICT (stock_code, timestamp) 
DO UPDATE SET close = EXCLUDED.close, volume = EXCLUDED.volume
```

---

## 🔟 **성과 분석 (일별)**

### 저장 위치: `performance` 테이블

```sql
INSERT INTO performance (
    date,           -- '2024-01-01'
    total_value,    -- 10500000 (총 자산)
    daily_return,   -- 0.015 (1.5%)
    cumulative_return, -- 0.105 (10.5%)
    win_rate,       -- 65.5
    trades_count,   -- 5
    profit_trades,  -- 3
    loss_trades,    -- 2
    max_drawdown,   -- -0.08
    sharpe_ratio,   -- 1.85
    user_id         -- 'uuid-1234-5678'
) VALUES (...)
```

---

## 📊 **데이터 흐름 요약**

```
1. 전략 생성 → strategies_v2 테이블
2. API 인증 → user_api_credentials 테이블
3. 신호 생성 → signals 테이블
4. 주문 실행 → orders 테이블
5. 포트폴리오 → portfolio 테이블
6. 실행 로그 → strategy_execution_logs 테이블
7. 가격 데이터 → price_data 테이블
8. 성과 분석 → performance 테이블
9. 시스템 로그 → system_logs 테이블
```

## 🕐 **실시간 실행 타이밍**

```
09:00:00 - 시장 개장, 전략 실행 시작
09:00:01 - 활성 전략 조회 (strategies_v2)
09:00:02 - 시장 데이터 수집 (API 호출)
09:00:03 - 전략 코드 실행
09:00:04 - 신호 생성 및 저장 (signals)
09:00:05 - 리스크 체크
09:00:06 - 주문 전송 (orders)
09:00:07 - 포트폴리오 업데이트
09:00:08 - 실행 로그 저장
...
09:01:00 - 다시 처음부터 반복
```