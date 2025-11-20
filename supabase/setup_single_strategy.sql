-- =====================================================
-- 1개 전략만 활성화 및 설정
-- =====================================================

-- 옵션 1: [템플릿] 볼린저밴드 1개만 사용
-- ================================================

-- STEP 1: 나머지 전략 모두 비활성화
UPDATE strategies
SET
  is_active = false,
  auto_trade_enabled = false,
  auto_execute = false,
  allocated_percent = 0,
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND name != '[템플릿] 볼린저밴드';

-- STEP 2: [템플릿] 볼린저밴드 완전 설정
UPDATE strategies
SET
  is_active = true,
  auto_trade_enabled = true,
  auto_execute = true,
  allocated_percent = 100,  -- 100% 할당 (1개 전략만 사용하므로)
  target_stocks = ARRAY['005930', '000660', '035420', '035720'],  -- 삼성전자, SK하이닉스, 네이버, 카카오
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND name = '[템플릿] 볼린저밴드';

-- STEP 3: 결과 확인
SELECT
  '=== ✅ 최종 설정 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  allocated_percent || '%' as allocation,
  target_stocks,
  COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) as stock_count,
  -- 실제 할당 금액
  TO_CHAR(
    ROUND((SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * allocated_percent / 100),
    'FM999,999,999'
  ) || '원' as allocated_amount,
  CASE
    WHEN is_active = false THEN '❌ 비활성화 (사용 안 함)'
    WHEN NOT auto_trade_enabled AND NOT auto_execute THEN '⚠️ 활성화되었지만 자동매매 꺼짐'
    WHEN COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) = 0 THEN '⚠️ 종목 미설정'
    ELSE '✅ 완전 설정 완료 (자동매매 가능)'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, name;

-- STEP 4: 요약
SELECT
  '=== 📊 요약 ===' as section,
  (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) as active_count,
  (SELECT name FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true LIMIT 1) as active_strategy,
  (SELECT SUM(allocated_percent) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) || '%' as total_allocation,
  (SELECT ARRAY_TO_STRING(target_stocks, ', ') FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true LIMIT 1) as monitoring_stocks,
  TO_CHAR(
    (SELECT available_cash FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' ORDER BY updated_at DESC LIMIT 1),
    'FM999,999,999'
  ) || '원' as account_balance,
  '✅ 설정 완료! 1-2분 후 n8n 워크플로우가 시작됩니다.' as next_step;
