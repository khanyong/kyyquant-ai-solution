"""
전체 종목 일봉 데이터 업데이트 스크립트
KOSPI + KOSDAQ 모든 종목의 최근 60일 데이터를 다운로드
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import time

sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()


def get_supabase_client():
    """Supabase 클라이언트 생성"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)


def update_stock_daily_prices(kiwoom, supabase, stock_code: str, stock_name: str, days: int = 60):
    """
    특정 종목의 일봉 데이터 업데이트
    """
    try:
        # 일봉 데이터 조회
        daily_data = kiwoom.get_historical_price(stock_code, period=days)

        if not daily_data:
            return 0

        # 모의투자 API 응답 구조 확인
        if isinstance(daily_data, dict) and 'stk_dt_pole_chart_qry' in daily_data:
            chart_list = daily_data['stk_dt_pole_chart_qry']
        else:
            chart_list = daily_data

        inserted = 0

        for item in chart_list:
            # 날짜 파싱
            trade_date = item.get('dt')
            if not trade_date or len(trade_date) != 8:
                continue

            formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"

            # 데이터 준비
            price_record = {
                'stock_code': stock_code,
                'trade_date': formatted_date,
                'open': float(item.get('open_pric', 0)),
                'high': float(item.get('high_pric', 0)),
                'low': float(item.get('low_pric', 0)),
                'close': float(item.get('cur_prc', 0)),
                'volume': int(item.get('trde_qty', 0)),
                'change_rate': float(item.get('trde_tern_rt', 0))
            }

            # Upsert
            result = supabase.table('kw_price_daily') \
                .upsert(price_record, on_conflict='stock_code,trade_date') \
                .execute()

            if result.data:
                inserted += 1

        return inserted

    except Exception as e:
        print(f"  [ERROR] {stock_code} ({stock_name}): {str(e)}")
        return 0


def main():
    print("=" * 80)
    print("전체 종목 일봉 데이터 업데이트")
    print("=" * 80)

    kiwoom = get_kiwoom_client()
    supabase = get_supabase_client()

    # 1. KOSPI 종목 리스트 조회
    print("\n1. KOSPI 종목 리스트 조회 중...")
    kospi_stocks = kiwoom.get_all_stock_list(market_type='0')

    # 2. KOSDAQ 종목 리스트 조회
    print("2. KOSDAQ 종목 리스트 조회 중...")
    kosdaq_stocks = kiwoom.get_all_stock_list(market_type='10')

    if not kospi_stocks and not kosdaq_stocks:
        print("[ERROR] 종목 리스트 조회 실패")
        return

    # 전체 종목 합치기
    all_stocks = []
    if kospi_stocks:
        all_stocks.extend([(s.get('code'), s.get('name', ''), 'KOSPI') for s in kospi_stocks])
    if kosdaq_stocks:
        all_stocks.extend([(s.get('code'), s.get('name', ''), 'KOSDAQ') for s in kosdaq_stocks])

    print(f"\n총 {len(all_stocks)}개 종목 발견")
    print(f"  - KOSPI: {len(kospi_stocks) if kospi_stocks else 0}개")
    print(f"  - KOSDAQ: {len(kosdaq_stocks) if kosdaq_stocks else 0}개")
    print()
    print("데이터 다운로드를 시작합니다...")
    print()

    # 3. 각 종목별로 업데이트
    print(f"\n데이터 다운로드 시작...")
    print("=" * 80)

    total_inserted = 0
    success_count = 0
    fail_count = 0

    start_time = time.time()

    for i, (stock_code, stock_name, market) in enumerate(all_stocks, 1):
        if not stock_code:
            continue

        print(f"[{i}/{len(all_stocks)}] {market} {stock_code} ({stock_name})")

        inserted = update_stock_daily_prices(kiwoom, supabase, stock_code, stock_name, days=60)

        if inserted > 0:
            success_count += 1
            total_inserted += inserted
            print(f"  OK: {inserted} records saved")
        else:
            fail_count += 1
            print(f"  SKIP: No data")

        # API 호출 제한 고려 (rate limit 429 에러 방지를 위해 1초 대기)
        time.sleep(1.0)

        # 진행상황 출력 (100개마다)
        if i % 100 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(all_stocks) - i) * avg_time
            print(f"\n--- 진행상황: {i}/{len(all_stocks)} ({i/len(all_stocks)*100:.1f}%) ---")
            print(f"    경과 시간: {elapsed/60:.1f}분")
            print(f"    예상 남은 시간: {remaining/60:.1f}분")
            print(f"    성공: {success_count}, 실패: {fail_count}\n")

    elapsed_total = time.time() - start_time

    print()
    print("=" * 80)
    print("완료")
    print("=" * 80)
    print(f"총 소요 시간: {elapsed_total/60:.1f}분")
    print(f"성공: {success_count}개 종목")
    print(f"실패: {fail_count}개 종목")
    print(f"총 {total_inserted:,}개 레코드 저장")
    print("=" * 80)


if __name__ == "__main__":
    main()
