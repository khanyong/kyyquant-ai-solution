-- ============================================================
-- 전략 초기화 및 표준 템플릿 재생성
-- ============================================================
-- 목적: 기존 전략 삭제 + 표준 형식(left/right)으로 템플릿 재생성
-- 주의: 기존 사용자 전략이 모두 삭제됩니다!
-- ============================================================

-- ------------------------------------------------------------
-- 1. 백업 (혹시 모를 롤백용)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS strategies_backup_before_reset AS
SELECT * FROM strategies;

SELECT COUNT(*) as backed_up_count FROM strategies_backup_before_reset;


-- ------------------------------------------------------------
-- 2. 기존 전략 모두 삭제
-- ------------------------------------------------------------

-- 관련 테이블도 있다면 CASCADE (backtest_runs 등)
DELETE FROM strategies;

-- 확인
SELECT COUNT(*) as remaining_strategies FROM strategies;
-- 결과: 0


-- ------------------------------------------------------------
-- 3. 표준 템플릿 전략 생성 (left/right 형식)
-- ------------------------------------------------------------

-- 3.1 골든크로스 (SMA 20/60 크로스)
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] 골든크로스',
    'SMA 20이 SMA 60을 상향 돌파 시 매수',
    '{
        "indicators": [
            {
                "name": "sma",
                "type": "SMA",
                "params": {"period": 20}
            },
            {
                "name": "sma",
                "type": "SMA",
                "params": {"period": 60}
            }
        ],
        "buyConditions": [
            {
                "left": "sma_20",
                "operator": "crossover",
                "right": "sma_60"
            }
        ],
        "sellConditions": [
            {
                "left": "sma_20",
                "operator": "crossunder",
                "right": "sma_60"
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.2 MACD 시그널
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] MACD 시그널',
    'MACD가 시그널선을 상향 돌파하고 0 이상일 때 매수',
    '{
        "indicators": [
            {
                "name": "macd",
                "type": "MACD",
                "params": {
                    "fast": 12,
                    "slow": 26,
                    "signal": 9
                }
            }
        ],
        "buyConditions": [
            {
                "left": "macd",
                "operator": "crossover",
                "right": "macd_signal"
            },
            {
                "left": "macd",
                "operator": ">",
                "right": 0
            }
        ],
        "sellConditions": [
            {
                "left": "macd",
                "operator": "crossunder",
                "right": "macd_signal"
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.3 RSI 반전
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] RSI 반전',
    'RSI 과매도(30 이하) 매수, 과매수(70 이상) 매도',
    '{
        "indicators": [
            {
                "name": "rsi",
                "type": "RSI",
                "params": {"period": 14}
            }
        ],
        "buyConditions": [
            {
                "left": "rsi",
                "operator": "<",
                "right": 30
            }
        ],
        "sellConditions": [
            {
                "left": "rsi",
                "operator": ">",
                "right": 70
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.4 볼린저밴드
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] 볼린저밴드',
    '가격이 하단 밴드 아래 + RSI 40 이하 매수, 상단 밴드 위 매도',
    '{
        "indicators": [
            {
                "name": "bollinger_bands",
                "type": "BollingerBands",
                "params": {
                    "period": 20,
                    "stddev": 2
                }
            },
            {
                "name": "rsi",
                "type": "RSI",
                "params": {"period": 14}
            }
        ],
        "buyConditions": [
            {
                "left": "close",
                "operator": "<",
                "right": "bb_lower"
            },
            {
                "left": "rsi",
                "operator": "<",
                "right": 40
            }
        ],
        "sellConditions": [
            {
                "left": "close",
                "operator": ">",
                "right": "bb_upper"
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.5 스윙 트레이딩
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] 스윙 트레이딩',
    'SMA 20 > SMA 60 + RSI < 60 + MACD > 0 매수',
    '{
        "indicators": [
            {
                "name": "sma",
                "type": "SMA",
                "params": {"period": 20}
            },
            {
                "name": "sma",
                "type": "SMA",
                "params": {"period": 60}
            },
            {
                "name": "rsi",
                "type": "RSI",
                "params": {"period": 14}
            },
            {
                "name": "macd",
                "type": "MACD",
                "params": {
                    "fast": 12,
                    "slow": 26,
                    "signal": 9
                }
            }
        ],
        "buyConditions": [
            {
                "left": "sma_20",
                "operator": ">",
                "right": "sma_60"
            },
            {
                "left": "rsi",
                "operator": "<",
                "right": 60
            },
            {
                "left": "macd",
                "operator": ">",
                "right": 0
            }
        ],
        "sellConditions": [
            {
                "left": "sma_20",
                "operator": "<",
                "right": "sma_60"
            },
            {
                "left": "rsi",
                "operator": ">",
                "right": 70
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.6 스캘핑
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] 스캘핑',
    '가격이 SMA 5 위 + RSI 50 이하 매수, RSI 70 이상 매도',
    '{
        "indicators": [
            {
                "name": "sma",
                "type": "SMA",
                "params": {"period": 5}
            },
            {
                "name": "rsi",
                "type": "RSI",
                "params": {"period": 14}
            }
        ],
        "buyConditions": [
            {
                "left": "close",
                "operator": ">",
                "right": "sma_5"
            },
            {
                "left": "rsi",
                "operator": "<",
                "right": 50
            }
        ],
        "sellConditions": [
            {
                "left": "rsi",
                "operator": ">",
                "right": 70
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.7 Stochastic 반전
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] Stochastic 반전',
    'Stochastic %K < 20 매수, %K > 80 매도',
    '{
        "indicators": [
            {
                "name": "stochastic",
                "type": "Stochastic",
                "params": {
                    "k_period": 14,
                    "d_period": 3
                }
            }
        ],
        "buyConditions": [
            {
                "left": "stoch_k",
                "operator": "<",
                "right": 20
            }
        ],
        "sellConditions": [
            {
                "left": "stoch_k",
                "operator": ">",
                "right": 80
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- 3.8 ATR 브레이크아웃
INSERT INTO strategies (id, name, description, config, is_active, created_at) VALUES (
    gen_random_uuid(),
    '[템플릿] ATR 브레이크아웃',
    '가격이 SMA + 2*ATR 돌파 시 매수',
    '{
        "indicators": [
            {
                "name": "sma",
                "type": "SMA",
                "params": {"period": 20}
            },
            {
                "name": "atr",
                "type": "ATR",
                "params": {"period": 14}
            }
        ],
        "buyConditions": [
            {
                "left": "close",
                "operator": ">",
                "right": "sma_20"
            }
        ],
        "sellConditions": [
            {
                "left": "close",
                "operator": "<",
                "right": "sma_20"
            }
        ]
    }'::jsonb,
    true,
    NOW()
);


-- ------------------------------------------------------------
-- 4. 결과 확인
-- ------------------------------------------------------------

SELECT
    id,
    name,
    description,
    config->'indicators' as indicators,
    jsonb_array_length(config->'indicators') as indicator_count,
    config->'buyConditions' as buy_conditions,
    config->'sellConditions' as sell_conditions,
    created_at
FROM strategies
ORDER BY created_at;


-- ------------------------------------------------------------
-- 5. 검증: 모든 조건이 left/right 형식인지 확인
-- ------------------------------------------------------------

DO $$
DECLARE
    strategy_rec RECORD;
    condition_rec RECORD;
    invalid_count INT := 0;
BEGIN
    FOR strategy_rec IN SELECT id, name, config FROM strategies
    LOOP
        -- buyConditions 검증
        FOR condition_rec IN
            SELECT * FROM jsonb_array_elements(strategy_rec.config->'buyConditions')
        LOOP
            IF NOT (condition_rec.value ? 'left' AND condition_rec.value ? 'right') THEN
                RAISE NOTICE '❌ Invalid buy condition in %: %',
                    strategy_rec.name, condition_rec.value;
                invalid_count := invalid_count + 1;
            END IF;
        END LOOP;

        -- sellConditions 검증
        FOR condition_rec IN
            SELECT * FROM jsonb_array_elements(strategy_rec.config->'sellConditions')
        LOOP
            IF NOT (condition_rec.value ? 'left' AND condition_rec.value ? 'right') THEN
                RAISE NOTICE '❌ Invalid sell condition in %: %',
                    strategy_rec.name, condition_rec.value;
                invalid_count := invalid_count + 1;
            END IF;
        END LOOP;
    END LOOP;

    IF invalid_count = 0 THEN
        RAISE NOTICE '✅ All conditions use standard format (left/right)';
    ELSE
        RAISE NOTICE '⚠️  Found % invalid conditions', invalid_count;
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '  - Total strategies: %', (SELECT COUNT(*) FROM strategies);
    RAISE NOTICE '  - Template strategies: %', (SELECT COUNT(*) FROM strategies WHERE name LIKE '[템플릿]%');
END $$;


-- ------------------------------------------------------------
-- 6. 정리 (성공 확인 후 1주일 뒤)
-- ------------------------------------------------------------

-- 백업 테이블 제거
-- DROP TABLE IF EXISTS strategies_backup_before_reset;