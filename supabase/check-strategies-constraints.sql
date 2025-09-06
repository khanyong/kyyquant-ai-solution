-- 1. strategies 테이블의 제약조건 확인
SELECT 
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
JOIN pg_namespace nsp ON nsp.oid = con.connamespace
JOIN pg_class cls ON cls.oid = con.conrelid
WHERE cls.relname = 'strategies'
AND nsp.nspname = 'public';

-- 2. type 컬럼에 대한 체크 제약조건 확인
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'strategies'
AND column_name = 'type';

-- 3. 기존 데이터의 type 값들 확인
SELECT DISTINCT type, COUNT(*) as count
FROM public.strategies
GROUP BY type
ORDER BY count DESC;

-- 4. 체크 제약조건 삭제 (필요한 경우)
-- ALTER TABLE public.strategies DROP CONSTRAINT IF EXISTS strategies_type_check;

-- 5. 새로운 체크 제약조건 추가 (더 많은 타입 허용)
-- ALTER TABLE public.strategies 
-- ADD CONSTRAINT strategies_type_check 
-- CHECK (type IN ('TECHNICAL', 'FUNDAMENTAL', 'HYBRID', 'sma', 'rsi', 'momentum', 'bollinger', 'macd', 'custom'));