-- =====================================================
-- allocated_percent 50% 설정
-- =====================================================

-- 3개 전략에 50% 할당
UPDATE strategies
SET
  allocated_percent = 50,
  updated_at = NOW()
WHERE id IN (
  '19a10cf8-45fc-4a85-a54a-0960f74ea68f',  -- [분할] MACD+RSI 복합 전략
  'fcfcc830-856c-4ee6-93d3-8a556ecb71f0',  -- [템플릿] 골든크로스
  'de2718d0-f3fb-45ad-9610-50d46ca1bff0'   -- [분할] RSI 3단계 매수매도
);

-- 결과 확인
SELECT
  '=== ✅ 업데이트 결과 ===' as section,
  name,
  allocated_percent || '%' as percent,
  allocated_capital,
  -- 계좌 잔고 기준 실제 금액 계산
  TO_CHAR(
    ROUND((SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * allocated_percent / 100),
    'FM999,999,999'
  ) || '원' as allocated_amount,
  updated_at
FROM strategies
WHERE id IN (
  '19a10cf8-45fc-4a85-a54a-0960f74ea68f',
  'fcfcc830-856c-4ee6-93d3-8a556ecb71f0',
  'de2718d0-f3fb-45ad-9610-50d46ca1bff0'
)
ORDER BY name;

-- 전체 배분 합계 확인
SELECT
  '=== 전체 배분 현황 ===' as section,
  COUNT(*) as active_strategies,
  SUM(allocated_percent) || '%' as total_percent,
  TO_CHAR(
    (SELECT available_cash FROM kw_account_balance
     WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
     ORDER BY updated_at DESC LIMIT 1),
    'FM999,999,999'
  ) || '원' as account_balance,
  TO_CHAR(
    ROUND((SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * SUM(allocated_percent) / 100),
    'FM999,999,999'
  ) || '원' as total_allocated,
  CASE
    WHEN SUM(allocated_percent) > 100 THEN '⚠️ 100% 초과'
    WHEN SUM(allocated_percent) = 100 THEN '✅ 정확히 100%'
    ELSE '✅ ' || SUM(allocated_percent) || '% 사용'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;
