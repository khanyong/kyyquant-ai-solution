-- 주문 이력 테이블 생성
CREATE TABLE IF NOT EXISTS order_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  stock_code VARCHAR(20) NOT NULL,
  stock_name VARCHAR(100),
  order_type VARCHAR(10) NOT NULL, -- BUY, SELL
  quantity INTEGER NOT NULL,
  price NUMERIC,
  order_no TEXT,
  status TEXT NOT NULL, -- success, error, pending
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_order_history_created
  ON order_history(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_order_history_stock                        
  ON order_history(stock_code, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_order_history_strategy
  ON order_history(strategy_id, created_at DESC);

-- RLS 활성화
ALTER TABLE order_history ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 사용자는 자신의 전략 주문만 조회
CREATE POLICY "Users can view own orders"
  ON order_history FOR SELECT
  USING (
    strategy_id IN (
      SELECT id FROM strategies WHERE user_id = auth.uid()
    )
  );

-- RLS 정책: 서비스는 주문 삽입 가능
CREATE POLICY "Service can insert orders"
  ON order_history FOR INSERT
  WITH CHECK (true);

-- 최근 주문 이력 조회 함수
CREATE OR REPLACE FUNCTION get_recent_orders(
  p_user_id UUID,
  p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
  id UUID,
  strategy_id UUID,
  stock_code VARCHAR,
  stock_name VARCHAR,
  order_type VARCHAR,
  quantity INTEGER,
  price NUMERIC,
  order_no TEXT,
  status TEXT,
  message TEXT,
  created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  SELECT
    o.id,
    o.strategy_id,
    o.stock_code,
    o.stock_name,
    o.order_type,
    o.quantity,
    o.price,
    o.order_no,
    o.status,
    o.message,
    o.created_at
  FROM order_history o
  INNER JOIN strategies s ON o.strategy_id = s.id
  WHERE s.user_id = p_user_id
  ORDER BY o.created_at DESC
  LIMIT p_limit;
END;
$$;

-- 주문 통계 함수
CREATE OR REPLACE FUNCTION get_order_stats(
  p_user_id UUID,
  p_days INTEGER DEFAULT 7
)
RETURNS TABLE (
  total_orders BIGINT,
  buy_orders BIGINT,
  sell_orders BIGINT,
  success_orders BIGINT,
  failed_orders BIGINT,
  total_quantity BIGINT,
  total_amount NUMERIC
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*) as total_orders,
    COUNT(*) FILTER (WHERE order_type = 'BUY') as buy_orders,
    COUNT(*) FILTER (WHERE order_type = 'SELL') as sell_orders,
    COUNT(*) FILTER (WHERE status = 'success') as success_orders,
    COUNT(*) FILTER (WHERE status = 'error') as failed_orders,
    COALESCE(SUM(quantity), 0) as total_quantity,
    COALESCE(SUM(quantity * price), 0) as total_amount
  FROM order_history o
  INNER JOIN strategies s ON o.strategy_id = s.id
  WHERE s.user_id = p_user_id
    AND o.created_at > NOW() - INTERVAL '1 day' * p_days;
END;
$$;

COMMENT ON TABLE order_history IS '자동매매 주문 이력';
COMMENT ON COLUMN order_history.order_type IS 'BUY: 매수, SELL: 매도';
COMMENT ON COLUMN order_history.status IS 'success: 성공, error: 실패, pending: 대기중';
