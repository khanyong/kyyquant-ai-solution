"""
과거 일별 주가 데이터 다운로드
pykrx를 사용하여 과거 OHLCV 데이터를 다운로드하여 kw_price_daily 테이블에 저장
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

def check_existing_data(supabase, stock_code, start_date=None):
    """기존 데이터 확인 - 첫 날짜와 마지막 날짜 반환"""
    try:
        # 가장 오래된 날짜 확인
        first_result = supabase.table('kw_price_daily').select('trade_date').eq(
            'stock_code', stock_code
        ).order('trade_date').limit(1).execute()

        # 가장 최근 날짜 확인
        last_result = supabase.table('kw_price_daily').select('trade_date').eq(
            'stock_code', stock_code
        ).order('trade_date', desc=True).limit(1).execute()

        first_date = None
        last_date = None

        if first_result.data and len(first_result.data) > 0:
            first_date = datetime.strptime(first_result.data[0]['trade_date'], '%Y-%m-%d')

        if last_result.data and len(last_result.data) > 0:
            last_date = datetime.strptime(last_result.data[0]['trade_date'], '%Y-%m-%d')

        return first_date, last_date
    except Exception as e:
        print(f"    데이터 확인 실패: {e}")
        return None, None

def download_stock_history(stock_code, stock_name, start_date, end_date, supabase):
    """단일 종목 과거 데이터 다운로드"""
    try:
        # 기존 데이터 확인
        first_date, last_date = check_existing_data(supabase, stock_code)

        # 다운로드할 기간 결정
        download_start = start_date
        download_end = end_date

        if first_date and last_date:
            # 기존 데이터가 있는 경우
            if start_date >= first_date and end_date <= last_date:
                # 요청한 전체 기간이 이미 있음
                print(f"    이미 데이터 존재 ({first_date.strftime('%Y-%m-%d')} ~ {last_date.strftime('%Y-%m-%d')})")
                return 0
            elif start_date < first_date:
                # 더 과거 데이터가 필요한 경우
                download_end = first_date - timedelta(days=1)
                print(f"    과거 데이터 추가 다운로드 ({download_start.strftime('%Y-%m-%d')} ~ {download_end.strftime('%Y-%m-%d')})")
            elif end_date > last_date:
                # 더 최근 데이터가 필요한 경우
                download_start = last_date + timedelta(days=1)
                print(f"    최신 데이터 추가 다운로드 ({download_start.strftime('%Y-%m-%d')} ~ {download_end.strftime('%Y-%m-%d')})")

        if download_start > download_end:
            print(f"    다운로드할 데이터 없음")
            return 0

        # pykrx로 데이터 다운로드
        df = stock.get_market_ohlcv_by_date(
            download_start.strftime('%Y%m%d'),
            download_end.strftime('%Y%m%d'),
            stock_code
        )

        if df.empty:
            print(f"    데이터 없음")
            return 0

        # 데이터 준비
        records = []
        for date, row in df.iterrows():
            record = {
                'stock_code': stock_code,
                'trade_date': date.strftime('%Y-%m-%d'),
                'open': int(row['시가']),
                'high': int(row['고가']),
                'low': int(row['저가']),
                'close': int(row['종가']),
                'volume': int(row['거래량']),
                'trading_value': int(row['거래대금']) if '거래대금' in row else 0
            }
            records.append(record)

        # Supabase에 저장
        if records:
            # 배치로 삽입 (충돌 시 무시)
            for batch in [records[i:i+100] for i in range(0, len(records), 100)]:
                result = supabase.table('kw_price_daily').upsert(batch).execute()

            print(f"    {len(records)}개 레코드 저장 완료")
            return len(records)

        return 0

    except Exception as e:
        print(f"    오류 발생: {e}")
        return -1

def save_progress(stock_code, status='completed'):
    """진행 상황 저장"""
    progress_file = 'download_progress.txt'
    with open(progress_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()},{stock_code},{status}\n")

def load_completed_stocks():
    """완료된 종목 목록 로드"""
    progress_file = 'download_progress.txt'
    completed = set()
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3 and parts[2] == 'completed':
                    completed.add(parts[1])
    return completed

def download_all_historical_data(days=365, test_mode=False, resume=True):
    """전체 종목 과거 데이터 다운로드

    Args:
        days: 다운로드할 과거 일수 (기본 365일)
        test_mode: True면 주요 종목 10개만 테스트
        resume: True면 이전 진행상황에서 재시작
    """

    # Supabase 클라이언트
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("과거 일별 주가 데이터 다운로드")
    print("=" * 60)

    # 날짜 범위 설정
    # DB의 가장 오래된 데이터와 연결되도록 설정
    # 현재 DB: 2024-09-14 ~ 2025-09-12
    # 목표: 그 이전 데이터 다운로드
    end_date = datetime(2024, 9, 13)  # DB 데이터 시작일 하루 전
    start_date = end_date - timedelta(days=days)

    print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print(f"일수: {days}일")

    # 종목 리스트
    if test_mode:
        # 테스트 모드: 주요 종목만
        stocks = [
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
        print(f"\n[테스트 모드] {len(stocks)}개 종목만 다운로드")
    else:
        # 전체 모드: KOSPI 200 + KOSDAQ 150
        print("\n종목 리스트 가져오기...")
        try:
            # KOSPI200
            kospi200 = stock.get_index_portfolio_deposit_file("1028")  # KOSPI200 코드
            kospi_list = [(code, stock.get_market_ticker_name(code)) for code in kospi200]

            # KOSDAQ150
            kosdaq150 = stock.get_index_portfolio_deposit_file("2203")  # KOSDAQ150 코드
            kosdaq_list = [(code, stock.get_market_ticker_name(code)) for code in kosdaq150]

            stocks = kospi_list[:100] + kosdaq_list[:50]  # 상위 150개만
            print(f"총 {len(stocks)}개 종목 (KOSPI {len(kospi_list[:100])}, KOSDAQ {len(kosdaq_list[:50])})")
        except:
            # 실패 시 기본 종목만
            stocks = [
                ('005930', '삼성전자'),
                ('000660', 'SK하이닉스'),
                ('035720', '카카오'),
                ('005380', '현대차'),
                ('051910', 'LG화학')
            ]
            print(f"종목 리스트 가져오기 실패. 기본 {len(stocks)}개 종목만 다운로드")

    # 재시작 기능
    completed_stocks = set()
    if resume:
        completed_stocks = load_completed_stocks()
        if completed_stocks:
            print(f"\n[재시작 모드] 이미 완료된 종목 {len(completed_stocks)}개 건너뜀")

    # 다운로드 시작
    print("\n다운로드 시작...")
    print("-" * 40)

    total_records = 0
    success_count = 0
    fail_count = 0
    skip_count = 0

    start_time = datetime.now()

    for i, (code, name) in enumerate(stocks, 1):
        # 이미 완료된 종목은 건너뜀
        if code in completed_stocks:
            print(f"\n[{i}/{len(stocks)}] {name} ({code}) - 이미 완료됨, 건너뜀")
            skip_count += 1
            continue

        print(f"\n[{i}/{len(stocks)}] {name} ({code})")

        try:
            result = download_stock_history(code, name, start_date, end_date, supabase)

            if result > 0:
                success_count += 1
                total_records += result
                save_progress(code, 'completed')
            elif result == 0:
                skip_count += 1
                save_progress(code, 'skipped')
            else:
                fail_count += 1
                save_progress(code, 'failed')

        except KeyboardInterrupt:
            print("\n\n사용자가 중단했습니다. 진행 상황이 저장되었습니다.")
            print("다시 실행하면 중단된 지점부터 계속됩니다.")
            break
        except Exception as e:
            print(f"    예외 발생: {e}")
            fail_count += 1
            save_progress(code, 'error')

        # API 제한 방지 (0.5초 대기)
        time.sleep(0.5)

        # 진행 상황 표시 (10개마다)
        if i % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (len(stocks) - i) / rate if rate > 0 else 0
            print(f"\n진행: {i}/{len(stocks)} - 예상 남은 시간: {int(remaining//60)}분 {int(remaining%60)}초")

    # 최종 결과
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("다운로드 완료!")
    print(f"  처리 종목: {len(stocks)}개")
    print(f"  성공: {success_count}개")
    print(f"  스킵: {skip_count}개")
    print(f"  실패: {fail_count}개")
    print(f"  총 레코드: {total_records:,}개")
    print(f"  소요 시간: {int(total_time//60)}분 {int(total_time%60)}초")
    print("=" * 60)

    # 테이블 확인
    try:
        result = supabase.table('kw_price_daily').select('stock_code', count='exact').execute()
        total_in_db = result.count if hasattr(result, 'count') else 0
        print(f"\nkw_price_daily 테이블 총 레코드 수: {total_in_db:,}개")
    except Exception as e:
        print(f"\n테이블 확인 실패: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='과거 일별 주가 데이터 다운로드')
    parser.add_argument('--days', type=int, default=365, help='다운로드할 과거 일수 (기본: 365)')
    parser.add_argument('--test', action='store_true', help='테스트 모드 (10개 종목만)')
    parser.add_argument('--no-resume', action='store_true', help='처음부터 다시 시작 (진행상황 무시)')
    parser.add_argument('--reset', action='store_true', help='진행상황 파일 삭제 후 시작')

    args = parser.parse_args()

    # 진행상황 초기화
    if args.reset:
        progress_file = 'download_progress.txt'
        if os.path.exists(progress_file):
            os.remove(progress_file)
            print(f"진행상황 파일 삭제됨: {progress_file}")

    download_all_historical_data(
        days=args.days,
        test_mode=args.test,
        resume=not args.no_resume
    )