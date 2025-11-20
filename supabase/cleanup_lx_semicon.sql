-- ============================================================================
-- LX세미콘 데이터 정리 (손절 처리)
-- ============================================================================

-- 1단계: 현재 LX세미콘 관련 데이터 확인
SELECT '=== 정리 전 kw_portfolio ===' as section;
SELECT * FROM kw_portfolio WHERE stock_code = '067570';

SELECT '=== 정리 전 positions ===' as section;
SELECT * FROM positions WHERE stock_code = '067570';

SELECT '=== 정리 전 orders ===' as section;
SELECT * FROM orders WHERE stock_code = '067570' OR stock_name LIKE '%LX세미콘%';

-- 2단계: kw_portfolio에서 LX세미콘 삭제
DELETE FROM kw_portfolio WHERE stock_code = '067570';

-- 3단계: positions에서 LX세미콘 삭제 (있다면)
DELETE FROM positions WHERE stock_code = '067570';

-- 4단계: orders에서 LX세미콘 주문 삭제 (있다면)
-- 주의: 주문 히스토리를 유지하고 싶다면 이 단계는 건너뛰세요
-- DELETE FROM orders WHERE stock_code = '067570' OR stock_name LIKE '%LX세미콘%';

-- 5단계: 정리 후 확인
SELECT '=== 정리 후 kw_portfolio ===' as section;
SELECT COUNT(*) as remaining_count FROM kw_portfolio WHERE stock_code = '067570';

SELECT '=== 정리 후 positions ===' as section;
SELECT COUNT(*) as remaining_count FROM positions WHERE stock_code = '067570';

SELECT '=== 정리 후 현재 보유 종목 ===' as section;
SELECT
  kp.stock_code,
  kp.stock_name,
  kp.quantity,
  kp.avg_price,
  kp.purchase_amount,
  kp.profit_loss,
  kp.profit_loss_rate
FROM kw_portfolio kp
ORDER BY kp.updated_at DESC;

SELECT '=== 정리 후 positions 현황 ===' as section;
SELECT
  p.stock_code,
  p.stock_name,
  p.quantity,
  p.avg_buy_price,
  p.total_buy_amount,
  p.position_status,
  s.name as strategy_name
FROM positions p
LEFT JOIN strategies s ON p.strategy_id = s.id
WHERE p.position_status = 'open'
ORDER BY p.last_updated DESC;
