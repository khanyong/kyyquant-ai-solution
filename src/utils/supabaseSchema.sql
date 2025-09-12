-- Supabase strategies 테이블 스키마 업데이트
-- 전략 공유 기능을 위한 컬럼 추가

-- 기존 테이블에 is_public 컬럼이 없다면 추가
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT false;

-- 인덱스 추가 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_strategies_is_public ON strategies(is_public);
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_created_at ON strategies(created_at);

-- Row Level Security (RLS) 정책 업데이트
-- 기존 정책 삭제 (있다면)
DROP POLICY IF EXISTS "Users can view their own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can view public strategies" ON strategies;
DROP POLICY IF EXISTS "Users can insert their own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can update their own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can delete their own strategies" ON strategies;

-- 새로운 RLS 정책 생성
-- 1. 사용자는 자신의 전략을 모두 볼 수 있음
CREATE POLICY "Users can view their own strategies" 
ON strategies FOR SELECT 
USING (auth.uid() = user_id);

-- 2. 모든 사용자는 공개된 전략을 볼 수 있음
CREATE POLICY "Users can view public strategies" 
ON strategies FOR SELECT 
USING (is_public = true);

-- 3. 사용자는 자신의 전략만 생성할 수 있음
CREATE POLICY "Users can insert their own strategies" 
ON strategies FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- 4. 사용자는 자신의 전략만 수정할 수 있음
CREATE POLICY "Users can update their own strategies" 
ON strategies FOR UPDATE 
USING (auth.uid() = user_id);

-- 5. 사용자는 자신의 전략만 삭제할 수 있음
CREATE POLICY "Users can delete their own strategies" 
ON strategies FOR DELETE 
USING (auth.uid() = user_id);

-- 즐겨찾기 기능을 위한 별도 테이블 (추후 구현)
CREATE TABLE IF NOT EXISTS strategy_favorites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, strategy_id)
);

-- 즐겨찾기 테이블 RLS 활성화
ALTER TABLE strategy_favorites ENABLE ROW LEVEL SECURITY;

-- 즐겨찾기 RLS 정책
CREATE POLICY "Users can manage their own favorites" 
ON strategy_favorites FOR ALL 
USING (auth.uid() = user_id);

-- 전략 통계 뷰 (선택사항)
CREATE OR REPLACE VIEW strategy_stats AS
SELECT 
  s.id,
  s.name,
  s.user_id,
  s.is_public,
  s.created_at,
  s.updated_at,
  COUNT(DISTINCT sf.user_id) as favorite_count,
  COUNT(DISTINCT br.id) as backtest_count
FROM strategies s
LEFT JOIN strategy_favorites sf ON s.id = sf.strategy_id
LEFT JOIN backtest_results br ON s.id = br.strategy_id
GROUP BY s.id, s.name, s.user_id, s.is_public, s.created_at, s.updated_at;