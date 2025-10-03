-- indicator_columns 테이블의 MACD 컬럼명 수정

-- 1. 현재 MACD 관련 컬럼 확인
SELECT
    indicator_name,
    column_name,
    output_order,
    is_active
FROM indicator_columns
WHERE indicator_name = 'macd'
ORDER BY output_order;

-- 2. MACD의 첫 번째 컬럼명을 'macd'에서 'macd_line'으로 수정
UPDATE indicator_columns
SET column_name = 'macd_line'
WHERE indicator_name = 'macd' 
AND column_name = 'macd'
AND output_order = 1;

-- 3. 수정 확인
SELECT
    indicator_name,
    column_name,
    output_order,
    is_active
FROM indicator_columns
WHERE indicator_name = 'macd'
ORDER BY output_order;

-- 4. 모든 지표의 컬럼 확인
SELECT
    indicator_name,
    array_agg(column_name ORDER BY output_order) as columns
FROM indicator_columns
WHERE is_active = true
GROUP BY indicator_name
ORDER BY indicator_name;
