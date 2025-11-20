-- kw_price_current 테이블의 모든 컬럼 값 확인

SELECT
  stock_code,
  stock_name,
  current_price,
  change_price,
  change_rate,
  volume,
  trading_value,
  high_52w,
  low_52w,
  updated_at
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 5;

-- 특정 종목의 상세 데이터 (모든 컬럼)
SELECT *
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 1;
