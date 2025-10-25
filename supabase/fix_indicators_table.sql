-- ========================================
-- indicators 테이블 중복/불필요 항목 제거
-- Supabase SQL Editor에서 실행하세요
-- ========================================

-- ========================================
-- 1단계: 삭제 대상 확인
-- ========================================
SELECT
  name,
  output_columns,
  calculation_type,
  description
FROM indicators
WHERE name IN ('adx', 'close', 'volume')
ORDER BY name;

-- adx: dmi에 포함되어 있음 (dmi output에 adx 컬럼 있음)
-- close: price에 포함되어 있음 (price output에 close 컬럼 있음)
-- volume: price에 포함되어 있음 (price output에 volume 컬럼 있음)


-- ========================================
-- 2단계: 중복 indicators 삭제
-- ========================================

-- 2-1. adx 삭제 (dmi에 포함됨)
UPDATE indicators
SET is_active = false
WHERE name = 'adx';

-- 2-2. close 삭제 (price에 포함됨)
UPDATE indicators
SET is_active = false
WHERE name = 'close';

-- 2-3. volume 삭제 (price에 포함됨)
UPDATE indicators
SET is_active = false
WHERE name = 'volume';

-- 완전 삭제가 아닌 is_active = false로 비활성화
-- 혹시 참조되는 곳이 있을 수 있으므로


-- ========================================
-- 3단계: 삭제 결과 확인
-- ========================================
SELECT
  name,
  is_active,
  output_columns
FROM indicators
WHERE name IN ('adx', 'close', 'volume')
ORDER BY name;

-- 모두 is_active = false 여야 함


-- ========================================
-- 4단계: 최종 검증 (active indicators만)
-- ========================================
SELECT
  i.name as indicator_name,
  i.output_columns,
  COUNT(ic.column_name) as mapped_columns,
  ARRAY_AGG(ic.column_name ORDER BY ic.column_name) as mapped_column_list
FROM indicators i
LEFT JOIN indicator_columns ic ON i.name = ic.indicator_name
WHERE i.is_active = true
GROUP BY i.name, i.output_columns
ORDER BY i.name;

-- 기대 결과: adx, close, volume이 사라지고
-- 나머지 17개 indicator만 표시되어야 함


-- ========================================
-- 완료!
-- ========================================
-- indicators: 17개 (adx, close, volume 제외)
-- indicator_columns: 16개 indicator_name에 대한 컬럼 매핑
--
-- 다음 단계:
-- 1. backend/indicators/calculator.py 테스트
-- 2. 전략 조건에서 사용하는 indicator 이름 확인
--    - "나의 전략 7": ma_20, ma_12 필요
--    - "[분할] 볼린저밴드": bollinger_lower, rsi 필요
