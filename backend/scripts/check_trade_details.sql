-- 백테스트 거래 상세 정보 확인 스크립트

-- 1. 최근 백테스트 결과 확인
SELECT
    id,
    strategy_id,
    created_at,
    jsonb_array_length(trade_details) as trade_count
FROM backtest_results
ORDER BY created_at DESC
LIMIT 5;

-- 2. 가장 최근 백테스트의 거래 내역 상세 확인
WITH latest_backtest AS (
    SELECT id, trade_details
    FROM backtest_results
    ORDER BY created_at DESC
    LIMIT 1
)
SELECT
    jsonb_array_elements(trade_details) as trade
FROM latest_backtest;

-- 3. 특정 필드 존재 여부 확인
WITH latest_trades AS (
    SELECT jsonb_array_elements(trade_details) as trade
    FROM backtest_results
    ORDER BY created_at DESC
    LIMIT 1
)
SELECT
    trade->>'date' as trade_date,
    trade->>'stock_code' as stock_code,
    trade->>'stock_name' as stock_name,
    trade->>'action' as action,
    trade->>'signal_reason' as signal_reason,
    trade->'signal_details' as signal_details,
    CASE
        WHEN trade->>'signal_reason' IS NOT NULL THEN '✅ 있음'
        ELSE '❌ 없음'
    END as reason_status
FROM latest_trades;

-- 4. signal_reason이 없는 거래 확인
WITH all_trades AS (
    SELECT
        br.id as backtest_id,
        br.created_at,
        jsonb_array_elements(trade_details) as trade
    FROM backtest_results br
    WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
)
SELECT
    backtest_id,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN trade->>'signal_reason' IS NOT NULL THEN 1 END) as trades_with_reason,
    COUNT(CASE WHEN trade->>'signal_reason' IS NULL THEN 1 END) as trades_without_reason
FROM all_trades
GROUP BY backtest_id
ORDER BY backtest_id DESC;