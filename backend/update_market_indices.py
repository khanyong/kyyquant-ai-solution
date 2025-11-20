"""
KOSPI/KOSDAQ 지수 일봉 데이터 다운로드
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()


def get_supabase_client():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)


def update_index_data(kiwoom, supabase, index_code: str, index_name: str, days: int = 60):
    """
    지수 일봉 데이터 업데이트
    """
    try:
        print(f"\n[{index_name}] 일봉 데이터 다운로드 중...")

        # 지수도 get_historical_price 사용 (동일한 API)
        daily_data = kiwoom.get_historical_price(index_code, period=days)

        if not daily_data:
            print(f"  [WARNING] 데이터 없음")
            return 0

        # 응답 구조 확인
        if isinstance(daily_data, dict) and 'stk_dt_pole_chart_qry' in daily_data:
            chart_list = daily_data['stk_dt_pole_chart_qry']
        else:
            chart_list = daily_data

        inserted = 0

        for item in chart_list:
            trade_date = item.get('dt')
            if not trade_date or len(trade_date) != 8:
                continue

            formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"

            # 지수 데이터 저장 (kw_price_daily 테이블에 저장)
            index_record = {
                'stock_code': index_code,  # '0001' (KOSPI) 또는 '1001' (KOSDAQ)
                'trade_date': formatted_date,
                'open': float(item.get('open_pric', 0)),
                'high': float(item.get('high_pric', 0)),
                'low': float(item.get('low_pric', 0)),
                'close': float(item.get('cur_prc', 0)),
                'volume': int(item.get('trde_qty', 0)),
                'change_rate': float(item.get('trde_tern_rt', 0))
            }

            result = supabase.table('kw_price_daily') \
                .upsert(index_record, on_conflict='stock_code,trade_date') \
                .execute()

            if result.data:
                inserted += 1

        print(f"  [OK] {inserted}개 레코드 저장")
        return inserted

    except Exception as e:
        print(f"  [ERROR] {e}")
        return 0


def main():
    print("=" * 80)
    print("KOSPI/KOSDAQ 지수 일봉 데이터 업데이트")
    print("=" * 80)

    kiwoom = get_kiwoom_client()
    supabase = get_supabase_client()

    # KOSPI 지수 (코드: 0001)
    kospi_inserted = update_index_data(kiwoom, supabase, '0001', 'KOSPI', days=60)

    # KOSDAQ 지수 (코드: 1001)
    kosdaq_inserted = update_index_data(kiwoom, supabase, '1001', 'KOSDAQ', days=60)

    print()
    print("=" * 80)
    print("완료")
    print("=" * 80)
    print(f"KOSPI: {kospi_inserted}개 레코드")
    print(f"KOSDAQ: {kosdaq_inserted}개 레코드")
    print(f"총 {kospi_inserted + kosdaq_inserted}개 레코드 저장")
    print("=" * 80)


if __name__ == "__main__":
    main()
