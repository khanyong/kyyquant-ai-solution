"""
백테스트용 과거 데이터 다운로더
기간을 설정하면 해당 기간의 일봉 데이터를 다운로드
"""

import requests
import json
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def download_historical_data(stock_codes, start_date, end_date):
    """
    지정된 기간의 과거 일봉 데이터 다운로드

    Args:
        stock_codes: 종목코드 리스트 (예: ['005930', '000660'])
        start_date: 시작일 (예: '2024-01-01')
        end_date: 종료일 (예: '2024-12-31')
    """

    # Configuration
    nas_url = "http://192.168.50.150:8080"

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("백테스트용 과거 데이터 다운로드")
    print(f"기간: {start_date} ~ {end_date}")
    print(f"종목: {len(stock_codes)}개")
    print("=" * 60)

    total_saved = 0

    for stock_code in stock_codes:
        print(f"\n종목 {stock_code} 처리 중...")

        # NAS 서버의 일봉 데이터 API 호출
        response = requests.post(
            f"{nas_url}/api/market/daily-price",
            json={
                "stock_code": stock_code,
                "start_date": start_date,
                "end_date": end_date,
                "period": "D"  # Daily
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('success') and data.get('data'):
                daily_data = data['data']
                print(f"  {len(daily_data)}일치 데이터 수신")

                # 각 일자별 데이터를 kw_price_daily 테이블에 저장
                saved_count = 0
                for day_data in daily_data:
                    try:
                        # 데이터 변환
                        price_record = {
                            'stock_code': stock_code,
                            'date': day_data.get('date'),
                            'open': float(day_data.get('open', 0)),
                            'high': float(day_data.get('high', 0)),
                            'low': float(day_data.get('low', 0)),
                            'close': float(day_data.get('close', 0)),
                            'volume': int(day_data.get('volume', 0)),
                            'trading_value': int(day_data.get('trading_value', 0)),
                            'created_at': datetime.now().isoformat()
                        }

                        # Supabase에 저장 (upsert로 중복 방지)
                        result = supabase.table('kw_price_daily').upsert(price_record).execute()
                        saved_count += 1

                    except Exception as e:
                        print(f"    날짜 {day_data.get('date')} 저장 실패: {e}")

                print(f"  ✅ {saved_count}일치 데이터 저장 완료")
                total_saved += saved_count

            else:
                print(f"  ❌ 데이터 없음: {data.get('message', '알 수 없는 오류')}")
        else:
            print(f"  ❌ API 오류: {response.status_code}")

        # API 호출 제한 대응
        time.sleep(1)

    print(f"\n" + "=" * 60)
    print(f"✅ 전체 완료: {total_saved}건 저장")
    print("=" * 60)

    return total_saved

def download_backtest_period(strategy_name, start_date, end_date, stock_codes=None):
    """
    백테스트 전용 기간 데이터 다운로드

    Args:
        strategy_name: 전략명 (로그용)
        start_date: 백테스트 시작일
        end_date: 백테스트 종료일
        stock_codes: 종목 리스트 (None이면 기본 종목 사용)
    """

    if stock_codes is None:
        # 기본 백테스트 종목들
        stock_codes = [
            '005930',  # 삼성전자
            '000660',  # SK하이닉스
            '035720',  # 카카오
            '207940',  # 삼성바이오로직스
            '006400',  # 삼성SDI
            '051910',  # LG화학
            '028260',  # 삼성물산
            '012330',  # 현대모비스
            '096770',  # SK이노베이션
            '068270'   # 셀트리온
        ]

    print(f"전략 '{strategy_name}' 백테스트용 데이터 준비")
    print(f"대상 종목: {len(stock_codes)}개")

    return download_historical_data(stock_codes, start_date, end_date)

def main():
    """메인 함수 - 테스트 실행"""

    # 백테스트 예시: 2024년 1년간 데이터
    result = download_backtest_period(
        strategy_name="RSI 전략 테스트",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    print(f"\n백테스트 데이터 준비 완료: {result}건")

if __name__ == "__main__":
    main()