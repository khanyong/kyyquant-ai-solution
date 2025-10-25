-- stock_metadata 테이블에서 종목명 가져와서 kw_price_current 업데이트

-- 1. stock_metadata 테이블 확인
SELECT COUNT(*) as total_stocks FROM stock_metadata;

-- 2. kw_price_current의 모든 데이터에 종목명 업데이트
UPDATE kw_price_current kpc
SET stock_name = sm.stock_name
FROM stock_metadata sm
WHERE kpc.stock_code = sm.stock_code
  AND (kpc.stock_name IS NULL OR kpc.stock_name = kpc.stock_code);

-- 3. 업데이트 결과 확인
SELECT
  COUNT(*) as updated_count
FROM kw_price_current
WHERE stock_name IS NOT NULL
  AND stock_name != stock_code;

-- 4. 샘플 데이터 확인
SELECT
  stock_code,
  stock_name,
  current_price,
  change_rate,
  updated_at
FROM kw_price_current
WHERE stock_name != stock_code
ORDER BY updated_at DESC
LIMIT 10;

-- 5. 여전히 종목명이 없는 항목 확인
SELECT
  stock_code,
  stock_name,
  current_price
FROM kw_price_current
WHERE stock_name IS NULL OR stock_name = stock_code
LIMIT 10;
