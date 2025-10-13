-- 백테스트 결과의 investment_config 구조 확인
SELECT
  id,
  strategy_name,
  results_data->'investment_config' as investment_config,
  results_data->'investment_config'->>'universe_type' as universe_type,
  results_data->'investment_config'->>'filter_id' as filter_id,
  results_data->'investment_config'->>'filter_name' as filter_name,
  results_data->'investment_config'->>'stock_code' as stock_code,
  results_data->'investment_config'->>'stock_count' as stock_count,
  created_at
FROM backtest_results
ORDER BY created_at DESC
LIMIT 5;
