-- ⚠️ 개발용 간단한 RLS 정책 - 실제 존재하는 테이블만 처리
-- 모든 사용자가 모든 데이터에 접근 가능

-- 1. backtest_results 테이블
DO $$
BEGIN
    -- 기존 정책 삭제
    DROP POLICY IF EXISTS "Users can view own backtest results" ON backtest_results;
    DROP POLICY IF EXISTS "Users can insert own backtest results" ON backtest_results;
    DROP POLICY IF EXISTS "Users can update own backtest results" ON backtest_results;
    DROP POLICY IF EXISTS "Users can delete own backtest results" ON backtest_results;
    
    -- 개발용 정책 생성
    CREATE POLICY "Dev - Allow all access" ON backtest_results
        FOR ALL USING (true);
    
    RAISE NOTICE '✅ backtest_results 테이블: 모든 접근 허용';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE '⚠️ backtest_results 테이블 정책 변경 실패: %', SQLERRM;
END $$;

-- 2. strategies 테이블
DO $$
BEGIN
    -- 기존 정책 삭제
    DROP POLICY IF EXISTS "Users can view own strategies" ON strategies;
    DROP POLICY IF EXISTS "Users can insert own strategies" ON strategies;
    DROP POLICY IF EXISTS "Users can update own strategies" ON strategies;
    DROP POLICY IF EXISTS "Users can delete own strategies" ON strategies;
    
    -- 개발용 정책 생성
    CREATE POLICY "Dev - Allow all access" ON strategies
        FOR ALL USING (true);
    
    RAISE NOTICE '✅ strategies 테이블: 모든 접근 허용';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE '⚠️ strategies 테이블 정책 변경 실패: %', SQLERRM;
END $$;

-- 3. kw_investment_filters 테이블
DO $$
BEGIN
    -- 기존 정책 삭제
    DROP POLICY IF EXISTS "Users can view own filters" ON kw_investment_filters;
    DROP POLICY IF EXISTS "Users can insert own filters" ON kw_investment_filters;
    DROP POLICY IF EXISTS "Users can update own filters" ON kw_investment_filters;
    DROP POLICY IF EXISTS "Users can delete own filters" ON kw_investment_filters;
    
    -- 개발용 정책 생성
    CREATE POLICY "Dev - Allow all access" ON kw_investment_filters
        FOR ALL USING (true);
    
    RAISE NOTICE '✅ kw_investment_filters 테이블: 모든 접근 허용';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE '⚠️ kw_investment_filters 테이블 정책 변경 실패: %', SQLERRM;
END $$;

-- 메시지
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '⚠️  개발 모드 활성화됨';
    RAISE NOTICE '모든 사용자가 모든 데이터에 접근 가능합니다!';
    RAISE NOTICE '프로덕션 배포 전에 반드시 보안 정책을 복원하세요!';
    RAISE NOTICE '========================================';
END $$;