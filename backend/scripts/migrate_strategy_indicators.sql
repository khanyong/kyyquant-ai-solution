-- =====================================================
-- strategies 테이블의 config 컬럼에서 대문자 지표를 소문자로 변환
-- =====================================================

-- 백업 테이블 생성 (안전을 위해)
CREATE TABLE IF NOT EXISTS strategies_backup AS
SELECT * FROM strategies;

-- 대문자 지표를 소문자로 변환하는 함수
CREATE OR REPLACE FUNCTION convert_indicators_to_lowercase(config_json JSONB)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    -- config JSON을 문자열로 변환 후 대치
    result = config_json::text::jsonb;

    -- indicators 배열의 지표들 변환
    -- MA, SMA 관련
    result = replace(result::text, '"MA_', '"ma_')::jsonb;
    result = replace(result::text, '"SMA_', '"sma_')::jsonb;
    result = replace(result::text, '"EMA_', '"ema_')::jsonb;

    -- RSI 관련
    result = replace(result::text, '"RSI_', '"rsi_')::jsonb;
    result = replace(result::text, '"RSI"', '"rsi"')::jsonb;

    -- MACD 관련
    result = replace(result::text, '"MACD_', '"macd_')::jsonb;
    result = replace(result::text, '"MACD"', '"macd"')::jsonb;
    result = replace(result::text, '"MACD_signal"', '"macd_signal"')::jsonb;
    result = replace(result::text, '"MACD_SIGNAL"', '"macd_signal"')::jsonb;
    result = replace(result::text, '"MACD_hist"', '"macd_hist"')::jsonb;

    -- 볼린저밴드 관련
    result = replace(result::text, '"BB_upper"', '"bb_upper"')::jsonb;
    result = replace(result::text, '"BB_UPPER"', '"bb_upper"')::jsonb;
    result = replace(result::text, '"BB_lower"', '"bb_lower"')::jsonb;
    result = replace(result::text, '"BB_LOWER"', '"bb_lower"')::jsonb;
    result = replace(result::text, '"BB_middle"', '"bb_middle"')::jsonb;
    result = replace(result::text, '"BB_MIDDLE"', '"bb_middle"')::jsonb;

    -- Stochastic 관련
    result = replace(result::text, '"Stoch_K"', '"stoch_k"')::jsonb;
    result = replace(result::text, '"STOCH_K"', '"stoch_k"')::jsonb;
    result = replace(result::text, '"Stoch_D"', '"stoch_d"')::jsonb;
    result = replace(result::text, '"STOCH_D"', '"stoch_d"')::jsonb;

    -- 기타 지표들
    result = replace(result::text, '"ATR_', '"atr_')::jsonb;
    result = replace(result::text, '"OBV"', '"obv"')::jsonb;
    result = replace(result::text, '"ADX_', '"adx_')::jsonb;
    result = replace(result::text, '"CCI_', '"cci_')::jsonb;
    result = replace(result::text, '"MFI_', '"mfi_')::jsonb;
    result = replace(result::text, '"VR_', '"vr_')::jsonb;
    result = replace(result::text, '"PRICE"', '"price"')::jsonb;

    -- Volume 관련
    result = replace(result::text, '"VOLUME"', '"volume"')::jsonb;
    result = replace(result::text, '"Volume"', '"volume"')::jsonb;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- strategies 테이블의 config 컬럼 업데이트
UPDATE strategies
SET config = convert_indicators_to_lowercase(config),
    updated_at = NOW()
WHERE config IS NOT NULL;

-- 업데이트된 레코드 수 확인
SELECT COUNT(*) as updated_count FROM strategies WHERE config IS NOT NULL;

-- 변환 결과 샘플 확인 (처음 5개)
SELECT
    id,
    name,
    jsonb_pretty(config) as config
FROM strategies
WHERE config IS NOT NULL
LIMIT 5;

-- 함수 삭제 (더 이상 필요없음)
DROP FUNCTION IF EXISTS convert_indicators_to_lowercase(JSONB);

-- 확인 메시지
SELECT 'Migration completed successfully!' as status;