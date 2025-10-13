-- 1. 전략이 몇 개나 있는지 확인
SELECT COUNT(*) as total_strategies FROM strategies;

-- 2. 아무 전략이나 3개 가져오기
SELECT
    id,
    name,
    type,
    universe,
    target_stocks,
    auto_execute,
    auto_trade_enabled,
    is_active,
    config
FROM strategies
LIMIT 3;

-- 3. config 안에 투자유니버스 정보가 있는지 확인
SELECT
    id,
    name,
    config->'investment_universe' as investment_universe,
    config->'stocks' as stocks,
    config->'stock_codes' as stock_codes,
    config->'filtered_stocks' as filtered_stocks
FROM strategies
LIMIT 3;

-- 4. entry_conditions, exit_conditions 샘플
SELECT
    id,
    name,
    entry_conditions,
    exit_conditions
FROM strategies
LIMIT 2;
