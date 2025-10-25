-- kw_price_current 테이블에 stock_name 컬럼 추가
-- 목적: 종목명을 kw_stock_master와 조인 없이 직접 표시

-- 1. stock_name 컬럼 추가
ALTER TABLE kw_price_current
ADD COLUMN IF NOT EXISTS stock_name VARCHAR(100);

-- 2. 기존 데이터에 종목명 업데이트 (kw_stock_master에서 조인)
UPDATE kw_price_current kpc
SET stock_name = ksm.stock_name
FROM kw_stock_master ksm
WHERE kpc.stock_code = ksm.stock_code
  AND kpc.stock_name IS NULL;

-- 3. 인덱스 추가 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_kw_price_current_stock_name
ON kw_price_current(stock_name);

-- 4. 확인 쿼리
SELECT
  stock_code,
  stock_name,
  current_price,
  change_rate,
  updated_at
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 10;
