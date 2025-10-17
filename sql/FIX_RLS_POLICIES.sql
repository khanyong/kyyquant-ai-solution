-- RLS 정책 수정: kw_account_balance, kw_portfolio 테이블

-- 1. 기존 RLS 정책 삭제
DROP POLICY IF EXISTS "Users can view their own account balance" ON kw_account_balance;
DROP POLICY IF EXISTS "Users can insert their own account balance" ON kw_account_balance;
DROP POLICY IF EXISTS "Users can update their own account balance" ON kw_account_balance;

DROP POLICY IF EXISTS "Users can view their own portfolio" ON kw_portfolio;
DROP POLICY IF EXISTS "Users can insert their own portfolio" ON kw_portfolio;
DROP POLICY IF EXISTS "Users can update their own portfolio" ON kw_portfolio;
DROP POLICY IF EXISTS "Users can delete their own portfolio" ON kw_portfolio;

-- 2. RLS 활성화 확인
ALTER TABLE kw_account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio ENABLE ROW LEVEL SECURITY;

-- 3. 새로운 RLS 정책 생성 (SELECT)
CREATE POLICY "Users can view their own account balance"
  ON kw_account_balance
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own portfolio"
  ON kw_portfolio
  FOR SELECT
  USING (auth.uid() = user_id);

-- 4. INSERT 정책 (Edge Function에서 사용)
CREATE POLICY "Users can insert their own account balance"
  ON kw_account_balance
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can insert their own portfolio"
  ON kw_portfolio
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 5. UPDATE 정책
CREATE POLICY "Users can update their own account balance"
  ON kw_account_balance
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own portfolio"
  ON kw_portfolio
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 6. DELETE 정책 (포트폴리오 전체 삭제 후 재생성용)
CREATE POLICY "Users can delete their own portfolio"
  ON kw_portfolio
  FOR DELETE
  USING (auth.uid() = user_id);

-- 7. 정책 확인
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd
FROM pg_policies
WHERE tablename IN ('kw_account_balance', 'kw_portfolio')
ORDER BY tablename, cmd;

-- 8. 테스트 쿼리 (현재 사용자로 조회 가능한지 확인)
SELECT
  'Account Balance Test' as test_name,
  COUNT(*) as count
FROM kw_account_balance
WHERE user_id = auth.uid();

SELECT
  'Portfolio Test' as test_name,
  COUNT(*) as count
FROM kw_portfolio
WHERE user_id = auth.uid();
