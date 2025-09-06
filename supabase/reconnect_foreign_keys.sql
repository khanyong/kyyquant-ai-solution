-- ============================================
-- kw_ 테이블 생성 후 외래키 재연결
-- create_all_tables_consistent.sql 실행 후 실행
-- ============================================

-- 1. 호환성 뷰 생성 (기존 코드 작동용)
CREATE OR REPLACE VIEW stocks AS 
SELECT 
    stock_code as code,
    stock_name as name,
    market,
    sector_name as sector,
    updated_at as created_at,
    updated_at
FROM kw_stock_master;

CREATE OR REPLACE VIEW price_data AS
SELECT 
    id,
    stock_code,
    trade_date as date,
    open,
    high,
    low,
    close,
    volume,
    trading_value,
    created_at
FROM kw_price_daily;

CREATE OR REPLACE VIEW market_data AS
SELECT 
    gen_random_uuid() as id,
    stock_code,
    NULL as stock_name,
    current_price,
    NULL as open_price,
    NULL as high_price,
    NULL as low_price,
    NULL as close_price,
    NULL as prev_close,
    volume,
    volume as accumulated_volume,
    trading_value,
    change_price as change_amount,
    change_rate,
    NULL as bid_price,
    NULL as ask_price,
    NULL as bid_volume,
    NULL as ask_volume,
    updated_at as timestamp
FROM kw_price_current;

CREATE OR REPLACE VIEW realtime_prices AS
SELECT 
    gen_random_uuid() as id,
    stock_code,
    current_price,
    change_rate,
    volume,
    NULL as bid_price,
    NULL as ask_price,
    updated_at as timestamp,
    stock_code as unique_stock
FROM kw_price_current;

CREATE OR REPLACE VIEW news_alerts AS
SELECT 
    id,
    stock_code,
    title,
    content,
    source,
    url,
    'NEUTRAL' as sentiment,
    'MEDIUM' as importance,
    news_datetime as published_at,
    news_datetime as created_at
FROM kw_info_news;

-- 2. 사용자 테이블의 외래키 재연결
-- orders 테이블
ALTER TABLE orders 
    ADD CONSTRAINT orders_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code)
    ON DELETE SET NULL;  -- 종목이 삭제되어도 주문 기록은 유지

-- portfolio 테이블
ALTER TABLE portfolio 
    ADD CONSTRAINT portfolio_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code)
    ON DELETE CASCADE;  -- 종목이 삭제되면 포트폴리오에서도 제거

-- trading_signals 테이블
ALTER TABLE trading_signals 
    ADD CONSTRAINT trading_signals_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code)
    ON DELETE CASCADE;  -- 종목이 삭제되면 신호도 제거

-- positions 테이블 (있다면)
ALTER TABLE positions 
    ADD CONSTRAINT positions_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code)
    ON DELETE CASCADE;

-- trades 테이블 (있다면)
ALTER TABLE trades 
    ADD CONSTRAINT trades_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code)
    ON DELETE SET NULL;

-- 3. 최종 확인
SELECT '=== 시스템 상태 확인 ===' as status;

-- 사용자 테이블 (보존됨)
SELECT 
    'User Tables' as category,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('profiles', 'portfolio', 'orders', 'strategies', 'backtest_results', 'account_balance');

-- kw_ 테이블 (새로 생성)
SELECT 
    'KW Tables' as category,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name LIKE 'kw_%';

-- 호환성 뷰
SELECT 
    'Compatibility Views' as category,
    COUNT(*) as count
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name IN ('stocks', 'price_data', 'market_data', 'realtime_prices', 'news_alerts');

-- 외래키 확인
SELECT 
    'Foreign Keys' as category,
    COUNT(*) as count
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public'
    AND table_name IN ('orders', 'portfolio', 'trading_signals', 'positions', 'trades');

SELECT '✅ System reconnected successfully!' as result;