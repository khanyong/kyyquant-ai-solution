-- 종목명 업데이트 스크립트

-- 1. 최근 백테스트 결과의 종목명 업데이트
UPDATE backtest_results
SET trade_details = (
    SELECT jsonb_agg(
        trade || jsonb_build_object(
            'stock_name', COALESCE(sm.stock_name, trade->>'stock_code')
        )
    )
    FROM jsonb_array_elements(trade_details) AS trade
    LEFT JOIN stock_metadata sm ON sm.stock_code = trade->>'stock_code'
)
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
  AND trade_details IS NOT NULL;

-- 2. 업데이트 결과 확인
WITH updated_trades AS (
    SELECT
        br.id,
        trade->>'stock_code' as stock_code,
        trade->>'stock_name' as stock_name,
        sm.stock_name as correct_name
    FROM backtest_results br,
         jsonb_array_elements(br.trade_details) as trade
         LEFT JOIN stock_metadata sm ON sm.stock_code = trade->>'stock_code'
    WHERE br.created_at >= CURRENT_DATE - INTERVAL '1 day'
)
SELECT
    stock_code,
    stock_name as current_name,
    correct_name,
    CASE
        WHEN stock_name = correct_name THEN '✅ 일치'
        WHEN correct_name IS NULL THEN '⚠️ 메타데이터 없음'
        ELSE '❌ 불일치'
    END as status
FROM updated_trades
GROUP BY stock_code, stock_name, correct_name
ORDER BY stock_code;