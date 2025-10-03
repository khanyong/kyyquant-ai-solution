-- [분할] MACD+RSI 복합 전략 템플릿 추가
-- 3단계 분할 매수/매도 전략

INSERT INTO strategies (
  name,
  description,
  config,
  is_active,
  user_id,
  created_at,
  updated_at
)
VALUES (
  '[템플릿] MACD+RSI 복합 전략',
  'MACD와 RSI를 결합하여 강한 매수 신호 포착. 3단계 진입/청산으로 리스크 분산',
  '{
    "indicators": [
      {
        "name": "macd",
        "params": {
          "fast": 12,
          "slow": 26,
          "signal": 9
        }
      },
      {
        "name": "rsi",
        "params": {
          "period": 14
        }
      }
    ],
    "useStageBasedStrategy": true,
    "buyStageStrategy": {
      "enabled": true,
      "stages": [
        {
          "stage": 1,
          "enabled": true,
          "positionPercent": 40,
          "conditions": [
            {
              "left": "macd_line",
              "operator": ">",
              "right": "macd_signal"
            },
            {
              "left": "rsi",
              "operator": "<",
              "right": 50
            }
          ]
        },
        {
          "stage": 2,
          "enabled": true,
          "positionPercent": 40,
          "conditions": [
            {
              "left": "macd_line",
              "operator": ">",
              "right": "macd_signal"
            },
            {
              "left": "rsi",
              "operator": "<",
              "right": 40
            },
            {
              "left": "macd_hist",
              "operator": ">",
              "right": 0
            }
          ]
        },
        {
          "stage": 3,
          "enabled": true,
          "positionPercent": 50,
          "conditions": [
            {
              "left": "macd_line",
              "operator": ">",
              "right": "macd_signal"
            },
            {
              "left": "rsi",
              "operator": "<",
              "right": 30
            },
            {
              "left": "macd_hist",
              "operator": ">",
              "right": 0
            }
          ]
        }
      ]
    },
    "sellStageStrategy": {
      "enabled": true,
      "stages": [
        {
          "stage": 1,
          "enabled": true,
          "exitPercent": 40,
          "conditions": []
        },
        {
          "stage": 2,
          "enabled": true,
          "exitPercent": 40,
          "conditions": []
        },
        {
          "stage": 3,
          "enabled": true,
          "exitPercent": 20,
          "conditions": []
        }
      ]
    },
    "targetProfit": {
      "enabled": true,
      "mode": "staged",
      "staged": {
        "enabled": true,
        "stages": [
          {
            "stage": 1,
            "targetProfit": 4,
            "exitPercent": 40,
            "dynamicStopLoss": true
          },
          {
            "stage": 2,
            "targetProfit": 7,
            "exitPercent": 40,
            "dynamicStopLoss": true
          },
          {
            "stage": 3,
            "targetProfit": 12,
            "exitPercent": 20,
            "dynamicStopLoss": true
          }
        ]
      }
    },
    "stopLoss": {
      "enabled": true,
      "lossPercent": 6
    },
    "riskManagement": {
      "stopLoss": -6,
      "takeProfit": 0,
      "maxPositions": 5,
      "positionSize": 20,
      "trailingStop": false,
      "trailingStopPercent": 0
    }
  }'::jsonb,
  true,
  NULL,
  now(),
  now()
)
ON CONFLICT (name)
DO UPDATE SET
  description = EXCLUDED.description,
  config = EXCLUDED.config,
  updated_at = now();

-- 결과 확인
SELECT
  id,
  name,
  description,
  config->'useStageBasedStrategy' as use_staged,
  config->'buyStageStrategy'->'stages' as buy_stages,
  config->'targetProfit'->'staged'->'stages' as profit_stages,
  created_at
FROM strategies
WHERE name = '[템플릿] MACD+RSI 복합 전략';
