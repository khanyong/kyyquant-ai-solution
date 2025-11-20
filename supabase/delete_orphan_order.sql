-- user_id가 NULL인 잘못된 주문 삭제

DELETE FROM orders
WHERE id = 'a20ab112-64c3-4a4f-9ac3-1c56660e0258'
  AND user_id IS NULL;

-- 확인
SELECT
  '삭제 후 PENDING 주문' as status,
  COUNT(*) as count
FROM orders
WHERE status IN ('PENDING', 'PARTIAL');
