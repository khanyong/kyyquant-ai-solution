-- ============================================================================
-- 포트폴리오 데이터 디버깅 쿼리
-- ============================================================================
-- 현재 화면에 표시되는 데이터가 0원인 원인을 찾기 위한 진단 쿼리
-- ============================================================================

-- 1. 활성 전략 확인
SELECT
    '활성 전략 확인' as check_name,
    id,
    name,
    auto_execute,
    auto_trade_enabled,
    is_active,
    allocated_capital,
    allocated_percent,
    created_at
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 2. 전략-유니버스 연결 확인
SELECT
    '전략-유니버스 연결' as check_name,
    su.strategy_id,
    s.name as strategy_name,
    su.investment_filter_id,
    kif.name as filter_name,
    su.is_active,
    jsonb_array_length(kif.filtered_stocks) as stock_count
FROM strategy_universes su
JOIN strategies s ON su.strategy_id = s.id
JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE su.is_active = true
ORDER BY s.name;

-- 3. get_active_strategies_with_universe RPC 결과 확인
SELECT
    '활성 전략 with 유니버스' as check_name,
    *
FROM get_active_strategies_with_universe();

-- 4. 포지션 확인
SELECT
    '현재 포지션' as check_name,
    p.*,
    s.name as strategy_name
FROM positions p
LEFT JOIN strategies s ON p.strategy_id = s.id
WHERE p.status = 'open'
ORDER BY p.created_at DESC;

-- 5. 대기 중인 주문 확인
SELECT
    '대기 주문' as check_name,
    *
FROM orders
WHERE status = 'PENDING'
ORDER BY created_at DESC;

-- 6. 최근 시그널 확인 (24시간)
SELECT
    '최근 시그널' as check_name,
    ts.*,
    s.name as strategy_name
FROM trading_signals ts
LEFT JOIN strategies s ON ts.strategy_id = s.id
WHERE ts.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY ts.created_at DESC;

-- 7. 현재가 데이터 확인 (kw_price_current)
SELECT
    '현재가 데이터' as check_name,
    stock_code,
    stock_name,
    current_price,
    change_rate,
    volume,
    updated_at
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 20;

-- 8. 포트폴리오 통계 계산 (프론트엔드와 동일한 로직)
WITH strategy_allocation AS (
    SELECT
        SUM(allocated_capital) as total_allocated,
        COUNT(*) as active_count
    FROM strategies
    WHERE auto_execute = true AND is_active = true
),
position_stats AS (
    SELECT
        COUNT(*) as position_count,
        SUM(avg_price * quantity) as total_invested
    FROM positions
    WHERE status = 'open'
)
SELECT
    '포트폴리오 통계' as check_name,
    sa.total_allocated,
    sa.active_count as active_strategies,
    COALESCE(ps.position_count, 0) as total_positions,
    COALESCE(ps.total_invested, 0) as total_invested
FROM strategy_allocation sa
CROSS JOIN position_stats ps;

-- 9. strategies 테이블 스키마 확인
SELECT
    '컬럼 확인' as check_name,
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'strategies'
AND column_name IN ('allocated_capital', 'allocated_percent')
ORDER BY ordinal_position;

-- 10. 마이그레이션 적용 여부 확인 (제약 조건)
SELECT
    '제약 조건 확인' as check_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'strategies'
AND constraint_name IN ('check_allocated_percent', 'check_allocated_capital');
