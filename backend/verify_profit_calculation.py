"""
수익 계산 산식 정밀 검증
실제 Supabase 데이터와 비교
"""
from supabase import create_client

url = 'https://hznkyaomtrpzcayayayh.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM'

supabase = create_client(url, key)

# 최근 백테스트 결과 조회
response = supabase.table('backtest_results').select('*').order('created_at', desc=True).limit(1).execute()

if not response.data:
    print("No data found")
    exit(1)

result = response.data[0]
trades = result.get('trade_details', [])

initial_capital = result.get('initial_capital', 0)
final_capital = result.get('final_capital', 0)

print("=" * 80)
print("백테스트 수익 계산 산식 검증")
print("=" * 80)

# 1. DB에 저장된 값
print("\n[1] DB 저장된 값")
print(f"초기 자본: {initial_capital:,.0f}원")
print(f"최종 자본: {final_capital:,.0f}원")
print(f"DB의 total_return: {result.get('total_return')}")

# 2. 매매 거래에서 계산
buy_trades = [t for t in trades if t.get('action') == 'buy']
sell_trades = [t for t in trades if t.get('action') == 'sell']

print(f"\n[2] 거래 내역")
print(f"매수 거래: {len(buy_trades)}건")
print(f"매도 거래: {len(sell_trades)}건")

# 3. 매수 총액 계산
total_buy_amount = 0
total_buy_commission = 0

for trade in buy_trades:
    amount = trade.get('amount', 0)
    # trade_details에는 commission 필드가 없을 수 있음
    # amount는 이미 수량 * 가격
    total_buy_amount += amount

print(f"\n[3] 매수 집계")
print(f"총 매수 금액: {total_buy_amount:,.0f}원")

# 4. 매도 총액 및 수익 계산
total_sell_amount = 0
total_profit_from_trades = 0

for trade in sell_trades:
    amount = trade.get('amount', 0)
    profit_loss = trade.get('profit_loss', 0)

    total_sell_amount += amount
    total_profit_from_trades += profit_loss

print(f"\n[4] 매도 집계")
print(f"총 매도 금액: {total_sell_amount:,.0f}원")
print(f"매도 거래 profit_loss 합계: {total_profit_from_trades:,.0f}원")

# 5. 자본금 변화 추적
print(f"\n[5] 자본금 변화 분석")
print(f"초기 자본: {initial_capital:,.0f}원")
print(f"최종 자본: {final_capital:,.0f}원")
print(f"자본 증가: {final_capital - initial_capital:,.0f}원")

# 6. 수익 계산 검증
print(f"\n[6] 수익 계산 검증")

# 방법 1: 최종자본 - 초기자본
method1_profit = final_capital - initial_capital
method1_rate = (method1_profit / initial_capital) * 100

print(f"\n방법1 (최종-초기):")
print(f"  수익: {method1_profit:,.0f}원")
print(f"  수익률: {method1_rate:.2f}%")

# 방법 2: 매도 거래 profit_loss 합계
method2_profit = total_profit_from_trades
method2_rate = (method2_profit / initial_capital) * 100 if initial_capital > 0 else 0

print(f"\n방법2 (매도거래 수익합계):")
print(f"  수익: {method2_profit:,.0f}원")
print(f"  수익률: {method2_rate:.2f}%")

# 7. 차이 분석
diff = method1_profit - method2_profit

print(f"\n[7] 차이 분석")
print(f"방법1 - 방법2 = {diff:,.0f}원")

if abs(diff) < 100:
    print("결론: 차이가 거의 없음 - 계산 정확")
else:
    print("결론: 차이 발견 - 원인 분석 필요")
    print("\n가능한 원인:")
    print("1. 미청산 포지션의 평가 수익")
    print("2. 수수료 계산 방식 차이")
    print("3. 단계별 매수/매도로 인한 평균단가 변동")

    # 미청산 포지션 추정
    print(f"\n미청산 포지션 평가 수익 (추정): {diff:,.0f}원")

# 8. 샘플 거래로 산식 확인
print(f"\n[8] 샘플 거래로 수익 계산 산식 확인")

if sell_trades:
    sample_sell = sell_trades[0]
    print(f"\n첫 번째 매도 거래:")
    print(f"  날짜: {sample_sell.get('date')}")
    print(f"  종목: {sample_sell.get('stock_code')}")
    print(f"  수량: {sample_sell.get('quantity')}주")
    print(f"  가격: {sample_sell.get('price'):,.0f}원")
    print(f"  매도금액: {sample_sell.get('amount'):,.0f}원")
    print(f"  수익: {sample_sell.get('profit_loss'):,.0f}원")
    print(f"  수익률: {sample_sell.get('profit_rate'):.2f}%")

    # 역산으로 원가 추정
    amount = sample_sell.get('amount', 0)
    profit = sample_sell.get('profit_loss', 0)

    # profit = sell_amount - commission - cost
    # cost = sell_amount - commission - profit
    estimated_cost = amount - profit

    print(f"\n  역산한 매수 원가 (추정): {estimated_cost:,.0f}원")
    print(f"  산식: 매도금액 - 수익 = {amount:,.0f} - {profit:,.0f} = {estimated_cost:,.0f}")

# 9. 최종 결론
print(f"\n{'=' * 80}")
print("최종 결론")
print(f"{'=' * 80}")

print(f"\n올바른 수익 계산:")
print(f"  절대 수익: {method1_profit:,.0f}원 (최종자본 - 초기자본)")
print(f"  수익률: {method1_rate:.2f}% ((최종-초기) / 초기 * 100)")

print(f"\n현재 엔진 계산:")
if abs(method1_profit - method2_profit) < 100:
    print(f"  정확: 매도거래 수익합계({method2_profit:,.0f}원) ≈ 실제수익({method1_profit:,.0f}원)")
    print(f"  결론: 산식 정확 - 표기 형식만 수정 필요")
else:
    print(f"  주의: 매도거래 수익합계({method2_profit:,.0f}원) != 실제수익({method1_profit:,.0f}원)")
    print(f"  차이: {diff:,.0f}원")
    print(f"  결론: 미청산 포지션 또는 추가 검토 필요")
