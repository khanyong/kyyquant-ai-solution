-- positions 테이블 구조 확인
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'positions'
ORDER BY ordinal_position;

-- 현재 데이터 확인
SELECT * FROM positions LIMIT 5;
