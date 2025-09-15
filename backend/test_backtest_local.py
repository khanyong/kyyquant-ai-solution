import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# 현재 파일의 디렉토리를 기준으로 backend 경로 추가
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

# 백테스트 엔진 직접 임포트
from kiwoom_bridge.backtest_engine_advanced import AdvancedBacktestEngine
from rest_api.strategy_engine import StrategyEngine
import pandas as pd
import numpy as np


async def test_backtest_locally():
    """로컬에서 백테스트 엔진 직접 테스트"""

    print("=== 로컬 백테스트 테스트 시작 ===\n")

    # 테스트 전략 설정 (실제 프론트엔드에서 보내는 형식)
    strategy_config = {
        "name": "RSI + MA 전략",
        "indicators": [
            {"type": "ma", "period": 20},
            {"type": "rsi", "period": 14}
        ],
        "buyConditions": [
            {
                "indicator": "rsi_14",
                "operator": "<",
                "value": 40,  # 30에서 40으로 완화
                "combineWith": None
            },
            {
                "indicator": "close",
                "operator": ">",
                "value": "ma_20",
                "combineWith": "OR"  # AND에서 OR로 변경
            }
        ],
        "sellConditions": [
            {
                "indicator": "rsi_14",
                "operator": ">",
                "value": 60,  # 70에서 60으로 완화
                "combineWith": None
            }
        ],
        "targetProfit": {
            "enabled": True,
            "value": 5.0,
            "combineWith": "OR"
        },
        "stopLoss": {
            "enabled": True,
            "value": 3.0
        }
    }

    # 샘플 주가 데이터 생성 (실제 패턴을 시뮬레이션)
    dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
    n_days = len(dates)

    # 트렌드와 노이즈를 포함한 현실적인 주가 생성
    trend = np.linspace(100, 120, n_days)  # 상승 트렌드
    seasonal = 10 * np.sin(np.linspace(0, 4*np.pi, n_days))  # 계절성
    noise = np.random.normal(0, 5, n_days)  # 랜덤 노이즈

    prices = trend + seasonal + noise

    # OHLCV 데이터 생성
    sample_data = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.uniform(-2, 2, n_days),
        'high': prices + np.random.uniform(0, 5, n_days),
        'low': prices - np.random.uniform(0, 5, n_days),
        'close': prices,
        'volume': np.random.uniform(1000000, 3000000, n_days)
    })

    # 데이터 정합성 보정
    sample_data['high'] = sample_data[['open', 'high', 'close']].max(axis=1)
    sample_data['low'] = sample_data[['open', 'low', 'close']].min(axis=1)

    print(f"샘플 데이터 생성 완료: {len(sample_data)}일")
    print(f"가격 범위: {sample_data['close'].min():.2f} ~ {sample_data['close'].max():.2f}\n")

    # 1. StrategyEngine으로 지표 계산
    print("=== 지표 계산 시작 ===")
    strategy_engine = StrategyEngine()
    prepared_data = strategy_engine.prepare_data(sample_data.copy(), strategy_config)

    # 생성된 지표 확인
    indicator_columns = [col for col in prepared_data.columns
                        if col not in ['date', 'open', 'high', 'low', 'close', 'volume']]
    print(f"생성된 지표: {indicator_columns}\n")

    # 지표 값 샘플 출력
    print("=== 지표 값 샘플 (마지막 5일) ===")
    for col in ['close', 'ma_20', 'rsi_14']:
        if col in prepared_data.columns:
            print(f"{col}: {prepared_data[col].tail(5).values}")
    print()

    # 2. AdvancedBacktestEngine으로 백테스트 실행
    print("=== 백테스트 실행 ===")
    backtest_engine = AdvancedBacktestEngine()

    # 백테스트 파라미터
    initial_capital = 10000000  # 1천만원
    commission = 0.00015  # 0.015%
    slippage = 0.001  # 0.1%

    # 백테스트 실행
    try:
        # AdvancedBacktestEngine 초기화 시 파라미터 설정
        backtest_engine.initial_capital = initial_capital
        backtest_engine.commission = commission
        backtest_engine.slippage = slippage

        # run 메서드 호출
        result = backtest_engine.run(
            data=prepared_data,
            strategy_config=strategy_config
        )

        # 결과 출력
        print("\n=== 백테스트 결과 ===")
        print(f"총 수익률: {result.get('total_return', 0):.2f}%")
        print(f"승률: {result.get('win_rate', 0):.2f}%")
        print(f"최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
        print(f"샤프 비율: {result.get('sharpe_ratio', 0):.2f}")
        print(f"총 거래 횟수: {result.get('trades', [])}")
        print(f"수익 거래: {result.get('winning_trades', 0)}")
        print(f"손실 거래: {result.get('losing_trades', 0)}")

        # final_capital이 없을 수 있으므로 체크
        if 'final_capital' in result:
            print(f"최종 자산: {result['final_capital']:,.0f}원")
        elif 'equity_curve' in result and result['equity_curve']:
            print(f"최종 자산: {result['equity_curve'][-1]:,.0f}원")

        # 거래 내역 출력
        if result['trade_history']:
            print("\n=== 최근 거래 내역 (최대 5개) ===")
            for trade in result['trade_history'][:5]:
                action = "매수" if trade['action'] == 'buy' else "매도"
                print(f"{trade['date']}: {action} - 가격: {trade['price']:,.0f}, 수량: {trade['shares']}")
                if 'profit' in trade:
                    print(f"  수익: {trade['profit']:,.0f}원 ({trade.get('profit_pct', 0):.2f}%)")

    except Exception as e:
        print(f"백테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()


async def test_conditions_only():
    """조건 평가만 테스트"""

    print("\n=== 조건 평가 테스트 ===")

    # 간단한 테스트 데이터
    test_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'close': [100, 102, 98, 95, 93, 97, 101, 105, 103, 107],
        'ma_20': [100, 100, 99, 98, 97, 96, 97, 98, 99, 100],
        'rsi_14': [50, 55, 45, 30, 25, 35, 50, 70, 75, 60]
    })

    print("테스트 데이터:")
    print(test_data[['close', 'ma_20', 'rsi_14']])

    # 매수 조건 평가
    buy_conditions = [
        {"indicator": "rsi_14", "operator": "<", "value": 30, "combineWith": None},
        {"indicator": "close", "operator": ">", "value": "ma_20", "combineWith": "AND"}
    ]

    from kiwoom_bridge.backtest_engine_advanced import SignalGenerator

    buy_signal = SignalGenerator.evaluate_conditions(test_data, buy_conditions, 'buy')
    print(f"\n매수 신호: {buy_signal.tolist()}")

    # 매도 조건 평가
    sell_conditions = [
        {"indicator": "rsi_14", "operator": ">", "value": 70, "combineWith": None}
    ]

    sell_signal = SignalGenerator.evaluate_conditions(test_data, sell_conditions, 'sell')
    print(f"매도 신호: {sell_signal.tolist()}")


if __name__ == "__main__":
    print("로컬 백테스트 테스트 시작...\n")

    # 두 가지 테스트 실행
    asyncio.run(test_backtest_locally())
    asyncio.run(test_conditions_only())

    print("\n테스트 완료!")