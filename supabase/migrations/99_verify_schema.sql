-- =====================================================
-- 스키마 검증 쿼리
-- 목적: 모든 마이그레이션이 정상 적용되었는지 확인
-- =====================================================

-- 1. 테이블 존재 및 컬럼 개수 확인
SELECT
  table_name,
  (SELECT COUNT(*) FROM information_schema.columns
   WHERE table_name = t.table_name AND table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('strategy_monitoring', 'orders', 'trading_signals')
ORDER BY table_name;

-- 2. strategy_monitoring 테이블 구조 확인
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'strategy_monitoring'
ORDER BY ordinal_position;

-- 3. orders 테이블 새 컬럼 확인
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'orders'
  AND column_name IN ('auto_cancel_at', 'cancel_after_minutes', 'cancellation_reason', 'original_order_price')
ORDER BY ordinal_position;

-- 4. trading_signals 테이블 새 컬럼 확인
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'trading_signals'
  AND column_name IN ('order_id', 'signal_status')
ORDER BY ordinal_position;

-- 5. 인덱스 확인
SELECT
  schemaname,
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('strategy_monitoring', 'orders', 'trading_signals')
ORDER BY tablename, indexname;

-- 6. 제약 조건 확인
SELECT
  tc.table_name,
  tc.constraint_name,
  tc.constraint_type,
  cc.check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc
  ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
  AND tc.table_name IN ('strategy_monitoring', 'orders', 'trading_signals')
ORDER BY tc.table_name, tc.constraint_type;

-- 7. strategy_monitoring 데이터 확인
SELECT
  COUNT(*) as total_monitoring,
  COUNT(*) FILTER (WHERE is_near_entry = true) as near_entry_count,
  AVG(condition_match_score) as avg_score,
  MAX(condition_match_score) as max_score
FROM strategy_monitoring;

-- 8. orders 테이블 업데이트 확인
SELECT
  COUNT(*) as total_orders,
  COUNT(*) FILTER (WHERE auto_cancel_at IS NOT NULL) as with_auto_cancel,
  COUNT(*) FILTER (WHERE original_order_price IS NOT NULL) as with_original_price
FROM orders
WHERE status IN ('PENDING', 'PARTIAL');

-- 9. trading_signals 상태 분포 확인
SELECT
  signal_status,
  COUNT(*) as count
FROM trading_signals
GROUP BY signal_status
ORDER BY signal_status;

-- 10. 종합 확인 결과
SELECT
  '✅ 스키마 검증 완료' as message,
  NOW() as verified_at;
