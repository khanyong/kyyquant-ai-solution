-- ====================================================================
-- 전체 마이그레이션 실행 스크립트
-- 순서대로 실행하면 안전하게 테이블이 생성됩니다
-- ====================================================================

-- STEP 0: 실행 전 확인사항
-- 1. Supabase Dashboard > SQL Editor에서 실행
-- 2. 각 단계별로 실행하여 오류 확인
-- 3. 오류 발생 시 해당 단계만 수정 후 재실행

-- ====================================================================
-- STEP 1: 새 테이블 생성 (01_create_new_tables.sql)
-- ====================================================================
-- 먼저 01_create_new_tables.sql 실행

-- ====================================================================
-- STEP 2: positions 테이블 처리 (02_create_or_update_positions.sql)
-- ====================================================================
-- 다음 02_create_or_update_positions.sql 실행

-- ====================================================================
-- STEP 3: 기존 테이블 업데이트 (03_update_existing_tables.sql)
-- ====================================================================
-- 다음 03_update_existing_tables.sql 실행

-- ====================================================================
-- STEP 4: 인덱스 생성 (04_create_indexes.sql)
-- ====================================================================
-- 다음 04_create_indexes.sql 실행

-- ====================================================================
-- STEP 5: RLS 정책 (05_setup_rls_policies.sql)
-- ====================================================================
-- 마지막 05_setup_rls_policies.sql 실행

-- ====================================================================
-- 검증 쿼리 (모든 단계 완료 후 실행)
-- ====================================================================
-- 생성된 테이블 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'market_data',
    'technical_indicators',
    'kiwoom_orders',
    'positions',
    'account_balance',
    'strategy_execution_logs',
    'alerts',
    'system_settings'
)
ORDER BY table_name;

-- positions 테이블 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'positions'
AND column_name IN ('account_no', 'stock_code', 'user_id', 'strategy_id')
ORDER BY ordinal_position;

-- 인덱스 확인
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('positions', 'market_data', 'kiwoom_orders')
ORDER BY tablename, indexname;