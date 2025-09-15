"""
고급 전략 테스트 스크립트
- 분할 매수/매도
- 손절라인
- 트레일링 스탑
- 복합 지표 전략
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from datetime import datetime, timedelta
from kiwoom_bridge.backtest_engine_advanced import AdvancedBacktestEngine, SignalGenerator
from rest_api.strategy_engine import StrategyEngine
import pandas as pd
import numpy as np


def generate_realistic_stock_data(days=90, volatility=0.02, trend=0.001):
    """현실적인 주가 데이터 생성"""
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')

    # 기본 가격 설정
    initial_price = 50000
    prices = [initial_price]

    # 랜덤 워크 + 트렌드
    for i in range(1, days):
        change = np.random.normal(trend, volatility)
        new_price = prices[-1] * (1 + change)

        # 가격 급등/급락 이벤트 추가 (5% 확률)
        if np.random.random() < 0.05:
            shock = np.random.choice([-0.05, 0.05])  # ±5% 충격
            new_price *= (1 + shock)

        prices.append(new_price)

    prices = np.array(prices)

    # OHLCV 데이터 생성
    data = pd.DataFrame({
        'date': dates,
        'open': prices * np.random.uniform(0.99, 1.01, days),
        'high': prices * np.random.uniform(1.01, 1.03, days),
        'low': prices * np.random.uniform(0.97, 0.99, days),
        'close': prices,
        'volume': np.random.uniform(1000000, 5000000, days)
    })

    # 데이터 정합성 보정
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)

    return data


async def test_split_trading_strategy():
    """분할 매수/매도 전략 테스트"""
    print("\n" + "="*60)
    print("1. 분할 매수/매도 전략 테스트")
    print("="*60)

    strategy_config = {
        "name": "분할 매수/매도 전략",
        "indicators": [
            {"type": "ma", "period": 5},
            {"type": "ma", "period": 20},
            {"type": "rsi", "period": 14},
            {"type": "bb", "period": 20, "std_dev": 2}
        ],
        "buyConditions": [
            {
                "indicator": "close",
                "operator": "<",
                "value": "bb_lower",
                "combineWith": None
            },
            {
                "indicator": "rsi_14",
                "operator": "<",
                "value": 35,
                "combineWith": "OR"
            }
        ],
        "sellConditions": [
            {
                "indicator": "close",
                "operator": ">",
                "value": "bb_upper",
                "combineWith": None
            },
            {
                "indicator": "rsi_14",
                "operator": ">",
                "value": 65,
                "combineWith": "OR"
            }
        ],
        "splitTrading": {
            "enabled": True,
            "buyLevels": [
                {"priceLevel": 0, "percentage": 30},     # 첫 매수 30%
                {"priceLevel": -2, "percentage": 30},    # -2% 추가 30%
                {"priceLevel": -5, "percentage": 40}     # -5% 추가 40%
            ],
            "sellLevels": [
                {"profitLevel": 3, "percentage": 30},    # +3% 에서 30% 매도
                {"profitLevel": 5, "percentage": 30},    # +5% 에서 30% 매도
                {"profitLevel": 8, "percentage": 40}     # +8% 에서 40% 매도
            ]
        },
        "targetProfit": {
            "enabled": True,
            "value": 10.0,
            "combineWith": "OR"
        },
        "stopLoss": {
            "enabled": True,
            "value": 5.0
        }
    }

    # 데이터 생성 및 백테스트 실행
    data = generate_realistic_stock_data(days=90, volatility=0.025)

    engine = StrategyEngine()
    prepared_data = engine.prepare_data(data, strategy_config)

    backtest = AdvancedBacktestEngine()
    backtest.initial_capital = 10000000
    backtest.commission = 0.00015
    backtest.slippage = 0.001

    result = backtest.run(prepared_data, strategy_config)

    print(f"\n전략 결과:")
    print(f"  - 총 수익률: {result.get('total_return', 0):.2f}%")
    print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
    print(f"  - 최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
    print(f"  - 거래 횟수: {len(result.get('trades', []))}")

    return result


async def test_stop_loss_trailing_strategy():
    """손절 및 트레일링 스탑 전략 테스트"""
    print("\n" + "="*60)
    print("2. 손절 및 트레일링 스탑 전략")
    print("="*60)

    strategy_config = {
        "name": "손절 및 트레일링 스탑 전략",
        "indicators": [
            {"type": "ma", "period": 10},
            {"type": "ma", "period": 30},
            {"type": "macd", "fast": 12, "slow": 26, "signal": 9},
            {"type": "atr", "period": 14}
        ],
        "buyConditions": [
            {
                "indicator": "ma_10",
                "operator": "cross_above",
                "value": "ma_30",
                "combineWith": None
            },
            {
                "indicator": "macd",
                "operator": ">",
                "value": "macd_signal",
                "combineWith": "AND"
            }
        ],
        "sellConditions": [
            {
                "indicator": "ma_10",
                "operator": "cross_below",
                "value": "ma_30",
                "combineWith": None
            }
        ],
        "stopLoss": {
            "enabled": True,
            "value": 3.0,
            "type": "percentage"  # percentage 또는 atr
        },
        "trailingStop": {
            "enabled": True,
            "activation": 5.0,     # 5% 수익 후 활성화
            "distance": 2.0        # 최고점에서 2% 하락 시 매도
        },
        "targetProfit": {
            "enabled": True,
            "type": "stepped",  # 단계별 목표
            "levels": [
                {"profit": 5, "sellRatio": 0.3},
                {"profit": 10, "sellRatio": 0.3},
                {"profit": 15, "sellRatio": 0.4}
            ],
            "combineWith": "OR"
        }
    }

    # 데이터 생성 및 백테스트 실행
    data = generate_realistic_stock_data(days=120, volatility=0.02, trend=0.0005)

    engine = StrategyEngine()
    prepared_data = engine.prepare_data(data, strategy_config)

    backtest = AdvancedBacktestEngine()
    backtest.initial_capital = 10000000
    backtest.commission = 0.00015
    backtest.slippage = 0.001

    result = backtest.run(prepared_data, strategy_config)

    print(f"\n전략 결과:")
    print(f"  - 총 수익률: {result.get('total_return', 0):.2f}%")
    print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
    print(f"  - 최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
    print(f"  - 거래 횟수: {len(result.get('trades', []))}")

    # 손절/트레일링 스탑 발생 횟수 분석
    if 'trades' in result:
        stop_loss_count = sum(1 for t in result['trades']
                            if t.get('action') == 'sell' and t.get('reason') == 'stop_loss')
        trailing_stop_count = sum(1 for t in result['trades']
                                if t.get('action') == 'sell' and t.get('reason') == 'trailing_stop')
        print(f"  - 손절 발생: {stop_loss_count}회")
        print(f"  - 트레일링 스탑: {trailing_stop_count}회")

    return result


async def test_complex_multi_indicator_strategy():
    """복합 지표 전략 테스트"""
    print("\n" + "="*60)
    print("3. 복합 지표 전략 (RSI + MACD + 볼린저밴드 + 거래량)")
    print("="*60)

    strategy_config = {
        "name": "복합 지표 전략",
        "indicators": [
            {"type": "rsi", "period": 14},
            {"type": "macd", "fast": 12, "slow": 26, "signal": 9},
            {"type": "bb", "period": 20, "std_dev": 2},
            {"type": "volume", "period": 20},
            {"type": "ma", "period": 50},
            {"type": "ma", "period": 200},
            {"type": "stochastic", "k_period": 14, "d_period": 3}
        ],
        "buyConditions": [
            # 그룹 1: RSI 과매도
            {
                "indicator": "rsi_14",
                "operator": "<",
                "value": 30,
                "combineWith": None,
                "group": 1
            },
            # 그룹 2: MACD 골든크로스
            {
                "indicator": "macd",
                "operator": "cross_above",
                "value": "macd_signal",
                "combineWith": "OR",
                "group": 2
            },
            # 그룹 3: 볼린저밴드 하단 돌파
            {
                "indicator": "close",
                "operator": "<",
                "value": "bb_lower",
                "combineWith": "OR",
                "group": 3
            },
            # 추가 조건: 거래량 증가
            {
                "indicator": "volume",
                "operator": ">",
                "value": "volume_ma_20",
                "combineWith": "AND",
                "group": 0
            }
        ],
        "sellConditions": [
            # 그룹 1: RSI 과매수
            {
                "indicator": "rsi_14",
                "operator": ">",
                "value": 70,
                "combineWith": None,
                "group": 1
            },
            # 그룹 2: MACD 데드크로스
            {
                "indicator": "macd",
                "operator": "cross_below",
                "value": "macd_signal",
                "combineWith": "OR",
                "group": 2
            },
            # 그룹 3: 볼린저밴드 상단 돌파
            {
                "indicator": "close",
                "operator": ">",
                "value": "bb_upper",
                "combineWith": "OR",
                "group": 3
            }
        ],
        "positionSizing": {
            "method": "kelly",  # kelly, fixed, volatility_based
            "maxPositionSize": 0.3,  # 최대 30%
            "minPositionSize": 0.1   # 최소 10%
        },
        "riskManagement": {
            "maxDrawdown": 15,  # 15% 이상 손실 시 거래 중단
            "dailyLossLimit": 5,  # 일일 5% 이상 손실 시 당일 거래 중단
            "consecutiveLossStop": 3  # 3연패 시 거래 중단
        }
    }

    # 데이터 생성 및 백테스트 실행
    data = generate_realistic_stock_data(days=180, volatility=0.018, trend=0.0003)

    engine = StrategyEngine()
    prepared_data = engine.prepare_data(data, strategy_config)

    backtest = AdvancedBacktestEngine()
    backtest.initial_capital = 10000000
    backtest.commission = 0.00015
    backtest.slippage = 0.001

    result = backtest.run(prepared_data, strategy_config)

    print(f"\n전략 결과:")
    print(f"  - 총 수익률: {result.get('total_return', 0):.2f}%")
    print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
    print(f"  - 최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
    print(f"  - 샤프 비율: {result.get('sharpe_ratio', 0):.2f}")
    print(f"  - 거래 횟수: {len(result.get('trades', []))}")

    return result


async def test_pyramid_strategy():
    """피라미딩 전략 테스트"""
    print("\n" + "="*60)
    print("4. 피라미딩 전략 (추세 추종)")
    print("="*60)

    strategy_config = {
        "name": "피라미딩 전략",
        "indicators": [
            {"type": "ma", "period": 20},
            {"type": "ma", "period": 50},
            {"type": "atr", "period": 14},
            {"type": "adx", "period": 14}  # 추세 강도
        ],
        "buyConditions": [
            {
                "indicator": "close",
                "operator": ">",
                "value": "ma_20",
                "combineWith": None
            },
            {
                "indicator": "ma_20",
                "operator": ">",
                "value": "ma_50",
                "combineWith": "AND"
            },
            {
                "indicator": "adx_14",
                "operator": ">",
                "value": 25,  # 강한 추세
                "combineWith": "AND"
            }
        ],
        "pyramiding": {
            "enabled": True,
            "maxPositions": 3,  # 최대 3회 분할 매수
            "interval": {
                "type": "price",  # price 또는 time
                "value": 2  # 2% 상승마다 추가 매수
            },
            "sizeRatio": [1, 0.5, 0.25]  # 첫 매수 100%, 두 번째 50%, 세 번째 25%
        },
        "sellConditions": [
            {
                "indicator": "close",
                "operator": "<",
                "value": "ma_20",
                "combineWith": None
            }
        ],
        "stopLoss": {
            "enabled": True,
            "type": "atr",
            "multiplier": 2  # 2 ATR 손절
        }
    }

    # 상승 추세가 있는 데이터 생성
    data = generate_realistic_stock_data(days=150, volatility=0.015, trend=0.001)

    engine = StrategyEngine()
    prepared_data = engine.prepare_data(data, strategy_config)

    backtest = AdvancedBacktestEngine()
    backtest.initial_capital = 10000000
    backtest.commission = 0.00015
    backtest.slippage = 0.001

    result = backtest.run(prepared_data, strategy_config)

    print(f"\n전략 결과:")
    print(f"  - 총 수익률: {result.get('total_return', 0):.2f}%")
    print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
    print(f"  - 최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
    print(f"  - 거래 횟수: {len(result.get('trades', []))}")

    return result


async def test_mean_reversion_strategy():
    """평균회귀 전략 테스트"""
    print("\n" + "="*60)
    print("5. 평균회귀 전략 (박스권 매매)")
    print("="*60)

    strategy_config = {
        "name": "평균회귀 전략",
        "indicators": [
            {"type": "bb", "period": 20, "std_dev": 2},
            {"type": "rsi", "period": 14},
            {"type": "ma", "period": 20},
            {"type": "stochastic", "k_period": 14, "d_period": 3}
        ],
        "buyConditions": [
            # 볼린저 밴드 하단 근처
            {
                "indicator": "close",
                "operator": "<",
                "value": "bb_lower",
                "combineWith": None
            },
            # RSI 과매도
            {
                "indicator": "rsi_14",
                "operator": "<",
                "value": 30,
                "combineWith": "AND"
            },
            # 스토캐스틱 과매도
            {
                "indicator": "stoch_k",
                "operator": "<",
                "value": 20,
                "combineWith": "OR"
            }
        ],
        "sellConditions": [
            # 볼린저 밴드 중심선 도달
            {
                "indicator": "close",
                "operator": ">",
                "value": "bb_middle",
                "combineWith": None
            },
            # 또는 볼린저 밴드 상단 근처
            {
                "indicator": "close",
                "operator": ">",
                "value": "bb_upper",
                "combineWith": "OR"
            }
        ],
        "meanReversion": {
            "enabled": True,
            "targetReturn": "bb_middle",  # 중심선을 목표로
            "maxHoldingDays": 10  # 최대 10일 보유
        },
        "stopLoss": {
            "enabled": True,
            "value": 3.0
        }
    }

    # 박스권 움직임이 있는 데이터 생성 (낮은 trend)
    data = generate_realistic_stock_data(days=120, volatility=0.02, trend=0.0001)

    engine = StrategyEngine()
    prepared_data = engine.prepare_data(data, strategy_config)

    backtest = AdvancedBacktestEngine()
    backtest.initial_capital = 10000000
    backtest.commission = 0.00015
    backtest.slippage = 0.001

    result = backtest.run(prepared_data, strategy_config)

    print(f"\n전략 결과:")
    print(f"  - 총 수익률: {result.get('total_return', 0):.2f}%")
    print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
    print(f"  - 최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
    print(f"  - 평균 보유 기간: {result.get('avg_holding_days', 0):.1f}일")
    print(f"  - 거래 횟수: {len(result.get('trades', []))}")

    return result


async def run_all_tests():
    """모든 전략 테스트 실행"""
    print("="*60)
    print("고급 전략 백테스트 시작")
    print("="*60)

    results = {}

    # 1. 분할 매수/매도
    results['split_trading'] = await test_split_trading_strategy()

    # 2. 손절 및 트레일링 스탑
    results['stop_loss'] = await test_stop_loss_trailing_strategy()

    # 3. 복합 지표
    results['complex'] = await test_complex_multi_indicator_strategy()

    # 4. 피라미딩
    results['pyramid'] = await test_pyramid_strategy()

    # 5. 평균회귀
    results['mean_reversion'] = await test_mean_reversion_strategy()

    # 종합 결과 출력
    print("\n" + "="*60)
    print("종합 결과 비교")
    print("="*60)

    print(f"\n{'전략명':<25} {'수익률':>10} {'승률':>10} {'최대낙폭':>10} {'거래횟수':>10}")
    print("-"*65)

    for name, result in results.items():
        if result:
            print(f"{name:<25} "
                  f"{result.get('total_return', 0):>9.2f}% "
                  f"{result.get('win_rate', 0):>9.2f}% "
                  f"{result.get('max_drawdown', 0):>9.2f}% "
                  f"{len(result.get('trades', [])):>10}")

    # 최고 수익률 전략
    best_return = max(results.items(),
                     key=lambda x: x[1].get('total_return', 0) if x[1] else 0)
    print(f"\n최고 수익률 전략: {best_return[0]} ({best_return[1].get('total_return', 0):.2f}%)")

    # 최고 승률 전략
    best_winrate = max(results.items(),
                      key=lambda x: x[1].get('win_rate', 0) if x[1] else 0)
    print(f"최고 승률 전략: {best_winrate[0]} ({best_winrate[1].get('win_rate', 0):.2f}%)")

    # 최저 낙폭 전략
    best_drawdown = min(results.items(),
                       key=lambda x: x[1].get('max_drawdown', 100) if x[1] else 100)
    print(f"최저 낙폭 전략: {best_drawdown[0]} ({best_drawdown[1].get('max_drawdown', 0):.2f}%)")


if __name__ == "__main__":
    print("고급 전략 테스트를 시작합니다...")
    print("이 테스트는 시놀로지 NAS 없이 로컬에서 실행됩니다.\n")

    asyncio.run(run_all_tests())

    print("\n테스트 완료!")