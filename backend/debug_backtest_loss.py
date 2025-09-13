"""
백테스트 -50% 손실 문제 디버깅 스크립트
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_backtest_problem():
    """백테스트 문제 분석"""

    print("=" * 60)
    print("백테스트 -50% 손실 문제 분석")
    print("=" * 60)

    # 1. 수수료 영향 시뮬레이션
    print("\n1. 수수료 영향 분석:")
    initial_capital = 10000000
    commission_rate = 0.00015  # 0.015%
    trades_per_month = 20  # 월 20회 매매
    months = 12

    capital = initial_capital
    for month in range(months):
        for trade in range(trades_per_month):
            # 매수 수수료
            capital = capital * (1 - commission_rate)
            # 매도 수수료
            capital = capital * (1 - commission_rate)

    total_loss_pct = ((capital - initial_capital) / initial_capital) * 100
    print(f"  초기 자본: {initial_capital:,}원")
    print(f"  월 매매 횟수: {trades_per_month}회")
    print(f"  수수료율: {commission_rate * 100}%")
    print(f"  1년 후 자본: {capital:,.0f}원")
    print(f"  수수료만으로 인한 손실: {total_loss_pct:.2f}%")

    # 2. RSI 전략 문제점
    print("\n2. RSI 전략 설정 문제:")
    print("  현재 설정:")
    print("    - 매수: RSI < 30 (과매도)")
    print("    - 매도: RSI > 70 (과매수)")
    print("  문제점:")
    print("    - RSI가 30-70 사이에서만 움직이면 매매 신호 없음")
    print("    - 극단적 조건으로 매매 기회가 적음")
    print("    - 추세 시장에서는 효과적이지 않음")

    # 3. 권장 설정
    print("\n3. 권장 백테스트 설정:")
    print("  ✅ RSI 조건 완화:")
    print("    - 매수: RSI < 40")
    print("    - 매도: RSI > 60")
    print("  ✅ 손절/익절 설정:")
    print("    - 손절: -3%")
    print("    - 익절: +5%")
    print("  ✅ 포지션 관리:")
    print("    - 최대 포지션: 5개")
    print("    - 포지션당 비중: 20%")

    # 4. 실제 데이터 확인 필요
    print("\n4. 확인 필요 사항:")
    print("  ⚠️ 가격 데이터가 실제 데이터인지 확인")
    print("  ⚠️ 모든 종목이 동일한 가격(71,900원)이면 Mock 데이터")
    print("  ⚠️ 백테스트 로그에서 실제 매매 횟수 확인")
    print("  ⚠️ 슬리피지 설정 확인 (현재 0.1% = 0.001)")

    print("\n" + "=" * 60)
    print("💡 해결 방법:")
    print("1. RSI 조건을 40/60으로 완화")
    print("2. 실제 과거 데이터 다운로드 확인")
    print("3. 수수료를 0.01%로 낮춰서 테스트")
    print("4. 매매 로그를 확인하여 빈번한 매매 체크")
    print("=" * 60)

if __name__ == "__main__":
    analyze_backtest_problem()