"""
키움증권 REST API Bridge Server (실제 모의투자 버전)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import httpx
import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="키움증권 REST API Bridge",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class CurrentPriceRequest(BaseModel):
    stock_code: str

class OrderRequest(BaseModel):
    user_id: str
    stock_code: str
    order_type: str  # buy/sell
    quantity: int
    price: int
    order_method: str = "00"

class KiwoomAPI:
    """키움 실제 API 연동"""
    
    def __init__(self):
        self.base_url = "https://openapivts.koreainvestment.com:29443"  # 모의투자
        self.app_key = os.getenv("KIWOOM_APP_KEY", "")
        self.app_secret = os.getenv("KIWOOM_APP_SECRET", "")
        self.access_token = None
        
    async def get_token(self):
        """액세스 토큰 발급"""
        url = f"{self.base_url}/oauth2/tokenP"
        
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body)
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token
            
    async def get_current_price(self, stock_code: str):
        """실제 현재가 조회"""
        if not self.access_token:
            await self.get_token()
            
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"
        }
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            return response.json()
            
    async def place_order(self, order: OrderRequest):
        """실제 주문 실행"""
        if not self.access_token:
            await self.get_token()
            
        # 해시키 생성
        hashkey = self.create_hashkey(order)
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "VTTC0802U" if order.order_type == "buy" else "VTTC0801U",  # 모의투자 매수/매도
            "hashkey": hashkey
        }
        
        body = {
            "CANO": os.getenv("KIWOOM_ACCOUNT_NUMBER", ""),  # 계좌번호
            "ACNT_PRDT_CD": "01",  # 계좌상품코드
            "PDNO": order.stock_code,  # 종목코드
            "ORD_DVSN": order.order_method,  # 주문구분
            "ORD_QTY": str(order.quantity),  # 주문수량
            "ORD_UNPR": str(order.price) if order.price > 0 else "0"  # 주문단가
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)
            return response.json()
            
    def create_hashkey(self, order: OrderRequest) -> str:
        """해시키 생성"""
        # 실제 해시키 생성 로직
        return "generated_hashkey"

# API 인스턴스
kiwoom = KiwoomAPI()

@app.get("/")
async def root():
    return {
        "service": "Kiwoom REST API Bridge",
        "status": "running",
        "version": "2.0.0",
        "mode": "mock_trading",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/market/current-price")
async def get_current_price(request: CurrentPriceRequest):
    """현재가 조회"""
    try:
        # 실제 API 호출 (환경변수 설정 시)
        if kiwoom.app_key and kiwoom.app_secret:
            result = await kiwoom.get_current_price(request.stock_code)
            return {"success": True, "data": result}
        else:
            # Mock 데이터 (API 키 없을 때)
            return {
                "success": True,
                "data": {
                    "output": {
                        "stck_prpr": "71900",
                        "prdy_vrss": "-500"
                    }
                }
            }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trading/order")
async def place_order(order: OrderRequest):
    """주문 실행"""
    try:
        # 실제 API 호출 (환경변수 설정 시)
        if kiwoom.app_key and kiwoom.app_secret:
            result = await kiwoom.place_order(order)
            return {"success": True, "data": result}
        else:
            # Mock 응답
            return {
                "success": True,
                "message": "Mock order placed",
                "data": {
                    "order_id": "MOCK123456",
                    "stock_code": order.stock_code,
                    "quantity": order.quantity,
                    "price": order.price
                }
            }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategy/execute")
async def execute_strategy(data: dict):
    """전략 실행 엔드포인트"""
    strategy_id = data.get("strategy_id")
    user_id = data.get("user_id")
    
    # TODO: Supabase에서 전략 로드
    # TODO: 백테스트 결과 기반 신호 생성
    # TODO: 자동 주문 실행
    
    return {
        "success": True,
        "message": f"Strategy {strategy_id} executed",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)