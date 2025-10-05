"""
미청산 포지션의 평가손익 분석
"""
from supabase import create_client

url = 'https://hznkyaomtrpzcayayayh.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM'

supabase = create_client(url, key)
response = supabase.table('backtest_results').select('*').order('created_at', desc=True).limit(1).execute()

result = response.data[0]
trades = result.get('trade_details', [])

initial_capital = result.get('initial_capital', 0)
final_capital = result.get('final_capital', 0)

# 종목별 포지션 추적
positions = {}

for trade in sorted(trades, key=lambda x: x.get('date', '')):
    code = trade.get('stock_code')
    qty = trade.get('quantity', 0)
    price = trade.get('price', 0)
    amount = trade.get('amount', 0)
    action = trade.get('action')

    if code not in positions:
        positions[code] = {
            'quantity': 0,
            'total_cost': 0,
            'last_price': price
        }

    if action == 'buy':
        # 매수: 원가 누적
        positions[code]['quantity'] += qty
        positions[code]['total_cost'] += amount
        positions[code]['last_price'] = price
    elif action == 'sell':
        # 매도: 원가 차감 (비율로)
        if positions[code]['quantity'] > 0:
            sold_cost = positions[code]['total_cost'] * (qty / positions[code]['quantity'])
            positions[code]['quantity'] -= qty
            positions[code]['total_cost'] -= sold_cost
        positions[code]['last_price'] = price

print("=" * 80)
print("미청산 포지션 평가손익 분석")
print("=" * 80)

# 미청산 포지션만 필터링
unrealized_positions = {k: v for k, v in positions.items() if v['quantity'] > 0}

print(f"\n미청산 포지션 수: {len(unrealized_positions)}개")

total_unrealized_cost = 0
total_unrealized_value = 0

for code, pos in unrealized_positions.items():
    qty = pos['quantity']
    cost = pos['total_cost']
    last_price = pos['last_price']

    current_value = qty * last_price
    unrealized_pnl = current_value - cost
    unrealized_rate = (unrealized_pnl / cost * 100) if cost > 0 else 0

    total_unrealized_cost += cost
    total_unrealized_value += current_value

    if abs(unrealized_pnl) > 1000:  # 1000원 이상 손익만 표시
        print(f"{code}: {qty}주, 원가 {cost:,.0f}원, 평가액 {current_value:,.0f}원, "
              f"평가손익 {unrealized_pnl:,.0f}원 ({unrealized_rate:.2f}%)")

total_unrealized_pnl = total_unrealized_value - total_unrealized_cost

print(f"\n{'=' * 80}")
print("미청산 포지션 합계")
print(f"{'=' * 80}")
print(f"총 원가: {total_unrealized_cost:,.0f}원")
print(f"총 평가액: {total_unrealized_value:,.0f}원")
print(f"총 평가손익: {total_unrealized_pnl:,.0f}원")
print(f"평가손익률: {(total_unrealized_pnl / total_unrealized_cost * 100) if total_unrealized_cost > 0 else 0:.2f}%")

# 검증
print(f"\n{'=' * 80}")
print("전체 수익 검증")
print(f"{'=' * 80}")

sell_trades = [t for t in trades if t.get('action') == 'sell']
realized_profit = sum(t.get('profit_loss', 0) for t in sell_trades)

print(f"청산 수익 (매도거래 합계): {realized_profit:,.0f}원")
print(f"미청산 평가손익: {total_unrealized_pnl:,.0f}원")
print(f"─────────────────────────")
print(f"총 수익 (계산): {realized_profit + total_unrealized_pnl:,.0f}원")
print(f"총 수익 (DB): {final_capital - initial_capital:,.0f}원")
print(f"차이: {(realized_profit + total_unrealized_pnl) - (final_capital - initial_capital):,.0f}원")

if abs((realized_profit + total_unrealized_pnl) - (final_capital - initial_capital)) < 100:
    print("\n✅ 수익 계산 정확: 청산수익 + 미청산평가손익 = 총수익")
else:
    print("\n⚠️  차이 발생: 추가 검토 필요")
