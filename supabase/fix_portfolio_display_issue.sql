-- ============================================================================
-- 포트폴리오 화면 0원 문제 종합 해결 스크립트
-- ============================================================================
-- 문제: 할당금액, 포트폴리오 통계, 시그널 현황이 모두 0 또는 부정확하게 표시됨
-- 원인: 1) 마이그레이션 미적용, 2) allocated_capital/percent = 0, 3) 데이터 부족
-- ============================================================================

-- ============================================================================
-- STEP 1: 마이그레이션 적용 확인 및 필요시 적용
-- ============================================================================

-- 1.1 컬럼 존재 여부 확인
SELECT
    'allocated_capital 컬럼 존재 여부' as check_name,
    COUNT(*) as exists
FROM information_schema.columns
WHERE table_name = 'strategies'
AND column_name = 'allocated_capital';

-- 1.2 컬럼이 없으면 추가 (마이그레이션 적용)
DO $$
BEGIN
    -- allocated_capital 컬럼 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'strategies' AND column_name = 'allocated_capital'
    ) THEN
        ALTER TABLE strategies
        ADD COLUMN allocated_capital DECIMAL(15, 2) DEFAULT 0;

        COMMENT ON COLUMN strategies.allocated_capital IS '전략에 할당된 자금 (원)';

        RAISE NOTICE '✅ allocated_capital 컬럼 추가 완료';
    ELSE
        RAISE NOTICE '✅ allocated_capital 컬럼이 이미 존재합니다';
    END IF;

    -- allocated_percent 컬럼 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'strategies' AND column_name = 'allocated_percent'
    ) THEN
        ALTER TABLE strategies
        ADD COLUMN allocated_percent DECIMAL(5, 2) DEFAULT 0;

        COMMENT ON COLUMN strategies.allocated_percent IS '전체 계좌 잔고 대비 할당 비율 (%)';

        RAISE NOTICE '✅ allocated_percent 컬럼 추가 완료';
    ELSE
        RAISE NOTICE '✅ allocated_percent 컬럼이 이미 존재합니다';
    END IF;
END $$;

-- 1.3 제약 조건 추가 (이미 존재하면 에러 무시)
DO $$
BEGIN
    -- allocated_percent 범위 체크
    BEGIN
        ALTER TABLE strategies
        ADD CONSTRAINT check_allocated_percent
        CHECK (allocated_percent >= 0 AND allocated_percent <= 100);
        RAISE NOTICE '✅ check_allocated_percent 제약 조건 추가 완료';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE '✅ check_allocated_percent 제약 조건이 이미 존재합니다';
    END;

    -- allocated_capital 양수 체크
    BEGIN
        ALTER TABLE strategies
        ADD CONSTRAINT check_allocated_capital
        CHECK (allocated_capital >= 0);
        RAISE NOTICE '✅ check_allocated_capital 제약 조건 추가 완료';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE '✅ check_allocated_capital 제약 조건이 이미 존재합니다';
    END;
END $$;

-- 1.4 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_strategies_active_allocated
ON strategies(user_id, is_active, allocated_percent)
WHERE is_active = true;

-- 1.5 뷰 생성
CREATE OR REPLACE VIEW strategy_capital_allocation AS
SELECT
  user_id,
  COUNT(*) as total_strategies,
  COUNT(*) FILTER (WHERE is_active = true) as active_strategies,
  SUM(allocated_capital) FILTER (WHERE is_active = true) as total_allocated_capital,
  SUM(allocated_percent) FILTER (WHERE is_active = true) as total_allocated_percent,
  100 - COALESCE(SUM(allocated_percent) FILTER (WHERE is_active = true), 0) as remaining_percent
FROM strategies
GROUP BY user_id;

COMMENT ON VIEW strategy_capital_allocation IS '사용자별 전략 자금 할당 현황';

-- ============================================================================
-- STEP 2: 현재 상태 진단
-- ============================================================================

-- 2.1 활성 전략 확인
SELECT
    '현재 활성 전략' as info,
    id,
    name,
    auto_execute,
    is_active,
    allocated_capital,
    allocated_percent
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 2.2 할당 자금 문제 확인
SELECT
    '할당 자금 0원 전략' as warning,
    id,
    name,
    allocated_capital,
    allocated_percent
FROM strategies
WHERE auto_execute = true
AND is_active = true
AND (allocated_capital = 0 OR allocated_capital IS NULL);

-- ============================================================================
-- STEP 3: 할당 자금 설정 (실제 값으로 수정 필요)
-- ============================================================================

-- ⚠️ 중요: 아래 UPDATE 문을 실행하기 전에 각 전략의 실제 할당 금액을 확인하세요!
-- ⚠️ 예시 값(3,000,000원, 30%)을 실제 값으로 변경해야 합니다!

-- 예시: 첫 번째 활성 전략에 3,000,000원 (30%) 할당
-- UPDATE strategies
-- SET
--     allocated_capital = 3000000,
--     allocated_percent = 30
-- WHERE id = (
--     SELECT id FROM strategies
--     WHERE auto_execute = true AND is_active = true
--     ORDER BY created_at
--     LIMIT 1
-- );

-- 예시: 두 번째 활성 전략에 5,000,000원 (50%) 할당
-- UPDATE strategies
-- SET
--     allocated_capital = 5000000,
--     allocated_percent = 50
-- WHERE id = (
--     SELECT id FROM strategies
--     WHERE auto_execute = true AND is_active = true
--     ORDER BY created_at
--     OFFSET 1
--     LIMIT 1
-- );

-- 또는 모든 활성 전략에 동일한 할당 비율 적용 (균등 분배)
-- 예: 활성 전략이 2개면 각각 50%씩, 계좌 잔고가 10,000,000원이라고 가정
/*
DO $$
DECLARE
    strategy_count INTEGER;
    equal_percent DECIMAL(5,2);
    total_capital DECIMAL(15,2) := 10000000; -- 실제 계좌 잔고로 변경
BEGIN
    SELECT COUNT(*) INTO strategy_count
    FROM strategies
    WHERE auto_execute = true AND is_active = true;

    IF strategy_count > 0 THEN
        equal_percent := 100.0 / strategy_count;

        UPDATE strategies
        SET
            allocated_percent = equal_percent,
            allocated_capital = (total_capital * equal_percent / 100)
        WHERE auto_execute = true AND is_active = true;

        RAISE NOTICE '✅ % 개 전략에 각각 %% (% 원) 할당 완료',
            strategy_count,
            ROUND(equal_percent, 2),
            ROUND(total_capital * equal_percent / 100, 0);
    ELSE
        RAISE NOTICE '⚠️ 활성 전략이 없습니다';
    END IF;
END $$;
*/

-- ============================================================================
-- STEP 4: 업데이트 후 확인
-- ============================================================================

-- 4.1 할당 자금 확인
SELECT
    '할당 자금 확인' as result,
    id,
    name,
    allocated_capital,
    allocated_percent,
    CASE
        WHEN allocated_capital > 0 THEN '✅'
        ELSE '❌'
    END as status
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 4.2 전체 할당 현황
SELECT * FROM strategy_capital_allocation;

-- 4.3 get_active_strategies_with_universe RPC 테스트
SELECT
    strategy_id,
    strategy_name,
    allocated_capital,
    allocated_percent,
    filter_name,
    jsonb_array_length(filtered_stocks) as stock_count
FROM get_active_strategies_with_universe();

-- ============================================================================
-- STEP 5: 시그널 데이터 확인
-- ============================================================================

-- 5.1 최근 시그널 확인 (24시간)
SELECT
    '최근 시그널' as info,
    strategy_id,
    stock_code,
    stock_name,
    signal_type,
    current_price,
    created_at
FROM trading_signals
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 20;

-- 5.2 시그널이 없다면?
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '⚠️ 최근 24시간 내 시그널이 없습니다. 워크플로우 B가 실행되지 않았을 수 있습니다.'
        ELSE '✅ 시그널 데이터 존재: ' || COUNT(*) || '개'
    END as signal_status
FROM trading_signals
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- ============================================================================
-- STEP 6: 현재가 데이터 확인
-- ============================================================================

-- 6.1 현재가 데이터 확인
SELECT
    '현재가 데이터' as info,
    stock_code,
    stock_name,
    current_price,
    updated_at,
    EXTRACT(EPOCH FROM (NOW() - updated_at))/3600 as hours_ago
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 10;

-- 6.2 현재가 데이터가 오래되었는지 확인
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '❌ 현재가 데이터가 없습니다. 자동매매 모니터링 v38을 먼저 실행하세요!'
        WHEN MAX(updated_at) < NOW() - INTERVAL '3 hours' THEN '⚠️ 현재가 데이터가 3시간 이상 오래되었습니다 (' || MAX(updated_at)::text || ')'
        ELSE '✅ 현재가 데이터가 최신입니다 (' || MAX(updated_at)::text || ')'
    END as price_data_status
FROM kw_price_current;

-- ============================================================================
-- 요약 및 다음 단계
-- ============================================================================

SELECT '
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 포트폴리오 화면 수정 완료 체크리스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 1. allocated_capital, allocated_percent 컬럼 추가됨
✅ 2. 제약 조건 및 인덱스 추가됨
✅ 3. strategy_capital_allocation 뷰 생성됨

⚠️  다음 단계:

1. STEP 3의 UPDATE 문을 실행하여 각 전략에 할당 자금 설정
   - 주석 해제하고 실제 금액/비율로 변경
   - 또는 프론트엔드 "수정" 버튼으로 설정

2. 자동매매 모니터링 v38 워크플로우 실행 확인
   - kw_price_current 테이블에 현재가 데이터 저장

3. 워크플로우 B v6 실행 확인
   - trading_signals 테이블에 시그널 생성

4. 프론트엔드 새로고침
   - 할당금액, 포트폴리오 통계 정상 표시 확인

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
' as summary;
