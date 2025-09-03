-- ====================================================================
-- positions 테이블 문제 진단
-- 왜 account_no 오류가 계속 발생하는지 확인
-- ====================================================================

-- 1. positions 테이블이 실제로 있는지
SELECT 
    'positions 테이블 존재 여부' as check_type,
    EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'positions'
    ) as result;

-- 2. positions 테이블의 실제 컬럼들
SELECT 
    ordinal_position,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
ORDER BY ordinal_position;

-- 3. positions 테이블에 대한 모든 제약조건
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid = 'positions'::regclass::oid;

-- 4. positions 테이블과 관련된 뷰나 다른 객체가 있는지
SELECT 
    dependent.relname as dependent_object,
    dependent.relkind as object_type,
    pg_describe_object(dep.classid, dep.objid, dep.objsubid) as description
FROM pg_depend dep
JOIN pg_class dependent ON dep.objid = dependent.oid
WHERE dep.refobjid = 'positions'::regclass::oid
AND dependent.relname != 'positions';

-- 5. 현재 positions 테이블의 DDL 구조 추출
SELECT 
    'CREATE TABLE positions (' || E'\n' ||
    string_agg(
        '    ' || column_name || ' ' || 
        data_type || 
        CASE 
            WHEN character_maximum_length IS NOT NULL 
            THEN '(' || character_maximum_length || ')'
            WHEN numeric_precision IS NOT NULL 
            THEN '(' || numeric_precision || ',' || COALESCE(numeric_scale, 0) || ')'
            ELSE ''
        END ||
        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
        CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
        E',\n' ORDER BY ordinal_position
    ) || E'\n);' as current_ddl
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions';

-- 6. 혹시 다른 스키마에 positions가 있는지
SELECT 
    table_schema,
    table_name,
    COUNT(*) as column_count
FROM information_schema.tables
WHERE table_name = 'positions'
GROUP BY table_schema, table_name;