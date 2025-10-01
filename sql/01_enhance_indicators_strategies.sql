-- ============================================================
-- Phase 1: Supabase 스키마 강화 - 버전/체크섬/SSOT 보장
-- ============================================================
-- 목적: 지표/전략의 재현성·버전관리·검증 강화
-- 적용: Supabase SQL Editor에서 실행
-- ============================================================

-- ------------------------------------------------------------
-- 1. indicators 테이블 강화
-- ------------------------------------------------------------

-- 기존 테이블이 있다면 컬럼 추가 (없으면 CREATE 전체 실행)
ALTER TABLE IF EXISTS indicators
    ADD COLUMN IF NOT EXISTS version TEXT DEFAULT '1.0.0',
    ADD COLUMN IF NOT EXISTS checksum TEXT,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
    ADD COLUMN IF NOT EXISTS updated_by TEXT,
    ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 체크섬 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_indicator_checksum()
RETURNS TRIGGER AS $$
BEGIN
    -- formula.code + output_columns + default_params의 해시
    NEW.checksum := md5(
        COALESCE(NEW.formula->>'code', '') ||
        ARRAY_TO_STRING(NEW.output_columns, ',') ||
        COALESCE(NEW.default_params::text, '')
    );
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS indicator_checksum_trigger ON indicators;
CREATE TRIGGER indicator_checksum_trigger
    BEFORE INSERT OR UPDATE ON indicators
    FOR EACH ROW
    EXECUTE FUNCTION update_indicator_checksum();

-- 제약 조건 추가
DO $$
BEGIN
    -- formula에 code 키 필수 (python_code 타입인 경우)
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'indicators_formula_code_check'
    ) THEN
        ALTER TABLE indicators
        ADD CONSTRAINT indicators_formula_code_check
        CHECK (
            calculation_type != 'python_code'
            OR (formula ? 'code' AND LENGTH(formula->>'code') > 0)
        );
    END IF;

    -- output_columns 비어있지 않음
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'indicators_output_columns_check'
    ) THEN
        ALTER TABLE indicators
        ADD CONSTRAINT indicators_output_columns_check
        CHECK (ARRAY_LENGTH(output_columns, 1) > 0);
    END IF;

    -- name은 소문자로 정규화 (대소문자 무관 유니크)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'idx_indicators_name_version'
    ) THEN
        CREATE UNIQUE INDEX idx_indicators_name_version
        ON indicators (LOWER(name), version);
    END IF;
END $$;

-- 활성화된 지표만 조회하는 뷰 (백테스트에서 사용)
CREATE OR REPLACE VIEW active_indicators AS
SELECT
    id,
    name,
    calculation_type,
    formula,
    output_columns,
    default_params,
    version,
    checksum
FROM indicators
WHERE is_active = true;

COMMENT ON VIEW active_indicators IS '백테스트/실전에서 사용 가능한 활성 지표만 조회';


-- ------------------------------------------------------------
-- 2. strategies 테이블 강화
-- ------------------------------------------------------------

ALTER TABLE IF EXISTS strategies
    ADD COLUMN IF NOT EXISTS version TEXT DEFAULT '1.0.0',
    ADD COLUMN IF NOT EXISTS checksum TEXT,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
    ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 전략 체크섬 자동 업데이트
CREATE OR REPLACE FUNCTION update_strategy_checksum()
RETURNS TRIGGER AS $$
BEGIN
    -- config 전체의 해시 (indicators, buyConditions, sellConditions)
    NEW.checksum := md5(NEW.config::text);
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS strategy_checksum_trigger ON strategies;
CREATE TRIGGER strategy_checksum_trigger
    BEFORE INSERT OR UPDATE ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_strategy_checksum();

-- 전략 config 필수 필드 검증
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'strategies_config_check'
    ) THEN
        ALTER TABLE strategies
        ADD CONSTRAINT strategies_config_check
        CHECK (
            config ? 'indicators'
            AND config ? 'buyConditions'
            AND config ? 'sellConditions'
        );
    END IF;
END $$;

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_is_active ON strategies(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_strategies_tags ON strategies USING GIN(tags);

COMMENT ON COLUMN strategies.version IS '전략 버전 (SemVer)';
COMMENT ON COLUMN strategies.checksum IS 'config의 MD5 해시 (재현성 보장)';
COMMENT ON COLUMN strategies.tags IS '전략 분류 태그 (예: [''momentum'', ''long''])';


-- ------------------------------------------------------------
-- 3. 백테스트 기록 테이블 (재현성/감사 추적)
-- ------------------------------------------------------------

-- 백테스트 실행 기록
CREATE TABLE IF NOT EXISTS backtest_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 전략 참조
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    strategy_version TEXT NOT NULL,
    strategy_checksum TEXT NOT NULL,

    -- 사용된 지표 버전 (JSONB 배열)
    -- 예: [{"name": "macd", "version": "1.0.0", "checksum": "abc123"}, ...]
    indicators_versions JSONB NOT NULL,

    -- 실행 환경
    code_commit_hash TEXT,  -- Git 커밋 해시 (옵션)
    engine_version TEXT,    -- 백테스트 엔진 버전

    -- 실행 설정
    stock_codes TEXT[] NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital NUMERIC(15,2) DEFAULT 10000000,
    commission NUMERIC(6,5) DEFAULT 0.00015,
    slippage NUMERIC(6,5) DEFAULT 0.001,
    params JSONB DEFAULT '{}'::jsonb,  -- 기타 파라미터

    -- 실행 상태
    status TEXT DEFAULT 'pending',  -- pending/running/completed/failed
    error_message TEXT,

    -- 결과 요약 (completed 시)
    total_trades INTEGER,
    win_rate NUMERIC(5,2),
    total_return NUMERIC(10,4),
    sharpe_ratio NUMERIC(6,3),
    max_drawdown NUMERIC(10,4),
    result_summary JSONB,  -- 전체 결과 JSON

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- 메타
    created_by UUID,  -- user_id
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_backtest_runs_strategy ON backtest_runs(strategy_id);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_status ON backtest_runs(status);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_created_by ON backtest_runs(created_by);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_date_range ON backtest_runs(start_date, end_date);

COMMENT ON TABLE backtest_runs IS '백테스트 실행 기록 - 전략/지표 버전 고정으로 완전한 재현 가능';
COMMENT ON COLUMN backtest_runs.indicators_versions IS '실행 시점의 지표 정의 스냅샷 (버전+체크섬)';
COMMENT ON COLUMN backtest_runs.code_commit_hash IS '백테스트 코드의 Git 커밋 해시 (재현성)';


-- 백테스트 거래 기록 (Trade-level)
CREATE TABLE IF NOT EXISTS backtest_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES backtest_runs(id) ON DELETE CASCADE,

    -- 거래 정보
    stock_code TEXT NOT NULL,
    side TEXT NOT NULL,  -- buy/sell
    quantity INTEGER NOT NULL,
    price NUMERIC(12,2) NOT NULL,

    -- 타이밍
    trade_date DATE NOT NULL,
    trade_time TIME,
    signal_timestamp TIMESTAMPTZ,

    -- 손익
    pnl NUMERIC(15,2),
    pnl_percent NUMERIC(10,4),
    commission_paid NUMERIC(10,2),
    slippage_cost NUMERIC(10,2),

    -- 매매 이유 (선택)
    signal_reason TEXT,
    conditions_met JSONB,

    -- 포지션 정보
    position_size NUMERIC(15,2),  -- 총 포지션 가치
    entry_price NUMERIC(12,2),    -- 진입가 (매도 시)
    hold_days INTEGER,            -- 보유일수 (매도 시)

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_backtest_trades_run_id ON backtest_trades(run_id);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_stock_code ON backtest_trades(stock_code);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_date ON backtest_trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_side ON backtest_trades(side);

COMMENT ON TABLE backtest_trades IS '백테스트 개별 거래 기록 (매매 시점/가격/손익)';


-- 백테스트 자산 곡선 (Equity Curve)
CREATE TABLE IF NOT EXISTS backtest_equity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES backtest_runs(id) ON DELETE CASCADE,

    -- 시계열
    date DATE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,

    -- 자산
    equity NUMERIC(15,2) NOT NULL,
    cash NUMERIC(15,2) NOT NULL,
    position_value NUMERIC(15,2) NOT NULL,

    -- 성과 지표
    daily_return NUMERIC(10,6),
    cumulative_return NUMERIC(10,4),
    drawdown NUMERIC(10,4),
    drawdown_duration INTEGER,  -- 손실 지속일

    -- 포지션 스냅샷 (옵션)
    positions JSONB,  -- [{"code": "005930", "qty": 100, "value": 7000000}, ...]

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(run_id, date)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_backtest_equity_run_id ON backtest_equity(run_id);
CREATE INDEX IF NOT EXISTS idx_backtest_equity_date ON backtest_equity(run_id, date);

COMMENT ON TABLE backtest_equity IS '백테스트 일별 자산 곡선 (성과 추적/차트 렌더링)';


-- ------------------------------------------------------------
-- 4. 헬퍼 함수 - 백테스트 실행 기록 조회
-- ------------------------------------------------------------

-- 최근 백테스트 실행 조회
CREATE OR REPLACE FUNCTION get_recent_backtest_runs(
    p_strategy_id UUID DEFAULT NULL,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    strategy_name TEXT,
    stock_codes TEXT[],
    date_range TEXT,
    status TEXT,
    total_return NUMERIC,
    win_rate NUMERIC,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        br.id,
        s.name AS strategy_name,
        br.stock_codes,
        CONCAT(br.start_date::TEXT, ' ~ ', br.end_date::TEXT) AS date_range,
        br.status,
        br.total_return,
        br.win_rate,
        br.created_at
    FROM backtest_runs br
    LEFT JOIN strategies s ON br.strategy_id = s.id
    WHERE
        (p_strategy_id IS NULL OR br.strategy_id = p_strategy_id)
    ORDER BY br.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- 백테스트 성과 비교 (같은 전략의 여러 실행)
CREATE OR REPLACE FUNCTION compare_backtest_performance(
    p_strategy_id UUID
)
RETURNS TABLE (
    run_id UUID,
    date_range TEXT,
    total_return NUMERIC,
    sharpe_ratio NUMERIC,
    max_drawdown NUMERIC,
    total_trades INTEGER,
    win_rate NUMERIC,
    completed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id AS run_id,
        CONCAT(start_date::TEXT, ' ~ ', end_date::TEXT) AS date_range,
        total_return,
        sharpe_ratio,
        max_drawdown,
        total_trades,
        win_rate,
        completed_at
    FROM backtest_runs
    WHERE
        strategy_id = p_strategy_id
        AND status = 'completed'
    ORDER BY completed_at DESC;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- 5. 권한 설정 (RLS - Row Level Security)
-- ------------------------------------------------------------

-- 백테스트 기록은 소유자만 조회 가능 (선택적)
ALTER TABLE backtest_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY backtest_runs_policy ON backtest_runs
    FOR ALL
    USING (created_by = auth.uid());

-- 읽기 전용 정책 (팀 공유 시)
CREATE POLICY backtest_runs_read_policy ON backtest_runs
    FOR SELECT
    USING (
        created_by = auth.uid()
        OR EXISTS (
            SELECT 1 FROM strategies
            WHERE id = backtest_runs.strategy_id
            AND user_id = auth.uid()
        )
    );


-- ------------------------------------------------------------
-- 6. 초기 데이터 검증 및 마이그레이션
-- ------------------------------------------------------------

-- 기존 indicators 테이블에 체크섬 생성
UPDATE indicators
SET
    checksum = md5(
        COALESCE(formula->>'code', '') ||
        ARRAY_TO_STRING(output_columns, ',') ||
        COALESCE(default_params::text, '')
    ),
    version = COALESCE(version, '1.0.0')
WHERE checksum IS NULL;

-- 기존 strategies 테이블에 체크섬 생성
UPDATE strategies
SET
    checksum = md5(config::text),
    version = COALESCE(version, '1.0.0')
WHERE checksum IS NULL;


-- ------------------------------------------------------------
-- 7. 완료 확인 쿼리
-- ------------------------------------------------------------

DO $$
BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Phase 1 Schema Enhancement Complete';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Tables created/updated:';
    RAISE NOTICE '  - indicators (+ version/checksum)';
    RAISE NOTICE '  - strategies (+ version/checksum)';
    RAISE NOTICE '  - backtest_runs (new)';
    RAISE NOTICE '  - backtest_trades (new)';
    RAISE NOTICE '  - backtest_equity (new)';
    RAISE NOTICE '';
    RAISE NOTICE 'Next: Run preflight validation system';
END $$;