"""
키움증권 REST API를 통한 주가 데이터 다운로드
Supabase user_api_keys 테이블에서 API 키 로드
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# 상위 디렉토리 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rest_api.kiwoom_rest_impl import KiwoomRestAPI

load_dotenv()

class StockDataDownloader:
    """REST API 기반 주가 데이터 다운로더"""

    def __init__(self):
        # Supabase 클라이언트
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

        # API 키 로드
        self.api_keys = self.load_api_keys()

        # Kiwoom REST API 초기화
        self.kiwoom = KiwoomRestAPI()

        # API 키 설정
        if self.api_keys:
            self.kiwoom.app_key = self.api_keys.get('app_key')
            self.kiwoom.app_secret = self.api_keys.get('app_secret')
            self.kiwoom.account_no = self.api_keys.get('account_no')
            print(f"✅ API 키 로드 완료")
        else:
            print("❌ API 키를 찾을 수 없습니다. Supabase user_api_keys 테이블을 확인하세요.")
            sys.exit(1)

    def load_api_keys(self) -> Optional[Dict]:
        """Supabase에서 키움 API 키 로드"""
        try:
            # user_api_keys 테이블에서 키움 API 정보 조회
            response = self.supabase.table('user_api_keys').select("*").eq('provider', 'kiwoom').execute()

            if response.data and len(response.data) > 0:
                # 여러 행에서 키 정보 수집
                app_key = None
                app_secret = None
                account_no = None

                for row in response.data:
                    # key_type 필드로 구분
                    key_type = row.get('key_type', '')
                    if 'app_secret' in key_type or 'secret' in key_type.lower():
                        app_secret = row.get('encrypted_value') or row.get('key_name')
                    elif 'app_key' in key_type or 'app' in key_type.lower():
                        app_key = row.get('encrypted_value') or row.get('key_name')
                    elif 'account' in key_type.lower():
                        account_no = row.get('encrypted_value') or row.get('key_name')

                # 환경변수에서 누락된 값 보충
                if not app_key:
                    app_key = os.getenv('KIWOOM_APP_KEY')
                if not app_secret:
                    app_secret = os.getenv('KIWOOM_APP_SECRET')
                if not account_no:
                    account_no = os.getenv('KIWOOM_ACCOUNT_NO')

                return {
                    'app_key': app_key,
                    'app_secret': app_secret,
                    'account_no': account_no
                }
            else:
                # 대체 방법: 환경변수에서 직접 로드
                return {
                    'app_key': os.getenv('KIWOOM_APP_KEY'),
                    'app_secret': os.getenv('KIWOOM_APP_SECRET'),
                    'account_no': os.getenv('KIWOOM_ACCOUNT_NO')
                }

        except Exception as e:
            print(f"API 키 로드 오류: {e}")
            return None

    async def download_stock_list(self, limit: Optional[int] = None) -> List[Dict]:
        """종목 리스트 다운로드

        Args:
            limit: 다운로드할 종목 수 제한 (None이면 전체)
        """
        print("\n📋 종목 리스트 다운로드 중...")

        # Supabase에서 전체 종목 리스트 조회
        try:
            # 이미 저장된 종목 리스트 조회
            query = self.supabase.table('kw_stock_master').select("*")
            if limit:
                query = query.limit(limit)

            response = query.execute()

            if response.data and len(response.data) > 0:
                stocks = [
                    {
                        'code': item['stock_code'],
                        'name': item['stock_name'],
                        'market': item.get('market', 'KOSPI')
                    }
                    for item in response.data
                ]
                print(f"  ✅ 기존 종목 {len(stocks)}개 로드")
                return stocks

        except Exception as e:
            print(f"  ⚠️ 기존 종목 로드 실패: {e}")

        # 기본 종목 리스트 (최소한의 주요 종목)
        # 실제로는 키움 OpenAPI를 통해 전체 종목을 가져와야 함
        default_stocks = [
            {'code': '005930', 'name': '삼성전자', 'market': 'KOSPI'},
            {'code': '000660', 'name': 'SK하이닉스', 'market': 'KOSPI'},
            {'code': '035720', 'name': '카카오', 'market': 'KOSPI'},
            {'code': '035420', 'name': 'NAVER', 'market': 'KOSPI'},
            {'code': '051910', 'name': 'LG화학', 'market': 'KOSPI'},
            {'code': '006400', 'name': '삼성SDI', 'market': 'KOSPI'},
            {'code': '005380', 'name': '현대차', 'market': 'KOSPI'},
            {'code': '000270', 'name': '기아', 'market': 'KOSPI'},
            {'code': '068270', 'name': '셀트리온', 'market': 'KOSPI'},
            {'code': '105560', 'name': 'KB금융', 'market': 'KOSPI'},
            {'code': '207940', 'name': '삼성바이오로직스', 'market': 'KOSPI'},
            {'code': '005490', 'name': 'POSCO홀딩스', 'market': 'KOSPI'},
            {'code': '012330', 'name': '현대모비스', 'market': 'KOSPI'},
            {'code': '066570', 'name': 'LG전자', 'market': 'KOSPI'},
            {'code': '096770', 'name': 'SK이노베이션', 'market': 'KOSPI'},
            {'code': '028260', 'name': '삼성물산', 'market': 'KOSPI'},
            {'code': '034730', 'name': 'SK', 'market': 'KOSPI'},
            {'code': '003550', 'name': 'LG', 'market': 'KOSPI'},
            {'code': '017670', 'name': 'SK텔레콤', 'market': 'KOSPI'},
            {'code': '030200', 'name': 'KT', 'market': 'KOSPI'},
            {'code': '015760', 'name': '한국전력', 'market': 'KOSPI'},
            {'code': '352820', 'name': '하이브', 'market': 'KOSPI'},
            {'code': '086790', 'name': '하나금융지주', 'market': 'KOSPI'},
            {'code': '316140', 'name': '우리금융지주', 'market': 'KOSPI'},
            {'code': '055550', 'name': '신한지주', 'market': 'KOSPI'},
            {'code': '032830', 'name': '삼성생명', 'market': 'KOSPI'},
            {'code': '003490', 'name': '대한항공', 'market': 'KOSPI'},
            {'code': '010130', 'name': '고려아연', 'market': 'KOSPI'},
            {'code': '009150', 'name': '삼성전기', 'market': 'KOSPI'},
            {'code': '018260', 'name': '삼성에스디에스', 'market': 'KOSPI'}
        ]

        # limit 적용
        stocks_to_save = default_stocks[:limit] if limit else default_stocks

        # 종목 마스터 정보 저장
        saved_count = 0
        for stock in stocks_to_save:
            try:
                self.supabase.table('kw_stock_master').upsert({
                    'stock_code': stock['code'],
                    'stock_name': stock['name'],
                    'market': stock['market']
                }).execute()
                saved_count += 1
                if saved_count <= 10:  # 처음 10개만 출력
                    print(f"  ✅ {stock['name']} ({stock['code']}) 저장")
            except Exception as e:
                print(f"  ❌ {stock['name']} 저장 실패: {e}")

        if saved_count > 10:
            print(f"  ... 총 {saved_count}개 종목 저장 완료")

        return stocks_to_save

    async def download_price_data(self, stock_code: str, days: int = 365) -> pd.DataFrame:
        """일봉 가격 데이터 다운로드"""
        print(f"\n📈 {stock_code} 가격 데이터 다운로드 중...")

        # 기간 설정
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        # REST API로 OHLCV 데이터 조회
        ohlcv_data = await self.kiwoom.get_ohlcv(stock_code, start_date, end_date)

        if ohlcv_data:
            df = pd.DataFrame(ohlcv_data)
            print(f"  ✅ {len(df)}일 데이터 다운로드 완료")

            # Supabase에 저장
            for _, row in df.iterrows():
                try:
                    self.supabase.table('kw_price_daily').upsert({
                        'stock_code': stock_code,
                        'trade_date': row['date'],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume']
                    }).execute()
                except Exception as e:
                    print(f"  ⚠️ {row['date']} 저장 실패: {e}")

            return df
        else:
            print(f"  ❌ 데이터 다운로드 실패")
            return pd.DataFrame()

    async def download_current_price(self, stock_code: str) -> Dict:
        """현재가 다운로드"""
        print(f"\n💰 {stock_code} 현재가 조회 중...")

        price_data = await self.kiwoom.get_current_price(stock_code)

        if price_data:
            # Supabase에 저장
            try:
                self.supabase.table('kw_price_current').upsert({
                    'stock_code': stock_code,
                    'current_price': price_data.price,
                    'change_price': price_data.change,
                    'change_rate': price_data.change_rate,
                    'volume': price_data.volume,
                    'high': price_data.high,
                    'low': price_data.low,
                    'open': price_data.open,
                    'updated_at': datetime.now().isoformat()
                }).execute()

                print(f"  ✅ 현재가: {price_data.price:,}원 ({price_data.change_rate:+.2f}%)")
                return price_data.__dict__
            except Exception as e:
                print(f"  ❌ 현재가 저장 실패: {e}")

        return {}

    async def run_complete_download(self, stock_codes: List[str] = None, limit: int = None):
        """전체 데이터 다운로드 실행

        Args:
            stock_codes: 특정 종목 코드 리스트 (None이면 전체)
            limit: 다운로드할 종목 수 제한
        """
        print("\n" + "="*60)
        print("🚀 키움증권 REST API 데이터 다운로드 시작")
        print("="*60)

        # API 연결
        connected = await self.kiwoom.connect()
        if not connected:
            print("❌ API 연결 실패")
            return

        # 종목 리스트 결정
        if stock_codes:
            # 특정 종목만 다운로드
            stocks = []
            for code in stock_codes:
                # Supabase에서 종목명 조회
                try:
                    response = self.supabase.table('kw_stock_master').select("*").eq('stock_code', code).execute()
                    if response.data:
                        stocks.append({
                            'code': code,
                            'name': response.data[0]['stock_name'],
                            'market': response.data[0].get('market', 'KOSPI')
                        })
                    else:
                        # 종목명을 모르면 코드만으로 진행
                        stocks.append({
                            'code': code,
                            'name': code,
                            'market': 'KOSPI'
                        })
                except:
                    stocks.append({
                        'code': code,
                        'name': code,
                        'market': 'KOSPI'
                    })
            print(f"📌 지정된 {len(stocks)}개 종목 다운로드")
        else:
            # 전체 또는 제한된 수의 종목 다운로드
            stocks = await self.download_stock_list(limit=limit)

        print(f"\n총 {len(stocks)}개 종목 처리 예정")

        # 각 종목별 데이터 다운로드
        for idx, stock in enumerate(stocks, 1):
            code = stock['code']
            name = stock['name']

            print(f"\n{'='*40}")
            print(f"📊 [{idx}/{len(stocks)}] {name} ({code}) 처리 중...")
            print(f"{'='*40}")

            # 일봉 데이터 다운로드
            await self.download_price_data(code, days=365)

            # API 호출 제한 대응 (초당 5회)
            await asyncio.sleep(0.3)

            # 현재가 다운로드
            await self.download_current_price(code)

            # API 호출 제한 대응
            await asyncio.sleep(0.3)

        # 연결 해제
        await self.kiwoom.disconnect()

        print("\n" + "="*60)
        print("✅ 데이터 다운로드 완료!")
        print("="*60)

        # 통계 출력
        self.print_statistics()

    def print_statistics(self):
        """다운로드 통계 출력"""
        print("\n📊 다운로드 통계:")

        try:
            # 종목 수
            result = self.supabase.table('kw_stock_master').select("count", count='exact').execute()
            print(f"  - 종목 마스터: {result.count}개")

            # 일봉 데이터
            result = self.supabase.table('kw_price_daily').select("count", count='exact').execute()
            print(f"  - 일봉 데이터: {result.count}개")

            # 현재가
            result = self.supabase.table('kw_price_current').select("count", count='exact').execute()
            print(f"  - 현재가: {result.count}개")

        except Exception as e:
            print(f"  ❌ 통계 조회 실패: {e}")

async def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='키움증권 REST API 데이터 다운로드')
    parser.add_argument('--codes', type=str, help='특정 종목 코드 (쉼표로 구분, 예: 005930,000660,035720)')
    parser.add_argument('--limit', type=int, help='다운로드할 종목 수 제한')
    parser.add_argument('--all', action='store_true', help='전체 종목 다운로드 (주의: 시간이 오래 걸림)')

    args = parser.parse_args()

    downloader = StockDataDownloader()

    # 종목 코드 파싱
    stock_codes = None
    if args.codes:
        stock_codes = [code.strip() for code in args.codes.split(',')]
        print(f"🎯 지정 종목 다운로드: {stock_codes}")
    elif args.all:
        print("📊 전체 종목 다운로드 모드")
        limit = None
    else:
        # 기본: 상위 30개 종목만
        limit = args.limit if args.limit else 30
        print(f"📊 상위 {limit}개 종목 다운로드")

    await downloader.run_complete_download(stock_codes=stock_codes, limit=args.limit if not args.all else None)

if __name__ == "__main__":
    # Windows 환경에서 이벤트 루프 정책 설정
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 비동기 실행
    asyncio.run(main())