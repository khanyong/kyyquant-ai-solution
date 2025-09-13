"""
NAS Docker 컨테이너에서 실행되는 키움 REST API 데이터 다운로더
user_api_keys 테이블에서 키 정보를 읽어와서 사용
키움 REST API → Supabase 저장
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from supabase import create_client, Client
import logging
from dotenv import load_dotenv

# 환경변수 로드 - 프로젝트 루트의 .env 파일
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KiwoomDataDownloaderWithDBKeys:
    """Supabase에서 키를 읽어오는 키움 데이터 다운로더"""

    def __init__(self, user_id: str = None):
        # Supabase 클라이언트 (관리자 키 사용)
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )

        # 사용자 ID (기본값: 첫 번째 사용자)
        self.user_id = user_id

        # 키움 API 설정 (DB에서 로드)
        self.app_key = None
        self.app_secret = None
        self.account_no = None
        self.is_demo = True

        # API URL
        self.base_url = 'https://openapi.kiwoom.com:9443'
        self.access_token = None
        self.token_expires_at = None

        # DB에서 API 키 로드
        self.load_api_keys_from_db()

        logger.info(f"키움 데이터 다운로더 초기화 (DB 키 사용)")
        logger.info(f"사용자 ID: {self.user_id}")
        logger.info(f"모드: {'모의투자' if self.is_demo else '실전투자'}")
        logger.info(f"API URL: {self.base_url}")

    def load_api_keys_from_db(self):
        """user_api_keys 테이블에서 키 정보 로드"""
        try:
            # 특정 사용자 ID가 없으면 키움 제공자의 첫 번째 키 사용
            if self.user_id:
                result = self.supabase.table('user_api_keys').select("*").eq('user_id', self.user_id).eq('provider', 'kiwoom').execute()
            else:
                result = self.supabase.table('user_api_keys').select("*").eq('provider', 'kiwoom').limit(1).execute()

            if result.data:
                key_info = result.data[0]
                self.user_id = key_info['user_id']
                self.app_key = key_info.get('api_key')
                self.app_secret = key_info.get('api_secret')
                self.account_no = key_info.get('account_number')

                # 추가 설정이 있다면 config에서 읽기
                config = key_info.get('config', {})
                if isinstance(config, str):
                    import json
                    config = json.loads(config)

                self.is_demo = config.get('is_demo', True)

                logger.info(f"✅ DB에서 API 키 로드 성공")
                logger.info(f"   앱키: {self.app_key[:20]}..." if self.app_key else "   앱키: 없음")
                logger.info(f"   계좌: {self.account_no}" if self.account_no else "   계좌: 없음")
            else:
                logger.error("❌ DB에서 키움 API 키를 찾을 수 없습니다")
                logger.error("   user_api_keys 테이블에 키움 설정을 추가하세요")
                # 환경변수 대체 사용
                self.load_keys_from_env()

        except Exception as e:
            logger.error(f"DB 키 로드 오류: {e}")
            # 환경변수 대체 사용
            self.load_keys_from_env()

    def load_keys_from_env(self):
        """환경변수에서 키 로드 (백업)"""
        logger.info("환경변수에서 키 로드 중...")
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

    def get_access_token(self) -> Optional[str]:
        """액세스 토큰 발급"""
        if not self.app_key or not self.app_secret:
            logger.error("API 키 또는 시크릿이 없습니다")
            return None

        # 기존 토큰이 유효하면 재사용
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        logger.info("새 액세스 토큰 발급 중...")

        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        try:
            # SSL 검증 비활성화 (NAS 환경)
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=30,
                verify=False
            )

            logger.info(f"토큰 요청 응답: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 86400)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                logger.info("✅ 토큰 발급 성공")
                return self.access_token
            else:
                logger.error(f"토큰 발급 실패: {response.text}")
                return None

        except requests.exceptions.ConnectTimeout:
            logger.error("연결 시간 초과 - 네트워크 확인 필요")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"연결 오류: {e}")
            # 대체 URL 시도
            logger.info("대체 URL로 재시도...")
            return self.try_alternative_urls()
        except Exception as e:
            logger.error(f"토큰 발급 오류: {e}")

        return None

    def try_alternative_urls(self) -> Optional[str]:
        """대체 URL 시도"""
        alternative_urls = [
            'http://openapi.kiwoom.com:8080',  # HTTP
            'https://openapi.kiwoom.com:8443',  # 다른 포트
        ]

        for alt_url in alternative_urls:
            logger.info(f"대체 URL 시도: {alt_url}")
            try:
                url = f"{alt_url}/oauth2/token"
                response = requests.post(
                    url,
                    data={
                        "grant_type": "client_credentials",
                        "appkey": self.app_key,
                        "appsecret": self.app_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10,
                    verify=False
                )

                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data['access_token']
                    self.base_url = alt_url  # 성공한 URL로 변경
                    logger.info(f"✅ 대체 URL 성공: {alt_url}")
                    return self.access_token

            except Exception as e:
                logger.error(f"대체 URL 실패: {e}")

        return None

    def get_current_price(self, stock_code: str) -> Optional[Dict]:
        """현재가 조회"""
        token = self.get_access_token()
        if not token:
            logger.error("토큰 없음")
            return None

        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"

        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "VHKST01010100" if self.is_demo else "FHKST01010100"
        }

        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stock_code
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('rt_cd') == '0':
                    output = data['output']
                    return {
                        'stock_code': stock_code,
                        'current_price': int(output.get('stck_prpr', 0)),
                        'change_price': int(output.get('prdy_vrss', 0)),
                        'change_rate': float(output.get('prdy_ctrt', 0)),
                        'volume': int(output.get('acml_vol', 0)),
                        'trading_value': int(output.get('acml_tr_pbmn', 0)),
                        'high_52w': int(output.get('stck_mxpr', 0)),
                        'low_52w': int(output.get('stck_llam', 0)),
                        'market_cap': 0,
                        'shares_outstanding': 0,
                        'foreign_ratio': 0.0,
                        'updated_at': datetime.now().isoformat()
                    }

        except Exception as e:
            logger.error(f"현재가 조회 오류: {e}")

        return None

    def save_to_supabase(self, table: str, data: Dict) -> bool:
        """Supabase에 데이터 저장"""
        try:
            self.supabase.table(table).upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 저장 오류: {e}")
            return False

    def download_and_save(self, stock_codes: List[str]):
        """주가 데이터 다운로드 및 저장"""
        logger.info(f"종목 다운로드 시작: {stock_codes}")

        for code in stock_codes:
            logger.info(f"\n{code} 처리 중...")

            # 현재가 조회
            price_data = self.get_current_price(code)

            if price_data:
                # Supabase에 저장
                if self.save_to_supabase('kw_price_current', price_data):
                    logger.info(f"✅ {code} 저장 완료: {price_data['current_price']:,}원")
                else:
                    logger.error(f"❌ {code} 저장 실패")
            else:
                logger.error(f"❌ {code} 데이터 조회 실패")

            # API 호출 제한 대응
            time.sleep(0.5)

def main():
    """메인 함수"""
    downloader = KiwoomDataDownloaderWithDBKeys()

    # 테스트용 종목
    test_stocks = ['005930', '000660', '035720']  # 삼성전자, SK하이닉스, 카카오

    # 데이터 다운로드
    downloader.download_and_save(test_stocks)

    logger.info("\n✅ 다운로드 완료")

if __name__ == "__main__":
    main()