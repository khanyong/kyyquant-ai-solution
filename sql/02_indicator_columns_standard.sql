-- ============================================================
-- Phase 2.5a: 지표 컬럼 표준화 테이블
-- ============================================================
-- 목적: 지표명 → 생성 컬럼의 "계약" 명시화
-- 효과: 조건 검증 시 명확한 컬럼 목록 조회 가능
-- ============================================================

-- ------------------------------------------------------------
-- 1. indicator_columns 테이블 (지표-컬럼 매핑)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS indicator_columns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 지표 참조
    indicator_name TEXT NOT NULL,
    indicator_version TEXT DEFAULT '1.0.0',

    -- 생성 컬럼
    column_name TEXT NOT NULL,
    column_type TEXT DEFAULT 'numeric',  -- numeric/text/boolean
    column_description TEXT,

    -- 순서 (지표가 여러 컬럼 생성 시)
    output_order INTEGER DEFAULT 0,

    -- 메타
    is_primary BOOLEAN DEFAULT false,  -- 주 컬럼 (예: sma의 'sma')
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 제약
    UNIQUE(indicator_name, column_name)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_indicator_columns_name ON indicator_columns(indicator_name) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_indicator_columns_column ON indicator_columns(column_name);

COMMENT ON TABLE indicator_columns IS '지표가 생성하는 컬럼의 표준 정의 (명명 계약)';
COMMENT ON COLUMN indicator_columns.is_primary IS 'True면 지표의 대표 컬럼 (예: macd의 "macd")';


-- ------------------------------------------------------------
-- 2. 핵심 지표 10개 등록 (표준 컬럼명)
-- ------------------------------------------------------------

-- 2.1 SMA (Simple Moving Average)
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('sma', 'sma', 'Simple moving average value', true, 1)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.2 EMA (Exponential Moving Average)
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('ema', 'ema', 'Exponential moving average value', true, 1)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.3 MACD
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('macd', 'macd', 'MACD line (fast EMA - slow EMA)', true, 1),
('macd', 'macd_signal', 'Signal line (EMA of MACD)', false, 2),
('macd', 'macd_hist', 'Histogram (MACD - Signal)', false, 3)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.4 RSI (Relative Strength Index)
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('rsi', 'rsi', 'Relative Strength Index (0-100)', true, 1)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.5 Bollinger Bands
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('bollinger_bands', 'bb_upper', 'Upper band (SMA + std_dev * multiplier)', false, 1),
('bollinger_bands', 'bb_middle', 'Middle band (SMA)', true, 2),
('bollinger_bands', 'bb_lower', 'Lower band (SMA - std_dev * multiplier)', false, 3),
('bollinger_bands', 'bb_width', 'Band width (upper - lower)', false, 4),
('bollinger_bands', 'bb_pct', 'Price position within bands (0-1)', false, 5)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 별칭 (bb)
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('bb', 'bb_upper', 'Upper band', false, 1),
('bb', 'bb_middle', 'Middle band', true, 2),
('bb', 'bb_lower', 'Lower band', false, 3)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.6 Stochastic Oscillator
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('stochastic', 'stochastic_k', '%K line (fast stochastic)', true, 1),
('stochastic', 'stochastic_d', '%D line (slow stochastic, SMA of %K)', false, 2)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.7 ATR (Average True Range)
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('atr', 'atr', 'Average True Range (volatility)', true, 1),
('atr', 'atr_pct', 'ATR as percentage of close', false, 2)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.8 ADX (Average Directional Index)
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('adx', 'adx', 'Average Directional Index (trend strength)', true, 1),
('adx', 'plus_di', 'Positive Directional Indicator', false, 2),
('adx', 'minus_di', 'Negative Directional Indicator', false, 3)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.9 Volume MA
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('volume_ma', 'volume_ma', 'Volume moving average', true, 1),
('volume_ma', 'volume_ratio', 'Current volume / MA', false, 2)
ON CONFLICT (indicator_name, column_name) DO NOTHING;

-- 2.10 Parabolic SAR
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('parabolic_sar', 'psar', 'Parabolic SAR value', true, 1),
('parabolic_sar', 'psar_trend', 'Trend direction (1=up, -1=down)', false, 2)
ON CONFLICT (indicator_name, column_name) DO NOTHING;


-- ------------------------------------------------------------
-- 3. 가격 데이터 컬럼 (항상 존재)
-- ------------------------------------------------------------

INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('price', 'open', 'Opening price', false, 1),
('price', 'high', 'High price', false, 2),
('price', 'low', 'Low price', false, 3),
('price', 'close', 'Closing price', true, 4),
('price', 'volume', 'Trading volume', false, 5),
('price', 'trade_date', 'Trading date', false, 6)
ON CONFLICT (indicator_name, column_name) DO NOTHING;


-- ------------------------------------------------------------
-- 4. 헬퍼 함수
-- ------------------------------------------------------------

-- 지표가 생성하는 컬럼 조회
CREATE OR REPLACE FUNCTION get_indicator_columns(p_indicator_name TEXT)
RETURNS TABLE(column_name TEXT, is_primary BOOLEAN, output_order INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ic.column_name,
        ic.is_primary,
        ic.output_order
    FROM indicator_columns ic
    WHERE
        ic.indicator_name = p_indicator_name
        AND ic.is_active = true
    ORDER BY ic.output_order;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_indicator_columns IS '지표명으로 생성 컬럼 목록 조회';


-- 조건에서 사용 가능한 모든 컬럼 조회
CREATE OR REPLACE FUNCTION get_available_columns(p_indicator_names TEXT[])
RETURNS TABLE(column_name TEXT, source_indicator TEXT) AS $$
BEGIN
    RETURN QUERY
    -- 가격 데이터 (항상 포함)
    SELECT
        ic.column_name,
        'price'::TEXT as source_indicator
    FROM indicator_columns ic
    WHERE
        ic.indicator_name = 'price'
        AND ic.is_active = true

    UNION

    -- 지정된 지표들
    SELECT
        ic.column_name,
        ic.indicator_name as source_indicator
    FROM indicator_columns ic
    WHERE
        ic.indicator_name = ANY(p_indicator_names)
        AND ic.is_active = true

    ORDER BY column_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_available_columns IS '전략에서 사용 가능한 모든 컬럼 조회 (가격 + 지표들)';


-- ------------------------------------------------------------
-- 5. indicators 테이블과 동기화 체크
-- ------------------------------------------------------------

-- indicators 테이블의 output_columns가 indicator_columns와 일치하는지 검증
CREATE OR REPLACE FUNCTION validate_indicator_output_columns()
RETURNS TABLE(
    indicator_name TEXT,
    status TEXT,
    registered_columns TEXT[],
    declared_columns TEXT[],
    missing TEXT[],
    extra TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    WITH registered AS (
        SELECT
            ic.indicator_name,
            ARRAY_AGG(ic.column_name ORDER BY ic.output_order) as cols
        FROM indicator_columns ic
        WHERE ic.is_active = true AND ic.indicator_name != 'price'
        GROUP BY ic.indicator_name
    ),
    declared AS (
        SELECT
            i.name,
            i.output_columns as cols
        FROM indicators i
        WHERE i.is_active = true
    )
    SELECT
        COALESCE(r.indicator_name, d.name) as indicator_name,
        CASE
            WHEN r.cols = d.cols THEN '✓ Matched'
            WHEN r.cols IS NULL THEN '⚠ Not in standard table'
            WHEN d.cols IS NULL THEN '⚠ Not in indicators table'
            ELSE '❌ Mismatch'
        END as status,
        r.cols as registered_columns,
        d.cols as declared_columns,
        ARRAY(SELECT UNNEST(d.cols) EXCEPT SELECT UNNEST(r.cols)) as missing,
        ARRAY(SELECT UNNEST(r.cols) EXCEPT SELECT UNNEST(d.cols)) as extra
    FROM registered r
    FULL OUTER JOIN declared d ON r.indicator_name = d.name
    ORDER BY
        CASE
            WHEN r.cols = d.cols THEN 1
            ELSE 2
        END,
        indicator_name;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- 6. 검증 실행
-- ------------------------------------------------------------

DO $$
DECLARE
    rec RECORD;
    mismatch_count INT := 0;
BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Indicator Columns Standard Table';
    RAISE NOTICE '====================================';

    -- 등록된 지표 수
    RAISE NOTICE 'Registered indicators: %', (
        SELECT COUNT(DISTINCT indicator_name)
        FROM indicator_columns
        WHERE is_active = true AND indicator_name != 'price'
    );

    -- 총 컬럼 수
    RAISE NOTICE 'Total columns: %', (
        SELECT COUNT(*)
        FROM indicator_columns
        WHERE is_active = true
    );

    RAISE NOTICE '';
    RAISE NOTICE 'Sample mappings:';

    -- 샘플 출력
    FOR rec IN
        SELECT
            indicator_name,
            STRING_AGG(column_name, ', ' ORDER BY output_order) as columns
        FROM indicator_columns
        WHERE is_active = true AND indicator_name IN ('macd', 'rsi', 'bollinger_bands')
        GROUP BY indicator_name
        ORDER BY indicator_name
    LOOP
        RAISE NOTICE '  % → [%]', rec.indicator_name, rec.columns;
    END LOOP;

    RAISE NOTICE '';
    RAISE NOTICE 'Validation with indicators table:';

    -- 불일치 체크
    FOR rec IN SELECT * FROM validate_indicator_output_columns()
    LOOP
        IF rec.status != '✓ Matched' THEN
            mismatch_count := mismatch_count + 1;
            RAISE NOTICE '  % %', rec.status, rec.indicator_name;
            IF rec.missing IS NOT NULL AND ARRAY_LENGTH(rec.missing, 1) > 0 THEN
                RAISE NOTICE '    Missing in standard: %', rec.missing;
            END IF;
            IF rec.extra IS NOT NULL AND ARRAY_LENGTH(rec.extra, 1) > 0 THEN
                RAISE NOTICE '    Extra in standard: %', rec.extra;
            END IF;
        END IF;
    END LOOP;

    IF mismatch_count = 0 THEN
        RAISE NOTICE '  ✓ All indicators matched!';
    ELSE
        RAISE NOTICE '  ⚠ % mismatches found', mismatch_count;
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE 'Usage:';
    RAISE NOTICE '  SELECT * FROM get_indicator_columns(''macd'');';
    RAISE NOTICE '  SELECT * FROM get_available_columns(ARRAY[''macd'', ''rsi'']);';
END $$;