-- 1. 기존 전략 하나를 자동매매로 활성화
UPDATE strategies
SET auto_execute = true,
    is_active = true
WHERE id = (SELECT id FROM strategies LIMIT 1)
RETURNING id, name, auto_execute;

-- 2. 투자유니버스(필터) 하나 선택 (또는 생성)
-- 기존 필터 확인
SELECT id, name, filtered_stocks_count
FROM kw_investment_filters
WHERE is_active = true
LIMIT 3;

-- 3. 전략과 투자유니버스 연결
-- 위에서 확인한 strategy_id와 filter_id를 사용
INSERT INTO strategy_universes (strategy_id, investment_filter_id, is_active)
VALUES (
    (SELECT id FROM strategies WHERE auto_execute = true LIMIT 1),
    (SELECT id FROM kw_investment_filters WHERE is_active = true LIMIT 1),
    true
)
ON CONFLICT (strategy_id, investment_filter_id) DO UPDATE
SET is_active = true
RETURNING *;

-- 4. 연결 확인
SELECT * FROM get_active_strategies_with_universe();
