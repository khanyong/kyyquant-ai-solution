-- ========================================
-- stocks 테이블 empty 행 삭제 가이드
-- Supabase SQL Editor에서 순서대로 실행하세요
-- ========================================

-- ========================================
-- 1단계: empty 행 확인
-- ========================================
SELECT
  code,
  name,
  market,
  sector,
  created_at
FROM stocks
WHERE
  code IS NULL
  OR code = ''
  OR TRIM(code) = ''
  OR name IS NULL
  OR name = ''
  OR TRIM(name) = ''
ORDER BY created_at DESC;

-- 결과를 확인하고 삭제할 행이 맞는지 검토하세요.
-- 계속 진행하려면 다음 단계로 이동


-- ========================================
-- 2단계: Foreign Key 제약 확인
-- ========================================
SELECT
  tc.constraint_name,
  tc.table_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.table_name = 'stocks'
  AND tc.constraint_type = 'FOREIGN KEY';

-- Foreign Key가 있다면 참조하는 데이터를 먼저 삭제해야 합니다.


-- ========================================
-- 3단계: RLS 상태 확인
-- ========================================
SELECT
  schemaname,
  tablename,
  rowsecurity
FROM pg_tables
WHERE tablename = 'stocks';

-- rowsecurity가 true이면 RLS가 활성화된 상태입니다.


-- ========================================
-- 4단계: RLS 비활성화
-- ========================================
ALTER TABLE stocks DISABLE ROW LEVEL SECURITY;

-- RLS를 비활성화하면 관리자 권한으로 모든 행에 접근 가능합니다.


-- ========================================
-- 5단계: empty 행 삭제
-- ========================================
DELETE FROM stocks
WHERE
  code IS NULL
  OR code = ''
  OR TRIM(code) = ''
  OR name IS NULL
  OR name = ''
  OR TRIM(name) = '';

-- 삭제된 행 수를 확인하세요.


-- ========================================
-- 6단계: RLS 재활성화
-- ========================================
ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;

-- 보안을 위해 RLS를 다시 활성화합니다.


-- ========================================
-- 7단계: 삭제 결과 확인
-- ========================================
SELECT COUNT(*) as total_stocks FROM stocks;

SELECT
  code,
  name,
  market,
  COUNT(*) as count
FROM stocks
GROUP BY code, name, market
ORDER BY count DESC
LIMIT 10;

-- ========================================
-- 완료!
-- ========================================
