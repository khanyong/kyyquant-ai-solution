-- =====================================================
-- 자동매매 활성화 및 투자 유니버스 설정
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 1. 자동매매 활성화 (4개 전략)
UPDATE strategies
SET
  auto_trade_enabled = true,
  auto_execute = true,
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND id IN (
    '0bc60860-8c5b-41e1-a919-2abe09bd12fc',  -- [템플릿] 볼린저밴드
    '19a10cf8-45fc-4a85-a54a-0960f74ea68f',  -- [분할] MACD+RSI 복합 전략
    'fcfcc830-856c-4ee6-93d3-8a556ecb71f0',  -- [템플릿] 골든크로스
    'de2718d0-f3fb-45ad-9610-50d46ca1bff0'   -- [분할] RSI 3단계 매수매도
  );

-- 2. 투자 유니버스 설정 (1개 전략)
-- 대표 종목: 삼성전자(005930), SK하이닉스(000660), 네이버(035420), 카카오(035720)
UPDATE strategies
SET
  target_stocks = ARRAY['005930', '000660', '035420', '035720'],
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND id = 'a0515a88-a220-40de-8538-5e503336005c'  -- [분할] 볼린저밴드 2단계 매수
  AND auto_trade_enabled = true;

-- 3. 결과 확인
SELECT
  '=== ✅ 업데이트 결과 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  target_stocks,
  COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) as stock_count,
  CASE
    WHEN auto_trade_enabled = true AND COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) > 0
      THEN '✅ 자동매매 활성화 + 종목 설정 완료'
    WHEN auto_trade_enabled = true AND COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) = 0
      THEN '⚠️ 자동매매 활성화됐지만 종목 없음'
    ELSE '❌ 여전히 비활성화'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
ORDER BY name;
