-- Check columns of kw_stock_master
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'kw_stock_master';
