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
        실시간 현재가 조회 (모의투자 전용)

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

            # 모의투자 전용 API
            url = f"{self.base_url}/api/dostk/mrkcond"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "cont-yn": "N",
                "next-key": "",
                "api-id": "ka10007"  # 시세표성정보요청
            }
            body = {
                "stk_cd": stock_code  # 종목코드
            }

            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 응답 데이터 확인
            if not data or data.get('return_code') != 0:
                print(f"[KiwoomAPI] Price inquiry failed: {data.get('return_msg', 'Unknown error')}")
                return None

            # ka10007 API는 output 키 없이 직접 데이터 반환
            # 부호(+/-)를 제거하고 숫자로 변환
            def parse_price(value: str) -> int:
                if not value:
                    return 0
                return int(value.replace('+', '').replace('-', '').replace(',', ''))

            def parse_rate(value: str) -> float:
                if not value:
                    return 0.0
                # 부호 유지하며 파싱
                return float(value.replace('+', '').replace(',', ''))

            # 데이터 파싱
            result = {
                'stock_code': stock_code,
                'stock_name': data.get('stk_nm', ''),  # 종목명
                'current_price': parse_price(data.get('cur_prc', '0')),  # 현재가
                'change': parse_price(data.get('pred_close_pric', '0')) - parse_price(data.get('cur_prc', '0')),  # 전일대비 (전일종가 - 현재가)
                'change_rate': parse_rate(data.get('flu_rt', '0')),  # 등락률
                'volume': parse_price(data.get('trde_qty', '0')),  # 거래량
                'high': parse_price(data.get('high_pric', '0')),  # 고가
                'low': parse_price(data.get('low_pric', '0')),  # 저가
                'open': parse_price(data.get('open_pric', '0')),  # 시가
                'timestamp': datetime.now().isoformat()
            }

            print(f"[KiwoomAPI] {stock_code} {result['stock_name']} 현재가: {result['current_price']:,}원 ({result['change_rate']:+.2f}%)")
            return result

        except requests.exceptions.RequestException as e:
            print(f"[KiwoomAPI] HTTP request failed: {e}")
            return None
        except Exception as e:
            print(f"[KiwoomAPI] Unexpected error: {e}")
            return None

    def get_historical_price(self, stock_code: str, period: int = 100, base_date: Optional[str] = None) -> Optional[list]:
        """
        과거 일봉 데이터 조회 (모의투자 전용)

        Args:
            stock_code: 종목코드
            period: 조회 기간 (일) - 최대 600일
            base_date: 기준일자 (YYYYMMDD, None이면 오늘) - 과거 데이터 조회용

        Returns:
            일봉 데이터 리스트
        """
        try:
            token = self._get_access_token()

            # 기준일자 (기본값: 오늘)
            if not base_date:
                base_date = datetime.now().strftime('%Y%m%d')

            # 모의투자 전용 API
            url = f"{self.base_url}/api/dostk/chart"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "cont-yn": "N",
                "next-key": "",
                "api-id": "ka10081"  # 주식일봉차트조회
            }
            body = {
                "stk_cd": stock_code,  # 종목코드
                "base_dt": base_date,  # 기준일자 (YYYYMMDD)
                "upd_stkpc_tp": "1"  # 수정주가구분 (0: 미수정, 1: 수정주가)
            }

            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 응답 데이터 확인 (모의투자 API 응답 구조)
            if not data:
                print(f"[KiwoomAPI] Historical price inquiry failed: Invalid response")
                return None

            # 응답 구조: {"stk_cd": "...", "stk_dt_pole_chart_qry": [...]}
            if 'stk_dt_pole_chart_qry' in data:
                output = data['stk_dt_pole_chart_qry']
            elif isinstance(data, list):
                output = data
            else:
                # 데이터가 없는 경우 (정상적인 경우도 있음 - 예를 들어 너무 먼 과거)
                if isinstance(data, dict) and data.get('rt_cd') == '0':
                     return [] # 빈 리스트 반환
                
                print(f"[KiwoomAPI] Historical price inquiry failed: Unexpected response structure")
                print(f"[KiwoomAPI] Response keys: {list(data.keys())}")
                return None

            # 요청한 기간만큼만 반환 (최신순으로 정렬되어 있음)
            result = output[:period] if len(output) > period else output

            print(f"[KiwoomAPI] {stock_code} 일봉 데이터 조회 (기준: {base_date}): {len(result)}일치")
            return result

        except Exception as e:
            print(f"[KiwoomAPI] Historical price inquiry failed: {e}")
            return None

    def get_all_stock_list(self, market_type: str = '0') -> Optional[list]:
        """
        전체 종목 리스트 조회 (모의투자 전용)

        Args:
            market_type: 시장구분 ('0': KOSPI, '10': KOSDAQ)

        Returns:
            종목 리스트
            [
                {
                    'code': '005930',
                    'name': '삼성전자',
                    'market': 'KOSPI',
                    ...
                },
                ...
            ]
        """
        try:
            token = self._get_access_token()

            # 모의투자 전용 API
            url = f"{self.base_url}/api/dostk/stkinfo"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "cont-yn": "N",
                "next-key": "",
                "api-id": "ka10099"  # 종목정보 리스트 조회
            }
            body = {
                "mrkt_tp": market_type  # 시장구분
            }

            all_stocks = []
            cont_yn = "N"
            next_key = ""

            # 연속조회로 모든 종목 가져오기
            while True:
                headers["cont-yn"] = cont_yn
                headers["next-key"] = next_key

                response = requests.post(url, headers=headers, json=body, timeout=10)
                response.raise_for_status()

                data = response.json()

                # 응답 데이터 확인
                if not data or 'list' not in data:
                    break

                stocks = data.get('list', [])
                all_stocks.extend(stocks)

                # 연속조회 확인
                cont_yn = response.headers.get('cont-yn', 'N')
                next_key = response.headers.get('next-key', '')

                if cont_yn != 'Y':
                    break

            market_name = "KOSPI" if market_type == '0' else "KOSDAQ"
            print(f"[KiwoomAPI] {market_name} 종목 조회: {len(all_stocks)}개")
            return all_stocks

        except Exception as e:
            print(f"[KiwoomAPI] Stock list inquiry failed: {e}")
            return None

    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """
        계좌 잔고 조회

        Returns:
            {
                'account_no': '81126100-01',
                'total_asset': 10000000,  # 총 자산
                'cash_balance': 5000000,  # 예수금
                'stock_value': 5000000,  # 주식 평가 금액
                'profit_loss': 100000,  # 평가 손익
                'profit_loss_rate': 2.0  # 수익률
            }
        """
        try:
            token = self._get_access_token()

            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "TTTC8434R" if self.is_demo else "TTTC8434R"  # 계좌 잔고 조회
            }
            params = {
                "CANO": self.account_no.split('-')[0] if '-' in self.account_no else self.account_no[:8],
                "ACNT_PRDT_CD": self.account_no.split('-')[1] if '-' in self.account_no else self.account_no[8:],
                "AFHR_FLPR_YN": "N",  # 시간외 단일가 여부
                "OFL_YN": "",  # 오프라인 여부
                "INQR_DVSN": "02",  # 조회 구분 (01:대출일별, 02:종목별)
                "UNPR_DVSN": "01",  # 단가 구분
                "FUND_STTL_ICLD_YN": "N",  # 펀드결제분포함여부
                "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액자동상환여부
                "PRCS_DVSN": "01",  # 처리구분
                "CTX_AREA_FK100": "",  # 연속조회검색조건
                "CTX_AREA_NK100": ""  # 연속조회키
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rt_cd') != '0':
                error_msg = data.get('msg1', 'Unknown error')
                print(f"[KiwoomAPI] Balance inquiry failed: {error_msg}")
                return None

            output = data.get('output2', [{}])[0] if data.get('output2') else {}

            result = {
                'account_no': self.account_no,
                'total_asset': float(output.get('tot_evlu_amt', 0)),  # 총평가금액
                'cash_balance': float(output.get('dnca_tot_amt', 0)),  # 예수금총액
                'stock_value': float(output.get('scts_evlu_amt', 0)),  # 유가증권평가금액
                'profit_loss': float(output.get('evlu_pfls_smtl_amt', 0)),  # 평가손익합계금액
                'profit_loss_rate': float(output.get('evlu_pfls_rt', 0)),  # 평가손익율
                'timestamp': datetime.now().isoformat()
            }

            print(f"[KiwoomAPI] 계좌 잔고: {result['total_asset']:,.0f}원 (평가손익: {result['profit_loss']:+,.0f}원)")
            return result

        except requests.exceptions.RequestException as e:
            print(f"[KiwoomAPI] HTTP request failed: {e}")
            return None
        except Exception as e:
            print(f"[KiwoomAPI] Unexpected error: {e}")
            return None

    def get_holdings(self) -> Optional[list]:
        """
        보유 종목 조회

        Returns:
            [
                {
                    'stock_code': '005930',
                    'stock_name': '삼성전자',
                    'quantity': 10,
                    'average_price': 70000,
                    'current_price': 72000,
                    'profit_loss': 20000,
                    'profit_loss_rate': 2.86
                },
                ...
            ]
        """
        try:
            token = self._get_access_token()

            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "TTTC8434R" if self.is_demo else "TTTC8434R"
            }
            params = {
                "CANO": self.account_no.split('-')[0] if '-' in self.account_no else self.account_no[:8],
                "ACNT_PRDT_CD": self.account_no.split('-')[1] if '-' in self.account_no else self.account_no[8:],
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "02",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "01",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": ""
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rt_cd') != '0':
                return []

            output = data.get('output1', [])
            holdings = []

            for item in output:
                if int(item.get('hldg_qty', 0)) > 0:  # 보유 수량이 있는 종목만
                    holdings.append({
                        'stock_code': item.get('pdno', ''),  # 상품번호(종목코드)
                        'stock_name': item.get('prdt_name', ''),  # 상품명
                        'quantity': int(item.get('hldg_qty', 0)),  # 보유수량
                        'available_quantity': int(item.get('ord_psbl_qty', 0)),  # 주문가능수량
                        'average_price': float(item.get('pchs_avg_pric', 0)),  # 매입평균가격
                        'current_price': float(item.get('prpr', 0)),  # 현재가
                        'profit_loss': float(item.get('evlu_pfls_amt', 0)),  # 평가손익금액
                        'profit_loss_rate': float(item.get('evlu_pfls_rt', 0)),  # 평가손익율
                        'value': float(item.get('evlu_amt', 0))  # 평가금액
                    })

            print(f"[KiwoomAPI] 보유 종목: {len(holdings)}개")
            return holdings

        except Exception as e:
            print(f"[KiwoomAPI] Holdings inquiry failed: {e}")
            return []

    def order_stock(self, stock_code: str, quantity: int, price: int, order_type: str = "buy") -> Optional[Dict[str, Any]]:
        """
        주식 주문 (매수/매도)

        Args:
            stock_code: 종목코드
            quantity: 주문 수량
            price: 주문 가격 (0이면 시장가)
            order_type: "buy" (매수) 또는 "sell" (매도)

        Returns:
            {
                'order_no': '주문번호',
                'status': 'success',
                'message': '주문 완료'
            }
        """
        try:
            token = self._get_access_token()

            # 매수/매도 구분
            if order_type == "buy":
                tr_id = "VTTC0802U" if self.is_demo else "TTTC0802U"  # 주식 현금 매수 주문
            else:
                tr_id = "VTTC0801U" if self.is_demo else "TTTC0801U"  # 주식 현금 매도 주문

            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": tr_id
            }

            body = {
                "CANO": self.account_no.split('-')[0] if '-' in self.account_no else self.account_no[:8],
                "ACNT_PRDT_CD": self.account_no.split('-')[1] if '-' in self.account_no else self.account_no[8:],
                "PDNO": stock_code,  # 종목코드
                "ORD_DVSN": "01" if price > 0 else "00",  # 주문구분 (00:지정가, 01:시장가)
                "ORD_QTY": str(quantity),  # 주문수량
                "ORD_UNPR": str(price) if price > 0 else "0"  # 주문단가
            }

            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('rt_cd') != '0':
                error_msg = data.get('msg1', 'Unknown error')
                print(f"[KiwoomAPI] Order failed: {error_msg}")
                return {
                    'status': 'error',
                    'message': error_msg
                }

            output = data.get('output', {})
            order_no = output.get('KRX_FWDG_ORD_ORGNO', '') + output.get('ODNO', '')

            print(f"[KiwoomAPI] 주문 완료: {order_type.upper()} {stock_code} {quantity}주 @ {price:,}원 (주문번호: {order_no})")

            return {
                'order_no': order_no,
                'status': 'success',
                'message': data.get('msg1', '주문이 완료되었습니다'),
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            print(f"[KiwoomAPI] HTTP request failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
        except Exception as e:
            print(f"[KiwoomAPI] Unexpected error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


# 싱글톤 인스턴스
_kiwoom_client = None

def get_kiwoom_client() -> KiwoomAPIClient:
    """키움 API 클라이언트 싱글톤 인스턴스 반환"""
    global _kiwoom_client
    if _kiwoom_client is None:
        _kiwoom_client = KiwoomAPIClient()
    return _kiwoom_client
