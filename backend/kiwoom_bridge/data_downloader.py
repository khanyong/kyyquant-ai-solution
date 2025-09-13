"""
NAS Docker 컨테이너에서 실행되는 키움 REST API 데이터 다운로더
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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KiwoomDataDownloader:
    """NAS에서 실행되는 키움 데이터 다운로더"""

    def __init__(self):
        # Supabase 클라이언트
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

        # 키움 API 설정
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

        # API URL
        self.base_url = 'https://openapi.kiwoom.com:9443'
        self.access_token = None
        self.token_expires_at = None

        logger.info(f"키움 데이터 다운로더 초기화")
        logger.info(f"모드: {'모의투자' if self.is_demo else '실전투자'}")
        logger.info(f"API URL: {self.base_url}")

    def get_access_token(self) -> Optional[str]:
        """액세스 토큰 발급"""
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
                        'high': int(output.get('stck_hgpr', 0)),
                        'low': int(output.get('stck_lwpr', 0)),
                        'open': int(output.get('stck_oprc', 0))
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
                    logger.info(f"✅ {code} 저장 완료")
                else:
                    logger.error(f"❌ {code} 저장 실패")
            else:
                logger.error(f"❌ {code} 데이터 조회 실패")

            # API 호출 제한 대응
            time.sleep(0.5)

    def test_connection(self):
        """연결 테스트"""
        logger.info("\n" + "="*50)
        logger.info("키움 REST API 연결 테스트")
        logger.info("="*50)

        # 1. 네트워크 확인
        logger.info("\n1. 외부 네트워크 확인")
        try:
            response = requests.get("https://www.google.com", timeout=5)
            logger.info(f"   ✅ 인터넷 연결 정상")
        except:
            logger.error(f"   ❌ 인터넷 연결 실패")

        # 2. 키움 서버 연결
        logger.info("\n2. 키움 API 서버 연결")
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5,
                verify=False
            )
            logger.info(f"   상태 코드: {response.status_code}")
        except Exception as e:
            logger.error(f"   ❌ 연결 실패: {e}")

        # 3. 토큰 발급
        logger.info("\n3. 토큰 발급 테스트")
        token = self.get_access_token()
        if token:
            logger.info(f"   ✅ 토큰: {token[:50]}...")
        else:
            logger.error(f"   ❌ 토큰 발급 실패")

        return token is not None

def main():
    """메인 함수"""
    downloader = KiwoomDataDownloader()

    # 연결 테스트
    if not downloader.test_connection():
        logger.error("API 연결 실패 - 프로그램 종료")
        sys.exit(1)

    # 테스트용 종목
    test_stocks = ['005930', '000660', '035720']  # 삼성전자, SK하이닉스, 카카오

    # 데이터 다운로드
    downloader.download_and_save(test_stocks)

    logger.info("\n✅ 다운로드 완료")

if __name__ == "__main__":
    main()