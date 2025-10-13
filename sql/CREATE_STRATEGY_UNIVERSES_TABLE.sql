-- 전략과 투자유니버스를 연결하는 중간 테이블 생성
CREATE TABLE IF NOT EXISTS strategy_universes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id uuid NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    investment_filter_id uuid NOT NULL REFERENCES kw_investment_filters(id) ON DELETE CASCADE,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),

    -- 하나의 전략에 같은 투자유니버스가 중복 등록되지 않도록
    UNIQUE(strategy_id, investment_filter_id)
);

-- 인덱스 생성 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_strategy_universes_strategy
ON strategy_universes(strategy_id);

CREATE INDEX IF NOT EXISTS idx_strategy_universes_filter
ON strategy_universes(investment_filter_id);

CREATE INDEX IF NOT EXISTS idx_strategy_universes_active
ON strategy_universes(is_active) WHERE is_active = true;

-- 샘플 데이터 확인용 쿼리
-- 자동매매가 활성화된 전략과 연결된 투자유니버스 조회
SELECT
    s.id as strategy_id,
    s.name as strategy_name,
    s.auto_execute,
    s.auto_trade_enabled,
    kif.id as filter_id,
    kif.name as filter_name,
    kif.filtered_stocks_count,
    jsonb_array_length(kif.filtered_stocks) as actual_stock_count,
    kif.filtered_stocks -> 0 as first_stock,
    kif.filtered_stocks -> 1 as second_stock,
    kif.filtered_stocks -> 2 as third_stock
FROM strategies s
INNER JOIN strategy_universes su ON s.id = su.strategy_id
INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE s.auto_execute = true
    AND s.is_active = true
    AND su.is_active = true
    AND kif.is_active = true;
