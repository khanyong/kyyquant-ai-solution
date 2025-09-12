# Supabase 테이블 구조 분석 - 실전 매매 준비 상태

## 📊 현재 테이블 구조 분석

### ✅ 이미 구축된 핵심 테이블

#### 1. **strategies** - 전략 관리 ✅
```sql
- id, name, version, description
- is_active, is_test_mode, auto_trade_enabled  -- 실전/모의 구분 가능
- indicators, entry_conditions, exit_conditions
- risk_management, performance_metrics
- user_id -- 사용자별 관리
```
**평가**: 실전 매매를 위한 전략 관리 완벽 지원

#### 2. **user_api_credentials** - API 인증 정보 ✅
```sql
- api_key, api_secret (암호화 필요)
- account_no, account_product_code
- is_demo (모의/실전 구분)
- is_active, last_connected_at
```
**평가**: 증권사 API 연동 준비 완료

#### 3. **orders** - 주문 관리 ✅
```sql
- order_id, stock_code, stock_name
- order_type (buy/sell)
- quantity, price, order_method
- status (pending/executed/cancelled)
- executed_price, executed_quantity
- strategy_id, user_id
```
**평가**: 실전 주문 추적 가능

#### 4. **portfolio** - 포트폴리오 ✅
```sql
- stock_code, stock_name
- quantity, avg_price
- current_price, profit_loss
- user_id
```
**평가**: 보유 종목 관리 가능

#### 5. **signals** - 거래 신호 ✅
```sql
- stock_code, signal_type (buy/sell/hold)
- strategy_id, strength
- executed (실행 여부)
- user_id
```
**평가**: 신호 생성 및 추적 가능

#### 6. **performance** - 성과 분석 ✅
```sql
- daily_return, cumulative_return
- win_rate, sharpe_ratio
- max_drawdown
- user_id
```
**평가**: 실전 성과 추적 가능

#### 7. **strategy_schedules** - 자동매매 스케줄 ✅
```sql
- strategy_id
- start_time, end_time
- days_of_week
- is_active
```
**평가**: 자동매매 시간 설정 가능

---

## 🔍 실전 매매를 위한 추가 필요 테이블

### 1. **broker_accounts** - 증권사 계좌 관리 🆕
```sql
CREATE TABLE IF NOT EXISTS broker_accounts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    
    -- 증권사 정보
    broker_type TEXT NOT NULL, -- 'kis', 'ebest', 'ls'
    account_number TEXT NOT NULL,
    account_name TEXT,
    
    -- 계좌 유형
    is_paper_account BOOLEAN DEFAULT FALSE, -- 모의/실전
    is_margin_account BOOLEAN DEFAULT FALSE, -- 신용계좌
    is_futures_enabled BOOLEAN DEFAULT FALSE, -- 선물옵션
    
    -- 한도 설정
    daily_trade_limit DECIMAL(15, 2),
    max_position_size DECIMAL(15, 2),
    max_leverage DECIMAL(3, 1) DEFAULT 1.0,
    
    -- 상태
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_sync_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, broker_type, account_number)
);
```

### 2. **account_balances** - 계좌 잔고 🆕
```sql
CREATE TABLE IF NOT EXISTS account_balances (
    id SERIAL PRIMARY KEY,
    broker_account_id INTEGER REFERENCES broker_accounts(id),
    
    -- 현금 잔고
    total_cash DECIMAL(15, 2),
    available_cash DECIMAL(15, 2),
    locked_cash DECIMAL(15, 2), -- 미수/주문중
    
    -- 주식 평가
    stock_value DECIMAL(15, 2),
    total_value DECIMAL(15, 2),
    
    -- 손익
    daily_profit_loss DECIMAL(15, 2),
    daily_profit_loss_rate DECIMAL(7, 4),
    total_profit_loss DECIMAL(15, 2),
    total_profit_loss_rate DECIMAL(7, 4),
    
    -- 기타
    buying_power DECIMAL(15, 2), -- 매수가능금액
    
    snapshot_time TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(broker_account_id, snapshot_time)
);
```

### 3. **order_executions** - 체결 내역 🆕
```sql
CREATE TABLE IF NOT EXISTS order_executions (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    
    -- 체결 정보
    execution_id TEXT UNIQUE, -- 증권사 체결번호
    execution_price DECIMAL(10, 2),
    execution_quantity INTEGER,
    execution_amount DECIMAL(15, 2),
    
    -- 수수료/세금
    commission DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    other_fees DECIMAL(10, 2),
    
    executed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. **real_time_prices** - 실시간 시세 🆕
```sql
CREATE TABLE IF NOT EXISTS real_time_prices (
    id SERIAL PRIMARY KEY,
    stock_code TEXT NOT NULL,
    
    -- 현재가 정보
    current_price DECIMAL(10, 2),
    change_price DECIMAL(10, 2),
    change_rate DECIMAL(7, 4),
    
    -- 호가 정보
    bid_price1 DECIMAL(10, 2),
    bid_size1 INTEGER,
    ask_price1 DECIMAL(10, 2),
    ask_size1 INTEGER,
    
    -- 거래량
    volume BIGINT,
    volume_amount DECIMAL(15, 2),
    
    -- 기타
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    open_price DECIMAL(10, 2),
    
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- 파티션 키 (시간별 파티셔닝용)
    PRIMARY KEY (stock_code, timestamp)
);
```

### 5. **trading_permissions** - 거래 권한 관리 🆕
```sql
CREATE TABLE IF NOT EXISTS trading_permissions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) UNIQUE,
    
    -- 권한 레벨
    permission_level TEXT DEFAULT 'viewer', -- viewer/paper/real
    
    -- 거래 권한
    can_view_market BOOLEAN DEFAULT TRUE,
    can_paper_trade BOOLEAN DEFAULT FALSE,
    can_real_trade BOOLEAN DEFAULT FALSE,
    can_use_margin BOOLEAN DEFAULT FALSE,
    can_use_futures BOOLEAN DEFAULT FALSE,
    
    -- 한도
    daily_trade_count_limit INTEGER DEFAULT 10,
    daily_trade_amount_limit DECIMAL(15, 2),
    max_position_count INTEGER DEFAULT 20,
    max_position_value DECIMAL(15, 2),
    
    -- API 한도
    api_calls_per_minute INTEGER DEFAULT 60,
    api_calls_per_day INTEGER DEFAULT 10000,
    
    -- 검증
    identity_verified BOOLEAN DEFAULT FALSE,
    identity_verified_at TIMESTAMPTZ,
    trading_experience_years INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'conservative', -- conservative/moderate/aggressive
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6. **market_holidays** - 휴장일 관리 🆕
```sql
CREATE TABLE IF NOT EXISTS market_holidays (
    id SERIAL PRIMARY KEY,
    holiday_date DATE NOT NULL UNIQUE,
    holiday_name TEXT,
    market_type TEXT DEFAULT 'KRX', -- KRX, NYSE, etc
    is_half_day BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 7. **notification_settings** - 알림 설정 🆕
```sql
CREATE TABLE IF NOT EXISTS notification_settings (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) UNIQUE,
    
    -- 알림 채널
    email_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    push_enabled BOOLEAN DEFAULT FALSE,
    telegram_enabled BOOLEAN DEFAULT FALSE,
    
    -- 알림 유형
    order_executed BOOLEAN DEFAULT TRUE,
    signal_generated BOOLEAN DEFAULT TRUE,
    stop_loss_triggered BOOLEAN DEFAULT TRUE,
    daily_report BOOLEAN DEFAULT TRUE,
    error_alerts BOOLEAN DEFAULT TRUE,
    
    -- 알림 조건
    min_profit_alert DECIMAL(10, 2), -- 수익 알림 최소값
    max_loss_alert DECIMAL(10, 2), -- 손실 알림 최대값
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📈 기존 테이블 개선 사항

### 1. **orders** 테이블 개선
```sql
-- 추가 필요 컬럼
ALTER TABLE orders ADD COLUMN IF NOT EXISTS broker_account_id INTEGER REFERENCES broker_accounts(id);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS broker_order_id TEXT; -- 증권사 주문번호
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_channel TEXT DEFAULT 'web'; -- web/mobile/api/auto
ALTER TABLE orders ADD COLUMN IF NOT EXISTS is_paper_order BOOLEAN DEFAULT FALSE;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS commission DECIMAL(10, 2);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tax DECIMAL(10, 2);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;
```

### 2. **portfolio** 테이블 개선
```sql
-- 추가 필요 컬럼
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS broker_account_id INTEGER REFERENCES broker_accounts(id);
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS first_buy_date DATE;
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS last_buy_date DATE;
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS realized_profit_loss DECIMAL(15, 2);
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS dividend_received DECIMAL(15, 2);
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS target_price DECIMAL(10, 2);
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS stop_loss_price DECIMAL(10, 2);
```

### 3. **strategies** 테이블 개선
```sql
-- 추가 필요 컬럼
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS broker_account_id INTEGER REFERENCES broker_accounts(id);
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS max_position_size DECIMAL(15, 2);
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS max_position_count INTEGER;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS daily_loss_limit DECIMAL(15, 2);
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS is_paper_trading BOOLEAN DEFAULT TRUE;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS execution_priority INTEGER DEFAULT 0;
```

---

## 🔐 보안 강화 사항

### 1. RLS (Row Level Security) 추가 정책
```sql
-- broker_accounts 보안
ALTER TABLE broker_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only see own broker accounts" ON broker_accounts
    FOR ALL USING (auth.uid() = user_id);

-- account_balances 보안
ALTER TABLE account_balances ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only see own balances" ON account_balances
    FOR ALL USING (
        broker_account_id IN (
            SELECT id FROM broker_accounts WHERE user_id = auth.uid()
        )
    );

-- trading_permissions 보안
ALTER TABLE trading_permissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only see own permissions" ON trading_permissions
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Only admins can update permissions" ON trading_permissions
    FOR UPDATE USING (
        auth.uid() IN (
            SELECT user_id FROM user_roles WHERE role = 'admin'
        )
    );
```

### 2. 암호화 필요 컬럼
```sql
-- 민감 정보 암호화 (application level)
- user_api_credentials.api_secret
- user_api_credentials.account_no
- broker_accounts.account_number
- notification_settings (연락처 정보)
```

---

## 📊 성능 최적화

### 1. 인덱스 추가
```sql
-- 실시간 조회 성능 향상
CREATE INDEX idx_real_time_prices_stock_time ON real_time_prices(stock_code, timestamp DESC);
CREATE INDEX idx_account_balances_time ON account_balances(broker_account_id, snapshot_time DESC);
CREATE INDEX idx_order_executions_order ON order_executions(order_id, executed_at DESC);

-- 파티셔닝 (대용량 데이터)
-- real_time_prices 테이블을 일별 파티션으로 관리
CREATE TABLE real_time_prices_2025_01_11 PARTITION OF real_time_prices
    FOR VALUES FROM ('2025-01-11') TO ('2025-01-12');
```

### 2. 뷰(View) 생성
```sql
-- 사용자별 전체 포지션 뷰
CREATE VIEW user_total_positions AS
SELECT 
    p.user_id,
    p.stock_code,
    p.stock_name,
    SUM(p.quantity) as total_quantity,
    AVG(p.avg_price) as avg_price,
    SUM(p.quantity * rtp.current_price) as current_value,
    SUM(p.quantity * rtp.current_price) - SUM(p.quantity * p.avg_price) as profit_loss
FROM portfolio p
LEFT JOIN real_time_prices rtp ON p.stock_code = rtp.stock_code
GROUP BY p.user_id, p.stock_code, p.stock_name;

-- 일일 거래 요약 뷰
CREATE VIEW daily_trading_summary AS
SELECT 
    DATE(o.created_at) as trade_date,
    o.user_id,
    COUNT(*) as total_orders,
    SUM(CASE WHEN o.order_type = 'buy' THEN 1 ELSE 0 END) as buy_orders,
    SUM(CASE WHEN o.order_type = 'sell' THEN 1 ELSE 0 END) as sell_orders,
    SUM(CASE WHEN o.status = 'executed' THEN 1 ELSE 0 END) as executed_orders,
    SUM(o.executed_quantity * o.executed_price) as total_volume
FROM orders o
GROUP BY DATE(o.created_at), o.user_id;
```

---

## ✅ 결론

### 현재 상태
- **핵심 테이블 80% 준비 완료**: 전략, 주문, 포트폴리오, 신호 관리 가능
- **API 인증 구조 존재**: user_api_credentials 테이블로 기본 관리 가능
- **RLS 보안 적용**: 사용자별 데이터 격리

### 추가 필요 사항
1. **증권사 계좌 관리**: broker_accounts 테이블
2. **실시간 시세**: real_time_prices 테이블
3. **거래 권한**: trading_permissions 테이블
4. **계좌 잔고**: account_balances 테이블
5. **체결 내역**: order_executions 테이블

### 우선순위
1. **높음**: broker_accounts, trading_permissions (계좌 연동 필수)
2. **중간**: account_balances, order_executions (거래 추적)
3. **낮음**: market_holidays, notification_settings (부가 기능)

### 예상 작업량
- **스키마 추가**: 1-2일
- **RLS 정책 설정**: 1일
- **API 연동**: 3-5일
- **테스트**: 2-3일

**총 예상**: 1-2주면 실전 매매 가능한 데이터베이스 구조 완성