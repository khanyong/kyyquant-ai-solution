-- ============================================================================
-- FIX: n8n 워크플로우 "자동매매 전략 조회" 노드 데이터 누락 문제 해결
-- ============================================================================
-- 문제: RPC 함수가 strategy_id, strategy_name, entry_conditions, exit_conditions를 반환하지 않음
-- 원인: 데이터베이스 스키마 또는 RPC 함수 정의 불일치
-- ============================================================================

-- 1단계: 현재 RPC 함수 제거
DROP FUNCTION IF EXISTS get_active_strategies_with_universe();

-- 2단계: 올바른 RPC 함수 재생성
CREATE OR REPLACE FUNCTION get_active_strategies_with_universe()
RETURNS TABLE (
    strategy_id uuid,
    strategy_name text,
    entry_conditions jsonb,
    exit_conditions jsonb,
    filter_id uuid,
    filter_name text,
    filtered_stocks jsonb,
    allocated_capital numeric,
    allocated_percent numeric
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.id as strategy_id,
    s.name::text as strategy_name,
    COALESCE(s.entry_conditions, '{}'::jsonb) as entry_conditions,
    COALESCE(s.exit_conditions, '{}'::jsonb) as exit_conditions,
    kif.id as filter_id,
    kif.name::text as filter_name,
    kif.filtered_stocks as filtered_stocks,
    COALESCE(s.allocated_capital, 0)::numeric as allocated_capital,
    COALESCE(s.allocated_percent, 0)::numeric as allocated_percent
  FROM strategies s
  INNER JOIN strategy_universes su ON s.id = su.strategy_id
  INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
  WHERE
    s.auto_execute = true
    AND s.is_active = true
    AND su.is_active = true
    AND kif.is_active = true
  ORDER BY s.created_at DESC;
END;
$$;

-- 3단계: 권한 부여
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO anon;
GRANT EXECUTE ON FUNCTION public.get_active_strategies_with_universe() TO authenticated;

-- 4단계: 테스트 쿼리
SELECT
    strategy_id,
    strategy_name,
    entry_conditions,
    exit_conditions,
    filter_name,
    jsonb_array_length(filtered_stocks) as stock_count,
    allocated_capital,
    allocated_percent
FROM get_active_strategies_with_universe();

-- 5단계: 진단 - 활성 전략 확인
SELECT
    'Active Strategies' as check_name,
    COUNT(*) as count
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 6단계: 진단 - strategy_universes 연결 확인
SELECT
    'Active Strategy Universes' as check_name,
    COUNT(*) as count
FROM strategy_universes
WHERE is_active = true;

-- 7단계: 진단 - 전체 조인 결과 확인
SELECT
    s.id,
    s.name,
    s.entry_conditions IS NOT NULL as has_entry,
    s.exit_conditions IS NOT NULL as has_exit,
    kif.name as filter_name,
    jsonb_array_length(kif.filtered_stocks) as stock_count
FROM strategies s
LEFT JOIN strategy_universes su ON s.id = su.strategy_id
LEFT JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE s.auto_execute = true AND s.is_active = true;
