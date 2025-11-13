-- ============================================================================
-- allocated_capital 자동 계산 (실제 계좌 잔고 기준)
-- ============================================================================
-- kw_account_balance 테이블의 deposit(예수금)을 기준으로 계산
-- ============================================================================

-- 1. 업데이트 전 상태 확인
SELECT
    '업데이트 전' as status,
    s.name,
    s.allocated_percent,
    s.allocated_capital as current_capital,
    (s.allocated_percent / 100.0) * b.deposit as calculated_capital,
    TO_CHAR((s.allocated_percent / 100.0) * b.deposit, 'FM9,999,999') || '원' as formatted_capital
FROM strategies s
CROSS JOIN (
    SELECT deposit
    FROM kw_account_balance
    ORDER BY updated_at DESC
    LIMIT 1
) b
WHERE s.auto_execute = true AND s.is_active = true
ORDER BY s.created_at;

-- 2. allocated_capital 업데이트 (실제 계좌 잔고 기준)
UPDATE strategies
SET allocated_capital = (allocated_percent / 100.0) * (
    SELECT deposit
    FROM kw_account_balance
    ORDER BY updated_at DESC
    LIMIT 1
)
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
    TO_CHAR(
        (SELECT deposit FROM kw_account_balance ORDER BY updated_at DESC LIMIT 1) - SUM(allocated_capital),
        'FM9,999,999'
    ) || '원' as remaining_capital
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 5. 계좌 잔고와 비교
SELECT
    '잔고 비교' as comparison,
    TO_CHAR(b.deposit, 'FM9,999,999') || '원' as account_balance,
    TO_CHAR(COALESCE(s.total_allocated, 0), 'FM9,999,999') || '원' as total_allocated,
    TO_CHAR(b.deposit - COALESCE(s.total_allocated, 0), 'FM9,999,999') || '원' as remaining,
    ROUND(COALESCE(s.total_allocated, 0) / b.deposit * 100, 2) || '%' as allocated_rate
FROM (
    SELECT deposit
    FROM kw_account_balance
    ORDER BY updated_at DESC
    LIMIT 1
) b
CROSS JOIN (
    SELECT SUM(allocated_capital) as total_allocated
    FROM strategies
    WHERE auto_execute = true AND is_active = true
) s;

-- 예상 결과:
-- 현재 예수금: 10,000,000원
-- 나의 전략 77: 50% → 5,000,000원
-- 나의 전략 7:  30% → 3,000,000원
-- 합계: 80% → 8,000,000원
-- 잔여: 20% → 2,000,000원
