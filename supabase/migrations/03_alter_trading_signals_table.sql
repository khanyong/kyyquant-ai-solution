-- =====================================================
-- trading_signals 테이블 수정
-- 목적: 주문 추적 및 신호 상태 관리
-- =====================================================

-- 1. 주문 추적 컬럼 추가
ALTER TABLE trading_signals
ADD COLUMN IF NOT EXISTS order_id UUID REFERENCES orders(id),
ADD COLUMN IF NOT EXISTS signal_status VARCHAR(20) DEFAULT 'PENDING';

-- 2. 체크 제약 조건 추가
ALTER TABLE trading_signals
DROP CONSTRAINT IF EXISTS check_signal_status;

ALTER TABLE trading_signals
ADD CONSTRAINT check_signal_status
CHECK (signal_status IN ('PENDING', 'ORDERED', 'CANCELLED', 'EXECUTED'));

-- 3. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_trading_signals_status
ON trading_signals(signal_status);

CREATE INDEX IF NOT EXISTS idx_trading_signals_order_id
ON trading_signals(order_id)
WHERE order_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trading_signals_strategy_status
ON trading_signals(strategy_id, signal_status);

-- 4. 컬럼 설명 추가
COMMENT ON COLUMN trading_signals.order_id IS '생성된 주문 ID (orders 테이블 참조)';
COMMENT ON COLUMN trading_signals.signal_status IS '신호 상태: PENDING(대기), ORDERED(주문전송), CANCELLED(취소), EXECUTED(체결완료)';
