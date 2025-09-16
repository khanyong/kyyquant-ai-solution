-- Supabase 백테스트 거래 상세 정보 업데이트 스크립트
-- trade_details JSONB 필드에 새로운 속성 추가를 위한 마이그레이션

-- 1. 기존 backtest_results 테이블 구조 확인
-- trade_details 필드는 이미 JSONB 타입이므로 구조 변경 불필요
-- JSONB는 동적으로 새로운 필드를 추가할 수 있음

-- 2. 새로운 거래 상세 정보 구조 예시
/*
trade_details 배열의 각 객체 구조:
{
  "date": "2024-01-15",
  "stock_code": "005930",
  "stock_name": "삼성전자",        -- 새로 추가
  "action": "buy",
  "quantity": 10,
  "price": 65000,
  "amount": 650000,
  "profit_loss": 0,
  "profit_rate": 0,
  "signal_reason": "매수 신호 발생",   -- 새로 추가
  "signal_details": {                   -- 새로 추가
    "type": "signal",
    "conditions": ["RSI < 30", "MACD 골든크로스"]
  }
}
*/

-- 3. 기존 데이터 마이그레이션 (선택사항)
-- 기존 trade_details에 새 필드가 없는 경우 기본값 추가
UPDATE backtest_results
SET trade_details = (
  SELECT jsonb_agg(
    CASE
      WHEN (elem->>'stock_name') IS NULL THEN
        elem || jsonb_build_object(
          'stock_name', COALESCE(
            CASE elem->>'stock_code'
              WHEN '005930' THEN '삼성전자'
              WHEN '000660' THEN 'SK하이닉스'
              WHEN '035420' THEN 'NAVER'
              WHEN '035720' THEN '카카오'
              WHEN '051910' THEN 'LG화학'
              WHEN '006400' THEN '삼성SDI'
              WHEN '207940' THEN '삼성바이오로직스'
              WHEN '005380' THEN '현대차'
              WHEN '000270' THEN '기아'
              WHEN '068270' THEN '셀트리온'
              WHEN '105560' THEN 'KB금융'
              WHEN '055550' THEN '신한지주'
              WHEN '086790' THEN '하나금융지주'
              WHEN '316140' THEN '우리금융지주'
              WHEN '034730' THEN 'SK'
              WHEN '015760' THEN '한국전력'
              WHEN '032830' THEN '삼성생명'
              WHEN '003550' THEN 'LG'
              WHEN '034220' THEN 'LG디스플레이'
              WHEN '009150' THEN '삼성전기'
              ELSE elem->>'stock_code'
            END,
            elem->>'stock_code'
          ),
          'signal_reason', COALESCE(elem->>'signal_reason', ''),
          'signal_details', COALESCE(elem->'signal_details', '{}'::jsonb)
        )
      ELSE elem
    END
  )
  FROM jsonb_array_elements(trade_details) AS elem
)
WHERE trade_details IS NOT NULL
  AND jsonb_array_length(trade_details) > 0
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(trade_details) AS elem
    WHERE (elem->>'stock_name') IS NULL
  );

-- 4. 인덱스 추가 (성능 최적화)
-- trade_details 내의 stock_code로 검색 최적화
CREATE INDEX IF NOT EXISTS idx_backtest_results_trade_stock_codes
ON backtest_results
USING gin ((trade_details->'stock_code'));

-- 5. 뷰 생성 (선택사항) - 거래 분석용
CREATE OR REPLACE VIEW v_backtest_trades AS
SELECT
  br.id as backtest_id,
  br.strategy_id,
  br.user_id,
  br.created_at as backtest_date,
  trade->>'date' as trade_date,
  trade->>'stock_code' as stock_code,
  trade->>'stock_name' as stock_name,
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
WHERE
  br.trade_details IS NOT NULL;

-- 6. 통계 함수 생성 (선택사항)
CREATE OR REPLACE FUNCTION get_trade_statistics(p_user_id UUID, p_strategy_id UUID DEFAULT NULL)
RETURNS TABLE (
  total_trades INTEGER,
  buy_trades INTEGER,
  sell_trades INTEGER,
  profit_trades INTEGER,
  loss_trades INTEGER,
  avg_profit_rate NUMERIC,
  most_traded_stock TEXT,
  most_common_signal TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*)::INTEGER as total_trades,
    COUNT(*) FILTER (WHERE action = 'buy')::INTEGER as buy_trades,
    COUNT(*) FILTER (WHERE action = 'sell')::INTEGER as sell_trades,
    COUNT(*) FILTER (WHERE profit_loss > 0)::INTEGER as profit_trades,
    COUNT(*) FILTER (WHERE profit_loss < 0)::INTEGER as loss_trades,
    AVG(profit_rate)::NUMERIC as avg_profit_rate,
    MODE() WITHIN GROUP (ORDER BY stock_name) as most_traded_stock,
    MODE() WITHIN GROUP (ORDER BY signal_reason) as most_common_signal
  FROM v_backtest_trades
  WHERE user_id = p_user_id
    AND (p_strategy_id IS NULL OR strategy_id = p_strategy_id);
END;
$$ LANGUAGE plpgsql;

-- 7. 권한 설정
GRANT SELECT ON v_backtest_trades TO authenticated;
GRANT EXECUTE ON FUNCTION get_trade_statistics TO authenticated;

-- 8. RLS (Row Level Security) 정책
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own backtest trades"
ON backtest_results FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own backtest results"
ON backtest_results FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own backtest results"
ON backtest_results FOR UPDATE
USING (auth.uid() = user_id);

-- 실행 완료 메시지
SELECT 'Backtest trade details migration completed successfully' as status;