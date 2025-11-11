-- trading_signals 테이블에 필요한 컬럼 추가

-- current_price 컬럼 추가 (이미 price 컬럼이 있지만, 명확성을 위해 별도 추가)
ALTER TABLE trading_signals
ADD COLUMN IF NOT EXISTS current_price DECIMAL(10, 2);

-- change_rate 컬럼 추가 (등락률 %)
ALTER TABLE trading_signals
ADD COLUMN IF NOT EXISTS change_rate DECIMAL(10, 2);

-- 컬럼 코멘트 추가
COMMENT ON COLUMN trading_signals.current_price IS '신호 발생 시점의 현재가';
COMMENT ON COLUMN trading_signals.change_rate IS '신호 발생 시점의 등락률 (%)';
