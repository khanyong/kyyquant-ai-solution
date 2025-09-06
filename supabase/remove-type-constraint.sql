-- type 컬럼의 체크 제약조건 제거
ALTER TABLE public.strategies DROP CONSTRAINT IF EXISTS strategies_type_check;

-- 테스트 데이터 삽입 (type을 null 또는 원하는 값으로)
INSERT INTO public.strategies (
  user_id,
  name,
  description,
  type,  -- null로 설정
  config,
  indicators,
  entry_conditions,
  exit_conditions,
  risk_management,
  is_active,
  is_test_mode,
  position_size
) VALUES (
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
  '전략빌더 SMA 테스트',
  '이동평균선 교차 전략',
  NULL,  -- type을 null로 설정
  '{"strategy_type": "sma", "short_window": 20, "long_window": 60}'::jsonb,
  '{"list": []}'::jsonb,
  '{"buy": []}'::jsonb,
  '{"sell": []}'::jsonb,
  '{"stopLoss": -5, "takeProfit": 10}'::jsonb,
  true,
  false,
  10
) ON CONFLICT (id) DO UPDATE SET
  updated_at = NOW();

-- RSI 전략 예시
INSERT INTO public.strategies (
  user_id,
  name,
  description,
  config,
  is_active,
  is_test_mode,
  position_size
) VALUES (
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
  'RSI 과매수/과매도 전략',
  'RSI 지표 기반 매매',
  '{"strategy_type": "rsi", "rsi_period": 14, "oversold": 30, "overbought": 70}'::jsonb,
  true,
  false,
  10
) ON CONFLICT (id) DO UPDATE SET
  updated_at = NOW();

-- 볼린저 밴드 전략 예시
INSERT INTO public.strategies (
  user_id,
  name,
  description,
  config,
  is_active,
  is_test_mode,
  position_size
) VALUES (
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
  '볼린저 밴드 전략',
  '상하단 밴드 터치 매매',
  '{"strategy_type": "bollinger", "period": 20, "std_dev": 2}'::jsonb,
  true,
  false,
  10
) ON CONFLICT (id) DO UPDATE SET
  updated_at = NOW();

-- 저장된 전략 확인
SELECT 
  id,
  name,
  type,
  config->>'strategy_type' as strategy_type,
  config,
  is_active,
  created_at
FROM public.strategies 
WHERE is_active = true
ORDER BY created_at DESC
LIMIT 10;