-- =====================================================
-- orders 테이블 수정
-- 목적: 자동 취소 기능 및 주문 추적 강화
-- =====================================================

-- 1. 자동 취소 관련 컬럼 추가
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS auto_cancel_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS cancel_after_minutes INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS cancellation_reason TEXT,
ADD COLUMN IF NOT EXISTS original_order_price NUMERIC(10, 2);

-- 2. 기존 데이터에 대한 기본값 설정
UPDATE orders
SET
  original_order_price = order_price,
  cancel_after_minutes = 30,
  auto_cancel_at = created_at + INTERVAL '30 minutes'
WHERE original_order_price IS NULL
  AND status IN ('PENDING', 'PARTIAL');

-- 3. 인덱스 생성 (자동 취소 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_orders_auto_cancel
ON orders(auto_cancel_at)
WHERE status IN ('PENDING', 'PARTIAL') AND auto_cancel_at IS NOT NULL;

-- 4. 컬럼 설명 추가
COMMENT ON COLUMN orders.auto_cancel_at IS '자동 취소 예정 시각';
COMMENT ON COLUMN orders.cancel_after_minutes IS '주문 후 자동 취소까지 분 수 (기본 30분)';
COMMENT ON COLUMN orders.cancellation_reason IS '취소 사유 (자동 취소, 수동 취소, 호가 변동 등)';
COMMENT ON COLUMN orders.original_order_price IS '최초 주문 가격 (호가 변동 감지용)';
