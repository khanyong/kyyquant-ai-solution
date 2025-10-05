"""
키움증권 REST API 클라이언트
실시간 시세 조회 및 주문 기능
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class KiwoomAPIClient:
    """키움증권 REST API 클라이언트"""

    def __init__(self):
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

        # 환경 변수 확인
        if not self.app_key or not self.app_secret:
            print(f"[KiwoomAPI] WARNING: Missing credentials - APP_KEY: {bool(self.app_key)}, APP_SECRET: {bool(self.app_secret)}")
        else:
            print(f"[KiwoomAPI] Credentials loaded - APP_KEY: {self.app_key[:20]}..., MODE: {'DEMO' if self.is_demo else 'REAL'}")

        # API URL 설정 (환경 변수 우선, 없으면 모의투자/실전투자 구분)
        self.base_url = os.getenv('KIWOOM_API_URL')
        if not self.base_url:
            if self.is_demo:
                self.base_url = "https://mockapi.kiwoom.com"
            else:
                self.base_url = "https://openapi.kiwoom.com:9443"

        self.access_token = None
        self.token_expires_at = None

    def _get_access_token(self) -> str:
        """
        OAuth 2.0 액세스 토큰 발급
        토큰이 유효하면 캐시된 토큰 반환
        """
        # 토큰이 유효한 경우 기존 토큰 반환
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # 토큰 발급 요청
        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret  # 키움은 'secretkey' 사용
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()

            # 응답 코드 체크
            if result.get('return_code') != 0:
                error_msg = result.get('return_msg', 'Unknown error')
                raise Exception(f"Token issuance failed: {error_msg}")

            self.access_token = result['token']  # 키움은 'token' 필드 사용

            # 토큰 만료 시간 설정 (24시간 - 5분 여유)
            expires_in = result.get('expires_in', 86400)  # 기본 24시간
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            print(f"[KiwoomAPI] Access token issued successfully (expires at {self.token_expires_at})")
            return self.access_token

        except requests.exceptions.RequestException as e:
            print(f"[KiwoomAPI] Token issuance failed: {e}")
            raise Exception(f"Failed to get access token: {str(e)}")

    def get_current_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        실시간 현재가 조회

        Args:
            stock_code: 종목코드 (예: "005930")

        Returns:
            {
                'stock_code': '005930',
                'current_price': 77400,
                'change': 500,
                'change_rate': 0.65,
                'volume': 12345678,
                'high': 78000,
                'low': 77000,
                'open': 77500
            }
        """
        try:
            token = self._get_access_token()

            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"  # 현재가 조회 TR
            }
            params = {
                "fid_cond_mrkt_div_code": "J",  # KOSPI/KOSDAQ
                "fid_input_iscd": stock_code
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 응답 코드 확인
            if data.get('rt_cd') != '0':
                error_msg = data.get('msg1', 'Unknown error')
                print(f"[KiwoomAPI] Price inquiry failed: {error_msg}")
                return None

            output = data.get('output', {})

            # 데이터 파싱
            result = {
                'stock_code': stock_code,
                'current_price': int(output.get('stck_prpr', 0)),  # 현재가
                'change': int(output.get('prdy_vrss', 0)),  # 전일 대비
                'change_rate': float(output.get('prdy_ctrt', 0)),  # 전일 대비율
                'volume': int(output.get('acml_vol', 0)),  # 누적 거래량
                'high': int(output.get('stck_hgpr', 0)),  # 최고가
                'low': int(output.get('stck_lwpr', 0)),  # 최저가
                'open': int(output.get('stck_oprc', 0)),  # 시가
                'timestamp': datetime.now().isoformat()
            }

            print(f"[KiwoomAPI] {stock_code} 현재가: {result['current_price']:,}원")
            return result

        except requests.exceptions.RequestException as e:
            print(f"[KiwoomAPI] HTTP request failed: {e}")
            return None
        except Exception as e:
            print(f"[KiwoomAPI] Unexpected error: {e}")
            return None

    def get_historical_price(self, stock_code: str, period: int = 100) -> Optional[Dict[str, Any]]:
        """
        과거 일봉 데이터 조회

        Args:
            stock_code: 종목코드
            period: 조회 기간 (일)

        Returns:
            일봉 데이터 리스트
        """
        try:
            token = self._get_access_token()

            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010400"  # 일봉 조회 TR
            }
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": stock_code,
                "fid_period_div_code": "D",  # 일봉
                "fid_org_adj_prc": "0"  # 수정주가 미적용
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rt_cd') != '0':
                return None

            output = data.get('output', [])
            return output[:period]  # 요청한 기간만큼만 반환

        except Exception as e:
            print(f"[KiwoomAPI] Historical price inquiry failed: {e}")
            return None


# 싱글톤 인스턴스
_kiwoom_client = None

def get_kiwoom_client() -> KiwoomAPIClient:
    """키움 API 클라이언트 싱글톤 인스턴스 반환"""
    global _kiwoom_client
    if _kiwoom_client is None:
        _kiwoom_client = KiwoomAPIClient()
    return _kiwoom_client
