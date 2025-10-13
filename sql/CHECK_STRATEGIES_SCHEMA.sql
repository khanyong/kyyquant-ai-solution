-- strategies 테이블 스키마 확인
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'strategies'
ORDER BY ordinal_position;

-- 샘플 데이터 1개 확인
SELECT * FROM strategies LIMIT 1;

-- auto_execute 컬럼 존재 여부 확인
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'strategies'
    AND column_name LIKE '%auto%';

-- investment_filter 관련 컬럼 확인
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'strategies'
    AND (column_name LIKE '%filter%' OR column_name LIKE '%universe%');

-- 전략과 투자필터 연결 방식 확인 (JSON 필드 샘플)
SELECT
    id,
    name,
    CASE
        WHEN config::text LIKE '%filter%' THEN 'config에 filter 정보 있음'
        WHEN conditions::text LIKE '%filter%' THEN 'conditions에 filter 정보 있음'
        ELSE '연결 정보 없음'
    END as filter_connection
FROM strategies
LIMIT 3;
