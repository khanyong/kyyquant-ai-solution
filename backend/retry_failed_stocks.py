"""
실패한 종목만 재시도하는 스크립트
사용법: python retry_failed_stocks.py
"""

import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from api.kiwoom_client import KiwoomAPIClient

# .env 파일 로드
load_dotenv()

# Supabase 클라이언트 초기화
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Kiwoom API 클라이언트 초기화
kiwoom = KiwoomAPIClient()

def get_stocks_without_data(days_threshold=60):
    """
    최근 N일 이내 데이터가 없는 종목 조회
    """
    print(f"\n{'='*80}")
    print(f"최근 {days_threshold}일 이내 데이터 없는 종목 조회 중...")
    print(f"{'='*80}\n")

    cutoff_date = (datetime.now() - timedelta(days=days_threshold)).strftime('%Y-%m-%d')

    try:
        # stock_metadata에서 모든 종목 조회
        all_stocks = supabase.table('stock_metadata') \
            .select('stock_code, stock_name') \
            .execute()

        failed_stocks = []

        for stock in all_stocks.data:
            stock_code = stock['stock_code']
            stock_name = stock['stock_name']

            # 해당 종목의 최근 데이터 확인
            recent_data = supabase.table('kw_price_daily') \
                .select('trade_date') \
                .eq('stock_code', stock_code) \
                .gte('trade_date', cutoff_date) \
                .execute()

            if not recent_data.data or len(recent_data.data) < 30:  # 60일 중 30일 미만 데이터
                failed_stocks.append({
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'data_count': len(recent_data.data) if recent_data.data else 0
                })

        print(f"데이터 부족 종목: {len(failed_stocks)}개\n")
        return failed_stocks

    except Exception as e:
        print(f"ERROR: 종목 조회 실패 - {e}")
        return []

def retry_failed_stocks(failed_stocks):
    """
    실패한 종목들 재시도
    """
    total = len(failed_stocks)
    success_count = 0
    fail_count = 0

    print(f"\n{'='*80}")
    print(f"실패 종목 재시도 시작: {total}개")
    print(f"{'='*80}\n")

    start_time = time.time()

    for idx, stock in enumerate(failed_stocks, 1):
        stock_code = stock['stock_code']
        stock_name = stock['stock_name']

        print(f"[{idx}/{total}] {stock_code} {stock_name} (기존 데이터: {stock['data_count']}개)")

        try:
            # 60일치 데이터 다운로드
            daily_data = kiwoom.get_historical_price(
                stock_code=stock_code,
                period=60
            )

            if not daily_data:
                print(f"  SKIP: 데이터 없음")
                fail_count += 1
                time.sleep(1.0)
                continue

            # 모의투자 API 응답 구조 확인
            if isinstance(daily_data, dict) and 'stk_dt_pole_chart_qry' in daily_data:
                chart_list = daily_data['stk_dt_pole_chart_qry']
            else:
                chart_list = daily_data

            # Supabase에 업로드
            uploaded = 0
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
                    'close': float(item.get('cur_pric', 0)),
                    'volume': int(item.get('trde_qty', 0)),
                    'change_rate': float(item.get('trde_tern_rt', 0))
                }

                result = supabase.table('kw_price_daily') \
                    .upsert(price_record, on_conflict='stock_code,trade_date') \
                    .execute()

                if result.data:
                    uploaded += 1

            print(f"  OK: {uploaded}개 데이터 업로드")
            success_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            fail_count += 1

        # Rate limit 방지
        time.sleep(1.0)

        # 진행상황 출력 (10개마다)
        if idx % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / idx
            remaining = (total - idx) * avg_time

            print(f"\n--- 진행상황: {idx}/{total} ({idx/total*100:.1f}%) ---")
            print(f"    경과 시간: {elapsed/60:.1f}분")
            print(f"    예상 남은 시간: {remaining/60:.1f}분")
            print(f"    성공: {success_count}, 실패: {fail_count}\n")

    # 최종 결과
    total_time = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"재시도 완료")
    print(f"{'='*80}")
    print(f"총 소요 시간: {total_time/60:.1f}분")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"성공률: {success_count/total*100:.1f}%")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("실패 종목 재시도 스크립트")
    print("="*80 + "\n")

    # 1단계: 데이터 없는 종목 조회
    failed_stocks = get_stocks_without_data(days_threshold=60)

    if not failed_stocks:
        print("재시도할 종목이 없습니다.")
        sys.exit(0)

    # 2단계: 사용자 확인
    print(f"\n총 {len(failed_stocks)}개 종목을 재시도합니다.")
    print("예상 소요 시간: {:.1f}분".format(len(failed_stocks) * 1.0 / 60))

    response = input("\n계속하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        sys.exit(0)

    # 3단계: 재시도 실행
    retry_failed_stocks(failed_stocks)
