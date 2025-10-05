"""
엑셀 계산과 백테스트 엔진 계산 비교
"""
import pandas as pd
from supabase import create_client

# 엑셀 데이터 로드
excel_path = r'C:\Users\khanyong\OneDrive\Documents\KakaoTalk Downloads\볼린져밴드 2단계  매수전략 검증.xlsx'
df_excel = pd.read_excel(excel_path, sheet_name=0)

# Supabase 데이터 로드
url = 'https://hznkyaomtrpzcayayayh.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM'

supabase = create_client(url, key)
response = supabase.table('backtest_results').select('trade_details').order('created_at', desc=True).limit(1).execute()
trades_db = response.data[0].get('trade_details', [])

print("=" * 80)
print("엑셀 vs 백테스트 엔진 계산 비교")
print("=" * 80)

# 엑셀 매도 거래 수익 합계
action_col = df_excel.columns[3]
profit_col = df_excel.columns[7]

excel_sell_trades = df_excel[df_excel[action_col] == 'sell']
excel_total_profit = excel_sell_trades[profit_col].sum()

print(f"\n엑셀:")
print(f"  매도 거래 수: {len(excel_sell_trades)}건")
print(f"  총 수익: {excel_total_profit:,.2f}원")

# DB 매도 거래 수익 합계
db_sell_trades = [t for t in trades_db if t.get('action') == 'sell']
db_total_profit = sum(t.get('profit_loss', 0) for t in db_sell_trades)

print(f"\n백테스트 엔진 (DB):")
print(f"  매도 거래 수: {len(db_sell_trades)}건")
print(f"  총 수익: {db_total_profit:,.2f}원")

print(f"\n차이:")
diff = excel_total_profit - db_total_profit
print(f"  {diff:,.2f}원")
print(f"  ({diff / excel_total_profit * 100:.2f}%)")

# 거래별 비교 (날짜와 종목 매칭)
print(f"\n{'=' * 80}")
print("개별 거래 비교 (처음 10개 매도 거래)")
print(f"{'=' * 80}")

date_col = df_excel.columns[0]
code_col = df_excel.columns[1]
qty_col = df_excel.columns[4]
amount_col = df_excel.columns[6]

matched_count = 0
total_diff = 0

for i, excel_row in excel_sell_trades.head(10).iterrows():
    excel_date = str(excel_row[date_col])[:10]
    excel_code = str(int(excel_row[code_col])) if pd.notna(excel_row[code_col]) else ''
    excel_profit = excel_row[profit_col]
    excel_qty = excel_row[qty_col]

    # DB에서 매칭되는 거래 찾기
    matching_trades = [
        t for t in db_sell_trades
        if str(t.get('date', ''))[:10] == excel_date
        and str(t.get('stock_code', '')) == excel_code
        and abs(t.get('quantity', 0) - excel_qty) < 1
    ]

    if matching_trades:
        db_trade = matching_trades[0]
        db_profit = db_trade.get('profit_loss', 0)
        trade_diff = excel_profit - db_profit
        total_diff += trade_diff
        matched_count += 1

        print(f"\n{matched_count}. {excel_date} {excel_code}")
        print(f"   엑셀 수익: {excel_profit:,.2f}원")
        print(f"   DB 수익: {db_profit:,.2f}원")
        print(f"   차이: {trade_diff:,.2f}원")

        # 금액 비교
        excel_amount = excel_row[amount_col]
        db_amount = db_trade.get('amount', 0)
        print(f"   엑셀 금액: {excel_amount:,.2f}원")
        print(f"   DB 금액: {db_amount:,.2f}원")
        print(f"   금액 차이: {excel_amount - db_amount:,.2f}원")

print(f"\n{'=' * 80}")
print(f"매칭된 거래: {matched_count}개")
print(f"누적 차이: {total_diff:,.2f}원")
