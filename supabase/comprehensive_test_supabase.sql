-- =====================================================
-- 종합 시스템 동작 확인 테스트 (Supabase용)
-- =====================================================

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 1. strategy_monitoring 테이블 스키마 확인
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT
    column_name,
    data_type,
    CASE WHEN column_name IN ('exit_condition_match_score', 'exit_conditions_met', 'is_near_exit', 'is_held')
         THEN '✅ 신규 컬럼'
         ELSE ''
    END as status
FROM information_schema.columns
WHERE table_name = 'strategy_monitoring'
ORDER BY ordinal_position;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2. 최근 업데이트된 모니터링 데이터 (최근 5분)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT
    stock_code,
    stock_name,
    condition_match_score as buy_score,
    exit_condition_match_score as sell_score,
    is_near_entry as near_buy,
    is_near_exit as near_sell,
    is_held,
    CASE
        WHEN updated_at > NOW() - INTERVAL '1 minute' THEN '🟢 방금 전'
        WHEN updated_at > NOW() - INTERVAL '5 minute' THEN '🟡 5분 이내'
        ELSE '🔴 오래됨'
    END as freshness,
    updated_at
FROM strategy_monitoring
WHERE updated_at > NOW() - INTERVAL '5 minute'
ORDER BY updated_at DESC
LIMIT 10;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 3. 매수 대기 종목 (조건 80% 이상)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT
    stock_code,
    stock_name,
    condition_match_score,
    is_held,
    '🎯 매수 대기' as status
FROM strategy_monitoring
WHERE condition_match_score >= 80
  AND condition_match_score < 100
  AND updated_at > NOW() - INTERVAL '1 hour'
ORDER BY condition_match_score DESC;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 4. 매도 대기 종목 (보유 종목 + 조건 80% 이상) ⭐
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT
    sm.stock_code,
    sm.stock_name,
    sm.exit_condition_match_score,
    sm.is_held,
    p.quantity as portfolio_qty,
    CASE
        WHEN sm.is_held = false AND p.quantity > 0 THEN '❌ is_held 플래그 오류!'
        WHEN sm.is_held = true AND (p.quantity IS NULL OR p.quantity = 0) THEN '❌ 실제 미보유!'
        WHEN sm.is_held = true AND p.quantity > 0 THEN '✅ 정상'
        ELSE '⚠️ 확인 필요'
    END as validation,
    '🟢 매도 대기' as status
FROM strategy_monitoring sm
LEFT JOIN kw_portfolio p ON p.stock_code = sm.stock_code
WHERE sm.exit_condition_match_score >= 80
  AND sm.exit_condition_match_score < 100
  AND sm.is_held = true
  AND sm.updated_at > NOW() - INTERVAL '1 hour'
ORDER BY sm.exit_condition_match_score DESC;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 5. 보유 종목 vs is_held 플래그 일치 여부 검증
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WITH portfolio_stocks AS (
    SELECT DISTINCT stock_code
    FROM kw_portfolio
    WHERE quantity > 0
),
monitoring_held AS (
    SELECT DISTINCT stock_code, is_held
    FROM strategy_monitoring
)
SELECT
    COALESCE(p.stock_code, m.stock_code) as stock_code,
    CASE WHEN p.stock_code IS NOT NULL THEN '✅ 보유' ELSE '❌ 미보유' END as portfolio_status,
    CASE WHEN m.is_held = true THEN '✅ is_held=true' ELSE '❌ is_held=false' END as monitoring_status,
    CASE
        WHEN p.stock_code IS NOT NULL AND m.is_held = true THEN '✅ 정상'
        WHEN p.stock_code IS NULL AND (m.is_held = false OR m.is_held IS NULL) THEN '✅ 정상'
        WHEN p.stock_code IS NOT NULL AND m.is_held = false THEN '❌ 오류: 보유하는데 is_held=false'
        WHEN p.stock_code IS NULL AND m.is_held = true THEN '❌ 오류: 미보유인데 is_held=true'
        ELSE '⚠️ 알 수 없음'
    END as validation
FROM portfolio_stocks p
FULL OUTER JOIN monitoring_held m ON p.stock_code = m.stock_code
ORDER BY validation DESC;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 6. 최근 SELL 신호 확인 (보유 종목만 발생해야 함)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT
    ts.stock_code,
    ts.stock_name,
    ts.signal_type,
    ts.created_at,
    p.quantity as portfolio_qty,
    CASE
        WHEN ts.signal_type = 'sell' AND (p.quantity IS NULL OR p.quantity = 0)
            THEN '❌ 오류: 미보유 종목인데 SELL 신호!'
        WHEN ts.signal_type = 'sell' AND p.quantity > 0
            THEN '✅ 정상: 보유 종목 SELL'
        WHEN ts.signal_type = 'buy'
            THEN '✅ BUY 신호 (검증 불필요)'
        ELSE 'ℹ️ 기타'
    END as validation
FROM trading_signals ts
LEFT JOIN kw_portfolio p ON p.stock_code = ts.stock_code
WHERE ts.created_at > NOW() - INTERVAL '24 hours'
  AND ts.signal_type IN ('buy', 'sell')
ORDER BY ts.created_at DESC
LIMIT 20;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 7. 활성화된 전략 확인
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled,
    CASE
        WHEN entry_conditions IS NOT NULL THEN '✅' ELSE '❌'
    END as has_entry,
    CASE
        WHEN exit_conditions IS NOT NULL THEN '✅' ELSE '❌'
    END as has_exit,
    allocated_capital
FROM strategies
WHERE is_active = true
  AND auto_trade_enabled = true
ORDER BY created_at DESC;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- ✅ 테스트 완료!
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
