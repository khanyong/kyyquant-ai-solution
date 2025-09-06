-- strategies 테이블 생성 (이미 있으면 건너뜀)
CREATE TABLE IF NOT EXISTS public.strategies (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  type VARCHAR(50),
  parameters JSONB,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS (Row Level Security) 비활성화 (개발 환경용)
ALTER TABLE public.strategies DISABLE ROW LEVEL SECURITY;

-- 모든 사용자가 strategies 테이블에 접근할 수 있도록 권한 부여
GRANT ALL ON public.strategies TO anon;
GRANT ALL ON public.strategies TO authenticated;
GRANT ALL ON public.strategies TO service_role;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON public.strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_is_active ON public.strategies(is_active);
CREATE INDEX IF NOT EXISTS idx_strategies_created_at ON public.strategies(created_at DESC);

-- 업데이트 시간 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거가 이미 존재하면 삭제 후 재생성
DROP TRIGGER IF EXISTS update_strategies_updated_at ON public.strategies;

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE
    ON public.strategies 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- 테스트 데이터 삽입 (config 컬럼 사용)
INSERT INTO public.strategies (
  name,
  description,
  type,
  config,  -- parameters 대신 config 사용
  is_active,
  user_id
) VALUES (
  '테스트 전략',
  '저장 테스트용 전략',
  'custom',
  '{"test": true}'::jsonb,
  true,
  'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid
) ON CONFLICT DO NOTHING;

-- 저장된 전략 확인
SELECT * FROM public.strategies WHERE is_active = true;