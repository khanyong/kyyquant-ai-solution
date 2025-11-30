
-- Seed Mock Data for Auto Trading Dashboard
-- Run this in Supabase Dashboard -> SQL Editor

DO $$
DECLARE
  target_user_id uuid;
BEGIN
  -- Select the first user found in auth.users
  SELECT id INTO target_user_id FROM auth.users LIMIT 1;

  IF target_user_id IS NULL THEN
    RAISE NOTICE 'No user found in auth.users';
    RETURN;
  END IF;

  RAISE NOTICE 'Seeding data for User ID: %', target_user_id;

  -- 1. Insert Mock Account Balance
  INSERT INTO public.kw_account_balance (
    user_id,
    total_asset,
    total_cash,
    available_cash,
    order_cash,
    stock_value,
    profit_loss,
    profit_loss_rate,
    updated_at
  ) VALUES (
    target_user_id,
    100000000, -- Total Asset: 100M
    50000000,  -- Total Cash: 50M
    50000000,  -- Available Cash: 50M
    0,         -- Order Cash: 0
    50000000,  -- Stock Value: 50M
    2500000,   -- Profit/Loss: +2.5M
    2.5,       -- Profit/Loss Rate: +2.5%
    now()
  )
  ON CONFLICT (user_id) DO UPDATE SET
    total_asset = EXCLUDED.total_asset,
    total_cash = EXCLUDED.total_cash,
    available_cash = EXCLUDED.available_cash,
    stock_value = EXCLUDED.stock_value,
    profit_loss = EXCLUDED.profit_loss,
    profit_loss_rate = EXCLUDED.profit_loss_rate,
    updated_at = now();

  -- 2. Clear existing portfolio for this user
  DELETE FROM public.kw_portfolio WHERE user_id = target_user_id;

  -- 3. Insert Mock Portfolio Items
  INSERT INTO public.kw_portfolio (
    user_id,
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
  ) VALUES 
  (
    target_user_id,
    '005930',
    '삼성전자',
    100,
    100,
    70000,
    7000000,
    72000,
    7200000,
    200000,
    2.85,
    now()
  ),
  (
    target_user_id,
    '000660',
    'SK하이닉스',
    50,
    50,
    120000,
    6000000,
    125000,
    6250000,
    250000,
    4.16,
    now()
  );

  RAISE NOTICE 'Mock data seeded successfully.';
END $$;
