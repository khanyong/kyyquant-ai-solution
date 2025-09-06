-- ============================================
-- 기존 테이블을 kw_ 테이블로 마이그레이션
-- ============================================

-- 1. 기존 데이터 백업 (안전을 위해)
CREATE TABLE IF NOT EXISTS _backup_stocks AS SELECT * FROM stocks;
CREATE TABLE IF NOT EXISTS _backup_price_data AS SELECT * FROM price_data;
CREATE TABLE IF NOT EXISTS _backup_market_data AS SELECT * FROM market_data;
CREATE TABLE IF NOT EXISTS _backup_news_alerts AS SELECT * FROM news_alerts;

-- 2. kw_ 테이블로 데이터 이전
-- 종목 마스터 이전
INSERT INTO kw_stock_master (stock_code, stock_name, market, sector_name)
SELECT code, name, market, sector 
FROM stocks
ON CONFLICT (stock_code) DO NOTHING;

-- 일봉 데이터 이전
INSERT INTO kw_price_daily (stock_code, trade_date, open, high, low, close, volume, trading_value)
SELECT stock_code, date, open, high, low, close, volume, trading_value
FROM price_data
ON CONFLICT (stock_code, trade_date) DO NOTHING;

-- 실시간 가격 이전 (market_data와 realtime_prices 통합)
INSERT INTO kw_price_current (
    stock_code, 
    current_price, 
    change_price, 
    change_rate, 
    volume,
    trading_value
)
SELECT 
    stock_code,
    current_price,
    change_amount,
    change_rate,
    volume,
    trading_value
FROM market_data
ON CONFLICT (stock_code) DO UPDATE SET
    current_price = EXCLUDED.current_price,
    change_price = EXCLUDED.change_price,
    change_rate = EXCLUDED.change_rate,
    volume = EXCLUDED.volume,
    updated_at = NOW();

-- 뉴스 데이터 이전
INSERT INTO kw_info_news (stock_code, news_datetime, title, content, source, url)
SELECT 
    stock_code,
    published_at,
    title,
    content,
    source,
    url
FROM news_alerts
WHERE stock_code IS NOT NULL;

-- 3. 외래키 참조 업데이트
-- orders 테이블의 stock_code 참조 변경
ALTER TABLE orders 
    DROP CONSTRAINT IF EXISTS orders_stock_code_fkey;

ALTER TABLE orders 
    ADD CONSTRAINT orders_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code);

-- portfolio 테이블의 stock_code 참조 변경
ALTER TABLE portfolio 
    DROP CONSTRAINT IF EXISTS portfolio_stock_code_fkey;

ALTER TABLE portfolio 
    ADD CONSTRAINT portfolio_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code);

-- trading_signals 테이블의 stock_code 참조 변경
ALTER TABLE trading_signals 
    DROP CONSTRAINT IF EXISTS trading_signals_stock_code_fkey;

ALTER TABLE trading_signals 
    ADD CONSTRAINT trading_signals_stock_code_fkey 
    FOREIGN KEY (stock_code) 
    REFERENCES kw_stock_master(stock_code);

-- 4. 뷰 생성 (하위 호환성 유지)
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
    CASE 
        WHEN title LIKE '%상승%' OR title LIKE '%호재%' THEN 'POSITIVE'
        WHEN title LIKE '%하락%' OR title LIKE '%악재%' THEN 'NEGATIVE'
        ELSE 'NEUTRAL'
    END as sentiment,
    'MEDIUM' as importance,
    news_datetime as published_at,
    news_datetime as created_at
FROM kw_info_news;

-- 5. 기존 테이블 삭제 (뷰로 대체되었으므로)
-- 주의: 이 명령은 데이터 백업 확인 후 실행
/*
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS price_data CASCADE;
DROP TABLE IF EXISTS market_data CASCADE;
DROP TABLE IF EXISTS news_alerts CASCADE;
*/

-- 6. 확인
SELECT 'Migration completed!' as status;

-- 테이블 상태 확인
SELECT 
    'Original Tables' as category,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('stocks', 'price_data', 'market_data', 'news_alerts')
UNION ALL
SELECT 
    'New kw_ Tables' as category,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name LIKE 'kw_%'
UNION ALL
SELECT 
    'Compatibility Views' as category,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'VIEW'
    AND table_name IN ('stocks', 'price_data', 'market_data', 'news_alerts');