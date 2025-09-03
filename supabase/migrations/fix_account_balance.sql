-- ====================================================================
-- account_balance 테이블 문제 해결
-- account_no 컬럼이 없어서 인덱스 생성 실패
-- ====================================================================

-- 1. account_balance 테이블 현재 상태 확인
SELECT 
    'account_balance 테이블 컬럼' as info,
    COUNT(*) as column_count,
    string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'account_balance';

-- 2. account_no 컬럼 존재 확인
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'account_balance'
            AND column_name = 'account_no'
        ) THEN 'account_no 컬럼 있음'
        ELSE 'account_no 컬럼 없음 - 추가 필요'
    END as status;

-- 3. account_balance 테이블에 account_no 컬럼 추가 (없는 경우)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'account_balance') THEN
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'public' 
                       AND table_name = 'account_balance' 
                       AND column_name = 'account_no') THEN
            ALTER TABLE account_balance ADD COLUMN account_no varchar(20);
            RAISE NOTICE 'account_balance 테이블에 account_no 컬럼 추가됨';
        ELSE
            RAISE NOTICE 'account_no 컬럼이 이미 존재함';
        END IF;
    END IF;
END $$;

-- 4. 추가 후 확인
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'account_balance'
AND column_name = 'account_no';

-- 5. 이제 인덱스 생성 (account_no 컬럼 추가 후)
CREATE INDEX IF NOT EXISTS idx_balance_account_time 
ON account_balance(account_no, updated_at DESC);

-- 6. 결과 확인
SELECT 
    'account_balance 인덱스' as category,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename = 'account_balance'
AND indexname = 'idx_balance_account_time';