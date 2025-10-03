"""
매도 OR 로직 테스트
- 목표수익률 OR 지표 조건 검증
- 손절 우선순위 검증
"""

import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

from backtest.engine import BacktestEngine

def get_supabase_client() -> Client:
    """Get Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(url, key)

async def test_sell_or_logic():
    """매도 OR 로직 테스트"""

    # RSI 3단계 분할 매수/매도 전략
    # 매도: 목표수익률 3% OR RSI > 70
    strategy_config = {
        "useStageBasedStrategy": True,
        "indicators": [
            {"name": "rsi", "params": {"period": 14}}
        ],
        "buyStageStrategy": {
            "stages": [
                {
                    "stage": 1,
                    "enabled": True,
                    "positionPercent": 50,
                    "passAllRequired": False,
                    "conditions": [
                        {"left": "rsi", "operator": "<", "right": 35}
                    ]
                },
                {
                    "stage": 2,
                    "enabled": True,
                    "positionPercent": 50,
                    "passAllRequired": False,
                    "conditions": [
                        {"left": "rsi", "operator": "<", "right": 28}
                    ]
                },
                {
                    "stage": 3,
                    "enabled": True,
                    "positionPercent": 100,
                    "passAllRequired": False,
                    "conditions": [
                        {"left": "rsi", "operator": "<", "right": 20}
                    ]
                }
            ]
        },
        "sellStageStrategy": {
            "stages": [
                {
                    "stage": 1,
                    "enabled": True,
                    "exitPercent": 30,
                    "passAllRequired": False,
                    "targetProfit": {
                        "enabled": True,
                        "value": 3
                    },
                    "conditions": [
                        {"left": "rsi", "operator": ">", "right": 70}
                    ]
                },
                {
                    "stage": 2,
                    "enabled": True,
                    "exitPercent": 40,
                    "passAllRequired": False,
                    "targetProfit": {
                        "enabled": True,
                        "value": 7
                    },
                    "conditions": [
                        {"left": "rsi", "operator": ">", "right": 75}
                    ]
                },
                {
                    "stage": 3,
                    "enabled": True,
                    "exitPercent": 100,
                    "passAllRequired": False,
                    "targetProfit": {
                        "enabled": True,
                        "value": 12
                    },
                    "conditions": [
                        {"left": "rsi", "operator": ">", "right": 80}
                    ]
                }
            ],
            "stopLoss": {
                "enabled": True,
                "type": "dynamic",
                "stages": [
                    {"profitThreshold": 0, "stopLossPercent": -5},
                    {"profitThreshold": 3, "stopLossPercent": -3},
                    {"profitThreshold": 7, "stopLossPercent": 0}
                ]
            }
        }
    }

    print("=" * 80)
    print("매도 OR 로직 테스트")
    print("=" * 80)
    print("\n전략 설정:")
    print("- 매수: RSI 3단계 (35, 28, 20)")
    print("- 매도 1단계 (30%): 목표수익률 3% OR RSI > 70")
    print("- 매도 2단계 (40%): 목표수익률 7% OR RSI > 75")
    print("- 매도 3단계 (100%): 목표수익률 12% OR RSI > 80")
    print("- 손절: -5% → -3% (3% 이상) → 0% (7% 이상)")
    print()

    # Initialize engine
    engine = BacktestEngine()

    print("백테스트 실행 중...")
    results = await engine.run_with_config(
        strategy_config=strategy_config,
        stock_codes=["005930"],  # 삼성전자
        start_date="2024-01-01",
        end_date="2024-12-31",
        initial_capital=10_000_000
    )

    print("\n" + "=" * 80)
    print("백테스트 결과")
    print("=" * 80)

    # Debug: print all result keys
    print(f"Result keys: {list(results.keys())}")

    print(f"총 수익률: {results.get('total_return', 0):.2f}%")
    print(f"총 거래 횟수: {results.get('total_trades', 0)}")
    print(f"승률: {results.get('win_rate', 0):.2f}%")
    print(f"최대 낙폭: {results.get('max_drawdown', 0):.2f}%")
    print(f"최종 잔고: {results.get('final_capital', results.get('final_balance', 0)):,.0f}원")

    # 거래 상세 분석
    trades = results.get('trades', [])
    if trades:
        print(f"\n총 거래 수: {len(trades)}")
        print("\n주요 거래 샘플 (처음 10개):")
        print("-" * 80)

        for i, trade in enumerate(trades[:10], 1):
            # Debug: print all trade keys
            if i == 1:
                print(f"Trade object keys: {list(trade.keys())}\n")

            entry_reason = trade.get('buy_reason', trade.get('entry_reason', 'N/A'))
            exit_reason = trade.get('sell_reason', trade.get('exit_reason', 'N/A'))
            profit_rate = trade.get('profit_pct', trade.get('profit_rate', 0))

            print(f"\n거래 #{i}:")
            print(f"  매수: {trade.get('buy_date', trade.get('entry_date', 'N/A'))} @ {trade.get('buy_price', trade.get('entry_price', 0)):,.0f}원")
            print(f"  매수 이유: {entry_reason}")
            print(f"  매도: {trade.get('sell_date', trade.get('exit_date', 'N/A'))} @ {trade.get('sell_price', trade.get('exit_price', 0)):,.0f}원")
            print(f"  매도 이유: {exit_reason}")
            print(f"  수익률: {profit_rate:+.2f}%")

            # OR 조건 검증
            if 'OR' in exit_reason:
                print(f"  ✅ OR 조건으로 매도됨")
            elif 'Stop loss' in exit_reason:
                print(f"  ⚠️  손절로 매도됨")
            elif 'Stage' in exit_reason:
                print(f"  📊 단계별 조건으로 매도됨")
            elif 'Target profit' in exit_reason:
                print(f"  🎯 목표수익률로 매도됨")

    print("\n" + "=" * 80)
    print("테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_sell_or_logic())
