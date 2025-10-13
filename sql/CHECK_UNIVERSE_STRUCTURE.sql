-- 1. universe와 target_stocks 컬럼의 데이터 타입 확인
SELECT
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'strategies'
    AND column_name IN ('universe', 'target_stocks');

-- 2. 실제 데이터 샘플 확인
SELECT
    id,
    name,
    universe,
    target_stocks,
    is_active
FROM strategies
WHERE universe IS NOT NULL OR target_stocks IS NOT NULL
LIMIT 3;

-- 3. auto_execute 같은 자동매매 관련 컬럼 확인
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'strategies'
    AND (column_name LIKE '%auto%'
         OR column_name LIKE '%execute%'
         OR column_name LIKE '%active%');

-- 4. 전체 컬럼 목록 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'strategies'
ORDER BY ordinal_position;
