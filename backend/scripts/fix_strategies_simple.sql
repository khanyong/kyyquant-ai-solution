-- ================================================
-- Supabase 전략 수정 간단 버전
-- 템플릿별로 하나씩 실행 가능
-- ================================================

-- 1. 먼저 현재 상태 확인
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    config->'indicators' as indicators
FROM strategies
WHERE config->'indicators' IS NULL
   OR jsonb_array_length(config->'indicators') = 0;

-- 2. Golden Cross 전략 수정
UPDATE strategies
SET
    config = jsonb_set(
        jsonb_set(
            config,
            '{indicators}',
            '[
                {"type": "ma", "params": {"period": 20}},
                {"type": "ma", "params": {"period": 60}}
            ]'::jsonb
        ),
        '{buyConditions}',
        '[{"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}]'::jsonb
    ),
    updated_at = NOW()
WHERE config->>'templateId' = 'golden-cross'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 3. RSI Reversal 전략 수정
UPDATE strategies
SET
    config = jsonb_set(
        jsonb_set(
            jsonb_set(
                config,
                '{indicators}',
                '[{"type": "rsi", "params": {"period": 14}}]'::jsonb
            ),
            '{buyConditions}',
            '[{"indicator": "rsi_14", "operator": "<", "value": 30}]'::jsonb
        ),
        '{sellConditions}',
        '[{"indicator": "rsi_14", "operator": ">", "value": 70}]'::jsonb
    ),
    updated_at = NOW()
WHERE config->>'templateId' = 'rsi-reversal'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 4. Bollinger Band 전략 수정
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{indicators}',
        '[
            {"type": "bb", "params": {"period": 20, "std": 2}},
            {"type": "rsi", "params": {"period": 14}}
        ]'::jsonb
    ),
    updated_at = NOW()
WHERE config->>'templateId' = 'bollinger-band'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 5. MACD Signal 전략 수정
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{indicators}',
        '[{"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}]'::jsonb
    ),
    updated_at = NOW()
WHERE config->>'templateId' = 'macd-signal'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 6. 모든 조건문의 대문자를 소문자로 변환
UPDATE strategies
SET config = REPLACE(
    REPLACE(
        REPLACE(
            REPLACE(
                REPLACE(
                    config::text,
                    '"MA_20"', '"ma_20"'
                ),
                '"MA_60"', '"ma_60"'
            ),
            '"RSI_14"', '"rsi_14"'
        ),
        '"CROSS_ABOVE"', '"cross_above"'
    ),
    '"CROSS_BELOW"', '"cross_below"'
)::jsonb,
updated_at = NOW()
WHERE config::text LIKE '%MA_%'
   OR config::text LIKE '%RSI_%'
   OR config::text LIKE '%CROSS_%';

-- 7. 결과 확인
SELECT
    name,
    config->>'templateId' as template,
    jsonb_pretty(config->'indicators') as indicators,
    jsonb_pretty(config->'buyConditions') as buy_conditions
FROM strategies
WHERE updated_at > NOW() - INTERVAL '5 minutes'
ORDER BY updated_at DESC;