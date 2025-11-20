-- =====================================================
-- 자금 할당 문제 진단
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 1. 현재 계좌 잔고
SELECT
  '=== 1. 계좌 잔고 ===' as section,
  account_number,
  total_cash,
  available_cash,
  stock_value,
  total_asset,
  updated_at
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- 2. 전략별 자금 할당 설정
SELECT
  '=== 2. 전략별 자금 할당 ===' as section,
  id,
  name,
  is_active,
  allocated_capital,
  allocated_percent,
  position_size,
  CASE
    WHEN allocated_capital > 0 THEN '✅ 고정 금액: ' || TO_CHAR(allocated_capital, 'FM999,999,999') || '원'
    WHEN allocated_percent > 0 THEN '✅ 비율: ' || allocated_percent || '%'
    ELSE '❌ 미설정 (allocated_capital=0, allocated_percent=0)'
  END as allocation_status,
  -- 실제 계산되는 금액
  CASE
    WHEN allocated_capital > 0 THEN allocated_capital
    WHEN allocated_percent > 0 THEN
      ROUND((SELECT available_cash FROM kw_account_balance
             WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
             ORDER BY updated_at DESC LIMIT 1) * allocated_percent / 100)
    ELSE 0
  END as calculated_amount,
  TO_CHAR(
    CASE
      WHEN allocated_capital > 0 THEN allocated_capital
      WHEN allocated_percent > 0 THEN
        ROUND((SELECT available_cash FROM kw_account_balance
               WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
               ORDER BY updated_at DESC LIMIT 1) * allocated_percent / 100)
      ELSE 0
    END,
    'FM999,999,999'
  ) || '원' as calculated_display
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
ORDER BY name;

-- 3. 전체 배분 합계
SELECT
  '=== 3. 전체 배분 현황 ===' as section,
  COUNT(*) as active_strategy_count,
  SUM(allocated_percent) as total_allocated_percent,
  SUM(allocated_capital) as total_allocated_capital,
  (SELECT available_cash FROM kw_account_balance
   WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
   ORDER BY updated_at DESC LIMIT 1) as account_balance,
  -- 비율 기준 총 할당 금액
  ROUND((SELECT available_cash FROM kw_account_balance
         WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
         ORDER BY updated_at DESC LIMIT 1) * SUM(allocated_percent) / 100) as total_by_percent,
  CASE
    WHEN SUM(allocated_percent) > 100 THEN '⚠️ 배분 비율 합계가 100% 초과 (' || SUM(allocated_percent) || '%)'
    WHEN SUM(allocated_percent) = 0 AND SUM(allocated_capital) = 0 THEN '❌ 모든 전략에 자금 미배분'
    ELSE '✅ 정상'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- 4. 문제 진단
SELECT
  '=== 4. 🔍 문제 진단 ===' as section,
  CASE
    WHEN (SELECT COUNT(*) FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') = 0
      THEN '❌ 계좌 잔고 데이터 없음 (키움 계좌 동기화 필요)'
    WHEN (SELECT available_cash FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' ORDER BY updated_at DESC LIMIT 1) = 0
      THEN '❌ 계좌 잔고 0원'
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND (allocated_percent > 0 OR allocated_capital > 0)) = 0
      THEN '❌ 모든 전략의 allocated_percent와 allocated_capital이 0 (UI에서 50% 설정했지만 DB에 반영 안됨)'
    WHEN (SELECT SUM(allocated_percent) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) > 100
      THEN '⚠️ 배분 비율 합계 초과 (' || (SELECT SUM(allocated_percent) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) || '%)'
    ELSE '✅ 설정 정상'
  END as diagnosis,
  CASE
    WHEN (SELECT COUNT(*) FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') = 0
      THEN '→ 키움 계좌 동기화 버튼 클릭'
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND (allocated_percent > 0 OR allocated_capital > 0)) = 0
      THEN '→ UI에서 설정한 50%가 DB에 저장되지 않음. 프론트엔드 코드에서 UPDATE 쿼리 확인 필요'
    ELSE '→ 정상'
  END as solution;

-- 5. UI에서 설정했지만 DB에 반영되지 않은 경우 수동 업데이트
-- (전략 ID는 실제 활성화한 전략의 ID로 변경 필요)
SELECT
  '=== 5. 💡 임시 해결책 ===' as section,
  'UPDATE strategies SET allocated_percent = 50 WHERE id = ''' || id || ''' AND name = ''' || name || ''';' as update_query
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
  AND allocated_percent = 0
  AND allocated_capital = 0;
