-- ============================================================
-- 모든 백업 테이블 찾기
-- ============================================================

-- 1. 모든 테이블 목록 (backup 관련)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND (
    table_name LIKE '%backup%'
    OR table_name LIKE '%bak%'
    OR table_name LIKE '%old%'
)
ORDER BY table_name;

-- 2. strategies_backup 테이블 확인
SELECT COUNT(*) as strategies_backup_count FROM strategies_backup;

-- 3. strategies_backup에 데이터가 있다면 샘플 조회
SELECT id, name, description, created_at
FROM strategies_backup
ORDER BY created_at DESC
LIMIT 10;
