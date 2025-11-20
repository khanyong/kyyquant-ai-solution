-- 모든 전략 상세 정보

SELECT
  id,
  user_id,
  name,
  allocated_capital,
  is_active,
  created_at
FROM strategies
ORDER BY created_at DESC;
