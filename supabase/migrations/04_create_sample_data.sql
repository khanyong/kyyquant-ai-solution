-- =====================================================
-- 테스트용 샘플 데이터 생성 (선택사항)
-- 주의: 실제 데이터가 있는 경우 이 파일은 실행하지 마세요
-- =====================================================

-- 1. 매수 대기 종목 샘플 데이터
-- 실제 strategy_id는 본인의 전략 ID로 변경 필요
INSERT INTO strategy_monitoring (
  strategy_id,
  stock_code,
  stock_name,
  current_price,
  condition_match_score,
  conditions_met,
  is_near_entry
)
SELECT
  s.id,
  '005930',
  '삼성전자',
  72000,
  87.5,
  '{
    "rsi": {"required": "< 30", "current": "32", "met": false, "progress": "93.75"},
    "volume": {"required": "> 2x", "current": "1.8x", "met": false, "progress": "90"},
    "price_ma": {"required": "break below", "current": "approaching", "met": false, "progress": "85"}
  }'::jsonb,
  true
FROM strategies s
WHERE s.is_active = true
LIMIT 1
ON CONFLICT (strategy_id, stock_code) DO NOTHING;

-- 2. 추가 샘플 종목
INSERT INTO strategy_monitoring (
  strategy_id,
  stock_code,
  stock_name,
  current_price,
  condition_match_score,
  conditions_met,
  is_near_entry
)
SELECT
  s.id,
  '000660',
  'SK하이닉스',
  130000,
  82.0,
  '{
    "rsi": {"required": "< 30", "current": "33", "met": false, "progress": "90.91"},
    "volume": {"required": "> 2x", "current": "1.6x", "met": false, "progress": "80"},
    "price_ma": {"required": "break below", "current": "near", "met": false, "progress": "75"}
  }'::jsonb,
  true
FROM strategies s
WHERE s.is_active = true
LIMIT 1
ON CONFLICT (strategy_id, stock_code) DO NOTHING;

-- 3. 샘플 데이터 확인
SELECT
  sm.stock_name,
  sm.stock_code,
  sm.condition_match_score,
  sm.is_near_entry,
  s.name as strategy_name
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
ORDER BY sm.condition_match_score DESC;
