-- 자동매매가 활성화된 전략의 실제 데이터 확인
SELECT
    id,
    name,
    universe,
    target_stocks,
    auto_execute,
    auto_trade_enabled,
    is_active,
    entry_conditions,
    exit_conditions
FROM strategies
WHERE (auto_execute = true OR auto_trade_enabled = true)
    AND is_active = true
LIMIT 3;

-- universe나 target_stocks에 데이터가 있는 전략 확인
SELECT
    id,
    name,
    CASE
        WHEN universe IS NOT NULL THEN array_length(universe, 1)
        ELSE 0
    END as universe_count,
    CASE
        WHEN target_stocks IS NOT NULL THEN array_length(target_stocks, 1)
        ELSE 0
    END as target_stocks_count,
    universe[1:3] as universe_sample,
    target_stocks[1:3] as target_stocks_sample
FROM strategies
WHERE universe IS NOT NULL OR target_stocks IS NOT NULL
LIMIT 5;
