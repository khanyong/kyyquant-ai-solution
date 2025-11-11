"""키움 API 현재가 및 일봉 조회 테스트"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()

kiwoom = get_kiwoom_client()

print("=" * 60)
print("1. 현재가 조회 테스트 (삼성전자 005930)")
print("=" * 60)
current = kiwoom.get_current_price("005930")
if current:
    print(f"✅ 현재가 조회 성공:")
    print(f"   현재가: {current['current_price']:,}원")
    print(f"   등락: {current['change']:+,}원 ({current['change_rate']:+.2f}%)")
    print(f"   거래량: {current['volume']:,}")
else:
    print("❌ 현재가 조회 실패")

print()
print("=" * 60)
print("2. 일봉 데이터 조회 테스트")
print("=" * 60)
daily = kiwoom.get_historical_price("005930", period=5)
if daily:
    print(f"✅ 일봉 조회 성공: {len(daily)}개 데이터")
    print()
    print("최근 5일 데이터:")
    for item in daily[:5]:
        date = item.get('stck_bsop_date', '')
        close = item.get('stck_clpr', '0')
        volume = item.get('acml_vol', '0')
        print(f"  {date}: {int(close):,}원 (거래량: {int(volume):,})")
else:
    print("❌ 일봉 조회 실패")
