-- trading_signals 테이블의 signal_type CHECK 제약 조건 확인 및 수정

-- 1. 기존 제약 조건 확인
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'trading_signals'::regclass
AND conname LIKE '%signal_type%';

-- 2. 기존 제약 조건 삭제
ALTER TABLE trading_signals
DROP CONSTRAINT IF EXISTS trading_signals_signal_type_check;

-- 3. 새로운 제약 조건 추가 (buy, sell 허용)
ALTER TABLE trading_signals
ADD CONSTRAINT trading_signals_signal_type_check
CHECK (signal_type IN ('buy', 'sell', 'BUY', 'SELL'));

-- 또는 제약 조건 없이 사용하려면 3번 단계 생략
