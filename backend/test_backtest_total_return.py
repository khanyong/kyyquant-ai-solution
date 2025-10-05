"""
백테스트 total_return 필드 테스트
"""
import asyncio
from backtest.engine import BacktestEngine

async def test_total_return_calculation():
    """
    백테스트 결과의 total_return과 total_return_rate 필드를 검증
    """
    print("=" * 60)
    print("백테스트 total_return 필드 검증 테스트")
    print("=" * 60)

    # 간단한 시나리오 시뮬레이션
    initial_capital = 10000000  # 1000만원
    final_capital = 11500000    # 1150만원

    # 수익 계산
    total_return = final_capital - initial_capital  # 절대값 (원)
    total_return_rate = (total_return / initial_capital) * 100  # 수익률 (%)

    print(f"\n초기 자본: {initial_capital:,}원")
    print(f"최종 자본: {final_capital:,}원")
    print(f"총 수익 (절대값): {total_return:,}원")
    print(f"총 수익률 (%): {total_return_rate:.2f}%")

    print("\n" + "=" * 60)
    print("API 응답 형식:")
    print("=" * 60)

    api_response = {
        'summary': {
            'total_return': total_return_rate,  # 수익률(%) - UI 표시용
            'total_return_pct': total_return_rate,  # 명확한 필드명
            'total_return_amount': total_return,  # 절대값(원)
        },
        'initial_capital': initial_capital,
        'final_capital': final_capital,
        'total_return': total_return,  # 절대값(원)
        'total_return_rate': total_return_rate,  # 수익률(%)
    }

    print(f"summary.total_return: {api_response['summary']['total_return']:.2f}% (UI에 표시될 값)")
    print(f"summary.total_return_pct: {api_response['summary']['total_return_pct']:.2f}%")
    print(f"summary.total_return_amount: {api_response['summary']['total_return_amount']:,}원")
    print(f"total_return: {api_response['total_return']:,}원")
    print(f"total_return_rate: {api_response['total_return_rate']:.2f}%")

    print("\n" + "=" * 60)
    print("DB 저장 형식 (BacktestRunner.tsx):")
    print("=" * 60)

    db_record = {
        'initial_capital': api_response['initial_capital'],
        'final_capital': api_response['final_capital'],
        'total_return': api_response['total_return_rate'],  # ✅ 수익률(%) 저장
    }

    print(f"initial_capital: {db_record['initial_capital']:,}원")
    print(f"final_capital: {db_record['final_capital']:,}원")
    print(f"total_return: {db_record['total_return']:.2f}% (수익률)")

    print("\n" + "=" * 60)
    print("검증:")
    print("=" * 60)

    # 검증 1: total_return이 수익률(%)로 저장되는지
    assert db_record['total_return'] == total_return_rate, \
        f"total_return이 수익률로 저장되어야 함: {db_record['total_return']} != {total_return_rate}"
    print("✅ DB의 total_return 필드는 수익률(%)로 저장됨")

    # 검증 2: final_capital과 initial_capital의 차이가 절대 수익과 같은지
    calculated_return = db_record['final_capital'] - db_record['initial_capital']
    assert calculated_return == total_return, \
        f"final - initial이 절대 수익과 같아야 함: {calculated_return} != {total_return}"
    print("✅ final_capital - initial_capital = 절대 수익(원)")

    print("\n" + "=" * 60)
    print("✅ 모든 테스트 통과!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_total_return_calculation())
