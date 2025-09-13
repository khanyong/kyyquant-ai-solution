"""
Supabase stock_metadata 테이블의 종목 수 확인
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def check_stock_count():
    """테이블의 종목 수 확인"""

    # Supabase 연결
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("stock_metadata 테이블 현황")
    print("=" * 60)

    try:
        # 전체 종목 수 (페이지네이션 고려)
        all_stocks = []
        page = 0
        page_size = 1000

        while True:
            result = supabase.table('stock_metadata').select('stock_code, stock_name, market').range(
                page * page_size,
                (page + 1) * page_size - 1
            ).execute()

            if not result.data:
                break

            all_stocks.extend(result.data)
            page += 1

            if len(result.data) < page_size:
                break

        print(f"\n전체 종목 수: {len(all_stocks)}개")

        # 시장별 분류
        kospi_count = len([s for s in all_stocks if s['market'] == 'KOSPI'])
        kosdaq_count = len([s for s in all_stocks if s['market'] == 'KOSDAQ'])
        konex_count = len([s for s in all_stocks if s['market'] == 'KONEX'])
        etc_count = len([s for s in all_stocks if s['market'] not in ['KOSPI', 'KOSDAQ', 'KONEX']])

        print(f"\n시장별 분류:")
        print(f"  - KOSPI: {kospi_count}개")
        print(f"  - KOSDAQ: {kosdaq_count}개")
        print(f"  - KONEX: {konex_count}개")
        if etc_count > 0:
            print(f"  - 기타: {etc_count}개")

        # 샘플 출력
        print(f"\n종목 예시 (처음 10개):")
        for i, stock in enumerate(all_stocks[:10]):
            print(f"  {i+1}. [{stock['market']}] {stock['stock_code']} - {stock['stock_name']}")

    except Exception as e:
        print(f"오류: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_stock_count()