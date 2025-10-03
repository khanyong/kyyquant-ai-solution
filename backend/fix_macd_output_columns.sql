-- MACD 지표의 output_columns 확인 및 수정

-- 1. 현재 MACD 지표 확인
SELECT
    name,
    output_columns,
    formula
FROM indicators
WHERE name = 'macd';

-- 2. MACD 지표의 output_columns 수정
UPDATE indicators
SET output_columns = '["macd_line", "macd_signal", "macd_hist"]'::jsonb
WHERE name = 'macd';

-- 3. 수정 확인
SELECT
    name,
    output_columns,
    created_at,
    updated_at
FROM indicators
WHERE name = 'macd';

-- 4. 모든 지표의 output_columns 검증
SELECT
    name,
    output_columns,
    CASE
        WHEN output_columns IS NULL THEN '❌ NULL'
        WHEN jsonb_array_length(output_columns) = 0 THEN '⚠️  EMPTY'
        ELSE '✅ OK'
    END as status
FROM indicators
WHERE is_active = true
ORDER BY name;
