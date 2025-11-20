-- =====================================================
-- strategy_monitoring 테이블에 매도 조건 모니터링 컬럼 추가
-- 목적: 보유 종목의 매도 조건 근접도 추적
-- =====================================================

-- 1. 매도 조건 모니터링 컬럼 추가
ALTER TABLE strategy_monitoring
ADD COLUMN IF NOT EXISTS exit_condition_match_score NUMERIC(5, 2) DEFAULT 0,  -- 매도 조건 충족도 0~100점
ADD COLUMN IF NOT EXISTS exit_conditions_met JSONB DEFAULT '{}'::jsonb,        -- 매도 조건별 충족 여부
ADD COLUMN IF NOT EXISTS is_near_exit BOOLEAN DEFAULT false,                   -- 매도 조건 근접 (80% 이상)
ADD COLUMN IF NOT EXISTS is_held BOOLEAN DEFAULT false;                        -- 포트폴리오 보유 여부

-- 2. 매도 조건 근접 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_strategy_monitoring_near_exit
ON strategy_monitoring(strategy_id, is_near_exit)
WHERE is_near_exit = true AND is_held = true;

-- 3. 복합 인덱스: 보유 종목 + 매도 조건 점수
CREATE INDEX IF NOT EXISTS idx_strategy_monitoring_held_exit_score
ON strategy_monitoring(strategy_id, is_held, exit_condition_match_score DESC)
WHERE is_held = true;

-- 4. 컬럼 설명 추가
COMMENT ON COLUMN strategy_monitoring.exit_condition_match_score IS '매도 조건 충족도 점수 (0-100)';
COMMENT ON COLUMN strategy_monitoring.exit_conditions_met IS '각 매도 조건별 충족 상태 (JSONB)';
COMMENT ON COLUMN strategy_monitoring.is_near_exit IS '매도 조건 80% 이상 충족 여부 (보유 종목만)';
COMMENT ON COLUMN strategy_monitoring.is_held IS '현재 포트폴리오에 보유 중인 종목 여부';

-- 5. 기존 데이터 업데이트 (is_held 플래그 설정)
UPDATE strategy_monitoring sm
SET is_held = EXISTS (
    SELECT 1
    FROM kw_portfolio p
    JOIN strategies s ON s.user_id = p.user_id
    WHERE p.stock_code = sm.stock_code
      AND s.id = sm.strategy_id
      AND p.quantity > 0
)
WHERE is_held = false;
