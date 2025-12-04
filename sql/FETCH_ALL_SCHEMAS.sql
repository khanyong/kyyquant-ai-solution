-- Fetch schema for all major tables
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name IN (
    'strategies',
    'kw_portfolio',
    'orders',
    'kw_account_balance',
    'trading_signals',
    'strategy_universes',
    'kw_price_current',
    'kw_stock_master'
  )
ORDER BY table_name, ordinal_position;
