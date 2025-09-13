"""
한국거래소(KRX)에서 전체 종목을 배치로 수집하여 Supabase에 저장
"""

from pykrx import stock
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()

def save_batch_to_supabase(batch_data, supabase_client, batch_num):
    """배치 데이터를 Supabase에 저장"""
    success = 0
    skip = 0
    fail = 0

    for stock_info in batch_data:
        try:
            # 이미 있는지 확인
            existing = supabase_client.table('stock_metadata').select('stock_code').eq('stock_code', stock_info['stock_code']).execute()

            if existing.data:
                skip += 1
            else:
                # 새로운 종목 추가
                result = supabase_client.table('stock_metadata').insert(stock_info).execute()
                success += 1

        except Exception as e:
            print(f"      ERROR: {stock_info['stock_code']} - {e}")
            fail += 1

    print(f"   배치 {batch_num} 완료: 성공 {success}, 건너뜀 {skip}, 실패 {fail}")
    return success, skip, fail

def fetch_all_stocks_batch():
    """KRX에서 전체 종목을 배치로 수집"""

    print("=" * 60)
    print("한국거래소(KRX) 전체 종목 배치 수집")
    print("=" * 60)

    # Supabase 연결
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    # 오늘 날짜
    today = datetime.now().strftime("%Y%m%d")

    total_success = 0
    total_skip = 0
    total_fail = 0

    batch_size = 50  # 배치 크기

    # 1. KOSPI 종목 처리
    print("\n1. KOSPI 종목 처리 중...")
    try:
        kospi_tickers = stock.get_market_ticker_list(today, market="KOSPI")
        print(f"   총 {len(kospi_tickers)}개 종목")

        for i in range(0, len(kospi_tickers), batch_size):
            batch_tickers = kospi_tickers[i:i+batch_size]
            batch_data = []

            for ticker in batch_tickers:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    stock_info = {
                        "stock_code": ticker,
                        "stock_name": name,
                        "market": "KOSPI",
                        "sector": None,
                        "industry": None
                    }
                    batch_data.append(stock_info)
                    time.sleep(0.01)  # API 제한 방지
                except Exception as e:
                    print(f"      종목명 조회 실패: {ticker} - {e}")

            # 배치 저장
            s, sk, f = save_batch_to_supabase(batch_data, supabase, i//batch_size + 1)
            total_success += s
            total_skip += sk
            total_fail += f

            # 진행상황
            processed = min(i + batch_size, len(kospi_tickers))
            print(f"   KOSPI 진행: {processed}/{len(kospi_tickers)} ({processed*100//len(kospi_tickers)}%)")
            time.sleep(0.5)  # 배치 간 대기

    except Exception as e:
        print(f"   KOSPI 처리 실패: {e}")

    # 2. KOSDAQ 종목 처리
    print("\n2. KOSDAQ 종목 처리 중...")
    try:
        kosdaq_tickers = stock.get_market_ticker_list(today, market="KOSDAQ")
        print(f"   총 {len(kosdaq_tickers)}개 종목")

        for i in range(0, len(kosdaq_tickers), batch_size):
            batch_tickers = kosdaq_tickers[i:i+batch_size]
            batch_data = []

            for ticker in batch_tickers:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    stock_info = {
                        "stock_code": ticker,
                        "stock_name": name,
                        "market": "KOSDAQ",
                        "sector": None,
                        "industry": None
                    }
                    batch_data.append(stock_info)
                    time.sleep(0.01)  # API 제한 방지
                except Exception as e:
                    print(f"      종목명 조회 실패: {ticker} - {e}")

            # 배치 저장
            s, sk, f = save_batch_to_supabase(batch_data, supabase, i//batch_size + 1)
            total_success += s
            total_skip += sk
            total_fail += f

            # 진행상황
            processed = min(i + batch_size, len(kosdaq_tickers))
            print(f"   KOSDAQ 진행: {processed}/{len(kosdaq_tickers)} ({processed*100//len(kosdaq_tickers)}%)")
            time.sleep(0.5)  # 배치 간 대기

    except Exception as e:
        print(f"   KOSDAQ 처리 실패: {e}")

    # 3. KONEX 종목 처리 (선택사항)
    print("\n3. KONEX 종목 처리 중...")
    try:
        konex_tickers = stock.get_market_ticker_list(today, market="KONEX")
        print(f"   총 {len(konex_tickers)}개 종목")

        for i in range(0, len(konex_tickers), batch_size):
            batch_tickers = konex_tickers[i:i+batch_size]
            batch_data = []

            for ticker in batch_tickers:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    stock_info = {
                        "stock_code": ticker,
                        "stock_name": name,
                        "market": "KONEX",
                        "sector": None,
                        "industry": None
                    }
                    batch_data.append(stock_info)
                    time.sleep(0.01)  # API 제한 방지
                except Exception as e:
                    print(f"      종목명 조회 실패: {ticker} - {e}")

            # 배치 저장
            s, sk, f = save_batch_to_supabase(batch_data, supabase, i//batch_size + 1)
            total_success += s
            total_skip += sk
            total_fail += f

            # 진행상황
            processed = min(i + batch_size, len(konex_tickers))
            print(f"   KONEX 진행: {processed}/{len(konex_tickers)} ({processed*100//len(konex_tickers)}%)")
            time.sleep(0.5)  # 배치 간 대기

    except Exception as e:
        print(f"   KONEX 처리 실패: {e}")

    # 최종 결과
    print("\n" + "=" * 60)
    print("배치 처리 완료!")
    print(f"  총 성공: {total_success}개")
    print(f"  총 건너뜀: {total_skip}개 (이미 존재)")
    print(f"  총 실패: {total_fail}개")
    print("=" * 60)

    # 전체 종목 수 확인
    try:
        total_result = supabase.table('stock_metadata').select('stock_code', count='exact').execute()
        total_count = len(total_result.data) if total_result.data else 0
        print(f"\n현재 stock_metadata 테이블의 총 종목 수: {total_count}개")

        # 시장별 분류
        kospi = supabase.table('stock_metadata').select('stock_code').eq('market', 'KOSPI').execute()
        kosdaq = supabase.table('stock_metadata').select('stock_code').eq('market', 'KOSDAQ').execute()
        konex = supabase.table('stock_metadata').select('stock_code').eq('market', 'KONEX').execute()

        print(f"  - KOSPI: {len(kospi.data) if kospi.data else 0}개")
        print(f"  - KOSDAQ: {len(kosdaq.data) if kosdaq.data else 0}개")
        print(f"  - KONEX: {len(konex.data) if konex.data else 0}개")
    except Exception as e:
        print(f"테이블 확인 실패: {e}")

if __name__ == "__main__":
    fetch_all_stocks_batch()