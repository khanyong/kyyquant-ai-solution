-- ================================================
-- Supabase 전략 수정 SQL 스크립트
-- 빈 indicators 배열을 채우고 형식을 수정합니다
-- ================================================

-- 1. 백업 테이블 생성 (안전을 위해)
CREATE TABLE IF NOT EXISTS strategies_backup AS
SELECT * FROM strategies;

-- 2. 템플릿 기반 전략의 indicators 수정
-- golden-cross 템플릿
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[
        {"type": "ma", "params": {"period": 20}},
        {"type": "ma", "params": {"period": 60}}
    ]'::jsonb
)
WHERE config->>'templateId' = 'golden-cross'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- rsi-reversal 템플릿
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[{"type": "rsi", "params": {"period": 14}}]'::jsonb
)
WHERE config->>'templateId' = 'rsi-reversal'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- bollinger-band 템플릿
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[
        {"type": "bb", "params": {"period": 20, "std": 2}},
        {"type": "rsi", "params": {"period": 14}}
    ]'::jsonb
)
WHERE config->>'templateId' = 'bollinger-band'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- macd-signal 템플릿
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[{"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}]'::jsonb
)
WHERE config->>'templateId' = 'macd-signal'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- volume-spike 템플릿
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[
        {"type": "volume", "params": {}},
        {"type": "ma", "params": {"period": 20}}
    ]'::jsonb
)
WHERE config->>'templateId' = 'volume-spike'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- stochastic-oversold 템플릿
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    '[{"type": "stochastic", "params": {"k": 14, "d": 3}}]'::jsonb
)
WHERE config->>'templateId' = 'stochastic-oversold'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 3. 조건문에서 지표 추출하여 indicators 채우기
-- MA 지표를 사용하는 전략
WITH ma_strategies AS (
    SELECT id, config
    FROM strategies
    WHERE (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0)
      AND (
        config->'buyConditions' @> '[{"indicator": "ma_20"}]'::jsonb
        OR config->'buyConditions' @> '[{"indicator": "MA_20"}]'::jsonb
        OR config->'buyConditions' @> '[{"value": "ma_60"}]'::jsonb
        OR config->'buyConditions' @> '[{"value": "MA_60"}]'::jsonb
        OR config->'sellConditions' @> '[{"indicator": "ma_20"}]'::jsonb
        OR config->'sellConditions' @> '[{"indicator": "MA_20"}]'::jsonb
      )
)
UPDATE strategies s
SET config = jsonb_set(
    s.config,
    '{indicators}',
    '[
        {"type": "ma", "params": {"period": 20}},
        {"type": "ma", "params": {"period": 60}}
    ]'::jsonb
)
FROM ma_strategies m
WHERE s.id = m.id;

-- RSI 지표를 사용하는 전략
WITH rsi_strategies AS (
    SELECT id, config
    FROM strategies
    WHERE (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0)
      AND (
        config->'buyConditions' @> '[{"indicator": "rsi"}]'::jsonb
        OR config->'buyConditions' @> '[{"indicator": "RSI"}]'::jsonb
        OR config->'buyConditions' @> '[{"indicator": "rsi_14"}]'::jsonb
        OR config->'buyConditions' @> '[{"indicator": "RSI_14"}]'::jsonb
      )
)
UPDATE strategies s
SET config = jsonb_set(
    s.config,
    '{indicators}',
    '[{"type": "rsi", "params": {"period": 14}}]'::jsonb
)
FROM rsi_strategies r
WHERE s.id = r.id;

-- 4. buyConditions의 대문자를 소문자로 변환
UPDATE strategies
SET config = jsonb_set(
    config,
    '{buyConditions}',
    (
        SELECT jsonb_agg(
            CASE
                WHEN elem->>'indicator' IS NOT NULL THEN
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                elem,
                                '{indicator}',
                                to_jsonb(
                                    LOWER(
                                        REPLACE(REPLACE(elem->>'indicator', 'MA_', 'ma_'), 'RSI_', 'rsi_')
                                    )
                                )
                            ),
                            '{operator}',
                            to_jsonb(
                                CASE
                                    WHEN elem->>'operator' = 'CROSS_ABOVE' OR
                                         (elem->>'operator' = '>' AND LOWER(elem->>'indicator') LIKE '%ma%')
                                    THEN 'cross_above'
                                    WHEN elem->>'operator' = 'CROSS_BELOW' OR
                                         (elem->>'operator' = '<' AND LOWER(elem->>'indicator') LIKE '%ma%')
                                    THEN 'cross_below'
                                    ELSE LOWER(COALESCE(elem->>'operator', ''))
                                END
                            )
                        ),
                        '{value}',
                        to_jsonb(
                            CASE
                                WHEN elem->>'value' ~ '^[A-Z]+_' THEN
                                    LOWER(REPLACE(REPLACE(elem->>'value', 'MA_', 'ma_'), 'RSI_', 'rsi_'))
                                ELSE elem->>'value'
                            END
                        )
                    )
                ELSE elem
            END
        )
        FROM jsonb_array_elements(config->'buyConditions') AS elem
    )
)
WHERE config->'buyConditions' IS NOT NULL
  AND jsonb_array_length(config->'buyConditions') > 0;

-- 5. sellConditions의 대문자를 소문자로 변환
UPDATE strategies
SET config = jsonb_set(
    config,
    '{sellConditions}',
    (
        SELECT jsonb_agg(
            CASE
                WHEN elem->>'indicator' IS NOT NULL THEN
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                elem,
                                '{indicator}',
                                to_jsonb(
                                    LOWER(
                                        REPLACE(REPLACE(elem->>'indicator', 'MA_', 'ma_'), 'RSI_', 'rsi_')
                                    )
                                )
                            ),
                            '{operator}',
                            to_jsonb(
                                CASE
                                    WHEN elem->>'operator' = 'CROSS_BELOW' OR
                                         (elem->>'operator' = '<' AND LOWER(elem->>'indicator') LIKE '%ma%')
                                    THEN 'cross_below'
                                    WHEN elem->>'operator' = 'CROSS_ABOVE' OR
                                         (elem->>'operator' = '>' AND LOWER(elem->>'indicator') LIKE '%ma%')
                                    THEN 'cross_above'
                                    ELSE LOWER(COALESCE(elem->>'operator', ''))
                                END
                            )
                        ),
                        '{value}',
                        to_jsonb(
                            CASE
                                WHEN elem->>'value' ~ '^[A-Z]+_' THEN
                                    LOWER(REPLACE(REPLACE(elem->>'value', 'MA_', 'ma_'), 'RSI_', 'rsi_'))
                                ELSE elem->>'value'
                            END
                        )
                    )
                ELSE elem
            END
        )
        FROM jsonb_array_elements(config->'sellConditions') AS elem
    )
)
WHERE config->'sellConditions' IS NOT NULL
  AND jsonb_array_length(config->'sellConditions') > 0;

-- 6. indicators 배열의 type을 소문자로 변환하고 params 구조 확인
UPDATE strategies
SET config = jsonb_set(
    config,
    '{indicators}',
    (
        SELECT jsonb_agg(
            CASE
                -- params가 없고 period가 직접 있는 경우
                WHEN elem->>'params' IS NULL AND elem->>'period' IS NOT NULL THEN
                    jsonb_build_object(
                        'type', LOWER(COALESCE(elem->>'type', 'ma')),
                        'params', jsonb_build_object('period', (elem->>'period')::int)
                    )
                -- params가 이미 있는 경우 type만 소문자로
                WHEN elem->>'params' IS NOT NULL THEN
                    jsonb_set(
                        elem,
                        '{type}',
                        to_jsonb(LOWER(COALESCE(elem->>'type', '')))
                    )
                ELSE elem
            END
        )
        FROM jsonb_array_elements(config->'indicators') AS elem
    )
)
WHERE config->'indicators' IS NOT NULL
  AND jsonb_array_length(config->'indicators') > 0;

-- 7. updated_at 필드 업데이트
UPDATE strategies
SET updated_at = NOW()
WHERE config IS NOT NULL;

-- 8. 수정 결과 확인
SELECT
    name,
    config->>'templateId' as template,
    jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) as indicator_count,
    config->'indicators' as indicators,
    jsonb_array_length(COALESCE(config->'buyConditions', '[]'::jsonb)) as buy_conditions,
    jsonb_array_length(COALESCE(config->'sellConditions', '[]'::jsonb)) as sell_conditions
FROM strategies
ORDER BY updated_at DESC
LIMIT 10;

-- 9. 문제가 있는 전략 확인
SELECT
    id,
    name,
    'Empty indicators' as issue
FROM strategies
WHERE config->'indicators' IS NULL
   OR jsonb_array_length(config->'indicators') = 0

UNION ALL

SELECT
    id,
    name,
    'Uppercase in conditions' as issue
FROM strategies
WHERE config::text ~ '[A-Z]+_[0-9]+'
   OR config::text ~ 'CROSS_ABOVE'
   OR config::text ~ 'CROSS_BELOW';

-- 10. 실행 통계
SELECT
    COUNT(*) as total_strategies,
    COUNT(CASE WHEN jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) > 0 THEN 1 END) as with_indicators,
    COUNT(CASE WHEN jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) = 0 THEN 1 END) as empty_indicators
FROM strategies;