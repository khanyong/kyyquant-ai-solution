-- Fetch schema for remaining tables
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name IN (
    'kw_account_balance',
    'strategy_universes',
    'kw_price_current'
  )
ORDER BY table_name, ordinal_position;
