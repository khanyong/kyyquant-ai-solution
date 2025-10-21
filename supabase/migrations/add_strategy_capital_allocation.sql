-- 전략별 자금 할당 기능 추가
-- 각 전략에 할당된 자금을 관리하기 위한 컬럼 추가

-- strategies 테이블에 자금 할당 컬럼 추가
ALTER TABLE strategies
ADD COLUMN IF NOT EXISTS allocated_capital DECIMAL(15, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS allocated_percent DECIMAL(5, 2) DEFAULT 0;

-- 기존 컬럼에 주석 추가
COMMENT ON COLUMN strategies.allocated_capital IS '전략에 할당된 자금 (원)';
COMMENT ON COLUMN strategies.allocated_percent IS '전체 계좌 잔고 대비 할당 비율 (%)';

-- 할당 비율 유효성 체크 제약 조건 추가
ALTER TABLE strategies
ADD CONSTRAINT check_allocated_percent
CHECK (allocated_percent >= 0 AND allocated_percent <= 100);

-- 할당 자금 양수 체크
ALTER TABLE strategies
ADD CONSTRAINT check_allocated_capital
CHECK (allocated_capital >= 0);

-- 인덱스 추가 (활성화된 전략의 자금 할당 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_strategies_active_allocated
ON strategies(user_id, is_active, allocated_percent)
WHERE is_active = true;

-- 전략별 자금 할당 통계 뷰 생성
CREATE OR REPLACE VIEW strategy_capital_allocation AS
SELECT
  user_id,
  COUNT(*) as total_strategies,
  COUNT(*) FILTER (WHERE is_active = true) as active_strategies,
  SUM(allocated_capital) FILTER (WHERE is_active = true) as total_allocated_capital,
  SUM(allocated_percent) FILTER (WHERE is_active = true) as total_allocated_percent,
  100 - COALESCE(SUM(allocated_percent) FILTER (WHERE is_active = true), 0) as remaining_percent
FROM strategies
GROUP BY user_id;

COMMENT ON VIEW strategy_capital_allocation IS '사용자별 전략 자금 할당 현황';
