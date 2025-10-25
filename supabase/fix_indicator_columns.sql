-- ========================================
-- indicator_columns 테이블 불일치 수정
-- Supabase SQL Editor에서 순서대로 실행하세요
-- ========================================

-- ========================================
-- 1단계: 현재 상태 확인
-- ========================================
SELECT
  indicator_name,
  column_name,
  column_type,
  column_description
FROM indicator_columns
ORDER BY indicator_name, column_name;

-- 현재 상태:
-- - adx (3 columns) - 실제로는 dmi이어야 함
-- - atr (2 columns)
-- - bb (3 columns) + bollinger_bands (5 columns) - 중복!
-- - ema, ichimoku, macd, parabolic_sar, price, rsi, stochastic, volume_ma
-- indicators 테이블에는 20개 indicator가 있음


-- ========================================
-- 2단계: adx → dmi 이름 통일
-- ========================================
-- indicators 테이블에는 "dmi"로 되어 있지만
-- indicator_columns에는 "adx"로 잘못 되어 있음

UPDATE indicator_columns
SET indicator_name = 'dmi'
WHERE indicator_name = 'adx';

-- 결과: adx → dmi 로 통일


-- ========================================
-- 3단계: bollinger 이름 통일 + bb 중복 제거
-- ========================================
-- indicators 테이블에는 "bollinger"로 되어 있음
-- indicator_columns에는 "bb"(3개)와 "bollinger_bands"(5개)로 중복됨
-- "bollinger"로 통일하고 bb는 삭제

-- 3-1. bb 삭제 (중복이므로)
DELETE FROM indicator_columns
WHERE indicator_name = 'bb';

-- 3-2. bollinger_bands → bollinger로 변경
UPDATE indicator_columns
SET indicator_name = 'bollinger'
WHERE indicator_name = 'bollinger_bands';

-- 결과: bollinger_bands → bollinger 로 통일 (bb는 삭제됨)


-- ========================================
-- 4단계: parabolic_sar → parabolic 이름 통일
-- ========================================
-- indicators 테이블에는 "parabolic"로 되어 있지만
-- indicator_columns에는 "parabolic_sar"로 되어 있음

UPDATE indicator_columns
SET indicator_name = 'parabolic'
WHERE indicator_name = 'parabolic_sar';

-- 결과: parabolic_sar → parabolic 로 통일


-- ========================================
-- 5단계: 누락된 지표 추가
-- ========================================

-- 5-1. ma (Moving Average) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description)
VALUES
  ('ma', 'ma', 'numeric', '이동평균선');

-- 5-2. sma (Simple Moving Average) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description)
VALUES
  ('sma', 'sma', 'numeric', '단순 이동평균');

-- 5-3. cci (Commodity Channel Index) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description)
VALUES
  ('cci', 'cci', 'numeric', 'CCI 지표');

-- 5-4. obv (On-Balance Volume) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description)
VALUES
  ('obv', 'obv', 'numeric', '거래량 지표');

-- 5-5. vwap (Volume Weighted Average Price) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description)
VALUES
  ('vwap', 'vwap', 'numeric', '거래량 가중 평균가');

-- 5-6. williams (Williams %R) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description)
VALUES
  ('williams', 'williams_r', 'numeric', 'Williams %R 지표');


-- ========================================
-- 6단계: 수정 결과 확인
-- ========================================
SELECT
  indicator_name,
  column_name,
  column_type,
  column_description,
  COUNT(*) OVER (PARTITION BY indicator_name) as columns_per_indicator
FROM indicator_columns
ORDER BY indicator_name, column_name;

-- 기대 결과:
-- - dmi: 3개 컬럼 (adx, minus_di, plus_di)
-- - bollinger: 5개 컬럼 (bb_lower, bb_middle, bb_pct, bb_upper, bb_width)
-- - parabolic: 2개 컬럼 (psar, psar_trend)
-- - ma, sma, cci, obv, vwap, williams: 각 1개 컬럼


-- ========================================
-- 7단계: indicators 테이블과 비교 검증
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

-- 각 indicator의 output_columns 배열과
-- indicator_columns에 매핑된 컬럼 목록이 일치하는지 확인


-- ========================================
-- 완료!
-- ========================================
-- 수정 내용:
-- 1. adx → dmi로 변경 (indicators 테이블과 일치)
-- 2. bb 삭제 (중복), bollinger_bands → bollinger로 변경
-- 3. parabolic_sar → parabolic로 변경
-- 4. 누락된 6개 지표 추가: ma, sma, cci, obv, vwap, williams
--
-- 다음 단계:
-- 1. 7단계 쿼리 결과 확인하여 indicators와 indicator_columns 일치 확인
-- 2. backend/indicators/calculator.py가 정상 작동하는지 테스트
-- 3. n8n workflow에 지표 계산 로직 추가
