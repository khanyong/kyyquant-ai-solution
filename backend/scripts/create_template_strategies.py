"""
템플릿 전략 생성 스크립트 - 프론트엔드와 동일한 이름 사용, 정교한 설정
모든 지표는 소문자 사용
"""

import os
import json
from datetime import datetime
from supabase import create_client
import uuid

# Supabase 설정
SUPABASE_URL = 'https://kpnioqijldwmidguzwox.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY2NzY2NjgsImV4cCI6MjA0MjI1MjY2OH0.u8mE0Zii_TdN7Rwgehs83kYKVLWAuEz8sFYR2daJ4wA'

# 템플릿 전략 정의 - 프론트엔드 strategyTemplates.ts와 동일한 이름, 더 정교한 설정
TEMPLATE_STRATEGIES = [
    {
        "name": "[템플릿] 골든크로스",
        "description": "MA20이 MA60을 상향 돌파할 때 매수하는 정교한 추세 추종 전략",
        "config": {
            "indicators": [
                {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
                {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
                {"name": "sma_120", "type": "SMA", "params": {"period": 120}},
                {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}},
                {"name": "rsi", "type": "rsi", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "left": "sma_20",
                    "operator": ">",
                    "right": "sma_60"
                },
                {
                    "left": "sma_60",
                    "operator": ">",
                    "right": "sma_120"
                },
                {
                    "left": "volume",
                    "operator": ">",
                    "right": "volume_ma"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "30"
                },
                {
                    "left": "rsi",
                    "operator": "<",
                    "right": "70"
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
                    "right": "75"
                }
            ],
            "risk": {
                "stopLoss": 5,
                "takeProfit": 15,
                "positionSize": 100,
                "trailingStop": 3
            }
        }
    },
    {
        "name": "[템플릿] 볼린저밴드",
        "description": "밴드 하단 매수, 상단 매도하는 평균회귀 전략",
        "config": {
            "indicators": [
                {"name": "bb_upper", "type": "bb_upper", "params": {"period": 20, "std": 2}},
                {"name": "bb_lower", "type": "bb_lower", "params": {"period": 20, "std": 2}},
                {"name": "bb_middle", "type": "bb_middle", "params": {"period": 20}},
                {"name": "bb_width", "type": "bb_width", "params": {"period": 20, "std": 2}},
                {"name": "rsi", "type": "rsi", "params": {"period": 14}},
                {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}}
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
                    "right": "40"
                },
                {
                    "left": "bb_width",
                    "operator": ">",
                    "right": "0.02"
                },
                {
                    "left": "volume",
                    "operator": ">",
                    "right": "volume_ma"
                }
            ],
            "sellConditions": [
                {
                    "left": "close",
                    "operator": ">",
                    "right": "bb_upper"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "65"
                }
            ],
            "risk": {
                "stopLoss": 3,
                "takeProfit": 8,
                "positionSize": 100,
                "maxDrawdown": 10
            }
        }
    },
    {
        "name": "[템플릿] RSI 반전",
        "description": "RSI 과매도/과매수 구간 활용하는 반전 매매 전략",
        "config": {
            "indicators": [
                {"name": "rsi", "type": "rsi", "params": {"period": 14}},
                {"name": "rsi_prev", "type": "rsi", "params": {"period": 14, "shift": 1}},
                {"name": "rsi_9", "type": "rsi", "params": {"period": 9}},
                {"name": "sma_50", "type": "SMA", "params": {"period": 50}},
                {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}}
            ],
            "buyConditions": [
                {
                    "left": "rsi",
                    "operator": "<",
                    "right": "30"
                },
                {
                    "left": "rsi_9",
                    "operator": "<",
                    "right": "35"
                },
                {
                    "left": "close",
                    "operator": ">",
                    "right": "sma_50"
                },
                {
                    "left": "volume",
                    "operator": ">",
                    "right": "volume_ma"
                }
            ],
            "sellConditions": [
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "70"
                },
                {
                    "left": "rsi_9",
                    "operator": ">",
                    "right": "65"
                }
            ],
            "risk": {
                "stopLoss": 4,
                "takeProfit": 12,
                "positionSize": 100,
                "trailingStop": 2
            }
        }
    },
    {
        "name": "[템플릿] MACD 시그널",
        "description": "MACD 골든/데드 크로스를 활용한 추세 추종 전략",
        "config": {
            "indicators": [
                {"name": "macd", "type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "macd_signal", "type": "macd_signal", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "macd_hist", "type": "macd_hist", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "sma_200", "type": "SMA", "params": {"period": 200}},
                {"name": "rsi", "type": "rsi", "params": {"period": 14}},
                {"name": "adx", "type": "adx", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "left": "macd",
                    "operator": ">",
                    "right": "macd_signal"
                },
                {
                    "left": "macd",
                    "operator": ">",
                    "right": "0"
                },
                {
                    "left": "macd_hist",
                    "operator": ">",
                    "right": "0"
                },
                {
                    "left": "close",
                    "operator": ">",
                    "right": "sma_200"
                },
                {
                    "left": "adx",
                    "operator": ">",
                    "right": "25"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "40"
                }
            ],
            "sellConditions": [
                {
                    "left": "macd",
                    "operator": "<",
                    "right": "macd_signal"
                },
                {
                    "left": "macd_hist",
                    "operator": "<",
                    "right": "0"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "75"
                }
            ],
            "risk": {
                "stopLoss": 5,
                "takeProfit": 15,
                "positionSize": 100,
                "maxPositions": 3
            }
        }
    },
    {
        "name": "[템플릿] 스캘핑",
        "description": "단기 빠른 진입/청산을 위한 초단타 전략",
        "config": {
            "indicators": [
                {"name": "sma_5", "type": "SMA", "params": {"period": 5}},
                {"name": "ema_8", "type": "EMA", "params": {"period": 8}},
                {"name": "rsi_9", "type": "rsi", "params": {"period": 9}},
                {"name": "stoch_k", "type": "stoch_k", "params": {"period": 5, "smoothK": 3, "smoothD": 3}},
                {"name": "stoch_d", "type": "stoch_d", "params": {"period": 5, "smoothK": 3, "smoothD": 3}},
                {"name": "atr", "type": "atr", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "left": "close",
                    "operator": ">",
                    "right": "sma_5"
                },
                {
                    "left": "sma_5",
                    "operator": ">",
                    "right": "ema_8"
                },
                {
                    "left": "rsi_9",
                    "operator": "<",
                    "right": "50"
                },
                {
                    "left": "rsi_9",
                    "operator": ">",
                    "right": "30"
                },
                {
                    "left": "stoch_k",
                    "operator": ">",
                    "right": "stoch_d"
                },
                {
                    "left": "atr",
                    "operator": ">",
                    "right": "0.5"
                }
            ],
            "sellConditions": [
                {
                    "left": "rsi_9",
                    "operator": ">",
                    "right": "70"
                },
                {
                    "left": "stoch_k",
                    "operator": "<",
                    "right": "stoch_d"
                },
                {
                    "left": "close",
                    "operator": "<",
                    "right": "sma_5"
                }
            ],
            "risk": {
                "stopLoss": 2,
                "takeProfit": 3,
                "positionSize": 10,
                "maxPositions": 3,
                "trailingStop": 1,
                "trailingStopPercent": 1
            }
        }
    },
    {
        "name": "[템플릿] 스윙 트레이딩",
        "description": "중기 추세 포착을 위한 복합 지표 전략",
        "config": {
            "indicators": [
                {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
                {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
                {"name": "ema_10", "type": "EMA", "params": {"period": 10}},
                {"name": "rsi", "type": "rsi", "params": {"period": 14}},
                {"name": "macd", "type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "macd_signal", "type": "macd_signal", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "adx", "type": "adx", "params": {"period": 14}},
                {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}}
            ],
            "buyConditions": [
                {
                    "left": "sma_20",
                    "operator": ">",
                    "right": "sma_60"
                },
                {
                    "left": "ema_10",
                    "operator": ">",
                    "right": "sma_20"
                },
                {
                    "left": "rsi",
                    "operator": "<",
                    "right": "60"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "35"
                },
                {
                    "left": "macd",
                    "operator": ">",
                    "right": "0"
                },
                {
                    "left": "adx",
                    "operator": ">",
                    "right": "20"
                },
                {
                    "left": "volume",
                    "operator": ">",
                    "right": "volume_ma"
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
                    "right": "70"
                },
                {
                    "left": "macd",
                    "operator": "<",
                    "right": "macd_signal"
                }
            ],
            "risk": {
                "stopLoss": 7,
                "takeProfit": 15,
                "positionSize": 20,
                "maxPositions": 5,
                "trailingStop": 5
            }
        }
    },
    {
        "name": "[템플릿] 복합 전략 A",
        "description": "RSI → MACD → 거래량 3단계 검증 전략",
        "config": {
            "indicators": [
                {"name": "rsi", "type": "rsi", "params": {"period": 14}},
                {"name": "macd", "type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "macd_signal", "type": "macd_signal", "params": {"fast": 12, "slow": 26, "signal": 9}},
                {"name": "volume_ma", "type": "SMA", "params": {"period": 20, "source": "volume"}},
                {"name": "sma_50", "type": "SMA", "params": {"period": 50}},
                {"name": "bb_upper", "type": "bb_upper", "params": {"period": 20, "std": 2}},
                {"name": "bb_lower", "type": "bb_lower", "params": {"period": 20, "std": 2}}
            ],
            "buyConditions": [
                {
                    "left": "rsi",
                    "operator": "<",
                    "right": "35"
                },
                {
                    "left": "macd",
                    "operator": ">",
                    "right": "macd_signal"
                },
                {
                    "left": "volume",
                    "operator": ">",
                    "right": "volume_ma"
                },
                {
                    "left": "close",
                    "operator": ">",
                    "right": "sma_50"
                },
                {
                    "left": "close",
                    "operator": "<",
                    "right": "bb_lower"
                }
            ],
            "sellConditions": [
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "70"
                },
                {
                    "left": "macd",
                    "operator": "<",
                    "right": "macd_signal"
                },
                {
                    "left": "close",
                    "operator": ">",
                    "right": "bb_upper"
                }
            ],
            "risk": {
                "stopLoss": 5,
                "takeProfit": 12,
                "positionSize": 100,
                "maxPositions": 2
            }
        }
    },
    {
        "name": "[템플릿] 복합 전략 B",
        "description": "골든크로스 → 볼린저 → RSI 확인하는 다단계 전략",
        "config": {
            "indicators": [
                {"name": "sma_20", "type": "SMA", "params": {"period": 20}},
                {"name": "sma_60", "type": "SMA", "params": {"period": 60}},
                {"name": "bb_upper", "type": "bb_upper", "params": {"period": 20, "std": 2}},
                {"name": "bb_lower", "type": "bb_lower", "params": {"period": 20, "std": 2}},
                {"name": "bb_middle", "type": "bb_middle", "params": {"period": 20}},
                {"name": "rsi", "type": "rsi", "params": {"period": 14}},
                {"name": "stoch_k", "type": "stoch_k", "params": {"period": 14, "smoothK": 3, "smoothD": 3}},
                {"name": "adx", "type": "adx", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "left": "sma_20",
                    "operator": ">",
                    "right": "sma_60"
                },
                {
                    "left": "close",
                    "operator": "<",
                    "right": "bb_middle"
                },
                {
                    "left": "close",
                    "operator": ">",
                    "right": "bb_lower"
                },
                {
                    "left": "rsi",
                    "operator": "<",
                    "right": "50"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "30"
                },
                {
                    "left": "stoch_k",
                    "operator": "<",
                    "right": "40"
                },
                {
                    "left": "adx",
                    "operator": ">",
                    "right": "20"
                }
            ],
            "sellConditions": [
                {
                    "left": "sma_20",
                    "operator": "<",
                    "right": "sma_60"
                },
                {
                    "left": "close",
                    "operator": ">",
                    "right": "bb_upper"
                },
                {
                    "left": "rsi",
                    "operator": ">",
                    "right": "70"
                }
            ],
            "risk": {
                "stopLoss": 6,
                "takeProfit": 15,
                "positionSize": 100,
                "maxPositions": 3
            }
        }
    },
]

def create_templates():
    """템플릿 전략 생성"""

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\n" + "="*80)
    print("CREATING TEMPLATE STRATEGIES")
    print("="*80)

    # 먼저 기존 전략 이름들을 가져옴
    print("[INFO] Checking for existing strategies...")
    try:
        existing = supabase.table('strategies').select('name').execute()
        existing_names = [s['name'] for s in existing.data]
        print(f"[INFO] Found {len(existing_names)} existing strategies")
    except Exception as e:
        print(f"[WARNING] Could not check existing strategies: {str(e)[:50]}")
        existing_names = []

    created = []
    failed = []
    skipped = []

    for template in TEMPLATE_STRATEGIES:
        # 중복 이름 체크
        if template["name"] in existing_names:
            print(f"[SKIP] Already exists: {template['name']}")
            skipped.append(template["name"])
            continue

        try:
            # 전략 데이터 준비
            strategy_data = {
                "id": str(uuid.uuid4()),
                "name": template["name"],
                "description": template["description"],
                "config": template["config"],
                "user_id": None,  # 템플릿은 user_id가 없음
                "is_public": True,
                "created_at": datetime.now().isoformat()
            }

            # Supabase에 삽입
            result = supabase.table('strategies').insert(strategy_data).execute()

            print(f"[OK] Created: {template['name']}")
            created.append(template["name"])
            existing_names.append(template["name"])  # 성공한 것도 기존 목록에 추가

        except Exception as e:
            print(f"[ERROR] Failed: {template['name']} - {str(e)[:50]}")
            failed.append(template["name"])

    # 결과 요약
    print("\n" + "="*80)
    print("SUMMARY")
    print("-"*80)
    print(f"Successfully created: {len(created)} strategies")
    print(f"Skipped (already exists): {len(skipped)} strategies")
    print(f"Failed: {len(failed)} strategies")

    if created:
        print("\n[CREATED]:")
        for name in created:
            print(f"  - {name}")

    if skipped:
        print("\n[SKIPPED - Already Exists]:")
        for name in skipped:
            print(f"  - {name}")

    if failed:
        print("\n[FAILED]:")
        for name in failed:
            print(f"  - {name}")

    print("\n" + "="*80)
    print("[INFO] Template strategies have been created!")
    print("You can now test them with the backtest API")

    return created, failed

if __name__ == "__main__":
    created, failed = create_templates()