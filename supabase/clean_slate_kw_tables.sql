-- ============================================
-- 기존 중복 테이블 완전 삭제 후 새로 시작
-- 주의: 모든 데이터가 삭제됩니다!
-- ============================================

-- 1. 외래키 제약 먼저 제거
ALTER TABLE IF EXISTS orders DROP CONSTRAINT IF EXISTS orders_stock_code_fkey;
ALTER TABLE IF EXISTS portfolio DROP CONSTRAINT IF EXISTS portfolio_stock_code_fkey;
ALTER TABLE IF EXISTS trading_signals DROP CONSTRAINT IF EXISTS trading_signals_stock_code_fkey;
ALTER TABLE IF EXISTS realtime_prices DROP CONSTRAINT IF EXISTS realtime_prices_stock_code_fkey;

-- 2. 중복 테이블 완전 삭제
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS price_data CASCADE;
DROP TABLE IF EXISTS market_data CASCADE;
DROP TABLE IF EXISTS market_data_cache CASCADE;
DROP TABLE IF EXISTS news_alerts CASCADE;
DROP TABLE IF EXISTS realtime_prices CASCADE;
DROP TABLE IF EXISTS financial_ratios CASCADE;
DROP TABLE IF EXISTS investor_trading CASCADE;
DROP TABLE IF EXISTS realtime_price CASCADE;
DROP TABLE IF EXISTS stock_master CASCADE;

-- 3. 기존 백업 테이블도 삭제 (있다면)
DROP TABLE IF EXISTS _old_stocks CASCADE;
DROP TABLE IF EXISTS _old_price_data CASCADE;
DROP TABLE IF EXISTS _old_market_data CASCADE;
DROP TABLE IF EXISTS _old_news_alerts CASCADE;
DROP TABLE IF EXISTS _backup_stocks CASCADE;
DROP TABLE IF EXISTS _backup_price_data CASCADE;
DROP TABLE IF EXISTS _backup_market_data CASCADE;
DROP TABLE IF EXISTS _backup_news_alerts CASCADE;

-- 4. 확인
SELECT 'All duplicate tables removed!' as status;

-- 5. 이제 create_all_tables_consistent.sql 실행하여 kw_ 테이블 생성
-- 다음 파일을 실행하세요: create_all_tables_consistent.sql

-- 6. 호환성을 위한 뷰 생성 (기존 코드가 작동하도록)
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

-- 7. 외래키 재설정 (kw_stock_master 참조)
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

-- 8. 최종 확인
SELECT 
    'Tables' as type,
    COUNT(*) as count 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('stocks', 'price_data', 'market_data', 'news_alerts')
UNION ALL
SELECT 
    'Views (for compatibility)' as type,
    COUNT(*) as count
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name IN ('stocks', 'price_data', 'market_data', 'news_alerts', 'realtime_prices')
UNION ALL
SELECT 
    'New kw_ tables' as type,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name LIKE 'kw_%';

SELECT '✅ Clean slate completed! Now run create_all_tables_consistent.sql' as next_step;