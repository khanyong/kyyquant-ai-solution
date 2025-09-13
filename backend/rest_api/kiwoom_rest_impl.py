"""
키움증권 REST API 구현체 (크로스플랫폼)
Windows, Linux, NAS 등 모든 환경에서 동작
"""

import os
import asyncio
import aiohttp
import websockets
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kiwoom_api_interface import KiwoomAPIInterface, StockPrice, OrderResult, Balance

logger = logging.getLogger(__name__)
load_dotenv()

class KiwoomRestAPI(KiwoomAPIInterface):
    """키움 REST API 구현체"""
    
    def __init__(self):
        # 키움증권 OpenAPI+ REST API URL
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

        # 키움증권 REST API URL (문서 참조)
        self.base_url = 'https://openapi.kiwoom.com:9443'
        self.ws_url = 'ws://openapi.kiwoom.com:9443'

        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        
        self.access_token = None
        self.token_expires_at = None
        self.session = None
        self.ws_connection = None
        self._connected = False
        self.realtime_subscriptions = {}
        
    async def connect(self) -> bool:
        """REST API 연결 (토큰 발급)"""
        try:
            # aiohttp 세션 생성
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # 액세스 토큰 발급
            token = await self._get_access_token()
            if token:
                self._connected = True
                logger.info(f"REST API 연결 성공. 모드: {'모의투자' if self.is_demo else '실전투자'}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"REST API 연결 실패: {e}")
            return False
    
    async def _get_access_token(self) -> Optional[str]:
        """액세스 토큰 발급 또는 갱신"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        # 키움증권 API oauth2/token 엔드포인트 사용
        url = f"{self.base_url}/oauth2/token"

        # 문서에 따라 form-urlencoded 사용
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        try:
            # form data로 전송
            async with self.session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 86400)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    logger.info("액세스 토큰 발급 성공")
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"토큰 발급 실패: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"토큰 발급 오류: {e}")
            return None
    
    async def disconnect(self) -> bool:
        """연결 해제"""
        try:
            # WebSocket 연결 해제
            if self.ws_connection:
                await self.ws_connection.close()
                self.ws_connection = None
            
            # HTTP 세션 종료
            if self.session:
                await self.session.close()
                self.session = None
            
            self._connected = False
            logger.info("REST API 연결 해제")
            return True
            
        except Exception as e:
            logger.error(f"연결 해제 오류: {e}")
            return False
    
    async def get_current_price(self, stock_code: str) -> Optional[StockPrice]:
        """현재가 조회"""
        token = await self._get_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100" if not self.is_demo else "VHKST01010100"
        }
        
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stock_code
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['rt_cd'] == '0':
                        output = data['output']
                        return StockPrice(
                            code=stock_code,
                            name=output.get('hts_kor_isnm', ''),
                            price=int(output['stck_prpr']),
                            change=int(output['prdy_vrss']),
                            change_rate=float(output['prdy_ctrt']),
                            volume=int(output['acml_vol']),
                            high=int(output['stck_hgpr']),
                            low=int(output['stck_lwpr']),
                            open=int(output['stck_oprc']),
                            timestamp=datetime.now()
                        )
                    else:
                        logger.error(f"시세 조회 실패: {data.get('msg1', '')}")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"시세 조회 HTTP 오류: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"시세 조회 오류: {e}")
            return None
    
    async def get_ohlcv(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """일봉 데이터 조회"""
        token = await self._get_access_token()
        if not token:
            return []
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010400" if not self.is_demo else "VHKST01010400"
        }
        
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stock_code,
            "fid_period_div_code": "D",
            "fid_org_adj_prc": "1"
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['rt_cd'] == '0':
                        output = data['output']
                        
                        ohlcv_list = []
                        for item in output:
                            date = item['stck_bsop_date']
                            if start_date <= date <= end_date:
                                ohlcv_list.append({
                                    'date': date,
                                    'open': int(item['stck_oprc']),
                                    'high': int(item['stck_hgpr']),
                                    'low': int(item['stck_lwpr']),
                                    'close': int(item['stck_clpr']),
                                    'volume': int(item['acml_vol'])
                                })
                        
                        return ohlcv_list
                    else:
                        logger.error(f"일봉 조회 실패: {data.get('msg1', '')}")
                        return []
                else:
                    logger.error(f"일봉 조회 HTTP 오류: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"일봉 조회 오류: {e}")
            return []
    
    async def get_balance(self) -> Optional[Balance]:
        """계좌 잔고 조회"""
        token = await self._get_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "TTTC8434R" if not self.is_demo else "VTTC8434R"
        }
        
        params = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[9:],
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "N",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['rt_cd'] == '0':
                        output1 = data['output1']  # 보유 종목
                        output2 = data['output2'][0] if data['output2'] else {}  # 계좌 요약
                        
                        holdings = []
                        for item in output1:
                            if int(item.get('hldg_qty', 0)) > 0:
                                holdings.append({
                                    'code': item['pdno'],
                                    'name': item['prdt_name'],
                                    'quantity': int(item['hldg_qty']),
                                    'avg_price': float(item['pchs_avg_pric']),
                                    'current_price': int(item['prpr']),
                                    'eval_amount': int(item['evlu_amt']),
                                    'profit_loss': int(item['evlu_pfls_amt']),
                                    'profit_rate': float(item['evlu_pfls_rt'])
                                })
                        
                        return Balance(
                            total_eval=int(output2.get('tot_evlu_amt', 0)),
                            total_purchase=int(output2.get('pchs_amt_smtl_amt', 0)),
                            total_profit=int(output2.get('evlu_pfls_smtl_amt', 0)),
                            cash=int(output2.get('prvs_rcdl_excc_amt', 0)),
                            holdings=holdings,
                            timestamp=datetime.now()
                        )
                    else:
                        logger.error(f"잔고 조회 실패: {data.get('msg1', '')}")
                        return None
                else:
                    logger.error(f"잔고 조회 HTTP 오류: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"잔고 조회 오류: {e}")
            return None
    
    async def place_order(
        self, 
        stock_code: str, 
        quantity: int, 
        price: int, 
        order_type: str = 'buy',
        order_method: str = 'limit'
    ) -> Optional[OrderResult]:
        """주문 실행"""
        token = await self._get_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        # 거래 구분 코드 설정
        if order_type == 'buy':
            tr_id = "TTTC0802U" if not self.is_demo else "VTTC0802U"  # 매수
        else:
            tr_id = "TTTC0801U" if not self.is_demo else "VTTC0801U"  # 매도
        
        # 호가 구분
        if order_method == 'market':
            ord_dvsn = "01"  # 시장가
            price = "0"
        else:
            ord_dvsn = "00"  # 지정가
            price = str(price)
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id,
            "custtype": "P"
        }
        
        data = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_no[9:],
            "PDNO": stock_code,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": price
        }
        
        try:
            async with self.session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                
                if response.status == 200 and result.get('rt_cd') == '0':
                    output = result.get('output', {})
                    return OrderResult(
                        success=True,
                        order_no=output.get('ORD_NO', ''),
                        message='주문 성공',
                        timestamp=datetime.now(),
                        details=output
                    )
                else:
                    return OrderResult(
                        success=False,
                        order_no='',
                        message=result.get('msg1', '주문 실패'),
                        timestamp=datetime.now(),
                        details=result
                    )
                    
        except Exception as e:
            logger.error(f"주문 실행 오류: {e}")
            return OrderResult(
                success=False,
                order_no='',
                message=str(e),
                timestamp=datetime.now(),
                details={}
            )
    
    async def cancel_order(self, order_no: str) -> Optional[OrderResult]:
        """주문 취소"""
        # REST API의 주문 취소 엔드포인트 사용
        # /uapi/domestic-stock/v1/trading/order-cancel
        pass
    
    async def get_order_history(self, start_date: str = None) -> List[Dict]:
        """주문 내역 조회"""
        # REST API의 주문 내역 조회 엔드포인트 사용
        # /uapi/domestic-stock/v1/trading/inquire-daily-ccld
        pass
    
    async def subscribe_realtime(self, stock_codes: List[str], callback: callable):
        """실시간 시세 구독 (WebSocket)"""
        try:
            if not self.ws_connection:
                # WebSocket 연결
                self.ws_connection = await websockets.connect(self.ws_url)
                
                # 인증
                auth_data = {
                    "header": {
                        "appkey": self.app_key,
                        "appsecret": self.app_secret,
                        "custtype": "P",
                        "tr_type": "1"
                    },
                    "body": {
                        "grant_type": "client_credentials"
                    }
                }
                await self.ws_connection.send(json.dumps(auth_data))
            
            # 실시간 데이터 구독
            for code in stock_codes:
                self.realtime_subscriptions[code] = callback
                
                subscribe_data = {
                    "header": {
                        "appkey": self.app_key,
                        "appsecret": self.app_secret,
                        "custtype": "P",
                        "tr_type": "1",
                        "content_type": "utf-8"
                    },
                    "body": {
                        "input": {
                            "tr_id": "H0STCNT0",
                            "tr_key": code
                        }
                    }
                }
                await self.ws_connection.send(json.dumps(subscribe_data))
            
            # 비동기로 메시지 수신
            asyncio.create_task(self._handle_realtime_messages())
            
            logger.info(f"실시간 구독 시작: {stock_codes}")
            
        except Exception as e:
            logger.error(f"실시간 구독 오류: {e}")
    
    async def _handle_realtime_messages(self):
        """실시간 메시지 처리"""
        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                
                # 종목 코드 추출
                code = data.get('body', {}).get('tr_key')
                if code in self.realtime_subscriptions:
                    callback = self.realtime_subscriptions[code]
                    
                    # 콜백 실행
                    await callback({
                        'code': code,
                        'data': data.get('body', {}),
                        'timestamp': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"실시간 메시지 처리 오류: {e}")
    
    async def unsubscribe_realtime(self, stock_codes: List[str]):
        """실시간 구독 해제"""
        try:
            for code in stock_codes:
                if code in self.realtime_subscriptions:
                    del self.realtime_subscriptions[code]
                    
                    # 구독 해제 메시지 전송
                    if self.ws_connection:
                        unsubscribe_data = {
                            "header": {
                                "appkey": self.app_key,
                                "appsecret": self.app_secret,
                                "custtype": "P",
                                "tr_type": "2"  # 해제
                            },
                            "body": {
                                "input": {
                                    "tr_id": "H0STCNT0",
                                    "tr_key": code
                                }
                            }
                        }
                        await self.ws_connection.send(json.dumps(unsubscribe_data))
            
            logger.info(f"실시간 구독 해제: {stock_codes}")
            
        except Exception as e:
            logger.error(f"실시간 구독 해제 오류: {e}")
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    @property
    def api_type(self) -> str:
        return "rest"
    
    @property
    def platform(self) -> str:
        import platform
        system = platform.system().lower()
        if 'synology' in platform.platform().lower():
            return "nas"
        return system