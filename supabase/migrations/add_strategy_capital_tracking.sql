-- 전략별 자금 추적 및 검증 시스템
-- Phase 1: 실시간 자금 현황 뷰 및 검증 함수

-- ============================================
-- 1. 전략별 실시간 자금 현황 뷰
-- ============================================

CREATE OR REPLACE VIEW strategy_capital_status AS
SELECT
  s.id as strategy_id,
  s.user_id,
  s.name as strategy_name,
  s.allocated_capital,
  s.allocated_percent,
  s.is_active,

  -- 활성 포지션에 사용 중인 자금 (매수가 기준)
  COALESCE(
    (
      SELECT SUM(quantity * avg_buy_price)
      FROM positions
      WHERE strategy_id = s.id AND position_status = 'OPEN'
    ), 0
  ) as capital_in_use,

  -- 활성 포지션 개수
  COALESCE(
    (
      SELECT COUNT(*)
      FROM positions
      WHERE strategy_id = s.id AND position_status = 'OPEN'
    ), 0
  ) as active_positions,

  -- 총 평가 손익 (미실현 손익)
  COALESCE(
    (
      SELECT SUM(profit_loss)
      FROM positions
      WHERE strategy_id = s.id AND position_status = 'OPEN'
    ), 0
  ) as total_unrealized_pnl,

  -- 총 실현 손익 (청산된 포지션)
  COALESCE(
    (
      SELECT SUM(realized_profit_loss)
      FROM positions
      WHERE strategy_id = s.id AND position_status = 'CLOSED'
    ), 0
  ) as total_realized_pnl,

  -- 최종 업데이트 시간
  (
    SELECT MAX(last_updated)
    FROM positions
    WHERE strategy_id = s.id AND position_status = 'OPEN'
  ) as last_position_update

FROM strategies s
WHERE s.is_active = true;

COMMENT ON VIEW strategy_capital_status IS '전략별 실시간 자금 사용 현황 및 손익';

-- ============================================
-- 2. 전략별 가용 자금 계산 함수
-- ============================================

CREATE OR REPLACE FUNCTION get_strategy_available_capital(
  p_strategy_id UUID,
  p_account_balance DECIMAL DEFAULT NULL
) RETURNS DECIMAL AS $$
DECLARE
  v_allocated_capital DECIMAL;
  v_allocated_percent DECIMAL;
  v_capital_in_use DECIMAL;
  v_total_allocated DECIMAL;
  v_available_capital DECIMAL;
BEGIN
  -- 전략 정보 조회
  SELECT
    COALESCE(allocated_capital, 0),
    COALESCE(allocated_percent, 0)
  INTO v_allocated_capital, v_allocated_percent
  FROM strategies
  WHERE id = p_strategy_id AND is_active = true;

  -- 전략이 없거나 비활성
  IF NOT FOUND THEN
    RETURN 0;
  END IF;

  -- 사용 중인 자금 계산
  SELECT COALESCE(capital_in_use, 0)
  INTO v_capital_in_use
  FROM strategy_capital_status
  WHERE strategy_id = p_strategy_id;

  -- 할당된 총 자금 결정
  IF v_allocated_capital > 0 THEN
    -- 고정 금액 모드
    v_total_allocated := v_allocated_capital;
  ELSIF v_allocated_percent > 0 AND p_account_balance IS NOT NULL THEN
    -- 비율 모드 (계좌 잔고 필요)
    v_total_allocated := p_account_balance * v_allocated_percent / 100;
  ELSE
    -- 할당 없음 - 계좌 잔고 전체 사용 가능
    IF p_account_balance IS NOT NULL THEN
      v_total_allocated := p_account_balance;
    ELSE
      v_total_allocated := 999999999; -- 무제한
    END IF;
  END IF;

  -- 가용 자금 = 할당 자금 - 사용 중 자금
  v_available_capital := v_total_allocated - v_capital_in_use;

  -- 음수면 0 반환
  IF v_available_capital < 0 THEN
    RETURN 0;
  END IF;

  RETURN v_available_capital;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_strategy_available_capital IS '전략의 현재 가용 자금 계산';

-- ============================================
-- 3. 매수 전 자금 검증 함수
-- ============================================

CREATE OR REPLACE FUNCTION check_strategy_capital(
  p_strategy_id UUID,
  p_order_amount DECIMAL,
  p_account_balance DECIMAL DEFAULT NULL
) RETURNS JSONB AS $$
DECLARE
  v_strategy_name TEXT;
  v_allocated_capital DECIMAL;
  v_allocated_percent DECIMAL;
  v_capital_in_use DECIMAL;
  v_available_capital DECIMAL;
  v_total_allocated DECIMAL;
  v_active_positions INTEGER;
BEGIN
  -- 전략 정보 조회
  SELECT
    name,
    COALESCE(allocated_capital, 0),
    COALESCE(allocated_percent, 0)
  INTO v_strategy_name, v_allocated_capital, v_allocated_percent
  FROM strategies
  WHERE id = p_strategy_id AND is_active = true;

  -- 전략이 없거나 비활성
  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'allowed', false,
      'reason', '전략이 존재하지 않거나 비활성 상태입니다',
      'strategy_id', p_strategy_id,
      'available_capital', 0,
      'order_amount', p_order_amount
    );
  END IF;

  -- 현재 자금 상황 조회
  SELECT
    capital_in_use,
    active_positions
  INTO v_capital_in_use, v_active_positions
  FROM strategy_capital_status
  WHERE strategy_id = p_strategy_id;

  -- 데이터 없으면 기본값
  v_capital_in_use := COALESCE(v_capital_in_use, 0);
  v_active_positions := COALESCE(v_active_positions, 0);

  -- 할당된 총 자금 계산
  IF v_allocated_capital > 0 THEN
    -- 고정 금액 모드
    v_total_allocated := v_allocated_capital;
  ELSIF v_allocated_percent > 0 AND p_account_balance IS NOT NULL THEN
    -- 비율 모드
    v_total_allocated := p_account_balance * v_allocated_percent / 100;
  ELSE
    -- 할당 없음 - 무제한
    IF p_account_balance IS NOT NULL THEN
      v_total_allocated := p_account_balance;
    ELSE
      -- 계좌 잔고 정보 없으면 허용
      RETURN jsonb_build_object(
        'allowed', true,
        'reason', '할당 자금 미설정 (무제한)',
        'strategy_name', v_strategy_name,
        'available_capital', NULL,
        'order_amount', p_order_amount,
        'capital_in_use', v_capital_in_use,
        'active_positions', v_active_positions
      );
    END IF;
  END IF;

  -- 가용 자금 계산
  v_available_capital := v_total_allocated - v_capital_in_use;

  -- 검증 결과 반환
  IF p_order_amount <= v_available_capital THEN
    RETURN jsonb_build_object(
      'allowed', true,
      'reason', '자금 충분',
      'strategy_name', v_strategy_name,
      'total_allocated', v_total_allocated,
      'capital_in_use', v_capital_in_use,
      'available_capital', v_available_capital,
      'order_amount', p_order_amount,
      'remaining_after_order', v_available_capital - p_order_amount,
      'active_positions', v_active_positions,
      'allocation_mode', CASE
        WHEN v_allocated_capital > 0 THEN 'fixed'
        WHEN v_allocated_percent > 0 THEN 'percent'
        ELSE 'unlimited'
      END
    );
  ELSE
    RETURN jsonb_build_object(
      'allowed', false,
      'reason', '할당 자금 부족',
      'strategy_name', v_strategy_name,
      'total_allocated', v_total_allocated,
      'capital_in_use', v_capital_in_use,
      'available_capital', v_available_capital,
      'order_amount', p_order_amount,
      'shortfall', p_order_amount - v_available_capital,
      'active_positions', v_active_positions,
      'allocation_mode', CASE
        WHEN v_allocated_capital > 0 THEN 'fixed'
        WHEN v_allocated_percent > 0 THEN 'percent'
        ELSE 'unlimited'
      END
    );
  END IF;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION check_strategy_capital IS '전략별 매수 가능 여부 검증 (자금 초과 방지)';

-- ============================================
-- 4. 전략별 자금 이력 테이블 (선택)
-- ============================================

CREATE TABLE IF NOT EXISTS strategy_capital_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id),

  -- 변경 정보
  event_type VARCHAR(50) NOT NULL, -- 'position_open', 'position_close', 'allocation_change'

  -- 자금 스냅샷
  total_allocated DECIMAL(15, 2),
  capital_in_use DECIMAL(15, 2),
  available_capital DECIMAL(15, 2),

  -- 포지션 정보 (해당되는 경우)
  position_id UUID REFERENCES positions(id),
  order_amount DECIMAL(15, 2),

  -- 메타데이터
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_capital_history_strategy
ON strategy_capital_history(strategy_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_capital_history_user
ON strategy_capital_history(user_id, created_at DESC);

COMMENT ON TABLE strategy_capital_history IS '전략별 자금 변동 이력 추적';

-- ============================================
-- 5. 자금 이력 자동 기록 트리거 (선택)
-- ============================================

CREATE OR REPLACE FUNCTION track_strategy_capital_change()
RETURNS TRIGGER AS $$
DECLARE
  v_strategy_id UUID;
  v_user_id UUID;
  v_order_amount DECIMAL;
  v_event_type VARCHAR(50);
BEGIN
  IF TG_TABLE_NAME = 'positions' THEN
    v_strategy_id := COALESCE(NEW.strategy_id, OLD.strategy_id);
    v_user_id := COALESCE(NEW.user_id, OLD.user_id);
    v_order_amount := COALESCE(NEW.quantity * NEW.avg_buy_price, OLD.quantity * OLD.avg_buy_price);

    -- 이벤트 타입 결정
    IF TG_OP = 'INSERT' THEN
      v_event_type := 'position_open';
    ELSIF TG_OP = 'UPDATE' AND OLD.position_status = 'OPEN' AND NEW.position_status = 'CLOSED' THEN
      v_event_type := 'position_close';
    ELSE
      RETURN NEW;
    END IF;

    -- 이력 기록
    INSERT INTO strategy_capital_history (
      strategy_id,
      user_id,
      event_type,
      position_id,
      order_amount,
      total_allocated,
      capital_in_use,
      available_capital
    )
    SELECT
      v_strategy_id,
      v_user_id,
      v_event_type,
      COALESCE(NEW.id, OLD.id),
      v_order_amount,
      CASE
        WHEN s.allocated_capital > 0 THEN s.allocated_capital
        ELSE 0
      END,
      scs.capital_in_use,
      get_strategy_available_capital(v_strategy_id)
    FROM strategies s
    LEFT JOIN strategy_capital_status scs ON scs.strategy_id = s.id
    WHERE s.id = v_strategy_id;

  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
DROP TRIGGER IF EXISTS trigger_track_capital_on_position ON positions;
CREATE TRIGGER trigger_track_capital_on_position
AFTER INSERT OR UPDATE ON positions
FOR EACH ROW
EXECUTE FUNCTION track_strategy_capital_change();

-- ============================================
-- 6. 유틸리티: 전체 전략 자금 현황 조회 함수
-- ============================================

CREATE OR REPLACE FUNCTION get_all_strategies_capital_summary(p_user_id UUID)
RETURNS TABLE (
  strategy_id UUID,
  strategy_name TEXT,
  allocation_mode TEXT,
  total_allocated DECIMAL,
  capital_in_use DECIMAL,
  available_capital DECIMAL,
  utilization_rate DECIMAL,
  active_positions INTEGER,
  total_pnl DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    scs.strategy_id,
    scs.strategy_name,
    CASE
      WHEN scs.allocated_capital > 0 THEN '고정 금액'
      WHEN scs.allocated_percent > 0 THEN '비율 (' || scs.allocated_percent || '%)'
      ELSE '미설정'
    END as allocation_mode,
    CASE
      WHEN scs.allocated_capital > 0 THEN scs.allocated_capital
      ELSE 0
    END as total_allocated,
    scs.capital_in_use,
    CASE
      WHEN scs.allocated_capital > 0 THEN scs.allocated_capital - scs.capital_in_use
      ELSE 0
    END as available_capital,
    CASE
      WHEN scs.allocated_capital > 0 AND scs.allocated_capital > 0 THEN
        ROUND((scs.capital_in_use / scs.allocated_capital * 100)::numeric, 2)
      ELSE 0
    END as utilization_rate,
    scs.active_positions::INTEGER,
    (scs.total_unrealized_pnl + scs.total_realized_pnl) as total_pnl
  FROM strategy_capital_status scs
  WHERE scs.user_id = p_user_id
  ORDER BY scs.strategy_name;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_all_strategies_capital_summary IS '사용자의 전체 전략 자금 요약';
