"""
삼성전자 데이터 확인
"""

import os
import sys
from datetime import datetime
from supabase import create_client, Client

# 환경 변수
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://kpnioqijldwmidguzwox.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY2NzY2NjgsImV4cCI6MjA0MjI1MjY2OH0.u8mE0Zii_TdN7Rwgehs83kYKVLWAuEz8sFYR2daJ4wA')

def check_samsung_data():
    """삼성전자 데이터 확인"""

    print("="*60)
    print("삼성전자(005930) 데이터 확인")
    print("="*60)

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # 데이터 조회
        result = supabase.table('korea_stocks')\
            .select('*')\
            .eq('stock_code', '005930')\
            .gte('date', '2024-09-14')\
            .lte('date', '2025-09-12')\
            .order('date')\
            .execute()

        if result.data:
            print(f"데이터 개수: {len(result.data)}개")

            if len(result.data) > 0:
                print(f"\n첫 데이터: {result.data[0]['date']}")
                print(f"  Open: {result.data[0]['open']}")
                print(f"  Close: {result.data[0]['close']}")

                print(f"\n마지막 데이터: {result.data[-1]['date']}")
                print(f"  Open: {result.data[-1]['open']}")
                print(f"  Close: {result.data[-1]['close']}")

                # 가격 범위 확인
                prices = [d['close'] for d in result.data]
                print(f"\n가격 범위: {min(prices):,} ~ {max(prices):,}")
        else:
            print("데이터 없음!")

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_samsung_data()