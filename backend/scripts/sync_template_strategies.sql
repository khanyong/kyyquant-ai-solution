-- 템플릿 전략을 프론트엔드와 완전히 동기화
-- 기존 템플릿 전략 모두 삭제 후 재생성

-- 1. 기존 템플릿 전략 삭제
DELETE FROM strategies WHERE name LIKE '[템플릿]%';

-- 2. 프론트엔드와 동일한 템플릿 전략 생성

-- [템플릿] 골든크로스
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 골든크로스',
    'MA20이 MA60을 상향 돌파할 때 매수',
    '{
        "indicators": [
            {"name": "ma_20", "type": "SMA", "params": {"period": 20}},
            {"name": "ma_60", "type": "SMA", "params": {"period": 60}}
        ],
        "buyConditions": [
            {"left": "ma_20", "operator": "cross_above", "right": "ma_60"}
        ],
        "sellConditions": [
            {"left": "ma_20", "operator": "cross_below", "right": "ma_60"}
        ]
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] RSI 반전
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] RSI 반전',
    'RSI 과매도/과매수 구간 활용',
    '{
        "indicators": [
            {"name": "rsi_14", "type": "RSI", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "rsi_14", "operator": "<", "right": "30"}
        ],
        "sellConditions": [
            {"left": "rsi_14", "operator": ">", "right": "70"}
        ]
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] 볼린저밴드
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 볼린저밴드',
    '밴드 하단 매수, 상단 매도',
    '{
        "indicators": [
            {"name": "bb", "type": "BB", "params": {"period": 20, "std": 2}},
            {"name": "rsi_14", "type": "RSI", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "close", "operator": "<", "right": "bb_lower_20_2"},
            {"left": "rsi_14", "operator": "<", "right": "40"}
        ],
        "sellConditions": [
            {"left": "close", "operator": ">", "right": "bb_upper_20_2"}
        ]
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] MACD 시그널
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] MACD 시그널',
    'MACD 골든/데드 크로스',
    '{
        "indicators": [
            {"name": "macd", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ],
        "buyConditions": [
            {"left": "macd_12_26", "operator": "cross_above", "right": "macd_signal_12_26_9"},
            {"left": "macd_12_26", "operator": ">", "right": "0"}
        ],
        "sellConditions": [
            {"left": "macd_12_26", "operator": "cross_below", "right": "macd_signal_12_26_9"}
        ]
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] 스캘핑
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 스캘핑',
    '단기 빠른 진입/청산',
    '{
        "indicators": [
            {"name": "ma_5", "type": "SMA", "params": {"period": 5}},
            {"name": "rsi_9", "type": "RSI", "params": {"period": 9}}
        ],
        "buyConditions": [
            {"left": "close", "operator": ">", "right": "ma_5"},
            {"left": "rsi_9", "operator": "<", "right": "50"}
        ],
        "sellConditions": [
            {"left": "rsi_9", "operator": ">", "right": "70"}
        ],
        "targetProfit": {
            "simple": {
                "enabled": true,
                "value": 3
            }
        },
        "stopLoss": {
            "enabled": true,
            "value": 2
        },
        "risk": {
            "stopLoss": 2,
            "takeProfit": 3,
            "trailingStop": 1,
            "trailingStopPercent": 1,
            "positionSize": 10,
            "maxPositions": 3
        }
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] 스윙 트레이딩 (프론트엔드와 완전 일치)
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 스윙 트레이딩',
    '중기 추세 포착',
    '{
        "indicators": [
            {"name": "ma_20", "type": "SMA", "params": {"period": 20}},
            {"name": "ma_60", "type": "SMA", "params": {"period": 60}},
            {"name": "rsi_14", "type": "RSI", "params": {"period": 14}},
            {"name": "macd", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ],
        "buyConditions": [
            {"left": "ma_20", "operator": ">", "right": "ma_60"},
            {"left": "rsi_14", "operator": "<", "right": "60"},
            {"left": "macd_12_26", "operator": ">", "right": "0"}
        ],
        "sellConditions": [
            {"left": "ma_20", "operator": "<", "right": "ma_60"},
            {"left": "rsi_14", "operator": ">", "right": "70"}
        ],
        "targetProfit": {
            "simple": {
                "enabled": true,
                "value": 15
            }
        },
        "stopLoss": {
            "enabled": true,
            "value": 7
        },
        "risk": {
            "stopLoss": 7,
            "takeProfit": 15,
            "trailingStop": false,
            "trailingStopPercent": 0,
            "positionSize": 20,
            "maxPositions": 5
        }
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] 복합 전략 A
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 복합 전략 A',
    'RSI → MACD → 거래량 3단계 검증',
    '{
        "useStageBasedStrategy": true,
        "buyStageStrategy": {
            "stages": [
                {
                    "enabled": true,
                    "indicators": [{"type": "RSI", "params": {"period": 14}}],
                    "conditions": [{"left": "rsi_14", "operator": "<", "right": "35"}]
                },
                {
                    "enabled": true,
                    "indicators": [{"type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}],
                    "conditions": [{"left": "macd_12_26", "operator": "cross_above", "right": "macd_signal_12_26_9"}]
                },
                {
                    "enabled": true,
                    "indicators": [{"type": "SMA", "params": {"period": 20}}],
                    "conditions": [{"left": "volume", "operator": ">", "right": "volume_ma_20"}]
                }
            ]
        },
        "sellStageStrategy": {
            "stages": [
                {
                    "enabled": true,
                    "indicators": [{"type": "RSI", "params": {"period": 14}}],
                    "conditions": [{"left": "rsi_14", "operator": ">", "right": "70"}]
                },
                {
                    "enabled": true,
                    "indicators": [{"type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}],
                    "conditions": [{"left": "macd_12_26", "operator": "cross_below", "right": "macd_signal_12_26_9"}]
                },
                {
                    "enabled": false,
                    "indicators": [],
                    "conditions": []
                }
            ]
        }
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- [템플릿] 복합 전략 B
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 복합 전략 B',
    '골든크로스 → 볼린저 → RSI 확인',
    '{
        "useStageBasedStrategy": true,
        "buyStageStrategy": {
            "stages": [
                {
                    "enabled": true,
                    "indicators": [
                        {"type": "SMA", "params": {"period": 20}},
                        {"type": "SMA", "params": {"period": 60}}
                    ],
                    "conditions": [{"left": "ma_20", "operator": ">", "right": "ma_60"}]
                },
                {
                    "enabled": true,
                    "indicators": [{"type": "BB", "params": {"period": 20, "std": 2}}],
                    "conditions": [{"left": "close", "operator": "<", "right": "bb_middle_20"}]
                },
                {
                    "enabled": true,
                    "indicators": [{"type": "RSI", "params": {"period": 14}}],
                    "conditions": [{"left": "rsi_14", "operator": "<", "right": "50"}]
                }
            ]
        },
        "sellStageStrategy": {
            "stages": [
                {
                    "enabled": true,
                    "indicators": [
                        {"type": "SMA", "params": {"period": 20}},
                        {"type": "SMA", "params": {"period": 60}}
                    ],
                    "conditions": [{"left": "ma_20", "operator": "<", "right": "ma_60"}]
                },
                {
                    "enabled": true,
                    "indicators": [{"type": "BB", "params": {"period": 20, "std": 2}}],
                    "conditions": [{"left": "close", "operator": ">", "right": "bb_upper_20_2"}]
                },
                {
                    "enabled": false,
                    "indicators": [],
                    "conditions": []
                }
            ]
        }
    }'::jsonb,
    'f912da32-897f-4dbb-9242-3a438e9733a8'::uuid,
    true,
    NOW()
);

-- 확인
SELECT name, jsonb_pretty(config) FROM strategies WHERE name LIKE '[템플릿]%' ORDER BY name;