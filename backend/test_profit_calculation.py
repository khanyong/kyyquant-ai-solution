"""
수익률 계산 로직 테스트
"""

def test_profit_calculation():
    """
    수익 계산 로직 검증

    시나리오:
    - 매수: 10주 @ 50,000원 = 500,000원
    - 매수 수수료 (0.015%): 75원
    - 총 매수 원가: 500,075원

    - 매도: 10주 @ 55,000원 = 550,000원
    - 매도 수수료 (0.015%): 82.5원
    - 실수령액: 549,917.5원

    - 수익: 549,917.5 - 500,075 = 49,842.5원
    - 수익률: 49,842.5 / 500,075 * 100 = 9.97%
    """

    # 매수
    buy_price = 50000
    buy_quantity = 10
    buy_amount = buy_quantity * buy_price
    commission_rate = 0.00015
    buy_commission = buy_amount * commission_rate
    total_cost = buy_amount + buy_commission

    print("=== 매수 ===")
    print(f"가격: {buy_price:,}원")
    print(f"수량: {buy_quantity}주")
    print(f"매수 금액: {buy_amount:,}원")
    print(f"매수 수수료: {buy_commission:,.2f}원")
    print(f"총 원가: {total_cost:,.2f}원")

    # 매도
    sell_price = 55000
    sell_quantity = 10
    sell_amount = sell_quantity * sell_price
    sell_commission = sell_amount * commission_rate

    # 기존 잘못된 계산 (수수료 중복 차감)
    old_profit = sell_amount - total_cost - sell_commission
    old_profit_rate = old_profit / total_cost * 100

    # 수정된 계산
    net_sell_amount = sell_amount - sell_commission
    new_profit = net_sell_amount - total_cost
    new_profit_rate = new_profit / total_cost * 100

    print("\n=== 매도 ===")
    print(f"가격: {sell_price:,}원")
    print(f"수량: {sell_quantity}주")
    print(f"매도 금액: {sell_amount:,}원")
    print(f"매도 수수료: {sell_commission:,.2f}원")
    print(f"실수령액: {net_sell_amount:,.2f}원")

    print("\n=== 기존 계산 (잘못된 방식) ===")
    print(f"수익: {old_profit:,.2f}원")
    print(f"수익률: {old_profit_rate:.2f}%")

    print("\n=== 수정된 계산 (올바른 방식) ===")
    print(f"수익: {new_profit:,.2f}원")
    print(f"수익률: {new_profit_rate:.2f}%")

    print("\n=== 차이 ===")
    print(f"수익 차이: {new_profit - old_profit:,.2f}원")
    print(f"수익률 차이: {new_profit_rate - old_profit_rate:.2f}%p")

    # 검증
    expected_profit = 49842.5
    assert abs(new_profit - expected_profit) < 0.01, f"수익 계산 오류: {new_profit} != {expected_profit}"
    print("\n✅ 테스트 통과!")

if __name__ == "__main__":
    test_profit_calculation()
