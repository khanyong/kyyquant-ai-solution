"""
일봉 데이터 업데이트 스크립트
키움 REST API에서 일봉 데이터를 가져와 kw_price_daily 테이블에 저장

사용법:
  python update_daily_prices.py --stock 005930
  python update_daily_prices.py --stock 005930,000660,035720  # 여러 종목
  python update_daily_prices.py --all  # 모든 관심 종목
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import argparse

# 키움 API 클라이언트 임포트
sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()


def get_supabase_client():
    """Supabase 클라이언트 생성"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    return create_client(url, key)


def update_stock_daily_prices(stock_code: str, days: int = 100):
    """
    특정 종목의 일봉 데이터 업데이트

    Args:
        stock_code: 종목코드 (예: "005930")
        days: 가져올 일수 (기본 100일)
    """
    print(f"\n[{stock_code}] 일봉 데이터 업데이트 시작...")

    try:
        # 키움 API 클라이언트
        kiwoom = get_kiwoom_client()
        supabase = get_supabase_client()

        # 일봉 데이터 조회
        print(f"  키움 API에서 {days}일치 데이터 조회 중...")
        daily_data = kiwoom.get_historical_price(stock_code, period=days)

        if not daily_data:
            print(f"  [WARNING] 데이터 없음")
            return 0

        print(f"  {len(daily_data)}개 데이터 수신")

        # 데이터 변환 및 저장
        inserted = 0
        updated = 0

        for item in daily_data:
            # 날짜 파싱
            trade_date = item.get('stck_bsop_date')  # YYYYMMDD
            if not trade_date or len(trade_date) != 8:
                continue

            formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"

            # 데이터 준비
            price_record = {
                'stock_code': stock_code,
                'trade_date': formatted_date,
                'open': float(item.get('stck_oprc', 0)),
                'high': float(item.get('stck_hgpr', 0)),
                'low': float(item.get('stck_lwpr', 0)),
                'close': float(item.get('stck_clpr', 0)),
                'volume': int(item.get('acml_vol', 0)),
                'change_rate': float(item.get('prdy_ctrt', 0))
            }

            # Upsert (있으면 업데이트, 없으면 삽입)
            result = supabase.table('kw_price_daily') \
                .upsert(price_record, on_conflict='stock_code,trade_date') \
                .execute()

            if result.data:
                inserted += 1

        print(f"  [OK] 완료: {inserted}개 레코드 저장")
        return inserted

    except Exception as e:
        print(f"  [ERROR] 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def get_active_stocks():
    """활성 전략의 대상 종목 조회"""
    try:
        supabase = get_supabase_client()

        # 활성 전략 조회
        result = supabase.table('strategies') \
            .select('target_stocks') \
            .eq('is_active', True) \
            .execute()

        # 종목 코드 추출 (중복 제거)
        stock_codes = set()
        for strategy in result.data:
            targets = strategy.get('target_stocks', [])
            if isinstance(targets, list):
                stock_codes.update(targets)

        return list(stock_codes)

    except Exception as e:
        print(f"활성 종목 조회 실패: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description='키움 일봉 데이터 업데이트')
    parser.add_argument('--stock', help='종목코드 (쉼표로 구분)', default=None)
    parser.add_argument('--all', action='store_true', help='모든 활성 전략 종목')
    parser.add_argument('--days', type=int, default=100, help='조회 기간 (일)')

    args = parser.parse_args()

    print("=" * 60)
    print("키움 일봉 데이터 업데이트")
    print("=" * 60)

    # 종목 목록 결정
    stock_codes = []

    if args.all:
        print("활성 전략의 모든 종목 업데이트...")
        stock_codes = get_active_stocks()
        if not stock_codes:
            print("활성 종목이 없습니다. 기본 종목 사용")
            stock_codes = ['005930']  # 삼성전자
    elif args.stock:
        stock_codes = [s.strip() for s in args.stock.split(',')]
    else:
        # 기본값: 삼성전자
        stock_codes = ['005930']

    print(f"업데이트 대상: {', '.join(stock_codes)}")
    print(f"조회 기간: 최근 {args.days}일")
    print()

    # 각 종목별로 업데이트
    total_inserted = 0
    for stock_code in stock_codes:
        inserted = update_stock_daily_prices(stock_code, args.days)
        total_inserted += inserted

    print()
    print("=" * 60)
    print(f"완료: 총 {total_inserted}개 레코드 저장")
    print("=" * 60)


if __name__ == "__main__":
    main()
