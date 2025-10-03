-- MACD 지표의 output_columns 확인 및 수정 (text[] 타입)

-- 1. 현재 MACD 지표 확인
SELECT
    name,
    output_columns,
    array_length(output_columns, 1) as column_count
FROM indicators
WHERE name = 'macd';

-- 2. MACD 지표의 output_columns 수정 (text[] 형식)
UPDATE indicators
SET output_columns = ARRAY['macd_line', 'macd_signal', 'macd_hist']::text[]
WHERE name = 'macd';

-- 3. 수정 확인
SELECT
    name,
    output_columns,
    array_length(output_columns, 1) as column_count
FROM indicators
WHERE name = 'macd';

-- 4. 모든 지표의 output_columns 검증
SELECT
    name,
    output_columns,
    array_length(output_columns, 1) as column_count,
    CASE
        WHEN output_columns IS NULL THEN '❌ NULL'
        WHEN array_length(output_columns, 1) = 0 THEN '⚠️  EMPTY'
        WHEN array_length(output_columns, 1) IS NULL THEN '❌ NULL ARRAY'
        ELSE '✅ OK'
    END as status
FROM indicators
WHERE is_active = true
ORDER BY name;
