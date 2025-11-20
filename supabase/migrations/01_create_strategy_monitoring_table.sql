-- =====================================================
-- 전략 모니터링 테이블 생성
-- 목적: 조건 근접도 추적 (매수 대기 종목 관리)
-- =====================================================

-- 1. 테이블 생성
CREATE TABLE IF NOT EXISTS strategy_monitoring (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
  stock_code VARCHAR(10) NOT NULL,
  stock_name VARCHAR(100),
  current_price NUMERIC(10, 2),

  -- 조건 부합도
  condition_match_score NUMERIC(5, 2) DEFAULT 0,  -- 0~100점
  conditions_met JSONB DEFAULT '{}'::jsonb,        -- 각 조건별 충족 여부

  is_near_entry BOOLEAN DEFAULT false,  -- 진입 조건 근접 (80% 이상)

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(strategy_id, stock_code)
);

-- 2. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_strategy_monitoring_near_entry
ON strategy_monitoring(strategy_id, is_near_entry)
WHERE is_near_entry = true;

CREATE INDEX IF NOT EXISTS idx_strategy_monitoring_score
ON strategy_monitoring(strategy_id, condition_match_score DESC);

-- 3. 업데이트 시각 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_strategy_monitoring_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_strategy_monitoring_updated_at
BEFORE UPDATE ON strategy_monitoring
FOR EACH ROW
EXECUTE FUNCTION update_strategy_monitoring_updated_at();

-- 4. 테이블 설명 추가
COMMENT ON TABLE strategy_monitoring IS '전략별 모니터링 종목 및 조건 근접도 추적';
COMMENT ON COLUMN strategy_monitoring.condition_match_score IS '조건 충족도 점수 (0-100)';
COMMENT ON COLUMN strategy_monitoring.conditions_met IS '각 조건별 충족 상태 (JSONB)';
COMMENT ON COLUMN strategy_monitoring.is_near_entry IS '매수 조건 80% 이상 충족 여부';
