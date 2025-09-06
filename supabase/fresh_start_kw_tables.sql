-- ============================================
-- 데이터 이전 없이 새로 시작하는 방법
-- ============================================

-- 1. 기존 중복 테이블 이름 변경 (백업)
ALTER TABLE IF EXISTS stocks RENAME TO _old_stocks;
ALTER TABLE IF EXISTS price_data RENAME TO _old_price_data;
ALTER TABLE IF EXISTS market_data RENAME TO _old_market_data;
ALTER TABLE IF EXISTS news_alerts RENAME TO _old_news_alerts;

-- 2. kw_ 테이블 생성 (create_all_tables_consistent.sql 실행)
-- 이미 실행했다면 스킵

-- 3. 호환성을 위한 뷰 생성 (기존 코드가 작동하도록)
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

-- 4. 외래키 재설정
ALTER TABLE orders 
    DROP CONSTRAINT IF EXISTS orders_stock_code_fkey;

ALTER TABLE portfolio 
    DROP CONSTRAINT IF EXISTS portfolio_stock_code_fkey;

ALTER TABLE trading_signals 
    DROP CONSTRAINT IF EXISTS trading_signals_stock_code_fkey;

-- 외래키를 뷰가 아닌 실제 테이블로 연결
ALTER TABLE orders 
    ADD CONSTRAINT orders_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code);

ALTER TABLE portfolio 
    ADD CONSTRAINT portfolio_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code);

ALTER TABLE trading_signals 
    ADD CONSTRAINT trading_signals_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code);

-- 5. 확인
SELECT 'Fresh start completed!' as status;

-- 이전 테이블들 (백업)
SELECT 
    table_name,
    '(backup)' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name LIKE '_old_%'
ORDER BY table_name;

-- 새 kw_ 테이블들 (실제 사용)
SELECT 
    table_name,
    'active' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name LIKE 'kw_%'
ORDER BY table_name;

-- 호환성 뷰들
SELECT 
    table_name,
    'compatibility view' as status
FROM information_schema.views
WHERE table_schema = 'public' 
    AND table_name IN ('stocks', 'price_data', 'market_data', 'news_alerts')
ORDER BY table_name;

-- 6. 나중에 백업 테이블 삭제 (선택사항)
-- DROP TABLE IF EXISTS _old_stocks CASCADE;
-- DROP TABLE IF EXISTS _old_price_data CASCADE;
-- DROP TABLE IF EXISTS _old_market_data CASCADE;
-- DROP TABLE IF EXISTS _old_news_alerts CASCADE;