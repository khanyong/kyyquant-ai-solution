-- ============================================
-- 템플릿 전략 생성 SQL 스크립트
-- Supabase SQL Editor에서 직접 실행
-- ============================================

-- 1. 먼저 기존 템플릿 확인 (선택사항)
SELECT name FROM strategies
WHERE name LIKE '[템플릿]%'
ORDER BY created_at DESC;

-- 2. 기존 템플릿 삭제 (선택사항 - 필요시 주석 해제)
-- DELETE FROM strategies WHERE name LIKE '[템플릿]%';

-- 3. 템플릿 전략 삽입
-- 중복 체크 후 삽입

-- [템플릿] 골든크로스
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
SELECT
    gen_random_uuid(),
    '[템플릿] 골든크로스',
    'MA20이 MA60을 상향 돌파할 때 매수하는 정교한 추세 추종 전략',
    '{
        "indicators": [
            {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
            {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
            {"name": "sma_120", "type": "SMA", "params": {"period": 120}},
            {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}},
            {"name": "rsi", "type": "RSI", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "sma_20", "operator": ">", "right": "sma_60"},
            {"left": "sma_60", "operator": ">", "right": "sma_120"},
            {"left": "volume", "operator": ">", "right": "volume_ma"},
            {"left": "rsi", "operator": ">", "right": "30"},
            {"left": "rsi", "operator": "<", "right": "70"}
        ],
        "sellConditions": [
            {"left": "sma_20", "operator": "<", "right": "sma_60"},
            {"left": "rsi", "operator": ">", "right": "75"}
        ],
        "risk": {
            "stopLoss": 5,
            "takeProfit": 15,
            "positionSize": 100,
            "trailingStop": 3
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] 볼린저밴드
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 볼린저밴드',
    '밴드 하단 매수, 상단 매도하는 평균회귀 전략',
    '{
        "indicators": [
            {"name": "bb_upper", "type": "BB_UPPER", "params": {"period": 20, "std": 2}},
            {"name": "bb_lower", "type": "BB_LOWER", "params": {"period": 20, "std": 2}},
            {"name": "bb_middle", "type": "BB_MIDDLE", "params": {"period": 20}},
            {"name": "bb_width", "type": "BB_WIDTH", "params": {"period": 20, "std": 2}},
            {"name": "rsi", "type": "RSI", "params": {"period": 14}},
            {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}}
        ],
        "buyConditions": [
            {"left": "close", "operator": "<", "right": "bb_lower"},
            {"left": "rsi", "operator": "<", "right": "40"},
            {"left": "bb_width", "operator": ">", "right": "0.02"},
            {"left": "volume", "operator": ">", "right": "volume_ma"}
        ],
        "sellConditions": [
            {"left": "close", "operator": ">", "right": "bb_upper"},
            {"left": "rsi", "operator": ">", "right": "65"}
        ],
        "risk": {
            "stopLoss": 3,
            "takeProfit": 8,
            "positionSize": 100,
            "maxDrawdown": 10
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] RSI 반전
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] RSI 반전',
    'RSI 과매도/과매수 구간 활용하는 반전 매매 전략',
    '{
        "indicators": [
            {"name": "rsi", "type": "RSI", "params": {"period": 14}},
            {"name": "rsi_prev", "type": "RSI", "params": {"period": 14, "shift": 1}},
            {"name": "rsi_9", "type": "RSI", "params": {"period": 9}},
            {"name": "sma_50", "type": "SMA", "params": {"period": 50}},
            {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}}
        ],
        "buyConditions": [
            {"left": "rsi", "operator": "<", "right": "30"},
            {"left": "rsi_9", "operator": "<", "right": "35"},
            {"left": "close", "operator": ">", "right": "sma_50"},
            {"left": "volume", "operator": ">", "right": "volume_ma"}
        ],
        "sellConditions": [
            {"left": "rsi", "operator": ">", "right": "70"},
            {"left": "rsi_9", "operator": ">", "right": "65"}
        ],
        "risk": {
            "stopLoss": 4,
            "takeProfit": 12,
            "positionSize": 100,
            "trailingStop": 2
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] MACD 시그널
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] MACD 시그널',
    'MACD 골든/데드 크로스를 활용한 추세 추종 전략',
    '{
        "indicators": [
            {"name": "macd", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "macd_signal", "type": "MACD_SIGNAL", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "macd_hist", "type": "MACD_HIST", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "sma_200", "type": "SMA", "params": {"period": 200}},
            {"name": "rsi", "type": "RSI", "params": {"period": 14}},
            {"name": "adx", "type": "ADX", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "macd", "operator": ">", "right": "macd_signal"},
            {"left": "macd", "operator": ">", "right": "0"},
            {"left": "macd_hist", "operator": ">", "right": "0"},
            {"left": "close", "operator": ">", "right": "sma_200"},
            {"left": "adx", "operator": ">", "right": "25"},
            {"left": "rsi", "operator": ">", "right": "40"}
        ],
        "sellConditions": [
            {"left": "macd", "operator": "<", "right": "macd_signal"},
            {"left": "macd_hist", "operator": "<", "right": "0"},
            {"left": "rsi", "operator": ">", "right": "75"}
        ],
        "risk": {
            "stopLoss": 5,
            "takeProfit": 15,
            "positionSize": 100,
            "maxPositions": 3
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] 스캘핑
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 스캘핑',
    '단기 빠른 진입/청산을 위한 초단타 전략',
    '{
        "indicators": [
            {"name": "sma_5", "type": "SMA", "params": {"period": 5}},
            {"name": "ema_8", "type": "EMA", "params": {"period": 8}},
            {"name": "rsi_9", "type": "RSI", "params": {"period": 9}},
            {"name": "stoch_k", "type": "STOCH_K", "params": {"period": 5, "smoothK": 3, "smoothD": 3}},
            {"name": "stoch_d", "type": "STOCH_D", "params": {"period": 5, "smoothK": 3, "smoothD": 3}},
            {"name": "atr", "type": "ATR", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "close", "operator": ">", "right": "sma_5"},
            {"left": "sma_5", "operator": ">", "right": "ema_8"},
            {"left": "rsi_9", "operator": "<", "right": "50"},
            {"left": "rsi_9", "operator": ">", "right": "30"},
            {"left": "stoch_k", "operator": ">", "right": "stoch_d"},
            {"left": "atr", "operator": ">", "right": "0.5"}
        ],
        "sellConditions": [
            {"left": "rsi_9", "operator": ">", "right": "70"},
            {"left": "stoch_k", "operator": "<", "right": "stoch_d"},
            {"left": "close", "operator": "<", "right": "sma_5"}
        ],
        "risk": {
            "stopLoss": 2,
            "takeProfit": 3,
            "positionSize": 10,
            "maxPositions": 3,
            "trailingStop": 1,
            "trailingStopPercent": 1
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] 스윙 트레이딩
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 스윙 트레이딩',
    '중기 추세 포착을 위한 복합 지표 전략',
    '{
        "indicators": [
            {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
            {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
            {"name": "ema_10", "type": "EMA", "params": {"period": 10}},
            {"name": "rsi", "type": "RSI", "params": {"period": 14}},
            {"name": "macd", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "macd_signal", "type": "MACD_SIGNAL", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "adx", "type": "ADX", "params": {"period": 14}},
            {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}}
        ],
        "buyConditions": [
            {"left": "sma_20", "operator": ">", "right": "sma_60"},
            {"left": "ema_10", "operator": ">", "right": "sma_20"},
            {"left": "rsi", "operator": "<", "right": "60"},
            {"left": "rsi", "operator": ">", "right": "35"},
            {"left": "macd", "operator": ">", "right": "0"},
            {"left": "adx", "operator": ">", "right": "20"},
            {"left": "volume", "operator": ">", "right": "volume_ma"}
        ],
        "sellConditions": [
            {"left": "sma_20", "operator": "<", "right": "sma_60"},
            {"left": "rsi", "operator": ">", "right": "70"},
            {"left": "macd", "operator": "<", "right": "macd_signal"}
        ],
        "risk": {
            "stopLoss": 7,
            "takeProfit": 15,
            "positionSize": 20,
            "maxPositions": 5,
            "trailingStop": 5
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] 복합 전략 A
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 복합 전략 A',
    'RSI → MACD → 거래량 3단계 검증 전략',
    '{
        "indicators": [
            {"name": "rsi", "type": "RSI", "params": {"period": 14}},
            {"name": "macd", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "macd_signal", "type": "MACD_SIGNAL", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}},
            {"name": "sma_50", "type": "SMA", "params": {"period": 50}},
            {"name": "bb_upper", "type": "BB_UPPER", "params": {"period": 20, "std": 2}},
            {"name": "bb_lower", "type": "BB_LOWER", "params": {"period": 20, "std": 2}}
        ],
        "buyConditions": [
            {"left": "rsi", "operator": "<", "right": "35"},
            {"left": "macd", "operator": ">", "right": "macd_signal"},
            {"left": "volume", "operator": ">", "right": "volume_ma"},
            {"left": "close", "operator": ">", "right": "sma_50"},
            {"left": "close", "operator": "<", "right": "bb_lower"}
        ],
        "sellConditions": [
            {"left": "rsi", "operator": ">", "right": "70"},
            {"left": "macd", "operator": "<", "right": "macd_signal"},
            {"left": "close", "operator": ">", "right": "bb_upper"}
        ],
        "risk": {
            "stopLoss": 5,
            "takeProfit": 12,
            "positionSize": 100,
            "maxPositions": 2
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- [템플릿] 복합 전략 B
INSERT INTO strategies (id, name, description, config, user_id, is_public, created_at)
VALUES (
    gen_random_uuid(),
    '[템플릿] 복합 전략 B',
    '골든크로스 → 볼린저 → RSI 확인하는 다단계 전략',
    '{
        "indicators": [
            {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
            {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
            {"name": "bb_upper", "type": "BB_UPPER", "params": {"period": 20, "std": 2}},
            {"name": "bb_lower", "type": "BB_LOWER", "params": {"period": 20, "std": 2}},
            {"name": "bb_middle", "type": "BB_MIDDLE", "params": {"period": 20}},
            {"name": "rsi", "type": "RSI", "params": {"period": 14}},
            {"name": "stoch_k", "type": "STOCH_K", "params": {"period": 14, "smoothK": 3, "smoothD": 3}},
            {"name": "adx", "type": "ADX", "params": {"period": 14}}
        ],
        "buyConditions": [
            {"left": "sma_20", "operator": ">", "right": "sma_60"},
            {"left": "close", "operator": "<", "right": "bb_middle"},
            {"left": "close", "operator": ">", "right": "bb_lower"},
            {"left": "rsi", "operator": "<", "right": "50"},
            {"left": "rsi", "operator": ">", "right": "30"},
            {"left": "stoch_k", "operator": "<", "right": "40"},
            {"left": "adx", "operator": ">", "right": "20"}
        ],
        "sellConditions": [
            {"left": "sma_20", "operator": "<", "right": "sma_60"},
            {"left": "close", "operator": ">", "right": "bb_upper"},
            {"left": "rsi", "operator": ">", "right": "70"}
        ],
        "risk": {
            "stopLoss": 6,
            "takeProfit": 15,
            "positionSize": 100,
            "maxPositions": 3
        }
    }'::jsonb,
    NULL,
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM strategies WHERE name = '[템플릿] 골든크로스'
);

-- 3. 생성된 템플릿 확인
SELECT
    name,
    description,
    created_at,
    jsonb_array_length(config->'indicators') as indicator_count,
    jsonb_array_length(config->'buyConditions') as buy_conditions,
    jsonb_array_length(config->'sellConditions') as sell_conditions
FROM strategies
WHERE name LIKE '[템플릿]%'
ORDER BY created_at DESC;