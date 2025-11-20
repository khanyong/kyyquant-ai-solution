-- 잘못된 가격 데이터 정리
-- 실행 시간: 약 1초 이내
-- 영향 범위: current_price가 0이거나 NULL인 레코드 삭제

-- 1. current_price가 0인 데이터 수 확인
DO $$
DECLARE
  v_total_count INT;
  v_zero_price_count INT;
  v_valid_price_count INT;
  v_deleted_count INT;
  v_remaining_count INT;
BEGIN
  -- 삭제 전 통계
  SELECT
    COUNT(*),
    COUNT(CASE WHEN current_price::numeric = 0 THEN 1 END),
    COUNT(CASE WHEN current_price::numeric > 0 THEN 1 END)
  INTO v_total_count, v_zero_price_count, v_valid_price_count
  FROM kw_price_current;

  RAISE NOTICE '=== 삭제 전 상태 ===';
  RAISE NOTICE '전체 데이터: % 개', v_total_count;
  RAISE NOTICE '0원 데이터: % 개', v_zero_price_count;
  RAISE NOTICE '유효 데이터: % 개', v_valid_price_count;

  -- current_price가 0이거나 NULL인 데이터 삭제
  DELETE FROM kw_price_current
  WHERE current_price::numeric = 0 OR current_price IS NULL;

  GET DIAGNOSTICS v_deleted_count = ROW_COUNT;

  -- 삭제 후 통계
  SELECT COUNT(*) INTO v_remaining_count FROM kw_price_current;

  RAISE NOTICE '';
  RAISE NOTICE '=== 삭제 후 상태 ===';
  RAISE NOTICE '삭제된 데이터: % 개', v_deleted_count;
  RAISE NOTICE '남은 데이터: % 개', v_remaining_count;
  RAISE NOTICE '';
  RAISE NOTICE '✅ 정리 완료!';
END $$;

-- 2. 남은 데이터 확인 (최근 10개)
SELECT
  stock_code,
  stock_name,
  current_price,
  change_rate,
  volume,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 10;
