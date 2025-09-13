"""
단일 종목 다운로드 테스트
"""

import requests
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv()

# Supabase 클라이언트 초기화
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

# NAS REST API URL
nas_url = "http://192.168.50.150:8080"

def test_single_stock():
    """삼성전자 1개만 테스트"""

    stock_code = "005930"
    stock_name = "삼성전자"

    print(f"\n{'='*60}")
    print(f"종목: {stock_name} ({stock_code})")
    print(f"{'='*60}")

    # 1. NAS API에서 현재가 조회
    try:
        response = requests.post(
            f"{nas_url}/api/market/current-price",
            json={"stock_code": stock_code},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                price_data = data['data']
                print(f"[OK] Price data retrieved successfully")
                print(f"  - Current: {price_data['current_price']:,} won")
                print(f"  - Change: {price_data['change_price']:+,} won ({price_data['change_rate']:+.2f}%)")
                print(f"  - Volume: {price_data['volume']:,}")
                print(f"  - Source: {data.get('source')}")
                print(f"  - Kiwoom Token: {data.get('kiwoom_token')}")

                # 2. Supabase에 저장 (기존 테이블 구조에 맞게)
                save_data = {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'current_price': price_data['current_price'],
                    'change_price': price_data['change_price'],
                    'change_rate': price_data['change_rate'],
                    'volume': price_data['volume'],
                    'updated_at': datetime.now().isoformat()
                }

                result = supabase.table('kw_price_current').upsert(save_data).execute()
                print(f"\n[OK] Saved to Supabase")

            else:
                print(f"[ERROR] Failed to get price: {data.get('error')}")
        else:
            print(f"[ERROR] API error: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Exception: {e}")

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    test_single_stock()