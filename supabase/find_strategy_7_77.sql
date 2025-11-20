-- "나의 전략 7", "나의 전략 77" 찾기

SELECT
  id,
  name,
  allocated_capital,
  is_active,
  created_at
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND (name LIKE '%나의 전략%' OR name LIKE '%전략 7%')
ORDER BY name;

-- 모든 전략 목록 (이름 포함)
SELECT
  id,
  name,
  allocated_capital,
  is_active
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY created_at DESC;
