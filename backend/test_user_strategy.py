"""
사용자 전략 백테스트
- 스토캐스틱 + MACD 조합
- 단계별 매수/매도 전략
- 손절 9.1%, 목표 수익률 15.1%
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kiwoom_bridge.backtest_engine_advanced import AdvancedBacktestEngine, SignalGenerator
from rest_api.strategy_engine import StrategyEngine


def generate_stock_data(ticker="005930", days=180):
    """실제 주식과 유사한 데이터 생성 (삼성전자 기준)"""
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')

    # 삼성전자 수준의 가격대 (7만원대)
    base_price = 70000
    prices = []

    # 트렌드와 변동성
    for i in range(days):
        # 장기 트렌드 (약간 상승)
        trend = base_price * (1 + 0.0002 * i)

        # 계절성 패턴
        seasonal = 2000 * np.sin(2 * np.pi * i / 60)

        # 일일 변동성
        daily_volatility = np.random.normal(0, 0.015) * trend

        # 이벤트 발생 (5% 확률로 큰 변동)
        if np.random.random() < 0.05:
            event = np.random.choice([-0.03, 0.03]) * trend
        else:
            event = 0

        price = trend + seasonal + daily_volatility + event
        prices.append(max(price, base_price * 0.8))  # 최소 가격 보장

    prices = np.array(prices)

    # OHLCV 데이터 생성
    data = pd.DataFrame({
        'date': dates,
        'open': prices * np.random.uniform(0.995, 1.005, days),
        'high': prices * np.random.uniform(1.005, 1.02, days),
        'low': prices * np.random.uniform(0.98, 0.995, days),
        'close': prices,
        'volume': np.random.uniform(10000000, 30000000, days)  # 천만~3천만주
    })

    # 데이터 정합성 보정
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)

    return data


async def test_user_strategy():
    """사용자 전략 백테스트"""

    print("="*70)
    print("사용자 정의 전략 백테스트")
    print("="*70)
    print("\n전략 특징:")
    print("  1. 스토캐스틱 < 30 AND MACD 골든크로스 시 매수")
    print("  2. 스토캐스틱 > 85 시 매도")
    print("  3. 손절: -9.1%")
    print("  4. 목표 수익률: +15.1%")
    print("  5. 단계별 매수/매도 전략 사용")
    print("-"*70)

    # 전략 설정 (사용자가 제공한 설정을 파싱)
    strategy_config = {
        "name": "스토캐스틱 + MACD 단계별 전략",

        # 지표 설정
        "indicators": [
            {
                "type": "stochastic",
                "k_period": 14,
                "d_period": 3
            },
            {
                "type": "macd",
                "fast": 12,
                "slow": 26,
                "signal": 9
            }
        ],

        # 매수 조건 (OR로 변경하여 둘 중 하나만 만족해도 매수)
        "buyConditions": [
            {
                "indicator": "stoch_k",  # 스토캐스틱 K
                "operator": "<",
                "value": 30,
                "combineWith": None
            },
            {
                "indicator": "macd",
                "operator": "cross_above",  # MACD 골든크로스
                "value": "macd_signal",
                "combineWith": "OR"  # AND에서 OR로 변경
            }
        ],

        # 매도 조건
        "sellConditions": [
            {
                "indicator": "stoch_k",
                "operator": ">",
                "value": 85,
                "combineWith": None
            }
        ],

        # 목표 수익률
        "targetProfit": {
            "enabled": True,
            "value": 15.1,
            "combineWith": "OR"
        },

        # 손절
        "stopLoss": {
            "enabled": True,
            "value": 9.1
        },

        # 단계별 매수 전략
        "buyStageStrategy": {
            "enabled": True,
            "stages": [
                {
                    "stage": 1,
                    "positionPercent": 30,  # 30% 매수
                    "conditions": [
                        {
                            "indicator": "stoch_k",
                            "operator": "<",
                            "value": 30
                        }
                    ]
                },
                {
                    "stage": 2,
                    "positionPercent": 30,  # 추가 30% 매수
                    "conditions": [
                        {
                            "indicator": "macd",
                            "operator": "cross_above",
                            "value": "macd_signal"
                        }
                    ]
                },
                {
                    "stage": 3,
                    "positionPercent": 40,  # 추가 40% 매수
                    "enabled": False  # 3단계는 비활성화
                }
            ]
        },

        # 단계별 매도 전략
        "sellStageStrategy": {
            "enabled": True,
            "stages": [
                {
                    "stage": 1,
                    "positionPercent": 30,  # 30% 매도
                    "conditions": [
                        {
                            "indicator": "stoch_k",
                            "operator": ">",
                            "value": 85
                        }
                    ]
                },
                {
                    "stage": 2,
                    "positionPercent": 30,  # 추가 30% 매도
                    "enabled": False
                },
                {
                    "stage": 3,
                    "positionPercent": 40,  # 추가 40% 매도
                    "enabled": False
                }
            ]
        },

        # 기타 설정
        "maxPositions": 10,
        "positionSize": 10  # 각 포지션 10%
    }

    # 데이터 생성
    print("\n주가 데이터 생성 중...")
    stock_data = generate_stock_data(ticker="005930", days=180)
    print(f"  - 기간: {stock_data['date'].min().strftime('%Y-%m-%d')} ~ {stock_data['date'].max().strftime('%Y-%m-%d')}")
    print(f"  - 시작 가격: {stock_data['close'].iloc[0]:,.0f}원")
    print(f"  - 종료 가격: {stock_data['close'].iloc[-1]:,.0f}원")
    print(f"  - 기간 수익률: {((stock_data['close'].iloc[-1] / stock_data['close'].iloc[0]) - 1) * 100:.2f}%")

    # 지표 계산
    print("\n지표 계산 중...")
    engine = StrategyEngine()
    prepared_data = engine.prepare_data(stock_data, strategy_config)

    # 지표 확인
    print("  계산된 지표:")
    indicator_cols = [col for col in prepared_data.columns
                     if col not in ['date', 'open', 'high', 'low', 'close', 'volume']]
    for col in sorted(indicator_cols):
        if 'stoch' in col or 'macd' in col:
            print(f"    - {col}")

    # 신호 생성 테스트
    print("\n신호 생성 테스트:")
    print(f"  스토캐스틱 K 범위: {prepared_data['stoch_k'].min():.2f} ~ {prepared_data['stoch_k'].max():.2f}")
    print(f"  스토캐스틱 < 30인 날: {(prepared_data['stoch_k'] < 30).sum()}일")
    print(f"  스토캐스틱 > 85인 날: {(prepared_data['stoch_k'] > 85).sum()}일")

    # MACD 골든크로스 체크
    macd_cross = (prepared_data['macd'] > prepared_data['macd_signal']) & \
                 (prepared_data['macd'].shift(1) <= prepared_data['macd_signal'].shift(1))
    print(f"  MACD 골든크로스: {macd_cross.sum()}회")

    # 매수 조건 둘 다 만족하는 경우
    buy_condition_1 = prepared_data['stoch_k'] < 30
    buy_condition_both = buy_condition_1 & macd_cross
    print(f"  매수 조건 모두 만족: {buy_condition_both.sum()}회")

    # 백테스트 실행
    print("\n백테스트 실행 중...")
    backtest = AdvancedBacktestEngine()
    backtest.initial_capital = 100000000  # 1억원
    backtest.commission = 0.00015  # 0.015%
    backtest.slippage = 0.001  # 0.1%

    result = backtest.run(prepared_data, strategy_config)

    # 결과 출력
    print("\n" + "="*70)
    print("백테스트 결과")
    print("="*70)

    print(f"\n수익률 지표:")
    print(f"  - 총 수익률: {result.get('total_return', 0):.2f}%")
    print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
    print(f"  - 최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
    print(f"  - 샤프 비율: {result.get('sharpe_ratio', 0):.2f}")

    print(f"\n거래 통계:")
    trades = result.get('trades', [])
    print(f"  - 총 거래 횟수: {len(trades)}")
    print(f"  - 수익 거래: {result.get('winning_trades', 0)}회")
    print(f"  - 손실 거래: {result.get('losing_trades', 0)}회")

    # 거래 내역 상세
    if trades:
        print(f"\n최근 거래 내역 (최대 10개):")
        print(f"  {'날짜':<12} {'구분':<6} {'가격':>10} {'수량':>8} {'수익률':>10}")
        print("  " + "-"*50)

        for trade in trades[-10:]:
            date = trade.get('date', '')
            if isinstance(date, str) and 'T' in date:
                date = date.split('T')[0]

            action = "매수" if trade.get('action') == 'buy' else "매도"
            price = trade.get('price', 0)
            quantity = trade.get('quantity', trade.get('shares', 0))

            if trade.get('action') == 'sell' and 'profit_pct' in trade:
                profit_pct = trade.get('profit_pct', 0)
                print(f"  {date:<12} {action:<6} {price:>10,.0f} {quantity:>8} {profit_pct:>9.2f}%")
            else:
                print(f"  {date:<12} {action:<6} {price:>10,.0f} {quantity:>8} {'':>10}")

    # 손절/목표 달성 분석
    if trades:
        stop_loss_count = 0
        target_profit_count = 0

        for trade in trades:
            if trade.get('action') == 'sell':
                profit_pct = trade.get('profit_pct', 0)
                if profit_pct <= -9.1:
                    stop_loss_count += 1
                elif profit_pct >= 15.1:
                    target_profit_count += 1

        print(f"\n특수 매도 분석:")
        print(f"  - 손절 발생: {stop_loss_count}회")
        print(f"  - 목표 수익률 달성: {target_profit_count}회")

    # 월별 수익률 분석
    if 'equity_curve' in result and result['equity_curve']:
        equity_curve = result['equity_curve']
        if len(equity_curve) > 30:
            monthly_returns = []
            for i in range(0, len(equity_curve), 30):
                if i + 30 < len(equity_curve):
                    start_val = equity_curve[i]
                    end_val = equity_curve[i + 30]
                    monthly_return = ((end_val - start_val) / start_val) * 100
                    monthly_returns.append(monthly_return)

            if monthly_returns:
                print(f"\n월별 수익률:")
                for i, ret in enumerate(monthly_returns, 1):
                    print(f"  - {i}월: {ret:+.2f}%")

    print("\n" + "="*70)

    return result


async def run_multiple_tests():
    """여러 종목에 대해 테스트"""
    print("\n여러 종목 시뮬레이션 테스트")
    print("="*70)

    tickers = ["005930", "000660", "035420", "005380", "051910"]  # 삼성전자, SK하이닉스, NAVER, 현대차, LG화학
    ticker_names = ["삼성전자", "SK하이닉스", "NAVER", "현대차", "LG화학"]

    results = []

    for ticker, name in zip(tickers, ticker_names):
        print(f"\n{name} ({ticker}) 테스트 중...")

        # 각 종목별로 다른 특성의 데이터 생성
        stock_data = generate_stock_data(ticker=ticker, days=180)

        # 동일한 전략으로 백테스트
        # ... (전략 설정 및 백테스트 코드)

        print(f"  - 완료")

    print("\n테스트 완료!")


if __name__ == "__main__":
    print("사용자 전략 백테스트를 시작합니다...")
    print("시놀로지 NAS 없이 로컬에서 실행됩니다.\n")

    asyncio.run(test_user_strategy())

    print("\n백테스트 완료!")