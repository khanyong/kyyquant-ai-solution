-- Add missing columns to trading_signals table for n8n workflow B
-- This resolves the error: "Could not find the 'confidence' column"

-- Add confidence column (신호 신뢰도)
ALTER TABLE public.trading_signals
ADD COLUMN IF NOT EXISTS confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100);

-- Add strategy_name column (전략 이름)
ALTER TABLE public.trading_signals
ADD COLUMN IF NOT EXISTS strategy_name VARCHAR(100);

-- Add change_rate column (등락률)
ALTER TABLE public.trading_signals
ADD COLUMN IF NOT EXISTS change_rate DECIMAL(10,2);

-- Add status column (신호 상태)
ALTER TABLE public.trading_signals
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'cancelled', 'expired'));

-- Add comments for documentation
COMMENT ON COLUMN public.trading_signals.confidence IS '신호 신뢰도 (0-100)';
COMMENT ON COLUMN public.trading_signals.strategy_name IS '전략 이름';
COMMENT ON COLUMN public.trading_signals.change_rate IS '등락률 (%)';
COMMENT ON COLUMN public.trading_signals.status IS '신호 상태 (pending/executed/cancelled/expired)';

-- Update signal_type CHECK constraint to accept lowercase values
ALTER TABLE public.trading_signals
DROP CONSTRAINT IF EXISTS trading_signals_signal_type_check;

ALTER TABLE public.trading_signals
ADD CONSTRAINT trading_signals_signal_type_check CHECK (signal_type IN ('buy', 'sell', 'BUY', 'SELL', 'HOLD'));

-- Verify the columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'trading_signals'
  AND column_name IN ('confidence', 'strategy_name', 'change_rate', 'status')
ORDER BY column_name;
