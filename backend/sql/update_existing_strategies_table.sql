-- ============================================
-- 기존 strategies 테이블에 필요한 컬럼 추가
-- 기존 데이터를 보존하면서 새 기능 추가
-- ============================================

-- 1. 새로운 컬럼들 추가 (기존 테이블 수정)
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS version TEXT DEFAULT '1.0.0',
ADD COLUMN IF NOT EXISTS author TEXT,
ADD COLUMN IF NOT EXISTS strategy_type TEXT DEFAULT 'custom',
ADD COLUMN IF NOT EXISTS timeframe TEXT DEFAULT '1d',
ADD COLUMN IF NOT EXISTS universe TEXT[],  -- 대상 종목 배열
ADD COLUMN IF NOT EXISTS is_test_mode BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS auto_trade_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS strategy_code TEXT,  -- Python 코드 저장
ADD COLUMN IF NOT EXISTS code_hash TEXT,
ADD COLUMN IF NOT EXISTS performance_metrics JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS last_signal_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS last_trade_at TIMESTAMPTZ;

-- 2. config 컬럼 구조 표준화를 위한 새 컬럼들 (선택사항)
-- 기존 config를 세분화하려면 추가
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS indicators JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS entry_conditions JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS exit_conditions JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS risk_management JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS backtest_settings JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS notifications JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS custom_parameters JSONB DEFAULT '{}';

-- 3. 기존 config 데이터를 새 컬럼으로 마이그레이션 (선택사항)
-- config 필드에 있던 데이터를 세분화된 필드로 이동
UPDATE strategies 
SET 
    indicators = COALESCE(config->'indicators', '{}'),
    entry_conditions = COALESCE(config->'entry_conditions', '{}'),
    exit_conditions = COALESCE(config->'exit_conditions', '{}'),
    risk_management = COALESCE(config->'risk_management', '{}')
WHERE config IS NOT NULL;

-- 4. 인덱스 추가 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_strategies_active_auto 
ON strategies(is_active, auto_trade_enabled) 
WHERE is_active = true AND auto_trade_enabled = true;

CREATE INDEX IF NOT EXISTS idx_strategies_user_active 
ON strategies(user_id, is_active);

-- 5. 기본 전략 설정 템플릿 (config 구조 예시)
-- 이제 config 또는 개별 컬럼 모두 사용 가능
COMMENT ON COLUMN strategies.config IS '
레거시 호환용. 새 전략은 개별 컬럼 사용 권장.
예시 구조:
{
  "indicators": {
    "rsi_enabled": true,
    "rsi_period": 14,
    "macd_enabled": true
  },
  "entry_conditions": {
    "buy_signals_required": 3,
    "min_volume_ratio": 1.5
  },
  "exit_conditions": {
    "stop_loss_percent": 3.0,
    "take_profit_percent": 10.0
  },
  "risk_management": {
    "max_positions": 3,
    "daily_loss_limit": 2.0
  }
}';

-- 6. 전략 코드 저장 예시
COMMENT ON COLUMN strategies.strategy_code IS '
Python 전략 코드를 TEXT로 저장.
예시:
def calculate_signal(data):
    if data["rsi"] < 30:
        return {"type": "buy", "strength": 0.8}
    elif data["rsi"] > 70:
        return {"type": "sell", "strength": 0.8}
    return {"type": "hold", "strength": 0}
';

-- 7. 뷰 생성 - 활성 전략만 조회
CREATE OR REPLACE VIEW active_strategies AS
SELECT 
    s.*,
    u.email as user_email
FROM strategies s
LEFT JOIN auth.users u ON s.user_id = u.id
WHERE s.is_active = true 
AND s.auto_trade_enabled = true;

-- 8. 함수 - 전략 설정 가져오기 (통합)
CREATE OR REPLACE FUNCTION get_strategy_config(strategy_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT 
        jsonb_build_object(
            'name', name,
            'type', type,
            'version', version,
            'timeframe', timeframe,
            'universe', universe,
            'indicators', COALESCE(indicators, config->'indicators', '{}'),
            'entry_conditions', COALESCE(entry_conditions, config->'entry_conditions', '{}'),
            'exit_conditions', COALESCE(exit_conditions, config->'exit_conditions', '{}'),
            'risk_management', COALESCE(risk_management, config->'risk_management', '{}')
        )
    INTO result
    FROM strategies
    WHERE id = strategy_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 실행 방법:
-- 1. Supabase SQL Editor에서 실행
-- 2. 기존 데이터는 모두 보존됨
-- 3. 새 기능이 추가됨
-- ============================================