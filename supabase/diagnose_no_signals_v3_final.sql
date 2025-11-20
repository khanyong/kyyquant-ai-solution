-- =====================================================
-- 매수 신호 미발생 원인 진단 (최종본)
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 1. 활성 전략이 있는가?
SELECT
  '=== 1. 활성 전략 확인 ===' as section,
  COUNT(*) as active_strategy_count,
  STRING_AGG(name, ', ') as strategy_names,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 활성 전략 없음 → 전략을 먼저 생성하고 활성화하세요'
    ELSE '✅ 활성 전략 ' || COUNT(*) || '개 존재'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- 2. 전략별 상세 정보
SELECT
  '=== 2. 전략 상세 설정 ===' as section,
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
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, created_at DESC;

-- 3. 투자 유니버스 확인
SELECT
  '=== 3. 투자 유니버스 확인 ===' as section,
  s.name as strategy_name,
  CASE
    WHEN s.target_stocks IS NOT NULL THEN ARRAY_LENGTH(s.target_stocks, 1)
    WHEN s.universe IS NOT NULL THEN ARRAY_LENGTH(s.universe, 1)
    ELSE (SELECT COUNT(*) FROM investment_universe iu WHERE iu.strategy_id = s.id)
  END as stock_count,
  COALESCE(
    ARRAY_TO_STRING(s.target_stocks, ', '),
    ARRAY_TO_STRING(s.universe, ', '),
    (SELECT STRING_AGG(stock_code, ', ') FROM investment_universe iu WHERE iu.strategy_id = s.id)
  ) as stocks,
  CASE
    WHEN COALESCE(
      ARRAY_LENGTH(s.target_stocks, 1),
      ARRAY_LENGTH(s.universe, 1),
      (SELECT COUNT(*) FROM investment_universe iu WHERE iu.strategy_id = s.id)
    ) = 0 OR COALESCE(
      ARRAY_LENGTH(s.target_stocks, 1),
      ARRAY_LENGTH(s.universe, 1),
      (SELECT COUNT(*) FROM investment_universe iu WHERE iu.strategy_id = s.id)
    ) IS NULL
      THEN '❌ 투자 유니버스 비어있음 → 모니터링할 종목을 추가하세요'
    ELSE '✅ 모니터링 종목 설정됨'
  END as status
FROM strategies s
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true;

-- 4. investment_universe 테이블 확인
SELECT
  '=== 4. investment_universe 테이블 ===' as section,
  s.name as strategy_name,
  iu.stock_code,
  iu.stock_name,
  iu.created_at
FROM investment_universe iu
JOIN strategies s ON s.id = iu.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
ORDER BY s.name, iu.stock_code;

-- 5. strategy_monitoring 실행 여부
SELECT
  '=== 5. 조건 모니터링 워크플로우 ===' as section,
  COUNT(*) as monitored_stocks,
  MAX(updated_at) as last_update,
  ROUND(EXTRACT(EPOCH FROM (NOW() - COALESCE(MAX(updated_at), NOW() - INTERVAL '999 days'))) / 60) as minutes_since_update,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ strategy_monitoring 비어있음 → n8n workflow-v7-1 미실행'
    WHEN MAX(updated_at) < NOW() - INTERVAL '30 minutes' THEN '❌ 30분 이상 업데이트 없음 → workflow-v7-1 중단'
    WHEN MAX(updated_at) < NOW() - INTERVAL '5 minutes' THEN '⚠️ 5분 이상 업데이트 없음'
    ELSE '✅ 정상 작동 (최근 5분 이내)'
  END as status
FROM strategy_monitoring sm
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = sm.strategy_id
    AND s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
);

-- 6. 모니터링 중인 종목 상세
SELECT
  '=== 6. 모니터링 종목 현황 ===' as section,
  sm.stock_code,
  sm.stock_name,
  sm.current_price,
  sm.condition_match_score,
  sm.is_near_entry,
  sm.conditions_met,
  sm.updated_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - sm.updated_at)) / 60) as minutes_ago,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '🔴 조건 100% 충족 → 즉시 매수!'
    WHEN sm.condition_match_score >= 80 THEN '🟡 조건 80% 이상 → 매수 대기'
    WHEN sm.condition_match_score >= 50 THEN '🔵 조건 50% 이상'
    ELSE '⚪ 조건 미달'
  END as signal_status
FROM strategy_monitoring sm
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = sm.strategy_id
    AND s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
)
ORDER BY sm.condition_match_score DESC, sm.updated_at DESC
LIMIT 10;

-- 7. 최근 시그널 이력
SELECT
  '=== 7. 최근 시그널 (24시간) ===' as section,
  COUNT(*) as signal_count,
  MAX(created_at) as last_signal_time,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 시그널 없음'
    ELSE '✅ 시그널 ' || COUNT(*) || '건 발생'
  END as status
FROM trading_signals ts
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = ts.strategy_id
    AND s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
)
AND ts.created_at > NOW() - INTERVAL '24 hours';

-- 8. 시그널 상세
SELECT
  '=== 8. 시그널 상세 ===' as section,
  ts.stock_code,
  ts.stock_name,
  ts.signal_type,
  ts.current_price,
  ts.signal_status,
  ts.created_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - ts.created_at)) / 60) as minutes_ago
FROM trading_signals ts
WHERE EXISTS (
  SELECT 1 FROM strategies s
  WHERE s.id = ts.strategy_id
    AND s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
)
AND ts.created_at > NOW() - INTERVAL '24 hours'
ORDER BY ts.created_at DESC
LIMIT 10;

-- 9. 시장 데이터 상태
SELECT
  '=== 9. 시장 데이터 ===' as section,
  COUNT(*) as total_stocks,
  COUNT(CASE WHEN current_price > 0 THEN 1 END) as valid_price_count,
  MAX(updated_at) as last_update,
  ROUND(EXTRACT(EPOCH FROM (NOW() - COALESCE(MAX(updated_at), NOW() - INTERVAL '999 days'))) / 60) as minutes_since_update,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 시장 데이터 없음'
    WHEN MAX(updated_at) < NOW() - INTERVAL '30 minutes' THEN '⚠️ 오래된 데이터'
    ELSE '✅ 최신 데이터'
  END as status
FROM kw_price_current;

-- 10. 종합 진단 🔍
SELECT
  '=== 10. 🔍 종합 진단 ===' as section,
  CASE
    -- 1순위: 활성 전략
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '❌ 활성 전략 없음'

    -- 2순위: 자동매매 미활성화
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND (auto_trade_enabled = true OR auto_execute = true)) = 0
      THEN '❌ 자동매매 비활성화 (auto_trade_enabled 또는 auto_execute를 true로 설정)'

    -- 3순위: 투자 유니버스 없음
    WHEN NOT EXISTS (
      SELECT 1 FROM strategies s
      WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
        AND s.is_active = true
        AND (
          s.target_stocks IS NOT NULL AND ARRAY_LENGTH(s.target_stocks, 1) > 0
          OR s.universe IS NOT NULL AND ARRAY_LENGTH(s.universe, 1) > 0
          OR EXISTS (SELECT 1 FROM investment_universe iu WHERE iu.strategy_id = s.id)
        )
    )
      THEN '❌ 투자 유니버스 비어있음'

    -- 4순위: 워크플로우 미실행
    WHEN NOT EXISTS (SELECT 1 FROM strategy_monitoring sm)
      THEN '❌ workflow-v7-1 미실행 (n8n 확인)'

    -- 5순위: 워크플로우 중단
    WHEN (SELECT MAX(updated_at) FROM strategy_monitoring) < NOW() - INTERVAL '30 minutes'
      THEN '❌ workflow-v7-1 중단됨 (30분 이상 업데이트 없음)'

    -- 6순위: 시장 데이터 없음
    WHEN (SELECT COUNT(*) FROM kw_price_current WHERE current_price > 0) = 0
      THEN '❌ 시장 데이터 없음'

    -- 7순위: 조건 미달 (정상)
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) < 80
      THEN '⚠️ 정상: 조건 충족도 < 80점 (매수 조건 미달)'

    -- 8순위: 조건 근접 (정상)
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) < 100
      THEN '⏳ 정상: 조건 근접 중 (80-99점)'

    -- 9순위: 조건 100점이지만 신호 없음
    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) >= 100
      AND NOT EXISTS (
        SELECT 1 FROM trading_signals ts
        WHERE ts.created_at > NOW() - INTERVAL '5 minutes'
      )
      THEN '❌ 조건 100점이지만 신호 미발생 → workflow-v7-2 확인'

    ELSE '✅ 시스템 정상'
  END as diagnosis,

  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '→ 전략을 생성하고 is_active=true로 설정'

    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND (auto_trade_enabled = true OR auto_execute = true)) = 0
      THEN '→ 전략의 auto_trade_enabled 또는 auto_execute를 true로 업데이트'

    WHEN NOT EXISTS (
      SELECT 1 FROM strategies s
      WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
        AND s.is_active = true
        AND (
          s.target_stocks IS NOT NULL AND ARRAY_LENGTH(s.target_stocks, 1) > 0
          OR s.universe IS NOT NULL AND ARRAY_LENGTH(s.universe, 1) > 0
          OR EXISTS (SELECT 1 FROM investment_universe iu WHERE iu.strategy_id = s.id)
        )
    )
      THEN '→ target_stocks 또는 universe에 종목 코드 추가 (예: ARRAY[''005930'', ''000660''])'

    WHEN NOT EXISTS (SELECT 1 FROM strategy_monitoring)
      THEN '→ n8n에서 workflow-v7-1-condition-monitoring을 Active로 설정'

    WHEN COALESCE((SELECT MAX(condition_match_score) FROM strategy_monitoring), 0) < 80
      THEN '→ 시장 조건이 매수 조건을 충족할 때까지 대기 (정상)'

    ELSE '→ 계속 모니터링'
  END as solution;

-- 11. 최고 점수 종목
SELECT
  '=== 11. 🏆 최고 점수 종목 TOP 5 ===' as section,
  sm.stock_code,
  sm.stock_name,
  sm.condition_match_score as score,
  sm.current_price,
  sm.conditions_met,
  sm.updated_at,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '🔴 100점 → 즉시 매수!'
    WHEN sm.condition_match_score >= 90 THEN '🟠 90-99점 → 매우 근접'
    WHEN sm.condition_match_score >= 80 THEN '🟡 80-89점 → 근접'
    WHEN sm.condition_match_score >= 50 THEN '🔵 50-79점 → 중간'
    ELSE '⚪ <50점 → 낮음'
  END as status
FROM strategy_monitoring sm
ORDER BY sm.condition_match_score DESC
LIMIT 5;

-- 12. 자동매매 활성화 상태 확인
SELECT
  '=== 12. 자동매매 설정 확인 ===' as section,
  s.name,
  s.is_active,
  s.auto_trade_enabled,
  s.auto_execute,
  CASE
    WHEN s.is_active = false THEN '❌ 전략 비활성화'
    WHEN s.auto_trade_enabled = false AND s.auto_execute = false THEN '❌ 자동매매 꺼짐'
    WHEN s.auto_trade_enabled = true OR s.auto_execute = true THEN '✅ 자동매매 활성화'
    ELSE '⚠️ 확인 필요'
  END as status,
  CASE
    WHEN s.is_active = false THEN 'UPDATE strategies SET is_active=true WHERE id=''' || s.id || ''';'
    WHEN s.auto_trade_enabled = false AND s.auto_execute = false THEN 'UPDATE strategies SET auto_trade_enabled=true WHERE id=''' || s.id || ''';'
    ELSE '설정 정상'
  END as fix_query
FROM strategies s
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY s.is_active DESC, s.created_at DESC;
