-- ⚠️ 개발용 RLS 정책 - 프로덕션에서는 사용하지 마세요!
-- 이 정책은 모든 사용자가 모든 데이터에 접근할 수 있게 합니다.

-- 1. backtest_results 테이블 - 모든 접근 허용
DROP POLICY IF EXISTS "Users can view own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can insert own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can update own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can delete own backtest results" ON backtest_results;

CREATE POLICY "Dev - Allow all read access to backtest_results" ON backtest_results
    FOR SELECT USING (true);

CREATE POLICY "Dev - Allow all insert to backtest_results" ON backtest_results
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Dev - Allow all update to backtest_results" ON backtest_results
    FOR UPDATE USING (true);

CREATE POLICY "Dev - Allow all delete from backtest_results" ON backtest_results
    FOR DELETE USING (true);

-- 2. strategies 테이블 - 모든 접근 허용
DROP POLICY IF EXISTS "Users can view own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can insert own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can update own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can delete own strategies" ON strategies;

CREATE POLICY "Dev - Allow all read access to strategies" ON strategies
    FOR SELECT USING (true);

CREATE POLICY "Dev - Allow all insert to strategies" ON strategies
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Dev - Allow all update to strategies" ON strategies
    FOR UPDATE USING (true);

CREATE POLICY "Dev - Allow all delete from strategies" ON strategies
    FOR DELETE USING (true);

-- 3. investment_filters 테이블 - 모든 접근 허용 (테이블이 존재하는 경우)
-- saved_filters 테이블이 없으므로 investment_filters나 다른 이름일 수 있음
-- 실제 테이블 이름에 맞게 수정 필요

-- investment_filters 테이블이 있다면:
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'investment_filters') THEN
        DROP POLICY IF EXISTS "Users can view own filters" ON investment_filters;
        DROP POLICY IF EXISTS "Users can insert own filters" ON investment_filters;
        DROP POLICY IF EXISTS "Users can update own filters" ON investment_filters;
        DROP POLICY IF EXISTS "Users can delete own filters" ON investment_filters;

        CREATE POLICY "Dev - Allow all read access to investment_filters" ON investment_filters
            FOR SELECT USING (true);
        CREATE POLICY "Dev - Allow all insert to investment_filters" ON investment_filters
            FOR INSERT WITH CHECK (true);
        CREATE POLICY "Dev - Allow all update to investment_filters" ON investment_filters
            FOR UPDATE USING (true);
        CREATE POLICY "Dev - Allow all delete from investment_filters" ON investment_filters
            FOR DELETE USING (true);
    END IF;
END $$;

-- 확인 메시지
DO $$
BEGIN
    RAISE NOTICE '⚠️ 개발용 RLS 정책이 적용되었습니다. 모든 사용자가 모든 데이터에 접근 가능합니다!';
    RAISE NOTICE '프로덕션 배포 전에 반드시 원래 정책으로 되돌리세요!';
END $$;