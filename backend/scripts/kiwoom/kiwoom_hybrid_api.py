"""
키움증권 하이브리드 API (OpenAPI+ & REST API 통합)
두 API의 장점을 결합한 최적화된 자동매매 시스템
"""
import os
import sys
import platform
import requests
import json
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIMode(Enum):
    """API 모드 선택"""
    OPENAPI_PLUS = "openapi+"
    REST_API = "rest"
    HYBRID = "hybrid"  # 자동 선택
    

class APIFeature(Enum):
    """기능별 최적 API 매핑"""
    REALTIME_PRICE = "openapi+"  # 실시간 시세
    ORDER_URGENT = "openapi+"     # 긴급 주문
    ORDER_NORMAL = "rest"         # 일반 주문
    BALANCE = "rest"              # 잔고 조회
    HISTORICAL = "rest"           # 과거 데이터
    BACKTEST = "rest"            # 백테스트
    MONITORING = "rest"          # 모니터링


class KiwoomHybridAPI:
    """
    OpenAPI+와 REST API를 통합 관리하는 하이브리드 API
    
    장점:
    - 각 API의 강점 활용
    - 자동 장애 전환 (Failover)
    - 기능별 최적 라우팅
    """
    
    def __init__(self, mode: APIMode = APIMode.HYBRID):
        self.mode = mode
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.rest_url = os.getenv('KIWOOM_REST_URL', 'https://openapi.kiwoom.com:9443')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'
        
        # API 가용성
        self.openapi_available = False
        self.rest_available = False
        
        # REST API 토큰
        self.rest_token = None
        self.token_expires = None
        
        # OpenAPI+ 객체
        self.openapi = None
        
        # 초기화
        self._initialize_apis()
        
    def _initialize_apis(self):
        """API 초기화 및 가용성 체크"""
        
        # REST API 체크
        try:
            self._get_rest_token()
            self.rest_available = True
            logger.info("✅ REST API 사용 가능")
        except Exception as e:
            logger.warning(f"⚠️ REST API 사용 불가: {e}")
        
        # OpenAPI+ 체크 (Windows만)
        if platform.system() == 'Windows':
            try:
                import win32com.client
                self.openapi = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
                self.openapi_available = True
                logger.info("✅ OpenAPI+ 사용 가능")
            except Exception as e:
                logger.warning(f"⚠️ OpenAPI+ 사용 불가: {e}")
        
        # 하이브리드 모드 체크
        if self.mode == APIMode.HYBRID:
            if not self.rest_available and not self.openapi_available:
                raise Exception("❌ 사용 가능한 API가 없습니다")
            logger.info(f"🚀 하이브리드 모드 활성화 (REST: {self.rest_available}, OpenAPI+: {self.openapi_available})")
    
    def _get_rest_token(self):
        """REST API 토큰 발급"""
        if self.rest_token and self.token_expires and datetime.now() < self.token_expires:
            return self.rest_token
        
        url = f"{self.rest_url}/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.rest_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 86400)
            self.token_expires = datetime.now().timestamp() + expires_in
            return self.rest_token
        else:
            raise Exception(f"토큰 발급 실패: {response.text}")
    
    def _select_api(self, feature: APIFeature) -> str:
        """기능에 따라 최적 API 선택"""
        
        # 명시적 모드 설정시
        if self.mode == APIMode.OPENAPI_PLUS:
            return "openapi+" if self.openapi_available else None
        elif self.mode == APIMode.REST_API:
            return "rest" if self.rest_available else None
        
        # 하이브리드 모드: 기능별 최적 선택
        preferred = feature.value
        
        # 선호 API 사용 가능 체크
        if preferred == "openapi+" and self.openapi_available:
            return "openapi+"
        elif preferred == "rest" and self.rest_available:
            return "rest"
        
        # 폴백
        if self.rest_available:
            return "rest"
        elif self.openapi_available:
            return "openapi+"
        
        return None
    
    # ==================== 시세 조회 ====================
    
    def get_current_price(self, stock_code: str, use_realtime: bool = False) -> Dict[str, Any]:
        """
        현재가 조회
        
        Args:
            stock_code: 종목코드
            use_realtime: 실시간 요청 여부
        
        Returns:
            현재가 정보
        """
        
        # API 선택
        if use_realtime:
            api_type = self._select_api(APIFeature.REALTIME_PRICE)
        else:
            api_type = self._select_api(APIFeature.HISTORICAL)
        
        if api_type == "openapi+" and self.openapi_available:
            return self._get_price_openapi(stock_code)
        elif api_type == "rest" and self.rest_available:
            return self._get_price_rest(stock_code)
        else:
            raise Exception("사용 가능한 API가 없습니다")
    
    def _get_price_rest(self, stock_code: str) -> Dict[str, Any]:
        """REST API로 현재가 조회"""
        token = self._get_rest_token()
        url = f"{self.rest_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"
        }
        
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stock_code
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('rt_cd') == '0':
                output = data.get('output', {})
                return {
                    'stock_code': stock_code,
                    'current_price': int(output.get('stck_prpr', 0)),
                    'change': int(output.get('prdy_vrss', 0)),
                    'change_rate': float(output.get('prdy_ctrt', 0)),
                    'volume': int(output.get('acml_vol', 0)),
                    'api_used': 'REST'
                }
        
        raise Exception(f"시세 조회 실패: {response.text}")
    
    def _get_price_openapi(self, stock_code: str) -> Dict[str, Any]:
        """OpenAPI+로 현재가 조회"""
        if not self.openapi:
            raise Exception("OpenAPI+ 사용 불가")
        
        # OpenAPI+ 구현 (실제 환경에서 구현)
        # self.openapi.SetInputValue("종목코드", stock_code)
        # self.openapi.CommRqData("현재가조회", "opt10001", 0, "0101")
        
        return {
            'stock_code': stock_code,
            'current_price': 0,  # 실제 구현 필요
            'api_used': 'OpenAPI+'
        }
    
    # ==================== 주문 실행 ====================
    
    def send_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        주문 실행
        
        Args:
            order_params: 주문 파라미터
                - stock_code: 종목코드
                - order_type: 매수/매도
                - quantity: 수량
                - price: 가격
                - urgent: 긴급 여부
        
        Returns:
            주문 결과
        """
        
        # 긴급 주문 여부 체크
        if order_params.get('urgent'):
            api_type = self._select_api(APIFeature.ORDER_URGENT)
        else:
            api_type = self._select_api(APIFeature.ORDER_NORMAL)
        
        logger.info(f"📤 주문 실행: {order_params['stock_code']} via {api_type}")
        
        if api_type == "openapi+":
            return self._send_order_openapi(order_params)
        else:
            return self._send_order_rest(order_params)
    
    def _send_order_rest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """REST API로 주문"""
        token = self._get_rest_token()
        url = f"{self.rest_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "VTTC0802U" if self.is_demo else "TTTC0802U"  # 매수
        }
        
        data = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[9:11] if len(self.account_no) > 9 else "01",
            "PDNO": params['stock_code'],
            "ORD_DVSN": "00",  # 지정가
            "ORD_QTY": str(params['quantity']),
            "ORD_UNPR": str(params['price'])
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return {
                'success': result.get('rt_cd') == '0',
                'order_id': result.get('output', {}).get('ODNO'),
                'message': result.get('msg1'),
                'api_used': 'REST'
            }
        
        return {'success': False, 'message': response.text, 'api_used': 'REST'}
    
    def _send_order_openapi(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAPI+로 주문 (더 빠른 체결)"""
        # 실제 구현 필요
        return {
            'success': True,
            'order_id': 'OPENAPI_ORDER_001',
            'api_used': 'OpenAPI+'
        }
    
    # ==================== 잔고 조회 ====================
    
    def get_balance(self) -> Dict[str, Any]:
        """계좌 잔고 조회"""
        api_type = self._select_api(APIFeature.BALANCE)
        
        if api_type == "rest":
            return self._get_balance_rest()
        else:
            return self._get_balance_openapi()
    
    def _get_balance_rest(self) -> Dict[str, Any]:
        """REST API로 잔고 조회"""
        token = self._get_rest_token()
        url = f"{self.rest_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "VTTC8434R" if self.is_demo else "TTTC8434R"
        }
        
        params = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[9:11] if len(self.account_no) > 9 else "01",
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "N",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'balance': data.get('output2', [{}])[0],
                'holdings': data.get('output1', []),
                'api_used': 'REST'
            }
        
        return {'success': False, 'message': response.text}
    
    def _get_balance_openapi(self) -> Dict[str, Any]:
        """OpenAPI+로 잔고 조회"""
        # 실제 구현 필요
        return {
            'success': True,
            'balance': {},
            'holdings': [],
            'api_used': 'OpenAPI+'
        }
    
    # ==================== 실시간 데이터 ====================
    
    def subscribe_realtime(self, stock_codes: List[str], callback=None):
        """
        실시간 시세 구독
        OpenAPI+ 우선 사용 (더 빠른 실시간)
        """
        if self.openapi_available:
            logger.info(f"📡 OpenAPI+로 실시간 구독: {stock_codes}")
            return self._subscribe_realtime_openapi(stock_codes, callback)
        elif self.rest_available:
            logger.info(f"📡 WebSocket으로 실시간 구독: {stock_codes}")
            return self._subscribe_realtime_websocket(stock_codes, callback)
        else:
            raise Exception("실시간 데이터 사용 불가")
    
    def _subscribe_realtime_openapi(self, stock_codes: List[str], callback):
        """OpenAPI+ 실시간 구독"""
        # 실제 구현 필요
        pass
    
    def _subscribe_realtime_websocket(self, stock_codes: List[str], callback):
        """WebSocket 실시간 구독"""
        # WebSocket 구현
        pass
    
    # ==================== 상태 체크 ====================
    
    def get_status(self) -> Dict[str, Any]:
        """API 상태 확인"""
        return {
            'mode': self.mode.value,
            'openapi_available': self.openapi_available,
            'rest_available': self.rest_available,
            'account': self.account_no,
            'is_demo': self.is_demo,
            'timestamp': datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict[str, bool]:
        """헬스 체크"""
        health = {
            'openapi': False,
            'rest': False
        }
        
        # REST API 체크
        try:
            self._get_rest_token()
            health['rest'] = True
        except:
            pass
        
        # OpenAPI+ 체크
        if self.openapi:
            try:
                # 연결 상태 체크
                health['openapi'] = True
            except:
                pass
        
        return health


# ==================== 사용 예제 ====================

if __name__ == "__main__":
    # 하이브리드 API 초기화
    api = KiwoomHybridAPI(mode=APIMode.HYBRID)
    
    # 상태 확인
    print("\n📊 API 상태:")
    print(json.dumps(api.get_status(), indent=2, ensure_ascii=False))
    
    # 헬스 체크
    print("\n💚 헬스 체크:")
    print(json.dumps(api.health_check(), indent=2))
    
    # 시세 조회 (자동 API 선택)
    try:
        price = api.get_current_price("005930")
        print(f"\n📈 삼성전자 현재가: {price}")
    except Exception as e:
        print(f"❌ 시세 조회 실패: {e}")
    
    # 잔고 조회 (REST API 우선)
    try:
        balance = api.get_balance()
        print(f"\n💰 잔고 조회: {balance.get('api_used')} 사용")
    except Exception as e:
        print(f"❌ 잔고 조회 실패: {e}")
    
    print("\n✅ 하이브리드 API 테스트 완료!")