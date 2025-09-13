"""
Supabase에 저장된 종목 데이터 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def check_saved_stocks():
    """저장된 종목 데이터 확인"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("Supabase에 저장된 종목 데이터")
    print("=" * 60)

    try:
        # kw_price_current 테이블에서 모든 종목 조회
        result = supabase.table('kw_price_current').select("*").execute()

        if result.data:
            print(f"총 {len(result.data)}개 종목 저장됨")
            print()

            for stock in result.data:
                stock_code = stock.get('stock_code')
                price = stock.get('current_price', 0)
                change_rate = stock.get('change_rate', 0)
                volume = stock.get('volume', 0)
                updated_at = stock.get('updated_at', 'N/A')

                # 종목명 매핑
                stock_names = {
                    '005930': '삼성전자',
                    '000660': 'SK하이닉스',
                    '035720': '카카오'
                }

                name = stock_names.get(stock_code, '알 수 없음')

                print(f"종목: {name} ({stock_code})")
                print(f"  현재가: {price:,}원")
                print(f"  등락률: {change_rate}%")
                print(f"  거래량: {volume:,}주")
                print(f"  업데이트: {updated_at[:19] if updated_at != 'N/A' else 'N/A'}")
                print()

        else:
            print("저장된 종목 데이터가 없습니다.")

    except Exception as e:
        print(f"오류: {e}")

    print("=" * 60)

if __name__ == "__main__":
    check_saved_stocks()