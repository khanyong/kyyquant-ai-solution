-- ============================================
-- 기존 strategies 테이블 수정 SQL
-- Supabase SQL Editor에서 실행
-- ============================================

-- 1단계: 필수 컬럼 추가
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS version TEXT DEFAULT '1.0.0',
ADD COLUMN IF NOT EXISTS author TEXT,
ADD COLUMN IF NOT EXISTS timeframe TEXT DEFAULT '1d',
ADD COLUMN IF NOT EXISTS universe TEXT[],
ADD COLUMN IF NOT EXISTS is_test_mode BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS auto_trade_enabled BOOLEAN DEFAULT FALSE;

-- 2단계: 전략 코드 및 성과 관련 컬럼 추가
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS strategy_code TEXT,
ADD COLUMN IF NOT EXISTS code_hash TEXT,
ADD COLUMN IF NOT EXISTS performance_metrics JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS last_signal_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS last_trade_at TIMESTAMPTZ;

-- 3단계: 세분화된 설정 컬럼 추가 (선택사항이지만 권장)
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS indicators JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS entry_conditions JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS exit_conditions JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS risk_management JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS backtest_settings JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS notifications JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS custom_parameters JSONB DEFAULT '{}';

-- 4단계: 기존 config 데이터를 새 컬럼으로 복사 (데이터가 있는 경우)
UPDATE strategies 
SET 
    indicators = CASE 
        WHEN config ? 'indicators' THEN config->'indicators'
        ELSE '{}'::jsonb 
    END,
    entry_conditions = CASE 
        WHEN config ? 'entry_conditions' THEN config->'entry_conditions'
        ELSE '{}'::jsonb 
    END,
    exit_conditions = CASE 
        WHEN config ? 'exit_conditions' THEN config->'exit_conditions'
        ELSE '{}'::jsonb 
    END,
    risk_management = CASE 
        WHEN config ? 'risk_management' THEN config->'risk_management'
        ELSE '{}'::jsonb 
    END
WHERE config IS NOT NULL AND config != '{}'::jsonb;

-- 5단계: 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_strategies_active_auto 
ON strategies(is_active, auto_trade_enabled) 
WHERE is_active = true AND auto_trade_enabled = true;

CREATE INDEX IF NOT EXISTS idx_strategies_user_active 
ON strategies(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_strategies_universe 
ON strategies USING GIN(universe);

-- 6단계: 기본값 설정 (기존 레코드에 대해)
UPDATE strategies 
SET 
    version = '1.0.0' WHERE version IS NULL;

UPDATE strategies 
SET 
    timeframe = '1d' WHERE timeframe IS NULL;

UPDATE strategies 
SET 
    is_test_mode = TRUE WHERE is_test_mode IS NULL;

UPDATE strategies 
SET 
    auto_trade_enabled = FALSE WHERE auto_trade_enabled IS NULL;

-- 7단계: 컬럼 설명 추가 (문서화)
COMMENT ON COLUMN strategies.strategy_code IS 'Python 전략 실행 코드';
COMMENT ON COLUMN strategies.universe IS '대상 종목 코드 배열 (예: {005930, 000660})';
COMMENT ON COLUMN strategies.indicators IS '기술적 지표 설정 (RSI, MACD, BB 등)';
COMMENT ON COLUMN strategies.entry_conditions IS '진입 조건 설정';
COMMENT ON COLUMN strategies.exit_conditions IS '청산 조건 설정 (손절, 익절 등)';
COMMENT ON COLUMN strategies.risk_management IS '리스크 관리 설정';
COMMENT ON COLUMN strategies.performance_metrics IS '실시간 성과 지표';
COMMENT ON COLUMN strategies.auto_trade_enabled IS '자동매매 활성화 여부';

-- 8단계: 뷰 생성 (편의 기능)
CREATE OR REPLACE VIEW active_trading_strategies AS
SELECT 
    s.id,
    s.user_id,
    s.name,
    s.type,
    s.version,
    s.timeframe,
    s.universe,
    s.is_active,
    s.auto_trade_enabled,
    s.last_signal_at,
    s.last_trade_at,
    s.performance_metrics,
    u.email as user_email
FROM strategies s
LEFT JOIN auth.users u ON s.user_id = u.id
WHERE s.is_active = true 
AND s.auto_trade_enabled = true;

-- 9단계: 함수 생성 - 전략 설정 통합 조회
CREATE OR REPLACE FUNCTION get_complete_strategy_config(strategy_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT 
        jsonb_build_object(
            'id', id,
            'name', name,
            'type', type,
            'version', version,
            'timeframe', timeframe,
            'universe', universe,
            'is_test_mode', is_test_mode,
            'auto_trade_enabled', auto_trade_enabled,
            -- config와 개별 컬럼 모두 지원
            'indicators', COALESCE(indicators, config->'indicators', '{}'),
            'entry_conditions', COALESCE(entry_conditions, config->'entry_conditions', '{}'),
            'exit_conditions', COALESCE(exit_conditions, config->'exit_conditions', '{}'),
            'risk_management', COALESCE(risk_management, config->'risk_management', '{}'),
            'backtest_settings', COALESCE(backtest_settings, config->'backtest_settings', '{}'),
            'notifications', COALESCE(notifications, config->'notifications', '{}'),
            'custom_parameters', COALESCE(custom_parameters, config->'custom_parameters', '{}'),
            'performance_metrics', performance_metrics,
            'last_signal_at', last_signal_at,
            'last_trade_at', last_trade_at
        )
    INTO result
    FROM strategies
    WHERE id = strategy_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 10단계: 트리거 - updated_at 자동 업데이트 (이미 있을 수 있음)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_strategies_updated_at ON strategies;
CREATE TRIGGER update_strategies_updated_at 
BEFORE UPDATE ON strategies 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 검증 쿼리 (실행 후 확인용)
-- ============================================

-- 테이블 구조 확인
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'strategies' 
-- ORDER BY ordinal_position;

-- 인덱스 확인
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'strategies';

-- 샘플 데이터 확인
-- SELECT id, name, version, universe, auto_trade_enabled 
-- FROM strategies 
-- LIMIT 5;