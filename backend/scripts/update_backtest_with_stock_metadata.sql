-- 기존 stock_metadata 테이블을 활용한 백테스트 거래 내역 개선
-- stock_metadata 테이블이 이미 존재하므로 이를 활용

-- 1. stock_metadata 테이블 구조 (확인됨)
-- - stock_code (종목코드)
-- - stock_name (종목명)
-- - market (시장)
-- - sector (업종)
-- - industry (산업)
-- - is_active (활성 여부)
-- - is_etf (ETF 여부)
-- - is_spac (SPAC 여부)

-- 2. 백테스트 거래 내역과 종목 메타데이터를 조인하는 뷰 생성
CREATE OR REPLACE VIEW v_backtest_trades_detail AS
SELECT
    br.id as backtest_id,
    br.strategy_id,
    br.user_id,
    br.created_at as backtest_date,
    trade->>'date' as trade_date,
    trade->>'stock_code' as stock_code,
    COALESCE(sm.stock_name, trade->>'stock_name', trade->>'stock_code') as stock_name,
    sm.market,
    sm.sector,
    trade->>'action' as action,
    (trade->>'quantity')::integer as quantity,
    (trade->>'price')::numeric as price,
    (trade->>'amount')::numeric as amount,
    (trade->>'profit_loss')::numeric as profit_loss,
    (trade->>'profit_rate')::numeric as profit_rate,
    trade->>'signal_reason' as signal_reason,
    trade->'signal_details' as signal_details
FROM
    backtest_results br,
    jsonb_array_elements(br.trade_details) as trade
    LEFT JOIN stock_metadata sm ON sm.stock_code = trade->>'stock_code'
WHERE
    br.trade_details IS NOT NULL;

-- 3. 종목명 조회 함수 (stock_metadata 활용)
CREATE OR REPLACE FUNCTION get_stock_name_from_metadata(p_stock_code VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_stock_name VARCHAR;
BEGIN
    SELECT stock_name INTO v_stock_name
    FROM stock_metadata
    WHERE stock_code = p_stock_code
      AND is_active = true
    LIMIT 1;

    RETURN COALESCE(v_stock_name, p_stock_code);
END;
$$ LANGUAGE plpgsql;

-- 4. 백테스트 결과 저장 시 종목명 자동 추가 트리거
CREATE OR REPLACE FUNCTION enrich_trade_details()
RETURNS TRIGGER AS $$
DECLARE
    enriched_trades JSONB;
BEGIN
    -- trade_details 배열의 각 요소에 종목명 추가
    SELECT jsonb_agg(
        CASE
            WHEN (elem->>'stock_name') IS NULL OR (elem->>'stock_name') = '' THEN
                elem || jsonb_build_object(
                    'stock_name', get_stock_name_from_metadata(elem->>'stock_code')
                )
            ELSE
                elem
        END
    ) INTO enriched_trades
    FROM jsonb_array_elements(NEW.trade_details) AS elem;

    NEW.trade_details = enriched_trades;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. 트리거 생성 (백테스트 결과 삽입/업데이트 시 자동 실행)
DROP TRIGGER IF EXISTS enrich_backtest_trade_details ON backtest_results;
CREATE TRIGGER enrich_backtest_trade_details
BEFORE INSERT OR UPDATE OF trade_details ON backtest_results
FOR EACH ROW
WHEN (NEW.trade_details IS NOT NULL)
EXECUTE FUNCTION enrich_trade_details();

-- 6. 기존 백테스트 결과 업데이트 (종목명이 없는 경우)
UPDATE backtest_results
SET trade_details = (
    SELECT jsonb_agg(
        CASE
            WHEN (elem->>'stock_name') IS NULL OR (elem->>'stock_name') = '' THEN
                elem || jsonb_build_object(
                    'stock_name', get_stock_name_from_metadata(elem->>'stock_code'),
                    'signal_reason', COALESCE(elem->>'signal_reason', ''),
                    'signal_details', COALESCE(elem->'signal_details', '{}'::jsonb)
                )
            ELSE
                elem
        END
    )
    FROM jsonb_array_elements(trade_details) AS elem
)
WHERE trade_details IS NOT NULL
  AND jsonb_array_length(trade_details) > 0
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(trade_details) AS elem
    WHERE (elem->>'stock_name') IS NULL OR (elem->>'stock_name') = ''
  );

-- 7. 거래 통계 분석 함수 (stock_metadata 정보 포함)
CREATE OR REPLACE FUNCTION analyze_trade_performance(p_user_id UUID, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    stock_code VARCHAR,
    stock_name VARCHAR,
    market VARCHAR,
    sector VARCHAR,
    total_trades INTEGER,
    buy_count INTEGER,
    sell_count INTEGER,
    total_profit NUMERIC,
    avg_profit_rate NUMERIC,
    win_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH trade_stats AS (
        SELECT
            t.stock_code,
            t.stock_name,
            t.market,
            t.sector,
            COUNT(*) as total_trades,
            COUNT(*) FILTER (WHERE t.action = 'buy') as buy_count,
            COUNT(*) FILTER (WHERE t.action = 'sell') as sell_count,
            SUM(t.profit_loss) as total_profit,
            AVG(t.profit_rate) as avg_profit_rate,
            COUNT(*) FILTER (WHERE t.profit_loss > 0) * 100.0 /
                NULLIF(COUNT(*) FILTER (WHERE t.action = 'sell'), 0) as win_rate
        FROM v_backtest_trades_detail t
        WHERE t.user_id = p_user_id
          AND t.backtest_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
        GROUP BY t.stock_code, t.stock_name, t.market, t.sector
    )
    SELECT * FROM trade_stats
    ORDER BY total_profit DESC;
END;
$$ LANGUAGE plpgsql;

-- 8. 권한 설정
GRANT SELECT ON v_backtest_trades_detail TO authenticated;
GRANT EXECUTE ON FUNCTION get_stock_name_from_metadata TO authenticated;
GRANT EXECUTE ON FUNCTION analyze_trade_performance TO authenticated;

-- 9. 인덱스 최적화
CREATE INDEX IF NOT EXISTS idx_stock_metadata_stock_code
ON stock_metadata(stock_code)
WHERE is_active = true;

-- 실행 완료 메시지
SELECT 'Backtest integration with stock_metadata completed successfully' as status;