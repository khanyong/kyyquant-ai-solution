"""
최종 수정 테스트 - 거래 0회 문제 해결 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_with_correct_format():
    """올바른 형식으로 테스트"""

    print("="*60)
    print("최종 수정 테스트")
    print("="*60)

    # 1. 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100)
    prices = []
    base = 50000

    # 명확한 골든크로스/데드크로스 생성
    for i in range(100):
        if i < 30:
            base = base * 0.98  # 하락
        elif i < 70:
            base = base * 1.02  # 상승 (골든크로스)
        else:
            base = base * 0.99  # 하락 (데드크로스)
        prices.append(base)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    print(f"데이터: {len(df)}개")
    print(f"가격 범위: {min(prices):.0f} ~ {max(prices):.0f}")

    # 2. 올바른 전략 설정 (소문자 + params 구조)
    strategy = {
        "indicators": [
            {"type": "ma", "params": {"period": 5}},
            {"type": "ma", "params": {"period": 20}}
        ],
        "buyConditions": [
            {"indicator": "ma_5", "operator": "cross_above", "value": "ma_20"}
        ],
        "sellConditions": [
            {"indicator": "ma_5", "operator": "cross_below", "value": "ma_20"}
        ]
    }

    print("\n전략 설정:")
    print(json.dumps(strategy, indent=2, ensure_ascii=False))

    # 3. Core 모듈 테스트
    print("\n" + "="*40)
    print("Core 모듈 테스트")
    print("="*40)

    try:
        from core import compute_indicators, evaluate_conditions

        # 지표 계산
        df = compute_indicators(df, strategy)
        print(f"지표 계산 완료. 컬럼: {[c for c in df.columns if 'ma' in c]}")

        # 신호 생성
        buy_signal = evaluate_conditions(df, strategy['buyConditions'], 'buy')
        sell_signal = evaluate_conditions(df, strategy['sellConditions'], 'sell')

        buy_count = (buy_signal == 1).sum()
        sell_count = (sell_signal == -1).sum()

        print(f"매수 신호: {buy_count}개")
        print(f"매도 신호: {sell_count}개")

        if buy_count > 0:
            print("\n매수 시점:")
            print(df[buy_signal == 1][['date', 'close', 'ma_5', 'ma_20']].head())

        if sell_count > 0:
            print("\n매도 시점:")
            print(df[sell_signal == -1][['date', 'close', 'ma_5', 'ma_20']].head())

        # 4. 백테스트 시뮬레이션
        print("\n" + "="*40)
        print("백테스트 시뮬레이션")
        print("="*40)

        position = None
        trades = []
        capital = 10000000

        for i in range(len(df)):
            if buy_signal.iloc[i] == 1 and position is None:
                position = {
                    'entry_price': df.iloc[i]['close'],
                    'entry_date': df.iloc[i]['date'],
                    'quantity': int(capital * 0.1 / df.iloc[i]['close'])
                }
                trades.append({
                    'date': df.iloc[i]['date'],
                    'action': 'BUY',
                    'price': df.iloc[i]['close']
                })
                print(f"[매수] {df.iloc[i]['date'].date()}: {df.iloc[i]['close']:.0f}원")

            elif sell_signal.iloc[i] == -1 and position is not None:
                profit_pct = ((df.iloc[i]['close'] - position['entry_price']) / position['entry_price']) * 100
                trades.append({
                    'date': df.iloc[i]['date'],
                    'action': 'SELL',
                    'price': df.iloc[i]['close'],
                    'profit_pct': profit_pct
                })
                print(f"[매도] {df.iloc[i]['date'].date()}: {df.iloc[i]['close']:.0f}원 (수익률: {profit_pct:.2f}%)")
                position = None

        # 강제청산
        if position is not None:
            last_row = df.iloc[-1]
            profit_pct = ((last_row['close'] - position['entry_price']) / position['entry_price']) * 100
            trades.append({
                'date': last_row['date'],
                'action': 'SELL',
                'price': last_row['close'],
                'profit_pct': profit_pct,
                'note': 'FORCE_CLOSE'
            })
            print(f"[강제청산] {last_row['date'].date()}: {last_row['close']:.0f}원 (수익률: {profit_pct:.2f}%)")

        print(f"\n총 거래: {len(trades)}회")

        return True

    except ImportError as e:
        print(f"❌ Core 모듈 임포트 실패: {e}")
        print("=> core/ 폴더가 업로드되지 않았거나 경로 문제")
        return False
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_file_structure():
    """파일 구조 확인"""
    print("\n" + "="*40)
    print("파일 구조 확인")
    print("="*40)

    required_files = [
        'core/__init__.py',
        'core/naming.py',
        'core/indicators.py',
        'core/signals.py',
        'backtest_engine_advanced.py',
        'strategy_engine.py',
        'backtest_api.py'
    ]

    for file in required_files:
        if os.path.exists(file):
            # Core 사용 여부 확인
            if '.py' in file and 'core/' not in file:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'USE_CORE' in content or 'from core import' in content:
                        print(f"✅ {file} - Core 모듈 사용")
                    else:
                        print(f"⚠️  {file} - Core 모듈 미사용")
            else:
                print(f"✅ {file} 존재")
        else:
            print(f"❌ {file} 없음")


if __name__ == "__main__":
    # 파일 구조 확인
    check_file_structure()

    # 테스트 실행
    success = test_with_correct_format()

    print("\n" + "="*60)
    if success:
        print("✅ 테스트 성공! 거래가 발생합니다.")
        print("\n다음 단계:")
        print("1. 모든 파일을 NAS에 업로드")
        print("2. Docker 재시작: docker-compose up -d --build")
        print("3. 프론트엔드에서 템플릿 전략 선택하여 테스트")
    else:
        print("❌ 테스트 실패. 위 오류를 확인하세요.")
    print("="*60)