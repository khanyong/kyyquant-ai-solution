"""
한국거래소(KRX)에서 전체 종목 리스트 수집
pykrx 라이브러리를 사용하여 모든 KOSPI/KOSDAQ 종목 정보 가져오기
"""

from pykrx import stock
from datetime import datetime
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv()

def fetch_all_stocks():
    """KRX에서 전체 종목 정보 수집"""

    print("=" * 60)
    print("한국거래소(KRX) 전체 종목 정보 수집")
    print("=" * 60)

    # Supabase 연결
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    # 오늘 날짜
    today = datetime.now().strftime("%Y%m%d")

    all_stocks = []

    # 1. KOSPI 종목 수집
    print("\n1. KOSPI 종목 수집 중...")
    try:
        kospi_tickers = stock.get_market_ticker_list(today, market="KOSPI")
        print(f"   KOSPI 종목 수: {len(kospi_tickers)}개")

        for i, ticker in enumerate(kospi_tickers):
            try:
                # 종목명 가져오기
                name = stock.get_market_ticker_name(ticker)

                # 종목 정보 (섹터 정보는 추가 API로 가져올 수 있음)
                stock_info = {
                    "stock_code": ticker,
                    "stock_name": name,
                    "market": "KOSPI",
                    "sector": None,  # 추후 업데이트 가능
                    "industry": None  # 추후 업데이트 가능
                }

                all_stocks.append(stock_info)

                # 진행상황 표시 (100개마다)
                if (i + 1) % 100 == 0:
                    print(f"   처리 중: {i + 1}/{len(kospi_tickers)}")

                # API 호출 제한 방지
                time.sleep(0.01)

            except Exception as e:
                print(f"   ERROR: {ticker} - {e}")
                continue

    except Exception as e:
        print(f"   KOSPI 종목 수집 실패: {e}")

    # 2. KOSDAQ 종목 수집
    print("\n2. KOSDAQ 종목 수집 중...")
    try:
        kosdaq_tickers = stock.get_market_ticker_list(today, market="KOSDAQ")
        print(f"   KOSDAQ 종목 수: {len(kosdaq_tickers)}개")

        for i, ticker in enumerate(kosdaq_tickers):
            try:
                # 종목명 가져오기
                name = stock.get_market_ticker_name(ticker)

                # 종목 정보
                stock_info = {
                    "stock_code": ticker,
                    "stock_name": name,
                    "market": "KOSDAQ",
                    "sector": None,  # 추후 업데이트 가능
                    "industry": None  # 추후 업데이트 가능
                }

                all_stocks.append(stock_info)

                # 진행상황 표시 (100개마다)
                if (i + 1) % 100 == 0:
                    print(f"   처리 중: {i + 1}/{len(kosdaq_tickers)}")

                # API 호출 제한 방지
                time.sleep(0.01)

            except Exception as e:
                print(f"   ERROR: {ticker} - {e}")
                continue

    except Exception as e:
        print(f"   KOSDAQ 종목 수집 실패: {e}")

    # 3. KONEX 종목 수집 (선택사항)
    print("\n3. KONEX 종목 수집 중...")
    try:
        konex_tickers = stock.get_market_ticker_list(today, market="KONEX")
        print(f"   KONEX 종목 수: {len(konex_tickers)}개")

        for i, ticker in enumerate(konex_tickers):
            try:
                # 종목명 가져오기
                name = stock.get_market_ticker_name(ticker)

                # 종목 정보
                stock_info = {
                    "stock_code": ticker,
                    "stock_name": name,
                    "market": "KONEX",
                    "sector": None,
                    "industry": None
                }

                all_stocks.append(stock_info)

                # 진행상황 표시 (50개마다)
                if (i + 1) % 50 == 0:
                    print(f"   처리 중: {i + 1}/{len(konex_tickers)}")

                # API 호출 제한 방지
                time.sleep(0.01)

            except Exception as e:
                print(f"   ERROR: {ticker} - {e}")
                continue

    except Exception as e:
        print(f"   KONEX 종목 수집 실패: {e}")

    print("\n" + "=" * 60)
    print(f"수집 완료! 총 {len(all_stocks)}개 종목")

    # 4. DataFrame으로 저장 (백업용)
    df = pd.DataFrame(all_stocks)
    csv_filename = f"krx_all_stocks_{today}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"CSV 파일 저장: {csv_filename}")

    # 5. Supabase에 저장
    print("\n" + "=" * 60)
    print("Supabase에 종목 정보 저장 중...")
    print("=" * 60)

    success_count = 0
    skip_count = 0
    fail_count = 0
    batch_size = 100  # 배치 크기

    for i in range(0, len(all_stocks), batch_size):
        batch = all_stocks[i:i + batch_size]

        for stock_info in batch:
            try:
                # 이미 있는지 확인
                existing = supabase.table('stock_metadata').select('stock_code').eq('stock_code', stock_info['stock_code']).execute()

                if existing.data:
                    skip_count += 1
                else:
                    # 새로운 종목 추가
                    result = supabase.table('stock_metadata').insert(stock_info).execute()
                    success_count += 1

            except Exception as e:
                print(f"   ERROR: {stock_info['stock_code']} - {e}")
                fail_count += 1

        # 진행상황 표시
        processed = min(i + batch_size, len(all_stocks))
        print(f"   진행: {processed}/{len(all_stocks)} ({processed*100//len(all_stocks)}%)")

        # API 제한 방지
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("저장 완료!")
    print(f"  성공: {success_count}개")
    print(f"  건너뜀: {skip_count}개 (이미 존재)")
    print(f"  실패: {fail_count}개")
    print("=" * 60)

    # 전체 종목 수 확인
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

if __name__ == "__main__":
    fetch_all_stocks()