-- ====================================================================
-- positions 테이블의 account_no 컬럼 확인 및 수정
-- ====================================================================

-- 1. positions 테이블 존재 확인
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'positions'
        ) THEN 'positions 테이블 존재함'
        ELSE 'positions 테이블 없음'
    END as table_status;

-- 2. positions 테이블의 모든 컬럼 확인
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
ORDER BY ordinal_position;

-- 3. account_no 컬럼 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'positions'
            AND column_name = 'account_no'
        ) THEN 'account_no 컬럼이 이미 있습니다'
        ELSE 'account_no 컬럼이 없습니다 - 추가 필요'
    END as account_no_status;

-- 4. account_no 컬럼이 없으면 추가
DO $$
BEGIN
    -- positions 테이블이 존재하는지 확인
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_name = 'positions') THEN
        
        -- account_no 컬럼이 없으면 추가
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'public' 
                       AND table_name = 'positions' 
                       AND column_name = 'account_no') THEN
            
            ALTER TABLE positions ADD COLUMN account_no varchar(20);
            RAISE NOTICE 'account_no 컬럼을 추가했습니다';
        ELSE
            RAISE NOTICE 'account_no 컬럼이 이미 존재합니다';
        END IF;
    ELSE
        RAISE NOTICE 'positions 테이블이 없습니다';
    END IF;
END $$;

-- 5. 추가 후 다시 확인
SELECT 
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
AND column_name = 'account_no';