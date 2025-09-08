-- 🔒 프로덕션용 RLS 정책 복원
-- 개발이 끝나면 이 스크립트를 실행하여 보안 정책을 복원하세요.

-- 1. backtest_results 테이블 - 개발 정책 제거 및 프로덕션 정책 복원
DROP POLICY IF EXISTS "Dev - Allow all read access to backtest_results" ON backtest_results;
DROP POLICY IF EXISTS "Dev - Allow all insert to backtest_results" ON backtest_results;
DROP POLICY IF EXISTS "Dev - Allow all update to backtest_results" ON backtest_results;
DROP POLICY IF EXISTS "Dev - Allow all delete from backtest_results" ON backtest_results;

CREATE POLICY "Users can view own backtest results" ON backtest_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own backtest results" ON backtest_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own backtest results" ON backtest_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own backtest results" ON backtest_results
    FOR DELETE USING (auth.uid() = user_id);

-- 2. strategies 테이블 - 개발 정책 제거 및 프로덕션 정책 복원
DROP POLICY IF EXISTS "Dev - Allow all read access to strategies" ON strategies;
DROP POLICY IF EXISTS "Dev - Allow all insert to strategies" ON strategies;
DROP POLICY IF EXISTS "Dev - Allow all update to strategies" ON strategies;
DROP POLICY IF EXISTS "Dev - Allow all delete from strategies" ON strategies;

CREATE POLICY "Users can view own strategies" ON strategies
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own strategies" ON strategies
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own strategies" ON strategies
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own strategies" ON strategies
    FOR DELETE USING (auth.uid() = user_id);

-- 3. saved_filters 테이블 - 개발 정책 제거 및 프로덕션 정책 복원
DROP POLICY IF EXISTS "Dev - Allow all read access to saved_filters" ON saved_filters;
DROP POLICY IF EXISTS "Dev - Allow all insert to saved_filters" ON saved_filters;
DROP POLICY IF EXISTS "Dev - Allow all update to saved_filters" ON saved_filters;
DROP POLICY IF EXISTS "Dev - Allow all delete from saved_filters" ON saved_filters;

CREATE POLICY "Users can view own filters" ON saved_filters
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own filters" ON saved_filters
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own filters" ON saved_filters
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own filters" ON saved_filters
    FOR DELETE USING (auth.uid() = user_id);

-- 확인 메시지
DO $$
BEGIN
    RAISE NOTICE '✅ 프로덕션 RLS 정책이 복원되었습니다. 각 사용자는 자신의 데이터만 접근 가능합니다.';
END $$;