-- kw_price_current 테이블 데이터 확인

-- 1. 전체 데이터 수
SELECT
  '=== 전체 데이터 수 ===' as section,
  COUNT(*) as total_count,
  COUNT(CASE WHEN current_price > 0 THEN 1 END) as with_price_count,
  COUNT(CASE WHEN current_price = 0 THEN 1 END) as zero_price_count
FROM kw_price_current;

-- 2. 최근 업데이트된 데이터 (상위 20개)
SELECT
  '=== 최근 업데이트 데이터 ===' as section;

SELECT
  stock_code,
  stock_name,
  current_price,
  change_price,
  change_rate,
  volume,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 20;

-- 3. current_price = 0인 데이터
SELECT
  '=== 현재가가 0인 데이터 ===' as section;

SELECT
  stock_code,
  stock_name,
  current_price,
  updated_at
FROM kw_price_current
WHERE current_price = 0
ORDER BY updated_at DESC
LIMIT 10;

-- 4. 활성 전략의 유니버스 종목 코드
SELECT
  '=== 활성 전략 유니버스 종목 ===' as section;

SELECT
  strategy_id,
  strategy_name,
  filtered_stocks
FROM get_active_strategies_with_universe()
LIMIT 10;
