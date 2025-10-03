-- ============================================================
-- 백업 테이블 확인 - 데이터 복구 가능 여부 체크
-- ============================================================

-- 1. strategies_backup 테이블 확인
SELECT COUNT(*) as backup_count FROM strategies_backup;

SELECT * FROM strategies_backup LIMIT 5;

-- 2. 다른 백업 테이블 존재 여부 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE '%strateg%backup%'
OR table_name LIKE '%backup%strateg%';

-- 3. strategies_backup_before_reset 테이블 확인 (이전 SQL 파일에서 생성한 백업)
SELECT COUNT(*) as backup_before_reset_count
FROM strategies_backup_before_reset;

SELECT * FROM strategies_backup_before_reset LIMIT 5;

-- 4. strategies_backup_before_format_migration 테이블 확인
SELECT COUNT(*) as backup_before_migration_count
FROM strategies_backup_before_format_migration;

SELECT * FROM strategies_backup_before_format_migration LIMIT 5;
