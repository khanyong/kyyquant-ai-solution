-- LX세미콘 140주 수동 동기화 (키움 API 500 에러 우회)

-- 1. 기존 테스트 데이터 삭제
DELETE FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 2. LX세미콘 실제 데이터 입력
INSERT INTO kw_portfolio (
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  available_quantity,
  avg_price,
  purchase_amount,
  current_price,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at
) VALUES (
  'f912da32-897f-4dbb-9242-3a438e9733a8',
  '8112-5100',
  '067570',           -- LX세미콘 종목코드
  'LX세미콘',
  140,                -- 수량
  140,                -- 주문가능수량
  52013.00,           -- 평균단가 (키움 앱에서 확인한 값)
  7281820,            -- 매입금액 (52013 × 140)
  51000.00,           -- 현재가 (대략)
  7140000,            -- 평가금액 (51000 × 140)
  -141820,            -- 손익 (7140000 - 7281820)
  -1.95,              -- 손익률 (-141820 / 7281820 × 100)
  NOW()
);

-- 3. 계좌 잔고 업데이트
UPDATE kw_account_balance
SET
  total_cash = 2718180,        -- 10000000 - 7281820
  available_cash = 2718180,
  stock_value = 7140000,
  total_asset = 9858180,       -- 2718180 + 7140000
  profit_loss = -141820,
  profit_loss_rate = -1.95,
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND account_number = '8112-5100';

-- 4. 확인
SELECT
  'LX세미콘 수동 동기화 완료' as status,
  stock_name,
  quantity,
  avg_price,
  current_price,
  evaluated_amount,
  profit_loss,
  profit_loss_rate
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

SELECT
  '계좌 잔고' as status,
  total_cash,
  stock_value,
  total_asset,
  profit_loss
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
