-- ============================================================================
-- 현재 데이터 상태 확인
-- ============================================================================

-- 1. 활성 전략의 할당 자금 확인
SELECT
    '1. 활성 전략 할당 자금' as step,
    id,
    name,
    auto_execute,
    is_active,
    allocated_capital,
    allocated_percent,
    CASE
        WHEN allocated_capital > 0 THEN '✅ 설정됨'
        ELSE '❌ 0원 (설정 필요)'
    END as status
FROM strategies
WHERE auto_execute = true AND is_active = true
ORDER BY created_at;

-- 2. get_active_strategies_with_universe RPC 결과
SELECT
    '2. RPC 결과' as step,
    strategy_id,
    strategy_name,
    allocated_capital,
    allocated_percent,
    filter_name,
    jsonb_array_length(filtered_stocks) as stock_count
FROM get_active_strategies_with_universe();

-- 3. 포지션 확인
SELECT
    '3. 현재 포지션' as step,
    COUNT(*) as position_count,
    COALESCE(SUM(avg_price * quantity), 0) as total_invested
FROM positions
WHERE status = 'open';

-- 4. 최근 시그널 확인 (24시간)
SELECT
    '4. 최근 시그널' as step,
    signal_type,
    COUNT(*) as count
FROM trading_signals
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY signal_type
ORDER BY signal_type;

-- 5. 현재가 데이터 확인
SELECT
    '5. 현재가 데이터' as step,
    COUNT(*) as total_stocks,
    MAX(updated_at) as last_update,
    EXTRACT(EPOCH FROM (NOW() - MAX(updated_at)))/3600 as hours_ago
FROM kw_price_current;

-- 6. 할당 자금 문제 진단
SELECT
    '6. 문제 진단' as step,
    CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM strategies
            WHERE auto_execute = true AND is_active = true
        ) THEN '❌ 활성 전략이 없습니다'
        WHEN EXISTS (
            SELECT 1 FROM strategies
            WHERE auto_execute = true AND is_active = true
            AND (allocated_capital = 0 OR allocated_capital IS NULL)
        ) THEN '⚠️ 활성 전략의 allocated_capital이 0입니다 → 프론트엔드에서 수정 버튼으로 설정하세요'
        ELSE '✅ 할당 자금이 정상적으로 설정되어 있습니다'
    END as diagnosis;

-- 7. 시그널 데이터 문제 진단
SELECT
    '7. 시그널 문제 진단' as step,
    CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM trading_signals
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        ) THEN '❌ 최근 24시간 내 시그널이 없습니다 → n8n 워크플로우 B를 실행하세요'
        WHEN EXISTS (
            SELECT 1 FROM trading_signals
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            AND signal_type = 'sell'
        ) AND NOT EXISTS (
            SELECT 1 FROM positions WHERE status = 'open'
        ) THEN '⚠️ 보유 종목이 없는데 매도 시그널이 있습니다 → 오래된 시그널일 수 있습니다'
        ELSE '✅ 시그널 데이터가 정상적입니다'
    END as signal_diagnosis;

-- 8. 현재가 데이터 문제 진단
SELECT
    '8. 현재가 문제 진단' as step,
    CASE
        WHEN NOT EXISTS (SELECT 1 FROM kw_price_current) THEN '❌ 현재가 데이터가 없습니다 → n8n 자동매매 모니터링 v38을 실행하세요'
        WHEN MAX(updated_at) < NOW() - INTERVAL '3 hours' THEN '⚠️ 현재가 데이터가 ' || ROUND(EXTRACT(EPOCH FROM (NOW() - MAX(updated_at)))/3600) || '시간 전입니다 → v38을 다시 실행하세요'
        ELSE '✅ 현재가 데이터가 최신입니다 (마지막 업데이트: ' || MAX(updated_at)::text || ')'
    END as price_diagnosis
FROM kw_price_current;
