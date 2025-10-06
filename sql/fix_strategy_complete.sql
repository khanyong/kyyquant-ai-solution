-- =====================================================
-- 나의 전략 A1 - 완전 수정 버전
-- =====================================================
-- 이 스크립트는 전체 config를 한 번에 교체합니다.
-- =====================================================

UPDATE strategies
SET
  config = '{
    "stopLoss": {
      "value": 10.6,
      "enabled": true
    },
    "indicators": [
      {
        "name": "rsi",
        "type": "RSI",
        "params": {
          "period": 14
        }
      },
      {
        "name": "stochastic",
        "type": "STOCHASTIC",
        "params": {
          "d": 3,
          "k": 14
        }
      },
      {
        "name": "ichimoku",
        "type": "ICHIMOKU",
        "params": {
          "kijun": 26,
          "chikou": 26,
          "senkou": 52,
          "tenkan": 9
        }
      }
    ],
    "takeProfit": 10,
    "stopLossOld": -5,
    "maxPositions": 10,
    "positionSize": 10,
    "targetProfit": {
      "mode": "staged",
      "simple": {
        "value": 5,
        "enabled": true,
        "combineWith": "OR"
      },
      "staged": {
        "stages": [
          {
            "stage": 1,
            "exitRatio": 50,
            "combineWith": "OR",
            "targetProfit": 10,
            "dynamicStopLoss": false
          },
          {
            "stage": 2,
            "exitRatio": 30,
            "combineWith": "OR",
            "targetProfit": 20,
            "dynamicStopLoss": false
          },
          {
            "stage": 3,
            "exitRatio": 20,
            "combineWith": "OR",
            "targetProfit": 30,
            "dynamicStopLoss": false
          }
        ],
        "enabled": true,
        "combineWith": "OR"
      }
    },
    "trailingStop": false,
    "buyConditions": [
      {
        "left": "rsi",
        "right": 32,
        "operator": "<"
      },
      {
        "left": "stochastic_k",
        "right": 20,
        "operator": "<"
      },
      {
        "left": "close",
        "operator": ">",
        "right": "ichimoku_tenkan"
      }
    ],
    "strategy_type": "custom",
    "sellConditions": [],
    "buyStageStrategy": {
      "type": "buy",
      "stages": [
        {
          "stage": 1,
          "enabled": true,
          "conditions": [
            {
              "left": "rsi",
              "right": 32,
              "operator": "<",
              "combineWith": "AND"
            }
          ],
          "indicators": [
            {
              "id": "ind_1759647050448",
              "name": "RSI",
              "value": 32,
              "params": {
                "period": 14
              },
              "operator": "<",
              "combineWith": "AND",
              "indicatorId": "rsi"
            }
          ],
          "passAllRequired": true,
          "positionPercent": 5
        },
        {
          "stage": 2,
          "enabled": true,
          "conditions": [
            {
              "left": "stochastic_k",
              "right": 20,
              "operator": "<",
              "combineWith": "AND"
            }
          ],
          "indicators": [
            {
              "id": "ind_1759647071591",
              "name": "스토캐스틱",
              "value": 20,
              "params": {
                "d": 3,
                "k": 14
              },
              "operator": "<",
              "combineWith": "AND",
              "indicatorId": "stochastic"
            }
          ],
          "passAllRequired": true,
          "positionPercent": 5
        },
        {
          "stage": 3,
          "enabled": true,
          "conditions": [
            {
              "left": "close",
              "operator": ">",
              "right": "ichimoku_tenkan",
              "combineWith": "AND"
            }
          ],
          "indicators": [
            {
              "id": "ind_1759647097393",
              "name": "일목균형표",
              "params": {
                "kijun": 26,
                "chikou": 26,
                "senkou": 52,
                "tenkan": 9
              },
              "operator": "price_above_tenkan",
              "combineWith": "AND",
              "indicatorId": "ichimoku"
            }
          ],
          "passAllRequired": true,
          "positionPercent": 20
        }
      ],
      "usedIndicators": {}
    },
    "sellStageStrategy": {
      "type": "sell",
      "stages": [
        {
          "stage": 1,
          "enabled": true,
          "conditions": [],
          "indicators": [],
          "passAllRequired": true,
          "positionPercent": 30
        },
        {
          "stage": 2,
          "enabled": false,
          "conditions": [],
          "indicators": [],
          "passAllRequired": true,
          "positionPercent": 30
        },
        {
          "stage": 3,
          "enabled": false,
          "conditions": [],
          "indicators": [],
          "passAllRequired": true,
          "positionPercent": 40
        }
      ],
      "usedIndicators": {}
    },
    "investmentUniverse": {
      "financialFilters": {
        "filters": {
          "sector": null,
          "investor": null,
          "financial": null,
          "valuation": {
            "bps": [0, 100000],
            "eps": [-1000, 10000],
            "pbr": [0.5, 1.5],
            "pcr": [0, 30],
            "peg": [0, 3],
            "per": [15, 40],
            "psr": [0, 5],
            "volume": [100, 10000],
            "marketCap": [500, 20000],
            "currentPrice": [1000, 100000],
            "foreignRatio": [10, 50],
            "priceToHigh52w": [50, 100]
          }
        },
        "timestamp": "2025-09-09T14:53:50.300Z",
        "filterStats": {
          "final": 131,
          "total": 3349,
          "afterSector": 0,
          "afterInvestor": 0,
          "afterFinancial": 0,
          "afterMarketCap": 131
        },
        "appliedFilters": {
          "sector": false,
          "investor": false,
          "financial": false,
          "valuation": true
        }
      }
    },
    "trailingStopPercent": 3,
    "useStageBasedStrategy": true
  }'::jsonb,
  updated_at = NOW()
WHERE name = '나의 전략 A1';

-- 업데이트 확인
SELECT
  id,
  name,
  config->'buyConditions' as buy_conditions,
  config->'buyStageStrategy'->'stages'->2->'conditions' as stage3_conditions,
  updated_at
FROM strategies
WHERE name = '나의 전략 A1';
