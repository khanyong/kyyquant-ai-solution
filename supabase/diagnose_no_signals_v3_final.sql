-- =====================================================
-- Diagnose missing buy signals (final)
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 1. Active strategies
SELECT
  '=== 1. 활성 전략 확인 ===' AS section,
  COUNT(*) AS active_strategy_count,
  STRING_AGG(name, ', ') AS strategy_names,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 활성 전략 없음'
    ELSE '✅ 활성 전략 ' || COUNT(*) || '개'
  END AS status
FROM strategies
WHERE is_active = true;

-- 2. Strategy details
SELECT
  '=== 2. 전략 상세 설정 ===' AS section,
  id,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  allocated_capital,
  allocated_percent,
  position_size,
  entry_conditions,
  exit_conditions,
  risk_management,
  universe,
  target_stocks,
  created_at,
  updated_at
FROM strategies
ORDER BY is_active DESC, created_at DESC;

SELECT
  '=== 3. 투자 유니버스 확인 ===' AS section,
  s.name AS strategy_name,
  CASE
    WHEN s.target_stocks IS NOT NULL THEN ARRAY_LENGTH(s.target_stocks, 1)
    WHEN s.universe IS NOT NULL THEN ARRAY_LENGTH(s.universe, 1)
    ELSE NULL  -- investment_universe 테이블이 없을 수 있으므로 보호
  END AS stock_count,
  CASE
    WHEN s.target_stocks IS NOT NULL THEN ARRAY_TO_STRING(s.target_stocks, ', ')
    WHEN s.universe IS NOT NULL THEN ARRAY_TO_STRING(s.universe, ', ')
    ELSE NULL
  END AS stocks,
  CASE
    WHEN COALESCE(
      ARRAY_LENGTH(s.target_stocks, 1),
      ARRAY_LENGTH(s.universe, 1)
    ) IS NULL
      OR COALESCE(
        ARRAY_LENGTH(s.target_stocks, 1),
        ARRAY_LENGTH(s.universe, 1)
      ) = 0
      THEN '❌ 유니버스 비어 있음 (investment_universe 테이블 없음 여부도 확인)'
    ELSE '✅ 모니터링 종목 설정됨'
  END AS status
FROM strategies s
WHERE s.is_active = true;

-- 4. investment_universe table (returns empty if table is missing)
SELECT
  '=== 4. investment_universe 테이블 ===' AS section,
  '테이블 없음 혹은 미사용' AS strategy_name,
  NULL::text AS stock_code,
  NULL::text AS stock_name,
  NULL::timestamptz AS created_at;

-- 5. strategy_monitoring execution status
SELECT
  '=== 5. 조건 모니터링 워크플로우 ===' AS section,
  COUNT(*) AS monitored_stocks,
  MAX(updated_at) AS last_update,
  ROUND(EXTRACT(EPOCH FROM (NOW() - COALESCE(MAX(updated_at), NOW() - INTERVAL '999 days'))) / 60) AS minutes_since_update,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ strategy_monitoring 비어 있음 → workflow-v7-1 확인'
    WHEN MAX(updated_at) < NOW() - INTERVAL '30 minutes' THEN '❌ 30분 이상 업데이트 없음'
    WHEN MAX(updated_at) < NOW() - INTERVAL '5 minutes' THEN '⚠️ 5분 이상 업데이트 없음'
    ELSE '✅ 최근 5분 이내 업데이트'
  END AS status
FROM strategy_monitoring sm
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = sm.strategy_id
);

-- 6. Monitored stocks
SELECT
  '=== 6. 모니터링 종목 현황 ===' AS section,
  sm.stock_code,
  sm.stock_name,
  sm.current_price,
  sm.condition_match_score,
  sm.is_near_entry,
  sm.conditions_met,
  sm.updated_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - sm.updated_at)) / 60) AS minutes_ago,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '🔴 100% → 즉시 매수'
    WHEN sm.condition_match_score >= 80 THEN '🟡 80% 이상 → 매수 대기'
    WHEN sm.condition_match_score >= 50 THEN '🔵 50% 이상'
    ELSE '⚪ 조건 미달'
  END AS signal_status
FROM strategy_monitoring sm
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = sm.strategy_id
)
ORDER BY sm.condition_match_score DESC, sm.updated_at DESC
LIMIT 10;

-- 7. Recent signals (24h)
SELECT
  '=== 7. 최근 시그널 (24시간) ===' AS section,
  COUNT(*) AS signal_count,
  MAX(created_at) AS last_signal_time,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 시그널 없음'
    ELSE '✅ 시그널 ' || COUNT(*) || '건'
  END AS status
FROM trading_signals ts
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = ts.strategy_id
)
AND ts.created_at > NOW() - INTERVAL '24 hours';

-- 8. Signal details
SELECT
  '=== 8. 시그널 상세 ===' AS section,
  ts.stock_code,
  ts.stock_name,
  ts.signal_type,
  ts.current_price,
  ts.signal_status,
  ts.created_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - ts.created_at)) / 60) AS minutes_ago
FROM trading_signals ts
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = ts.strategy_id
)
AND ts.created_at > NOW() - INTERVAL '24 hours'
ORDER BY ts.created_at DESC
LIMIT 10;

-- 9. Market data freshness
SELECT
  '=== 9. 시장 데이터 ===' AS section,
  COUNT(*) AS total_stocks,
  COUNT(CASE WHEN current_price > 0 THEN 1 END) AS valid_price_count,
  MAX(updated_at) AS last_update,
  ROUND(EXTRACT(EPOCH FROM (NOW() - COALESCE(MAX(updated_at), NOW() - INTERVAL '999 days'))) / 60) AS minutes_since_update,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 시장 데이터 없음'
    WHEN MAX(updated_at) < NOW() - INTERVAL '30 minutes' THEN '⚠️ 오래된 데이터'
    ELSE '✅ 최신 데이터'
  END AS status
FROM kw_price_current;

SELECT
  '=== 10. 🔍 종합 진단 ===' AS section,
  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE is_active = true) = 0
      THEN '❌ 활성 전략 없음'
    WHEN (SELECT COUNT(*) FROM strategies WHERE is_active = true AND (auto_trade_enabled = true OR auto_execute = true)) = 0
      THEN '❌ 자동매매 비활성'
    WHEN NOT EXISTS (
      SELECT 1 FROM strategies s
      WHERE s.is_active = true
        AND (
          (s.target_stocks IS NOT NULL AND ARRAY_LENGTH(s.target_stocks, 1) > 0)
          OR (s.universe IS NOT NULL AND ARRAY_LENGTH(s.universe, 1) > 0)
          -- investment_universe 테이블이 없을 수 있으므로 별도 테이블 조회는 생략
        )
    )
      THEN '❌ 투자 유니버스 비어 있음'
    WHEN NOT EXISTS (SELECT 1 FROM strategy_monitoring sm)
      THEN '❌ workflow-v7-1 미실행'
    WHEN (SELECT MAX(updated_at) FROM strategy_monitoring) < NOW() - INTERVAL '30 minutes'
      THEN '❌ workflow-v7-1 중단 (30분 이상)'
    WHEN (SELECT COUNT(*) FROM kw_price_current WHERE current_price > 0) = 0
      THEN '❌ 시장 데이터 없음'
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) < 80
      THEN '⚠️ 조건 충족도 < 80 (정상 대기)'
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) < 100
      THEN '⏳ 조건 근접 (80-99)'
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) >= 100
      AND NOT EXISTS (
        SELECT 1 FROM trading_signals ts
        WHERE ts.created_at > NOW() - INTERVAL '5 minutes'
      )
      THEN '❌ 조건 100인데 신호 없음 → workflow-v7-2 확인'
    ELSE '✅ 시스템 정상'
  END AS diagnosis,
  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE is_active = true) = 0
      THEN '→ 전략 생성 후 is_active=true 설정'
    WHEN (SELECT COUNT(*) FROM strategies WHERE is_active = true AND (auto_trade_enabled = true OR auto_execute = true)) = 0
      THEN '→ auto_trade_enabled 또는 auto_execute를 true로 설정'
    WHEN NOT EXISTS (
      SELECT 1 FROM strategies s
      WHERE s.is_active = true
        AND (
          (s.target_stocks IS NOT NULL AND ARRAY_LENGTH(s.target_stocks, 1) > 0)
          OR (s.universe IS NOT NULL AND ARRAY_LENGTH(s.universe, 1) > 0)
        )
    )
      THEN '→ target_stocks/universe에 종목 추가 (investment_universe 미구성 시)'
    WHEN NOT EXISTS (SELECT 1 FROM strategy_monitoring)
      THEN '→ n8n에서 workflow-v7-1-condition-monitoring 활성화'
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) < 80
      THEN '→ 시장 조건 충족까지 대기 (정상)'
    ELSE '→ 계속 모니터링'
  END AS solution;

-- 11. Top-5 highest scores
SELECT
  '=== 11. 🏆 최고 점수 종목 TOP 5 ===' AS section,
  sm.stock_code,
  sm.stock_name,
  sm.condition_match_score AS score,
  sm.current_price,
  sm.conditions_met,
  sm.updated_at,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '🔴 100점 → 즉시 매수'
    WHEN sm.condition_match_score >= 90 THEN '🟠 90-99점 → 매우 근접'
    WHEN sm.condition_match_score >= 80 THEN '🟡 80-89점 → 근접'
    WHEN sm.condition_match_score >= 50 THEN '🔵 50-79점 → 중간'
    ELSE '⚪ 50점 미만 → 낮음'
  END AS status
FROM strategy_monitoring sm
ORDER BY sm.condition_match_score DESC
LIMIT 5;

-- 12. Auto-trading flags
SELECT
  '=== 12. 자동매매 설정 확인 ===' AS section,
  s.name,
  s.is_active,
  s.auto_trade_enabled,
  s.auto_execute,
  CASE
    WHEN s.is_active = false THEN '❌ 전략 비활성화'
    WHEN s.auto_trade_enabled = false AND s.auto_execute = false THEN '❌ 자동매매 꺼짐'
    WHEN s.auto_trade_enabled = true OR s.auto_execute = true THEN '✅ 자동매매 활성'
    ELSE '⚠️ 확인 필요'
  END AS status,
  CASE
    WHEN s.is_active = false THEN 'UPDATE strategies SET is_active=true WHERE id=''' || s.id || ''';'
    WHEN s.auto_trade_enabled = false AND s.auto_execute = false THEN 'UPDATE strategies SET auto_trade_enabled=true WHERE id=''' || s.id || ''';'
    ELSE '설정 정상'
  END AS fix_query
FROM strategies s
ORDER BY s.is_active DESC, s.created_at DESC;
