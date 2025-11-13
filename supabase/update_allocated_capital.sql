-- ============================================================================
-- allocated_capital 자동 계산 및 업데이트
-- ============================================================================
-- 계좌 잔고: 10,000,000원
-- allocated_percent 기준으로 allocated_capital 계산
-- ============================================================================

-- 1. 업데이트 전 상태 확인
SELECT
    '업데이트 전' as status,
    name,
    allocated_percent,
    allocated_capital,
    (allocated_percent / 100.0) * 10000000 as calculated_capital
FROM strategies
WHERE auto_execute = true AND is_active = true
ORDER BY created_at;

-- 2. allocated_capital 업데이트
UPDATE strategies
SET allocated_capital = (allocated_percent / 100.0) * 10000000
WHERE auto_execute = true
AND is_active = true
AND allocated_percent > 0;

-- 3. 업데이트 후 결과 확인
SELECT
    '업데이트 후' as status,
    name,
    allocated_percent || '%' as percent,
    TO_CHAR(allocated_capital, 'FM9,999,999') || '원' as capital,
    CASE
        WHEN allocated_capital > 0 THEN '✅ 성공'
        ELSE '❌ 실패'
    END as result
FROM strategies
WHERE auto_execute = true AND is_active = true
ORDER BY created_at;

-- 4. 전체 할당 현황 요약
SELECT
    '전체 할당 현황' as summary,
    COUNT(*) as strategy_count,
    SUM(allocated_percent) || '%' as total_percent,
    TO_CHAR(SUM(allocated_capital), 'FM9,999,999') || '원' as total_capital,
    TO_CHAR(10000000 - SUM(allocated_capital), 'FM9,999,999') || '원' as remaining_capital
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 예상 결과:
-- 나의 전략 77: 50% → 5,000,000원
-- 나의 전략 7:  30% → 3,000,000원
-- 합계: 80% → 8,000,000원
-- 잔여: 20% → 2,000,000원
