-- 나의 전략 77의 최근 24시간 시그널 확인
SELECT
    signal_type,
    stock_code,
    stock_name,
    current_price,
    created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_ago
FROM trading_signals
WHERE strategy_id = 'e96a8ac8-8cef-4694-9f88-59bca61136ca'  -- 나의 전략 77
AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- 해당 전략의 현재 포지션 확인
SELECT
    stock_code,
    stock_name,
    quantity,
    position_status
FROM positions
WHERE strategy_id = 'e96a8ac8-8cef-4694-9f88-59bca61136ca'
AND position_status = 'open';
