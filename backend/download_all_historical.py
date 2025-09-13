"""
전체 종목 과거 데이터 통일 다운로드
모든 종목에 대해 동일한 기간의 데이터를 다운로드
"""

import os
import sys
from datetime import datetime, timedelta
import time
import pandas as pd
from pykrx import stock
from supabase import create_client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def download_all_stocks_unified(start_date, end_date, limit=None):
    """모든 종목에 대해 동일 기간 데이터 다운로드

    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        limit: 다운로드할 종목 수 제한
    """

    # Supabase 클라이언트
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("전체 종목 통일 기간 다운로드")
    print("=" * 60)
    print(f"기간: {start_date} ~ {end_date}")

    # 날짜 변환
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = (end_dt - start_dt).days
    print(f"일수: {days}일")

    # 종목 리스트 가져오기
    print("\n종목 리스트 가져오기...")

    try:
        # KOSPI 전체
        kospi_codes = stock.get_market_ticker_list(market="KOSPI")
        print(f"KOSPI 종목 수: {len(kospi_codes)}개")
        kospi_stocks = [(code, stock.get_market_ticker_name(code)) for code in kospi_codes]  # 전체

        # KOSDAQ 전체
        kosdaq_codes = stock.get_market_ticker_list(market="KOSDAQ")
        print(f"KOSDAQ 종목 수: {len(kosdaq_codes)}개")
        kosdaq_stocks = [(code, stock.get_market_ticker_name(code)) for code in kosdaq_codes]  # 전체

        all_stocks = kospi_stocks + kosdaq_stocks

        if limit:
            all_stocks = all_stocks[:limit]

        print(f"총 {len(all_stocks)}개 종목")

    except Exception as e:
        print(f"종목 리스트 가져오기 실패: {e}")
        # 기본 종목 사용
        all_stocks = [
            ('005930', '삼성전자'),
            ('000660', 'SK하이닉스'),
            ('035720', '카카오'),
            ('005380', '현대차'),
            ('051910', 'LG화학'),
            ('006400', '삼성SDI'),
            ('035420', 'NAVER'),
            ('068270', '셀트리온'),
            ('105560', 'KB금융'),
            ('055550', '신한지주')
        ]

    # 기존 데이터 삭제 옵션
    delete_existing = input("\n기존 데이터를 삭제하고 새로 다운로드하시겠습니까? (y/n): ").lower() == 'y'

    if delete_existing:
        print("\n기존 데이터 삭제 중...")
        for code, name in all_stocks:
            try:
                supabase.table('kw_price_daily').delete().eq('stock_code', code).gte(
                    'trade_date', start_date
                ).lte('trade_date', end_date).execute()
            except:
                pass
        print("삭제 완료")

    # 다운로드 시작
    print("\n다운로드 시작...")
    print("-" * 40)

    success_count = 0
    fail_count = 0
    total_records = 0
    start_time = datetime.now()

    for i, (code, name) in enumerate(all_stocks, 1):
        print(f"\n[{i}/{len(all_stocks)}] {name} ({code})")

        try:
            # pykrx로 데이터 다운로드
            df = stock.get_market_ohlcv_by_date(
                start_dt.strftime('%Y%m%d'),
                end_dt.strftime('%Y%m%d'),
                code
            )

            if df.empty:
                print(f"    데이터 없음")
                fail_count += 1
                continue

            # 데이터 준비
            records = []
            for date, row in df.iterrows():
                record = {
                    'stock_code': code,
                    'trade_date': date.strftime('%Y-%m-%d'),
                    'open': int(row['시가']),
                    'high': int(row['고가']),
                    'low': int(row['저가']),
                    'close': int(row['종가']),
                    'volume': int(row['거래량']),
                    'trading_value': int(row['거래대금']) if '거래대금' in row else 0
                }
                records.append(record)

            # Supabase에 저장 (upsert)
            if records:
                for batch in [records[i:i+100] for i in range(0, len(records), 100)]:
                    supabase.table('kw_price_daily').upsert(batch).execute()

                print(f"    {len(records)}개 레코드 저장 완료")
                success_count += 1
                total_records += len(records)

        except Exception as e:
            print(f"    오류: {e}")
            fail_count += 1

        # API 제한 방지
        time.sleep(0.5)

        # 진행 상황 (10개마다)
        if i % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (len(all_stocks) - i) / rate if rate > 0 else 0
            print(f"\n진행: {i}/{len(all_stocks)} - 남은 시간: {int(remaining//60)}분 {int(remaining%60)}초")

    # 완료
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("다운로드 완료!")
    print(f"  성공: {success_count}개 종목")
    print(f"  실패: {fail_count}개 종목")
    print(f"  총 레코드: {total_records:,}개")
    print(f"  소요 시간: {int(total_time//60)}분 {int(total_time%60)}초")
    print("=" * 60)

    # DB 확인
    try:
        result = supabase.table('kw_price_daily').select('stock_code', count='exact').eq(
            'trade_date', end_date
        ).execute()
        count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
        print(f"\n{end_date} 기준 데이터 있는 종목 수: {count}개")
    except Exception as e:
        print(f"\nDB 확인 실패: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='전체 종목 통일 기간 다운로드')
    parser.add_argument('--start', default='2023-09-14', help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--end', default='2024-09-13', help='종료 날짜 (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, help='다운로드할 종목 수 제한')

    args = parser.parse_args()

    download_all_stocks_unified(args.start, args.end, args.limit)