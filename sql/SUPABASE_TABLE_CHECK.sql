-- =====================================================
-- Supabase 기존 테이블 확인 SQL
-- =====================================================

-- 1. 모든 테이블 목록 조회
-- =====================================================
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    AND table_type = 'BASE TABLE'
ORDER BY table_schema, table_name;


-- 2. 각 테이블의 컬럼 구조 확인
-- =====================================================
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;


-- 3. 시장 데이터/시세 관련 테이블 검색
-- =====================================================
-- 'market', 'price', 'stock', 'quote' 키워드가 포함된 테이블
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_name = t.table_name AND table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND (
        table_name ILIKE '%market%' OR
        table_name ILIKE '%price%' OR
        table_name ILIKE '%stock%' OR
        table_name ILIKE '%quote%' OR
        table_name ILIKE '%trading%' OR
        table_name ILIKE '%candle%' OR
        table_name ILIKE '%ohlc%'
    )
ORDER BY table_name;


-- 4. 특정 테이블의 상세 구조 확인 (예시: stock_prices 테이블)
-- =====================================================
-- 테이블명을 실제 존재하는 테이블로 변경하여 실행
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default,
    (SELECT pg_catalog.col_description(c.oid, cols.ordinal_position::int)
     FROM pg_catalog.pg_class c
     WHERE c.oid = (SELECT ('"' || table_schema || '"."' || table_name || '"')::regclass::oid)
       AND c.relname = cols.table_name
    ) as column_description
FROM information_schema.columns cols
WHERE table_schema = 'public'
    AND table_name = 'stock_prices'  -- 테이블명 변경
ORDER BY ordinal_position;


-- 5. 시장 모니터링에 필요한 컬럼이 있는지 확인
-- =====================================================
-- 다음 컬럼들이 있으면 재사용 가능:
-- - stock_code (종목코드)
-- - current_price 또는 price (현재가)
-- - volume (거래량)
-- - timestamp 또는 created_at (시간)

SELECT
    table_name,
    STRING_AGG(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns
WHERE table_schema = 'public'
    AND (
        column_name ILIKE '%stock%' OR
        column_name ILIKE '%code%' OR
        column_name ILIKE '%price%' OR
        column_name ILIKE '%volume%' OR
        column_name ILIKE '%time%' OR
        column_name ILIKE '%date%'
    )
GROUP BY table_name
ORDER BY table_name;


-- 6. 테이블별 데이터 건수 확인
-- =====================================================
-- 실제 데이터가 있는 테이블 파악
SELECT
    schemaname,
    tablename,
    n_live_tup as row_count,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;


-- 7. 특정 테이블의 최신 데이터 샘플 확인
-- =====================================================
-- 테이블명을 실제 존재하는 테이블로 변경하여 실행
-- SELECT * FROM your_table_name
-- ORDER BY created_at DESC
-- LIMIT 5;


-- 8. 시간 컬럼이 있는 테이블 찾기
-- =====================================================
-- 실시간 모니터링에는 timestamp 컬럼 필수
SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
    AND data_type IN ('timestamp with time zone', 'timestamp without time zone', 'date', 'time')
ORDER BY table_name, column_name;


-- 9. 인덱스 확인
-- =====================================================
-- 기존 테이블의 인덱스가 시장 모니터링에 적합한지 확인
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;


-- 10. RLS (Row Level Security) 정책 확인
-- =====================================================
-- 기존 테이블의 보안 설정 확인
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;


-- =====================================================
-- 시장 모니터링 용도로 재사용 가능 여부 판단 기준
-- =====================================================
/*
재사용 가능한 테이블 조건:

✅ 필수 컬럼:
1. stock_code (VARCHAR) - 종목코드
2. price 또는 current_price (NUMERIC) - 현재가
3. timestamp 또는 created_at (TIMESTAMP) - 시간

✅ 권장 컬럼:
4. volume (BIGINT) - 거래량
5. high, low (NUMERIC) - 고가/저가
6. change_rate (NUMERIC) - 등락률

❌ 재사용 불가 조건:
- 컬럼 구조가 완전히 다른 경우
- 일봉/주봉 등 다른 용도의 데이터
- 실시간 업데이트가 불가능한 구조
*/


-- =====================================================
-- 예시: 기존 테이블이 적합한지 확인하는 쿼리
-- =====================================================
-- 아래 쿼리를 실행하여 조건을 만족하는 테이블 찾기

WITH table_columns AS (
    SELECT
        table_name,
        ARRAY_AGG(column_name) as columns
    FROM information_schema.columns
    WHERE table_schema = 'public'
    GROUP BY table_name
)
SELECT
    table_name,
    columns,
    -- 필수 컬럼 체크
    CASE
        WHEN columns && ARRAY['stock_code', 'code', 'symbol'] THEN '✅'
        ELSE '❌'
    END as has_stock_code,
    CASE
        WHEN columns && ARRAY['price', 'current_price', 'close'] THEN '✅'
        ELSE '❌'
    END as has_price,
    CASE
        WHEN columns && ARRAY['timestamp', 'created_at', 'date', 'time'] THEN '✅'
        ELSE '❌'
    END as has_timestamp,
    CASE
        WHEN columns && ARRAY['volume', 'trading_volume'] THEN '✅'
        ELSE '❌'
    END as has_volume
FROM table_columns
WHERE table_name NOT LIKE 'pg_%'
ORDER BY table_name;


-- =====================================================
-- 특정 테이블 데이터 확인 예시
-- =====================================================
-- 실제 테이블명으로 변경하여 실행
/*
-- 예시 1: stock_prices 테이블이 있는 경우
SELECT
    stock_code,
    current_price,
    volume,
    created_at,
    COUNT(*) OVER() as total_rows
FROM stock_prices
ORDER BY created_at DESC
LIMIT 10;

-- 예시 2: market_data 테이블이 있는 경우
SELECT
    symbol,
    price,
    volume,
    timestamp,
    COUNT(*) OVER() as total_rows
FROM market_data
ORDER BY timestamp DESC
LIMIT 10;
*/
