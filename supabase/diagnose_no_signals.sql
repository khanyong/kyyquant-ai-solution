-- =====================================================
-- 매수 신호 미발생 원인 진단
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 1. 활성 전략이 있는가?
SELECT
  '=== 1. 활성 전략 확인 ===' as section,
  COUNT(*) as active_strategy_count,
  STRING_AGG(name, ', ') as strategy_names,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 활성 전략 없음 → 전략을 먼저 생성하고 활성화하세요'
    ELSE '✅ 활성 전략 존재'
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
  position_size_percent,
  max_positions,
  max_investment_per_stock,
  entry_conditions,
  exit_conditions,
  created_at,
  updated_at
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, created_at DESC;

-- 3. 투자 유니버스 (모니터링할 종목)가 있는가?
SELECT
  '=== 3. 투자 유니버스 확인 ===' as section,
  s.name as strategy_name,
  COUNT(iu.stock_code) as universe_stock_count,
  STRING_AGG(iu.stock_code || '(' || iu.stock_name || ')', ', ') as stocks,
  CASE
    WHEN COUNT(iu.stock_code) = 0 THEN '❌ 투자 유니버스 비어있음 → 모니터링할 종목을 추가하세요'
    ELSE '✅ 모니터링 종목 ' || COUNT(iu.stock_code) || '개 설정됨'
  END as status
FROM strategies s
LEFT JOIN investment_universe iu ON iu.strategy_id = s.id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
GROUP BY s.id, s.name;

-- 4. 투자 유니버스 상세
SELECT
  '=== 4. 투자 유니버스 상세 ===' as section,
  s.name as strategy_name,
  iu.stock_code,
  iu.stock_name,
  iu.created_at
FROM investment_universe iu
JOIN strategies s ON s.id = iu.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
ORDER BY s.name, iu.stock_code;

-- 5. strategy_monitoring 테이블에 데이터가 쌓이고 있는가? (워크플로우 v7-1 실행 확인)
SELECT
  '=== 5. 조건 모니터링 실행 여부 ===' as section,
  COUNT(*) as monitored_stocks,
  MAX(updated_at) as last_update,
  EXTRACT(EPOCH FROM (NOW() - MAX(updated_at))) / 60 as minutes_since_update,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ strategy_monitoring 테이블 비어있음 → workflow-v7-1이 실행되지 않음'
    WHEN MAX(updated_at) < NOW() - INTERVAL '30 minutes' THEN '❌ 30분 이상 업데이트 없음 → workflow-v7-1 중단됨'
    WHEN MAX(updated_at) < NOW() - INTERVAL '5 minutes' THEN '⚠️ 5분 이상 업데이트 없음 → workflow-v7-1 지연'
    ELSE '✅ 정상 작동 중 (최근 5분 이내 업데이트)'
  END as status
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 6. strategy_monitoring 상세 데이터
SELECT
  '=== 6. 모니터링 중인 종목 현황 ===' as section,
  s.name as strategy_name,
  sm.stock_code,
  sm.stock_name,
  sm.current_price,
  sm.condition_match_score,
  sm.is_near_entry,
  sm.conditions_met,
  sm.updated_at,
  EXTRACT(EPOCH FROM (NOW() - sm.updated_at)) / 60 as minutes_ago,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '🟢 조건 100% 충족 → 매수 신호 발생해야 함'
    WHEN sm.condition_match_score >= 80 THEN '🟡 조건 80% 이상 → 매수 대기 중'
    ELSE '⚪ 조건 미달'
  END as signal_status
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY sm.condition_match_score DESC, sm.updated_at DESC;

-- 7. 최근 발생한 시그널이 있는가?
SELECT
  '=== 7. 최근 시그널 이력 ===' as section,
  COUNT(*) as signal_count,
  MAX(created_at) as last_signal_time,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 시그널 없음 → 조건이 충족되지 않았거나 workflow-v7-2가 작동하지 않음'
    ELSE '✅ 시그널 ' || COUNT(*) || '건 발생'
  END as status
FROM trading_signals ts
JOIN strategies s ON s.id = ts.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND ts.created_at > NOW() - INTERVAL '24 hours';

-- 8. 시그널 상세 (최근 24시간)
SELECT
  '=== 8. 시그널 상세 (24시간) ===' as section,
  s.name as strategy_name,
  ts.stock_code,
  ts.stock_name,
  ts.signal_type,
  ts.signal_strength,
  ts.current_price,
  ts.signal_status,
  ts.created_at,
  EXTRACT(EPOCH FROM (NOW() - ts.created_at)) / 60 as minutes_ago
FROM trading_signals ts
JOIN strategies s ON s.id = ts.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND ts.created_at > NOW() - INTERVAL '24 hours'
ORDER BY ts.created_at DESC
LIMIT 10;

-- 9. 현재 시장 데이터 (kw_price_current) 확인
SELECT
  '=== 9. 시장 데이터 확인 ===' as section,
  COUNT(*) as total_stocks,
  COUNT(CASE WHEN current_price > 0 THEN 1 END) as valid_price_count,
  MAX(updated_at) as last_update,
  EXTRACT(EPOCH FROM (NOW() - MAX(updated_at))) / 60 as minutes_since_update,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 시장 데이터 없음 → 가격 데이터 수집이 안 됨'
    WHEN MAX(updated_at) < NOW() - INTERVAL '30 minutes' THEN '⚠️ 오래된 데이터 (30분 이상)'
    ELSE '✅ 최신 데이터'
  END as status
FROM kw_price_current;

-- 10. 투자 유니버스 종목의 가격 데이터 존재 여부
SELECT
  '=== 10. 유니버스 종목 가격 데이터 ===' as section,
  iu.stock_code,
  iu.stock_name,
  kp.current_price,
  kp.change_rate,
  kp.volume,
  kp.updated_at,
  CASE
    WHEN kp.stock_code IS NULL THEN '❌ 가격 데이터 없음'
    WHEN kp.current_price = 0 OR kp.current_price IS NULL THEN '❌ 가격 0원'
    ELSE '✅ 정상'
  END as data_status
FROM investment_universe iu
JOIN strategies s ON s.id = iu.strategy_id
LEFT JOIN kw_price_current kp ON kp.stock_code = iu.stock_code
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
ORDER BY iu.stock_code;

-- 11. n8n 워크플로우 실행 추적 (strategy_monitoring 업데이트 패턴)
SELECT
  '=== 11. 워크플로우 실행 패턴 ===' as section,
  DATE_TRUNC('hour', sm.updated_at) as hour,
  COUNT(DISTINCT sm.id) as update_count,
  AVG(sm.condition_match_score) as avg_score,
  MAX(sm.condition_match_score) as max_score
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND sm.updated_at > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', sm.updated_at)
ORDER BY hour DESC;

-- 12. 종합 진단 및 문제점 파악
SELECT
  '=== 12. 🔍 종합 진단 ===' as section,
  CASE
    -- 1순위: 활성 전략
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '❌ 원인: 활성 전략 없음'

    -- 2순위: 투자 유니버스
    WHEN (SELECT COUNT(*) FROM investment_universe iu
          JOIN strategies s ON s.id = iu.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND s.is_active = true) = 0
      THEN '❌ 원인: 투자 유니버스 비어있음 (모니터링할 종목 없음)'

    -- 3순위: 워크플로우 중단
    WHEN NOT EXISTS (SELECT 1 FROM strategy_monitoring sm
                     JOIN strategies s ON s.id = sm.strategy_id
                     WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8')
      THEN '❌ 원인: workflow-v7-1 (조건 모니터링) 미실행 → n8n에서 워크플로우 Active 확인'

    WHEN (SELECT MAX(updated_at) FROM strategy_monitoring sm
          JOIN strategies s ON s.id = sm.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') < NOW() - INTERVAL '30 minutes'
      THEN '❌ 원인: workflow-v7-1 중단됨 (30분 이상 업데이트 없음)'

    -- 4순위: 가격 데이터
    WHEN (SELECT COUNT(*) FROM kw_price_current WHERE current_price > 0) = 0
      THEN '❌ 원인: 시장 가격 데이터 없음 → 가격 수집 워크플로우 확인'

    -- 5순위: 조건 충족도
    WHEN (SELECT MAX(condition_match_score) FROM strategy_monitoring sm
          JOIN strategies s ON s.id = sm.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') < 80
      THEN '⚠️ 정상: 모든 종목의 조건 충족도 < 80점 → 매수 조건 미달 (시장 상황 대기 중)'

    -- 6순위: 조건 80점 이상이지만 100점 미만
    WHEN (SELECT MAX(condition_match_score) FROM strategy_monitoring sm
          JOIN strategies s ON s.id = sm.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') < 100
      THEN '⏳ 정상: 매수 조건 근접 중 (80-99점) → 100점 도달 시 자동 매수'

    -- 7순위: 조건 100점이지만 신호 없음
    WHEN (SELECT MAX(condition_match_score) FROM strategy_monitoring sm
          JOIN strategies s ON s.id = sm.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') >= 100
      AND NOT EXISTS (SELECT 1 FROM trading_signals ts
                      JOIN strategies s ON s.id = ts.strategy_id
                      WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
                        AND ts.created_at > NOW() - INTERVAL '5 minutes')
      THEN '❌ 원인: 조건 100점 충족했지만 신호 미발생 → workflow-v7-2 (주문 생성) 확인 필요'

    ELSE '✅ 정상: 시스템 작동 중 (조건 충족 대기)'
  END as diagnosis,

  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '해결: 전략 페이지에서 전략을 생성하고 활성화하세요'

    WHEN (SELECT COUNT(*) FROM investment_universe iu
          JOIN strategies s ON s.id = iu.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND s.is_active = true) = 0
      THEN '해결: 전략 설정에서 투자 유니버스 종목을 추가하세요'

    WHEN NOT EXISTS (SELECT 1 FROM strategy_monitoring sm
                     JOIN strategies s ON s.id = sm.strategy_id
                     WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8')
      THEN '해결: n8n 대시보드에서 workflow-v7-1-condition-monitoring-fixed를 Active로 설정'

    WHEN (SELECT MAX(condition_match_score) FROM strategy_monitoring sm
          JOIN strategies s ON s.id = sm.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') < 80
      THEN '해결: 시장 상황이 매수 조건을 충족할 때까지 대기 (정상 동작)'

    WHEN (SELECT MAX(condition_match_score) FROM strategy_monitoring sm
          JOIN strategies s ON s.id = sm.strategy_id
          WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') >= 100
      THEN '해결: n8n에서 workflow-v7-2-buy-order-creation-fixed 실행 로그 확인'

    ELSE '계속 모니터링'
  END as solution;

-- 13. 최고 점수 종목 확인
SELECT
  '=== 13. 🏆 최고 점수 종목 ===' as section,
  s.name as strategy_name,
  sm.stock_code,
  sm.stock_name,
  sm.condition_match_score as score,
  sm.conditions_met,
  sm.is_near_entry,
  sm.current_price,
  sm.updated_at,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '🔴 즉시 매수 신호 발생해야 함!'
    WHEN sm.condition_match_score >= 90 THEN '🟠 매우 근접 (90-99점)'
    WHEN sm.condition_match_score >= 80 THEN '🟡 근접 (80-89점)'
    WHEN sm.condition_match_score >= 50 THEN '🔵 중간 (50-79점)'
    ELSE '⚪ 낮음 (<50점)'
  END as status
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY sm.condition_match_score DESC
LIMIT 5;
