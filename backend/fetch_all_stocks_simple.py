"""
한국거래소(KRX)에서 전체 종목 리스트 수집 - 간단 버전
pykrx 라이브러리를 사용하여 모든 KOSPI/KOSDAQ 종목 정보 가져오기
"""

from pykrx import stock
from datetime import datetime
import time

def fetch_and_display_stocks():
    """KRX에서 전체 종목 정보 수집하여 표시"""

    print("=" * 60)
    print("한국거래소(KRX) 전체 종목 정보 수집")
    print("=" * 60)

    # 오늘 날짜
    today = datetime.now().strftime("%Y%m%d")

    # 1. KOSPI 종목 수집
    print("\n1. KOSPI 종목 수:")
    try:
        kospi_tickers = stock.get_market_ticker_list(today, market="KOSPI")
        print(f"   총 {len(kospi_tickers)}개")
        print(f"   예시: {kospi_tickers[:5]}")
    except Exception as e:
        print(f"   오류: {e}")

    # 2. KOSDAQ 종목 수집
    print("\n2. KOSDAQ 종목 수:")
    try:
        kosdaq_tickers = stock.get_market_ticker_list(today, market="KOSDAQ")
        print(f"   총 {len(kosdaq_tickers)}개")
        print(f"   예시: {kosdaq_tickers[:5]}")
    except Exception as e:
        print(f"   오류: {e}")

    # 3. KONEX 종목 수집
    print("\n3. KONEX 종목 수:")
    try:
        konex_tickers = stock.get_market_ticker_list(today, market="KONEX")
        print(f"   총 {len(konex_tickers)}개")
        print(f"   예시: {konex_tickers[:5] if konex_tickers else 'N/A'}")
    except Exception as e:
        print(f"   오류: {e}")

    print("\n" + "=" * 60)

    # 전체 종목 수 계산
    total = len(kospi_tickers) + len(kosdaq_tickers) + len(konex_tickers if konex_tickers else [])
    print(f"전체 종목 수: {total}개")
    print("=" * 60)

if __name__ == "__main__":
    fetch_and_display_stocks()