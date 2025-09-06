-- ============================================
-- 외래키 재연결 수정 버전
-- ============================================

-- 1. 호환성 뷰 생성 (컬럼 매핑 수정)
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
    NOW() as created_at  -- created_at이 없으면 현재 시간 사용
FROM kw_price_daily;

CREATE OR REPLACE VIEW market_data AS
SELECT 
    gen_random_uuid() as id,
    stock_code,
    NULL::varchar as stock_name,
    current_price,
    NULL::decimal as open_price,
    NULL::decimal as high_price,
    NULL::decimal as low_price,
    NULL::decimal as close_price,
    NULL::decimal as prev_close,
    volume,
    volume as accumulated_volume,
    trading_value,
    change_price as change_amount,
    change_rate,
    NULL::decimal as bid_price,
    NULL::decimal as ask_price,
    NULL::bigint as bid_volume,
    NULL::bigint as ask_volume,
    updated_at as timestamp
FROM kw_price_current
WHERE stock_code IS NOT NULL;  -- NULL 제외

CREATE OR REPLACE VIEW realtime_prices AS
SELECT 
    gen_random_uuid() as id,
    stock_code,
    current_price,
    change_rate,
    volume,
    NULL::decimal as bid_price,
    NULL::decimal as ask_price,
    updated_at as timestamp,
    stock_code as unique_stock
FROM kw_price_current
WHERE stock_code IS NOT NULL;

CREATE OR REPLACE VIEW news_alerts AS
SELECT 
    id,
    stock_code,
    title,
    content,
    source,
    url,
    'NEUTRAL'::varchar as sentiment,
    'MEDIUM'::varchar as importance,
    news_datetime as published_at,
    news_datetime as created_at
FROM kw_info_news
WHERE stock_code IS NOT NULL;

-- 2. 먼저 kw_stock_master에 기본 종목 데이터 삽입 (외래키 참조를 위해)
INSERT INTO kw_stock_master (stock_code, stock_name, market, sector_name) 
VALUES 
    ('005930', '삼성전자', 'KOSPI', '전기전자'),
    ('000660', 'SK하이닉스', 'KOSPI', '전기전자'),
    ('035720', '카카오', 'KOSPI', 'IT서비스'),
    ('035420', '네이버', 'KOSPI', 'IT서비스'),
    ('005380', '현대차', 'KOSPI', '자동차')
ON CONFLICT (stock_code) DO NOTHING;

-- 3. 외래키가 있는 테이블 확인
DO $$
BEGIN
    -- orders 테이블이 있고 stock_code 컬럼이 있으면 외래키 추가
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'stock_code'
    ) THEN
        -- 기존 외래키 제거
        ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_stock_code_fkey;
        -- 새 외래키 추가
        ALTER TABLE orders 
            ADD CONSTRAINT orders_stock_code_fkey 
            FOREIGN KEY (stock_code) 
            REFERENCES kw_stock_master(stock_code)
            ON DELETE SET NULL;
        RAISE NOTICE 'orders 테이블 외래키 설정 완료';
    END IF;

    -- portfolio 테이블
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'portfolio' AND column_name = 'stock_code'
    ) THEN
        ALTER TABLE portfolio DROP CONSTRAINT IF EXISTS portfolio_stock_code_fkey;
        ALTER TABLE portfolio 
            ADD CONSTRAINT portfolio_stock_code_fkey 
            FOREIGN KEY (stock_code) 
            REFERENCES kw_stock_master(stock_code)
            ON DELETE CASCADE;
        RAISE NOTICE 'portfolio 테이블 외래키 설정 완료';
    END IF;

    -- trading_signals 테이블
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trading_signals' AND column_name = 'stock_code'
    ) THEN
        ALTER TABLE trading_signals DROP CONSTRAINT IF EXISTS trading_signals_stock_code_fkey;
        ALTER TABLE trading_signals 
            ADD CONSTRAINT trading_signals_stock_code_fkey 
            FOREIGN KEY (stock_code) 
            REFERENCES kw_stock_master(stock_code)
            ON DELETE CASCADE;
        RAISE NOTICE 'trading_signals 테이블 외래키 설정 완료';
    END IF;

    -- positions 테이블
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'positions' AND column_name = 'stock_code'
    ) THEN
        ALTER TABLE positions DROP CONSTRAINT IF EXISTS positions_stock_code_fkey;
        ALTER TABLE positions 
            ADD CONSTRAINT positions_stock_code_fkey 
            FOREIGN KEY (stock_code) 
            REFERENCES kw_stock_master(stock_code)
            ON DELETE CASCADE;
        RAISE NOTICE 'positions 테이블 외래키 설정 완료';
    END IF;

    -- trades 테이블
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'trades' AND column_name = 'stock_code'
    ) THEN
        ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_stock_code_fkey;
        ALTER TABLE trades 
            ADD CONSTRAINT trades_stock_code_fkey 
            FOREIGN KEY (stock_code) 
            REFERENCES kw_stock_master(stock_code)
            ON DELETE SET NULL;
        RAISE NOTICE 'trades 테이블 외래키 설정 완료';
    END IF;
END $$;

-- 4. 최종 확인
SELECT '=== 시스템 상태 ===' as status;

-- 사용자 테이블
SELECT 
    'User Tables' as category,
    table_name,
    'EXISTS' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('profiles', 'portfolio', 'orders', 'strategies', 'backtest_results', 'account_balance');

-- kw_ 테이블 개수
SELECT 
    'KW Tables Count' as category,
    COUNT(*)::text as table_name,
    'CREATED' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name LIKE 'kw_%';

-- 호환성 뷰
SELECT 
    'Compatibility Views' as category,
    table_name,
    'CREATED' as status
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name IN ('stocks', 'price_data', 'market_data', 'realtime_prices', 'news_alerts');

-- 외래키
SELECT 
    'Foreign Keys' as category,
    table_name || ' -> kw_stock_master' as table_name,
    'LINKED' as status
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public'
    AND constraint_name LIKE '%stock_code_fkey%';

SELECT '✅ System setup completed!' as result;