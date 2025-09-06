-- strategies 테이블은 이미 존재하므로 수정만 진행

-- RLS (Row Level Security) 비활성화 (개발 환경용)
ALTER TABLE public.strategies DISABLE ROW LEVEL SECURITY;

-- 모든 사용자가 strategies 테이블에 접근할 수 있도록 권한 부여
GRANT ALL ON public.strategies TO anon;
GRANT ALL ON public.strategies TO authenticated;
GRANT ALL ON public.strategies TO service_role;

-- 트리거가 이미 존재하면 삭제 후 재생성
DROP TRIGGER IF EXISTS update_strategies_updated_at ON public.strategies;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE
    ON public.strategies 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- 테스트 데이터 삽입 (실제 스키마에 맞게)
INSERT INTO public.strategies (
  user_id,
  name,
  description,
  type,
  config,  -- parameters가 아닌 config 사용
  indicators,
  entry_conditions,
  exit_conditions,
  risk_management,
  is_active,
  is_test_mode,
  position_size
) VALUES (
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
  '전략빌더 테스트',
  '전략빌더에서 생성한 테스트 전략',
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

-- 저장된 전략 확인
SELECT 
  id,
  name,
  description,
  type,
  config,
  is_active,
  created_at
FROM public.strategies 
WHERE is_active = true
ORDER BY created_at DESC
LIMIT 10;