-- Add missing columns to orders table for n8n workflow B
-- This resolves the error: "Could not find the 'api_response' column"

-- Add signal_id column (신호 ID 참조)
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS signal_id UUID REFERENCES trading_signals(id);

-- Add strategy_id column (전략 ID 참조)
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS strategy_id UUID REFERENCES strategies(id);

-- Add stock_name column (종목명)
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS stock_name VARCHAR(100);

-- Add order_method column (주문 방식: MARKET, LIMIT)
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS order_method VARCHAR(20) CHECK (order_method IN ('MARKET', 'LIMIT', 'STOP'));

-- Rename order_quantity to quantity (n8n 워크플로우와 일치)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'orders'
        AND column_name = 'order_quantity'
        AND table_schema = 'public'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'orders'
        AND column_name = 'quantity'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.orders RENAME COLUMN order_quantity TO quantity;
    END IF;
END $$;

-- Add quantity column if it doesn't exist
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS quantity INTEGER;

-- Rename order_status to status (n8n 워크플로우와 일치)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'orders'
        AND column_name = 'order_status'
        AND table_schema = 'public'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'orders'
        AND column_name = 'status'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.orders RENAME COLUMN order_status TO status;
    END IF;
END $$;

-- Add status column if it doesn't exist
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS status VARCHAR(20) CHECK (status IN ('PENDING', 'EXECUTED', 'CANCELLED', 'PARTIAL', 'FAILED'));

-- Add api_response column (키움 API 응답 저장용)
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS api_response JSONB;

-- Add comments for documentation
COMMENT ON COLUMN public.orders.signal_id IS '거래 신호 ID';
COMMENT ON COLUMN public.orders.strategy_id IS '전략 ID';
COMMENT ON COLUMN public.orders.stock_name IS '종목명';
COMMENT ON COLUMN public.orders.order_method IS '주문 방식 (MARKET/LIMIT/STOP)';
COMMENT ON COLUMN public.orders.quantity IS '주문 수량';
COMMENT ON COLUMN public.orders.status IS '주문 상태 (PENDING/EXECUTED/CANCELLED/PARTIAL/FAILED)';
COMMENT ON COLUMN public.orders.api_response IS '키움 API 응답 (JSON)';

-- Update order_type CHECK constraint to ensure consistency
ALTER TABLE public.orders
DROP CONSTRAINT IF EXISTS orders_order_type_check;

ALTER TABLE public.orders
ADD CONSTRAINT orders_order_type_check CHECK (order_type IN ('BUY', 'SELL'));

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_signal_id ON orders(signal_id);
CREATE INDEX IF NOT EXISTS idx_orders_strategy_id ON orders(strategy_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status) WHERE status = 'PENDING';
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);

-- Verify the columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'orders'
  AND column_name IN ('signal_id', 'strategy_id', 'stock_name', 'order_method', 'quantity', 'status', 'api_response')
ORDER BY column_name;
