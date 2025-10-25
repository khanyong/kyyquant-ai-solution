-- ========================================
-- 전략 조건에서 사용하는 지표 확인
-- ========================================

SELECT
  id,
  name,
  entry_conditions,
  exit_conditions,
  auto_execute,
  is_active
FROM strategies
WHERE auto_execute = true
  AND is_active = true
ORDER BY name;
