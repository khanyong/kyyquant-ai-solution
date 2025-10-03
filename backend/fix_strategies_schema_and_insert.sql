-- ============================================================
-- Strategies 테이블 스키마 수정 및 템플릿 전략 삽입
-- ============================================================

-- Phase 1: user_id를 NULL 허용으로 변경 (템플릿용)
ALTER TABLE strategies
ALTER COLUMN user_id DROP NOT NULL;

-- Phase 2: 기존 strategies를 strategies_backup으로 백업
DELETE FROM strategies_backup;
INSERT INTO strategies_backup SELECT * FROM strategies;

SELECT COUNT(*) as backup_count FROM strategies_backup;

-- Phase 3: 기존 전략 삭제
DELETE FROM strategies;

SELECT COUNT(*) as remaining_count FROM strategies;

-- Phase 4: 새로운 템플릿 전략 8개 생성
INSERT INTO strategies (name, description, config, is_active, user_id, created_at) VALUES
-- 1. 골든크로스
(
    '[템플릿] 골든크로스',
    'MACD > MACD 매수, 단기평균 추세',
    '{
        "indicators": [
            {"name": "sma", "params": {"period": 20}},
            {"name": "sma", "params": {"period": 60}}
        ],
        "buyConditions": [
            {"left": "sma_20", "operator": "crossover", "right": "sma_60"}
        ],
        "sellConditions": [
            {"left": "sma_20", "operator": "crossunder", "right": "sma_60"}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 2. RSI 반전
(
    '[템플릿] RSI 반전',
    'RSI 30 이하 매수, 과매도 반전 포착',
    '{
        "indicators": [
            {"name": "rsi", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "rsi", "operator": "<", "right": 30}
        ],
        "sellConditions": [
            {"left": "rsi", "operator": ">", "right": 70}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 3. 볼린저밴드
(
    '[템플릿] 볼린저밴드',
    '밴드 하단 매수, 변동성 활용 매매',
    '{
        "indicators": [
            {"name": "bb", "params": {"period": 20, "std": 2}},
            {"name": "rsi", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "close", "operator": "<", "right": "bb_lower"},
            {"left": "rsi", "operator": "<", "right": 40}
        ],
        "sellConditions": [
            {"left": "close", "operator": ">", "right": "bb_upper"}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 4. MACD 시그널
(
    '[템플릿] MACD 시그널',
    'MACD 크로스, 모멘텀 추종 매매',
    '{
        "indicators": [
            {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ],
        "buyConditions": [
            {"left": "macd_line", "operator": "crossover", "right": "macd_signal"},
            {"left": "macd_line", "operator": ">", "right": 0}
        ],
        "sellConditions": [
            {"left": "macd_line", "operator": "crossunder", "right": "macd_signal"}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 5. 복합 전략 A
(
    '[템플릿] 복합 전략 A',
    'RSI+MACD+거래량, 강한 확률 시스템',
    '{
        "indicators": [
            {"name": "rsi", "params": {"period": 14}},
            {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "volume_ma", "params": {"period": 20}}
        ],
        "buyConditions": [
            {"left": "rsi", "operator": "<", "right": 50},
            {"left": "macd_line", "operator": ">", "right": "macd_signal"},
            {"left": "volume", "operator": ">", "right": "volume_ma_20"}
        ],
        "sellConditions": [
            {"left": "rsi", "operator": ">", "right": 70},
            {"left": "macd_line", "operator": "<", "right": "macd_signal"}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 6. 복합 전략 B
(
    '[템플릿] 복합 전략 B',
    'MA+BB+RSI, 추세와 모멘텀 결합',
    '{
        "indicators": [
            {"name": "sma", "params": {"period": 20}},
            {"name": "bb", "params": {"period": 20, "std": 2}},
            {"name": "rsi", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "close", "operator": ">", "right": "sma_20"},
            {"left": "close", "operator": "<", "right": "bb_lower"},
            {"left": "rsi", "operator": "<", "right": 40}
        ],
        "sellConditions": [
            {"left": "close", "operator": ">", "right": "bb_upper"},
            {"left": "rsi", "operator": ">", "right": 70}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 7. 스캘핑
(
    '[템플릿] 스캘핑',
    '단기 진입/청산, 빠른 수익 확보',
    '{
        "indicators": [
            {"name": "sma", "params": {"period": 5}},
            {"name": "rsi", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "close", "operator": ">", "right": "sma_5"},
            {"left": "rsi", "operator": "<", "right": 50}
        ],
        "sellConditions": [
            {"left": "rsi", "operator": ">", "right": 70}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
),

-- 8. 스윙 트레이딩
(
    '[템플릿] 스윙 트레이딩',
    '중기 추세 포착, 안정적 수익 추구',
    '{
        "indicators": [
            {"name": "sma", "params": {"period": 20}},
            {"name": "sma", "params": {"period": 60}},
            {"name": "rsi", "params": {"period": 14}},
            {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ],
        "buyConditions": [
            {"left": "sma_20", "operator": ">", "right": "sma_60"},
            {"left": "rsi", "operator": "<", "right": 60},
            {"left": "macd_line", "operator": ">", "right": 0}
        ],
        "sellConditions": [
            {"left": "sma_20", "operator": "<", "right": "sma_60"},
            {"left": "rsi", "operator": ">", "right": 70}
        ]
    }'::jsonb,
    true,
    NULL,
    NOW()
);

-- Phase 5: 검증
SELECT COUNT(*) as created_count FROM strategies;

SELECT
    name,
    description,
    jsonb_array_length(config->'indicators') as indicator_count,
    jsonb_array_length(config->'buyConditions') as buy_condition_count,
    jsonb_array_length(config->'sellConditions') as sell_condition_count
FROM strategies
ORDER BY created_at;

-- 조건 형식 검증 (모두 left/right 형식이어야 함)
DO $$
DECLARE
    strategy_rec RECORD;
    invalid_count INT := 0;
BEGIN
    FOR strategy_rec IN SELECT id, name, config FROM strategies
    LOOP
        -- buyConditions 검증
        IF EXISTS (
            SELECT 1
            FROM jsonb_array_elements(strategy_rec.config->'buyConditions') AS cond
            WHERE NOT (cond ? 'left' AND cond ? 'right')
        ) THEN
            RAISE NOTICE '❌ Invalid buy condition in %', strategy_rec.name;
            invalid_count := invalid_count + 1;
        END IF;

        -- sellConditions 검증
        IF EXISTS (
            SELECT 1
            FROM jsonb_array_elements(strategy_rec.config->'sellConditions') AS cond
            WHERE NOT (cond ? 'left' AND cond ? 'right')
        ) THEN
            RAISE NOTICE '❌ Invalid sell condition in %', strategy_rec.name;
            invalid_count := invalid_count + 1;
        END IF;
    END LOOP;

    IF invalid_count = 0 THEN
        RAISE NOTICE '✅ All conditions use standard format (left/right)';
    ELSE
        RAISE NOTICE '⚠️  Found % invalid conditions', invalid_count;
    END IF;
END $$;
