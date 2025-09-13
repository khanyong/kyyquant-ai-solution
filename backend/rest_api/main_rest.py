"""
키움증권 REST API 기반 자동매매 시스템
Windows/Linux/NAS 모두 동일하게 작동
"""

import os
import json
import time
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class KiwoomRestAPI:
    """키움증권 REST API 클라이언트"""
    
    def __init__(self):
        self.base_url = os.getenv('KIWOOM_API_URL', 'https://openapi.kiwoom.com:9443')
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'
        
        self.access_token = None
        self.token_expires_at = None
        
        logger.info(f"KiwoomRestAPI 초기화 - 모의투자: {self.is_demo}")
    
    def get_access_token(self) -> str:
        """액세스 토큰 발급 또는 갱신"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.base_url}/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 86400)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info("액세스 토큰 발급 성공")
            return self.access_token
            
        except Exception as e:
            logger.error(f"토큰 발급 실패: {e}")
            raise
    
    def get_current_price(self, stock_code: str) -> Dict:
        """현재가 조회"""
        token = self.get_access_token()
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
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['rt_cd'] == '0':
                output = data['output']
                return {
                    'code': stock_code,
                    'price': int(output['stck_prpr']),
                    'change': int(output['prdy_vrss']),
                    'change_rate': float(output['prdy_ctrt']),
                    'volume': int(output['acml_vol']),
                    'high': int(output['stck_hgpr']),
                    'low': int(output['stck_lwpr']),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"시세 조회 실패: {data['msg1']}")
                return None
                
        except Exception as e:
            logger.error(f"시세 조회 오류: {e}")
            return None
    
    def get_balance(self) -> Dict:
        """계좌 잔고 조회"""
        token = self.get_access_token()
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
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['rt_cd'] == '0':
                output1 = data['output1']  # 보유 종목
                output2 = data['output2'][0]  # 계좌 요약
                
                holdings = []
                for item in output1:
                    if int(item['hldg_qty']) > 0:
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
                
                return {
                    'total_eval': int(output2['tot_evlu_amt']),
                    'total_purchase': int(output2['pchs_amt_smtl_amt']),
                    'total_profit': int(output2['evlu_pfls_smtl_amt']),
                    'cash': int(output2['prvs_rcdl_excc_amt']),
                    'holdings': holdings,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"잔고 조회 실패: {data['msg1']}")
                return None
                
        except Exception as e:
            logger.error(f"잔고 조회 오류: {e}")
            return None
    
    def place_order(self, stock_code: str, quantity: int, price: int, order_type: str = 'buy') -> Dict:
        """주문 실행
        order_type: 'buy' 또는 'sell'
        """
        token = self.get_access_token()
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        # 거래 구분 코드 설정
        if order_type == 'buy':
            tr_id = "TTTC0802U" if not self.is_demo else "VTTC0802U"  # 매수
            ord_dvsn = "00"  # 지정가
        else:
            tr_id = "TTTC0801U" if not self.is_demo else "VTTC0801U"  # 매도
            ord_dvsn = "00"  # 지정가
        
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
            "ORD_UNPR": str(price)
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result['rt_cd'] == '0':
                output = result['output']
                return {
                    'success': True,
                    'order_no': output['ORD_NO'],
                    'order_time': output['ORD_TMD'],
                    'message': '주문 성공',
                    'details': output
                }
            else:
                return {
                    'success': False,
                    'message': result['msg1'],
                    'details': result
                }
                
        except Exception as e:
            logger.error(f"주문 실행 오류: {e}")
            return {
                'success': False,
                'message': str(e)
            }


class AutoTradingSystem:
    """자동매매 시스템 - Windows/NAS 공통"""
    
    def __init__(self):
        self.api = KiwoomRestAPI()
        self.is_running = False
        self.strategies = []
        
    async def initialize(self):
        """시스템 초기화"""
        logger.info("자동매매 시스템 초기화 중...")
        
        # 토큰 발급 테스트
        try:
            self.api.get_access_token()
            logger.info("API 연결 성공")
            
            # 잔고 확인
            balance = self.api.get_balance()
            if balance:
                logger.info(f"계좌 잔고: {balance['cash']:,}원")
                logger.info(f"보유 종목: {len(balance['holdings'])}개")
            
            return True
            
        except Exception as e:
            logger.error(f"초기화 실패: {e}")
            return False
    
    async def monitor_market(self):
        """시장 모니터링 (1분 간격)"""
        watch_list = ['005930', '000660', '035720']  # 삼성전자, SK하이닉스, 카카오
        
        while self.is_running:
            try:
                for stock_code in watch_list:
                    price_data = self.api.get_current_price(stock_code)
                    if price_data:
                        logger.info(f"{stock_code}: {price_data['price']:,}원 ({price_data['change_rate']:+.2f}%)")
                
                await asyncio.sleep(60)  # 1분 대기
                
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                await asyncio.sleep(10)
    
    async def execute_strategy(self):
        """전략 실행 (5분 간격)"""
        while self.is_running:
            try:
                # 전략 로직 실행
                logger.info("전략 검사 중...")
                
                # 예시: 단순 모멘텀 전략
                price_data = self.api.get_current_price('005930')
                if price_data and price_data['change_rate'] > 2.0:
                    logger.info("매수 신호 감지!")
                    # 실제 주문은 주의해서 실행
                    # result = self.api.place_order('005930', 1, price_data['price'], 'buy')
                
                await asyncio.sleep(300)  # 5분 대기
                
            except Exception as e:
                logger.error(f"전략 실행 오류: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        """메인 실행 루프"""
        if not await self.initialize():
            logger.error("시스템 초기화 실패")
            return
        
        self.is_running = True
        logger.info("자동매매 시스템 시작")
        
        try:
            # 비동기 태스크 실행
            await asyncio.gather(
                self.monitor_market(),
                self.execute_strategy()
            )
        except KeyboardInterrupt:
            logger.info("시스템 종료 중...")
        finally:
            self.is_running = False
            logger.info("자동매매 시스템 종료")


# FastAPI 서버 (선택사항)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Auto Trading API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 API 인스턴스
kiwoom_api = KiwoomRestAPI()

@app.get("/")
async def root():
    return {"message": "Auto Trading System API", "status": "running"}

@app.get("/api/price/{stock_code}")
async def get_price(stock_code: str):
    """현재가 조회 API"""
    price_data = kiwoom_api.get_current_price(stock_code)
    if price_data:
        return price_data
    raise HTTPException(status_code=404, detail="Price data not found")

@app.get("/api/balance")
async def get_balance():
    """잔고 조회 API"""
    balance = kiwoom_api.get_balance()
    if balance:
        return balance
    raise HTTPException(status_code=500, detail="Failed to get balance")

@app.post("/api/order")
async def place_order(stock_code: str, quantity: int, price: int, order_type: str):
    """주문 실행 API"""
    result = kiwoom_api.place_order(stock_code, quantity, price, order_type)
    if result['success']:
        return result
    raise HTTPException(status_code=400, detail=result['message'])


if __name__ == "__main__":
    # CLI 모드 또는 API 서버 모드 선택
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        # API 서버 모드
        logger.info("Starting API Server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # 자동매매 모드
        logger.info("Starting Auto Trading System...")
        system = AutoTradingSystem()
        asyncio.run(system.run())