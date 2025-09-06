-- type 체크 제약조건 삭제 후 재생성
ALTER TABLE public.strategies DROP CONSTRAINT IF EXISTS strategies_type_check;

-- 더 많은 전략 타입을 허용하는 새 제약조건 추가
ALTER TABLE public.strategies 
ADD CONSTRAINT strategies_type_check 
CHECK (type IS NULL OR type IN (
    'TECHNICAL', 
    'FUNDAMENTAL', 
    'HYBRID',
    'sma',
    'rsi', 
    'momentum',
    'bollinger',
    'macd',
    'ichimoku',
    'volume_breakout',
    'pair_trading',
    'custom'
));

-- 이제 테스트 데이터 삽입 (타입 문제 해결됨)
INSERT INTO public.strategies (
  user_id,
  name,
  description,
  type,
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
  '전략빌더 테스트 SMA',
  '전략빌더에서 생성한 이동평균 전략',
  'sma',
  '{"short_window": 20, "long_window": 60}'::jsonb,
  '{"list": []}'::jsonb,
  '{"buy": []}'::jsonb,
  '{"sell": []}'::jsonb,
  '{"stopLoss": -5, "takeProfit": 10}'::jsonb,
  true,
  false,
  10
) ON CONFLICT (id) DO UPDATE SET
  updated_at = NOW();

-- RSI 전략 예시도 추가
INSERT INTO public.strategies (
  user_id,
  name,
  description,
  type,
  config,
  is_active,
  is_test_mode,
  position_size
) VALUES (
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
  'RSI 과매수/과매도',
  'RSI 30/70 전략',
  'rsi',
  '{"rsi_period": 14, "oversold": 30, "overbought": 70}'::jsonb,
  true,
  false,
  10
) ON CONFLICT (id) DO UPDATE SET
  updated_at = NOW();

-- 확인
SELECT 
  id,
  name,
  type,
  config,
  is_active
FROM public.strategies 
WHERE is_active = true
ORDER BY created_at DESC;