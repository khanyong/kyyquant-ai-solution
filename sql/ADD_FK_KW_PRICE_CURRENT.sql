-- kw_price_current 테이블에 kw_stock_master 외래키 추가

-- 1. 외래키 제약조건 추가
ALTER TABLE public.kw_price_current
ADD CONSTRAINT fk_kw_price_current_stock_code
FOREIGN KEY (stock_code)
REFERENCES public.kw_stock_master(stock_code)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- 2. 확인
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'kw_price_current';
