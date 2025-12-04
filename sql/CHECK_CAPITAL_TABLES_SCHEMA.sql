-- Check schema for strategy capital related tables
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name IN (
    'strategy_capital_allocation', 
    'strategy_capital_history', 
    'strategy_capital_status', 
    'strategy_execution_logs',
    'strategy_monitoring'
  )
ORDER BY table_name, ordinal_position;

-- Check if they are views or tables
SELECT 
    table_name, 
    table_type 
FROM information_schema.tables 
WHERE table_schema = 'public'
  AND table_name IN (
    'strategy_capital_allocation', 
    'strategy_capital_history', 
    'strategy_capital_status', 
    'strategy_execution_logs',
    'strategy_monitoring'
  );
