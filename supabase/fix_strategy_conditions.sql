-- ========================================
-- 전략 entry_conditions 수정
-- Supabase SQL Editor에서 실행하세요
-- ========================================

-- ========================================
-- 문제점:
-- 1. "나의 전략 7": right 값이 20, 12 (숫자)
--    → "ma_20", "ma_12" (문자열)로 수정 필요
-- 2. "[분할] 볼린저밴드": bollinger_lower, bollinger_upper 사용
--    → indicators.output_columns와 일치함 ✅
-- 3. 두 전략 모두 rsi 사용
--    → indicators.output_columns와 일치함 ✅
-- ========================================


-- ========================================
-- 1단계: "나의 전략 7" 수정
-- ========================================

UPDATE strategies
SET entry_conditions = jsonb_set(
  jsonb_set(
    entry_conditions,
    '{buy,0,right}',
    '"ma_20"'
  ),
  '{buy,1,right}',
  '"ma_12"'
)
WHERE name = '나의 전략 7';

-- 결과: close < 20 → close < ma_20
--      close < 12 → close < ma_12


-- ========================================
-- 2단계: "나의 전략 7" value 필드도 수정
-- ========================================

UPDATE strategies
SET entry_conditions = jsonb_set(
  jsonb_set(
    entry_conditions,
    '{buy,0,value}',
    '"ma_20"'
  ),
  '{buy,1,value}',
  '"ma_12"'
)
WHERE name = '나의 전략 7';

-- value 필드도 문자열로 변경


-- ========================================
-- 3단계: 수정 결과 확인
-- ========================================

SELECT
  id,
  name,
  entry_conditions->'buy' as buy_conditions
FROM strategies
WHERE name = '나의 전략 7';

-- 기대 결과:
-- buy_conditions[0].right = "ma_20"
-- buy_conditions[0].value = "ma_20"
-- buy_conditions[1].right = "ma_12"
-- buy_conditions[1].value = "ma_12"


-- ========================================
-- 4단계: 모든 활성 전략의 조건 확인
-- ========================================

SELECT
  name,
  entry_conditions->'buy' as buy_conditions,
  exit_conditions->'sell' as sell_conditions
FROM strategies
WHERE auto_execute = true
  AND is_active = true
ORDER BY name;

-- "[분할] 볼린저밴드": bollinger_lower, bollinger_upper, rsi 사용 ✅
-- "나의 전략 7": ma_20, ma_12 사용 ✅


-- ========================================
-- 5단계: 필요한 지표 목록 추출
-- ========================================

-- 모든 활성 전략에서 사용하는 지표 이름 추출
WITH strategy_conditions AS (
  SELECT
    jsonb_array_elements(entry_conditions->'buy') as buy_condition,
    jsonb_array_elements(exit_conditions->'sell') as sell_condition
  FROM strategies
  WHERE auto_execute = true
    AND is_active = true
),
all_indicators AS (
  SELECT DISTINCT (buy_condition->>'right') as indicator_name
  FROM strategy_conditions
  WHERE buy_condition->>'right' IS NOT NULL
  UNION
  SELECT DISTINCT (sell_condition->>'right') as indicator_name
  FROM strategy_conditions
  WHERE sell_condition->>'right' IS NOT NULL
)
SELECT
  indicator_name,
  CASE
    WHEN indicator_name ~ '^ma_\d+$' THEN 'ma with period ' || substring(indicator_name from '\d+$')
    WHEN indicator_name ~ '^bollinger_' THEN 'bollinger bands output column'
    WHEN indicator_name ~ '^\d+$' THEN 'numeric value (not indicator)'
    ELSE 'standard indicator'
  END as indicator_type
FROM all_indicators
WHERE indicator_name IS NOT NULL
  AND indicator_name != 'close'  -- close는 price에 포함됨
  AND indicator_name !~ '^\d+$'  -- 숫자만 있는 것은 제외 (45, 35, 75 등)
ORDER BY indicator_name;

-- 기대 결과:
-- bollinger_lower (bollinger bands output column)
-- bollinger_upper (bollinger bands output column)
-- ma_12 (ma with period 12)
-- ma_20 (ma with period 20)
-- rsi (standard indicator)


-- ========================================
-- 완료!
-- ========================================
-- 수정 내용:
-- 1. "나의 전략 7" entry_conditions.buy[0].right: 20 → "ma_20"
-- 2. "나의 전략 7" entry_conditions.buy[1].right: 12 → "ma_12"
-- 3. value 필드도 동일하게 수정
--
-- 다음 단계:
-- 1. n8n workflow v21 생성
-- 2. "지표 계산" 노드 추가 (백엔드 API 호출)
-- 3. indicators 객체에 ma_20, ma_12, bollinger_lower, bollinger_upper, rsi 추가
