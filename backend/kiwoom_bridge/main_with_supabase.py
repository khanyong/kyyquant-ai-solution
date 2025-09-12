"""
키움증권 REST API Bridge Server (Supabase 연동 버전)
Supabase에서 사용자별 API 키를 가져와서 사용
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import base64

load_dotenv()

app = FastAPI(
    title="키움증권 REST API Bridge",
    version="3.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", "https://hznkyaomtrpzcayayayh.supabase.co"),
    os.getenv("SUPABASE_KEY", "")  # anon key만 필요
)

# Models
class CurrentPriceRequest(BaseModel):
    stock_code: str
    user_id: str = None  # 선택적

class OrderRequest(BaseModel):
    user_id: str  # 필수 - Supabase에서 API 키 조회용
    stock_code: str
    order_type: str  # buy/sell
    quantity: int
    price: int
    order_method: str = "00"

class KiwoomAPI:
    """키움 API 연동 (Supabase에서 키 가져옴)"""
    
    def __init__(self):
        self.base_url = "https://openapivts.koreainvestment.com:29443"  # 모의투자
        self.tokens = {}  # 사용자별 토큰 캐시
        
    async def get_user_keys(self, user_id: str, is_test_mode: bool = True):
        """Supabase에서 사용자 API 키 가져오기"""
        try:
            # user_api_keys 테이블에서 조회
            result = supabase.from_("user_api_keys") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("provider", "kiwoom") \
                .eq("is_test_mode", is_test_mode) \
                .eq("is_active", True) \
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="API keys not found")
            
            keys = result.data[0]
            
            # Base64 디코딩
            app_key = base64.b64decode(keys['api_key']).decode('utf-8')
            app_secret = base64.b64decode(keys['api_secret']).decode('utf-8')
            
            # 계좌 정보 조회
            account_result = supabase.from_("user_accounts") \
                .select("account_number") \
                .eq("user_id", user_id) \
                .eq("is_test_mode", is_test_mode) \
                .eq("is_active", True) \
                .execute()
            
            account_number = account_result.data[0]['account_number'] if account_result.data else ""
            
            return {
                "app_key": app_key,
                "app_secret": app_secret,
                "account_number": account_number
            }
        except Exception as e:
            print(f"Error getting user keys: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    async def get_token(self, user_id: str):
        """사용자별 액세스 토큰 발급"""
        # 캐시된 토큰이 있으면 반환
        if user_id in self.tokens:
            return self.tokens[user_id]
            
        keys = await self.get_user_keys(user_id)
        
        url = f"{self.base_url}/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": keys["app_key"],
            "appsecret": keys["app_secret"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body)
            data = response.json()
            token = data.get("access_token")
            self.tokens[user_id] = token
            return token
            
    async def get_current_price(self, stock_code: str, user_id: str = None):
        """실제 현재가 조회"""
        # 공개 API는 인증 불필요
        url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
        
        headers = {
            "content-type": "application/json",
            "tr_id": "FHKST01010100"
        }
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                return response.json()
        except:
            # 실패 시 Mock 데이터 반환
            return {
                "output": {
                    "stck_prpr": "71900",
                    "prdy_vrss": "-500",
                    "prdy_ctrt": "-0.69"
                }
            }
            
    async def place_order(self, order: OrderRequest):
        """실제 주문 실행"""
        # 사용자 키 가져오기
        keys = await self.get_user_keys(order.user_id)
        token = await self.get_token(order.user_id)
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": keys["app_key"],
            "appsecret": keys["app_secret"],
            "tr_id": "VTTC0802U" if order.order_type == "buy" else "VTTC0801U"
        }
        
        body = {
            "CANO": keys["account_number"][:8],  # 계좌번호 앞 8자리
            "ACNT_PRDT_CD": keys["account_number"][8:10] if len(keys["account_number"]) > 8 else "01",
            "PDNO": order.stock_code,
            "ORD_DVSN": order.order_method,
            "ORD_QTY": str(order.quantity),
            "ORD_UNPR": str(order.price) if order.price > 0 else "0"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)
            return response.json()

# API 인스턴스
kiwoom = KiwoomAPI()

@app.get("/")
async def root():
    return {
        "service": "Kiwoom REST API Bridge",
        "status": "running",
        "version": "3.0.0",
        "mode": "supabase_integrated",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/market/current-price")
async def get_current_price(request: CurrentPriceRequest):
    """현재가 조회"""
    try:
        result = await kiwoom.get_current_price(request.stock_code, request.user_id)
        return {"success": True, "data": result}
    except Exception as e:
        print(f"Error: {e}")
        # 에러 시 Mock 데이터 반환
        return {
            "success": True,
            "data": {
                "output": {
                    "stck_prpr": "71900",
                    "prdy_vrss": "-500"
                }
            }
        }

@app.post("/api/trading/order")
async def place_order(order: OrderRequest):
    """주문 실행 - Supabase에서 사용자 API 키 조회"""
    try:
        # 실제 주문 실행
        result = await kiwoom.place_order(order)
        
        # 주문 내역 Supabase에 저장
        supabase.table("trading_orders").insert({
            "user_id": order.user_id,
            "stock_code": order.stock_code,
            "order_type": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "status": "completed",
            "order_response": result
        }).execute()
        
        return {"success": True, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Order error: {e}")
        # Mock 응답
        return {
            "success": True,
            "message": "Mock order (API keys not found)",
            "data": {
                "order_id": "MOCK123456",
                "stock_code": order.stock_code
            }
        }

@app.post("/api/test")
def test():
    return {"success": True, "message": "Test OK"}

# 백테스트 라우터 추가
try:
    from backtest_api import router as backtest_router
    app.include_router(backtest_router)
except ImportError:
    print("Backtest module not found. Skipping...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)