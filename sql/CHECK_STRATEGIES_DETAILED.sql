-- 1. strategies 테이블의 모든 컬럼 확인
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'strategies'
ORDER BY ordinal_position;

-- 2. 실제 전략 데이터 1개의 전체 구조 확인 (모든 컬럼)
SELECT *
FROM strategies
LIMIT 1;

-- 3. config JSON 필드의 키 확인
SELECT DISTINCT
    jsonb_object_keys(config) as config_keys
FROM strategies
WHERE config IS NOT NULL;

-- 4. conditions JSON 필드의 키 확인
SELECT DISTINCT
    jsonb_object_keys(conditions) as conditions_keys
FROM strategies
WHERE conditions IS NOT NULL;

-- 5. investment_filter_id 같은 컬럼이 있는지 확인
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'strategies'
    AND (column_name LIKE '%filter%'
         OR column_name LIKE '%universe%'
         OR column_name LIKE '%stock%');
