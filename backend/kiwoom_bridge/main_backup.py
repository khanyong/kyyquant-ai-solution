"""
키움증권 REST API Bridge Server
시놀로지 NAS에서 실행되는 FastAPI 서버
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import aiohttp
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
from supabase import create_client, Client

# 환경변수 로드
load_dotenv()

app = FastAPI(
    title="키움증권 REST API Bridge",
    description="Kiwoom Securities REST API Bridge for Auto Trading",
    version="1.0.0"
)

# CORS 설정 - Vercel 도메인 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3002",
        "https://*.vercel.app",  # Vercel 배포 도메인
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# === Models ===
class TokenRequest(BaseModel):
    """토큰 요청 모델"""
    user_id: str
    is_test_mode: bool = True

class OrderRequest(BaseModel):
    """주문 요청 모델"""
    user_id: str
    stock_code: str  # 종목코드
    order_type: str  # buy/sell
    quantity: int    # 수량
    price: int       # 가격 (0이면 시장가)
    order_method: str = "00"  # 00:지정가, 01:시장가

class CurrentPriceRequest(BaseModel):
    """현재가 조회 요청"""
    stock_code: str
    
class BalanceRequest(BaseModel):
    """잔고 조회 요청"""
    user_id: str

# === 키움 API 클라이언트 ===
class KiwoomAPI:
    """키움증권 REST API 클라이언트"""
    
    def __init__(self):
        self.test_base_url = "https://openapivts.koreainvestment.com:29443"  # 모의투자
        self.live_base_url = "https://openapi.koreainvestment.com:9443"      # 실전투자
        self.tokens = {}  # 사용자별 토큰 캐시
        
    async def get_user_keys(self, user_id: str, is_test_mode: bool) -> Dict:
        """Supabase에서 사용자 API 키 가져오기"""
        try:
            # API 키 조회
            result = await asyncio.to_thread(
                supabase.from_("user_api_keys")
                .select("*")
                .eq("user_id", user_id)
                .eq("provider", "kiwoom")
                .eq("is_test_mode", is_test_mode)
                .eq("is_active", True)
                .execute
            )
            
            if not result.data:
                raise HTTPException(status_code=404, detail="API keys not found")
            
            keys = {}
            for key_data in result.data:
                # Base64 디코딩
                decoded_value = key_data["encrypted_value"]
                if key_data["key_type"] == "app_key":
                    keys["app_key"] = decoded_value
                elif key_data["key_type"] == "app_secret":
                    keys["app_secret"] = decoded_value
                elif key_data["key_type"] == "account_number":
                    keys["account_number"] = decoded_value
                    
            if "app_key" not in keys or "app_secret" not in keys:
                raise HTTPException(status_code=400, detail="Required API keys missing")
                
            return keys
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_access_token(self, user_id: str, is_test_mode: bool) -> str:
        """접근 토큰 발급"""
        # 캐시 확인
        cache_key = f"{user_id}_{is_test_mode}"
        if cache_key in self.tokens:
            token_data = self.tokens[cache_key]
            if datetime.now() < token_data["expires_at"]:
                return token_data["access_token"]
        
        # 사용자 키 가져오기
        keys = await self.get_user_keys(user_id, is_test_mode)
        base_url = self.test_base_url if is_test_mode else self.live_base_url
        
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/oauth2/tokenP"
            headers = {"content-type": "application/json"}
            body = {
                "grant_type": "client_credentials",
                "appkey": keys["app_key"],
                "appsecret": keys["app_secret"]
            }
            
            async with session.post(url, headers=headers, json=body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
                    
                data = await response.json()
                
                # 토큰 캐싱
                self.tokens[cache_key] = {
                    "access_token": data["access_token"],
                    "expires_at": datetime.now() + timedelta(seconds=data.get("expires_in", 86400)),
                    "app_key": keys["app_key"],
                    "app_secret": keys["app_secret"],
                    "account_number": keys.get("account_number")
                }
                
                return data["access_token"]
    
    async def get_hashkey(self, body: dict, app_key: str, app_secret: str) -> str:
        """해시키 생성"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.test_base_url}/uapi/hashkey"
            headers = {
                "content-type": "application/json",
                "appkey": app_key,
                "appsecret": app_secret
            }
            
            async with session.post(url, headers=headers, json=body) as response:
                data = await response.json()
                return data.get("HASH", "")
    
    async def get_current_price(self, stock_code: str, is_test_mode: bool = True) -> Dict:
        """현재가 조회"""
        base_url = self.test_base_url if is_test_mode else self.live_base_url
        
        # 임시 app_key, app_secret (실제로는 공통 키 사용)
        app_key = os.getenv("KIWOOM_APP_KEY", "")
        app_secret = os.getenv("KIWOOM_APP_SECRET", "")
        
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {await self.get_access_token('system', is_test_mode)}",
                "appkey": app_key,
                "appsecret": app_secret,
                "tr_id": "FHKST01010100" if not is_test_mode else "VTTC0802U"
            }
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": stock_code
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
                    
                return await response.json()
    
    async def place_order(self, user_id: str, order: OrderRequest, is_test_mode: bool) -> Dict:
        """주문 실행"""
        # 사용자 정보 가져오기
        cache_key = f"{user_id}_{is_test_mode}"
        if cache_key not in self.tokens:
            await self.get_access_token(user_id, is_test_mode)
        
        token_data = self.tokens[cache_key]
        base_url = self.test_base_url if is_test_mode else self.live_base_url
        
        # 계좌번호 파싱 (예: "12345678-01" -> CANO: "12345678", ACNT_PRDT_CD: "01")
        account_parts = token_data["account_number"].split("-")
        
        body = {
            "CANO": account_parts[0],  # 계좌번호
            "ACNT_PRDT_CD": account_parts[1] if len(account_parts) > 1 else "01",  # 상품코드
            "PDNO": order.stock_code,  # 종목코드
            "ORD_DVSN": order.order_method,  # 주문구분
            "ORD_QTY": str(order.quantity),  # 주문수량
            "ORD_UNPR": str(order.price) if order.price > 0 else "0"  # 주문단가
        }
        
        # 해시키 생성
        hashkey = await self.get_hashkey(body, token_data["app_key"], token_data["app_secret"])
        
        async with aiohttp.ClientSession() as session:
            # TR_ID 설정 (모의/실전, 매수/매도에 따라 다름)
            if is_test_mode:
                tr_id = "VTTC0802U" if order.order_type == "buy" else "VTTC0801U"
            else:
                tr_id = "TTTC0802U" if order.order_type == "buy" else "TTTC0801U"
            
            url = f"{base_url}/uapi/domestic-stock/v1/trading/order-cash"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token_data['access_token']}",
                "appkey": token_data["app_key"],
                "appsecret": token_data["app_secret"],
                "tr_id": tr_id,
                "hashkey": hashkey
            }
            
            async with session.post(url, headers=headers, json=body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
                    
                result = await response.json()
                
                # 주문 기록 저장
                await asyncio.to_thread(
                    supabase.table("trading_orders")
                    .insert({
                        "user_id": user_id,
                        "stock_code": order.stock_code,
                        "order_type": order.order_type,
                        "quantity": order.quantity,
                        "price": order.price,
                        "order_method": order.order_method,
                        "is_test_mode": is_test_mode,
                        "order_response": result,
                        "created_at": datetime.now().isoformat()
                    })
                    .execute
                )
                
                return result
    
    async def get_balance(self, user_id: str, is_test_mode: bool) -> Dict:
        """계좌 잔고 조회"""
        # 토큰 가져오기
        cache_key = f"{user_id}_{is_test_mode}"
        if cache_key not in self.tokens:
            await self.get_access_token(user_id, is_test_mode)
        
        token_data = self.tokens[cache_key]
        base_url = self.test_base_url if is_test_mode else self.live_base_url
        account_parts = token_data["account_number"].split("-")
        
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token_data['access_token']}",
                "appkey": token_data["app_key"],
                "appsecret": token_data["app_secret"],
                "tr_id": "VTTC8434R" if is_test_mode else "TTTC8434R"
            }
            params = {
                "CANO": account_parts[0],
                "ACNT_PRDT_CD": account_parts[1] if len(account_parts) > 1 else "01",
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
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
                    
                return await response.json()

# API 인스턴스
kiwoom_api = KiwoomAPI()

# === API Endpoints ===

@app.get("/")
async def root():
    """헬스체크"""
    return {
        "service": "Kiwoom REST API Bridge",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/test")
async def test_endpoint():
    """테스트 엔드포인트 - 의존성 없음"""
    return {
        "success": True,
        "message": "Test endpoint working",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/test/echo")
async def test_echo(data: dict):
    """에코 테스트 - 받은 데이터 그대로 반환"""
    return {
        "success": True,
        "received": data,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/token")
async def get_token(request: TokenRequest):
    """접근 토큰 발급"""
    try:
        token = await kiwoom_api.get_access_token(request.user_id, request.is_test_mode)
        return {
            "success": True,
            "access_token": token,
            "mode": "test" if request.is_test_mode else "live"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market/current-price")
async def get_current_price(request: CurrentPriceRequest):
    """현재가 조회"""
    try:
        print(f"[DEBUG] Received request: {request.stock_code}")
        
        # 테스트용 Mock 데이터 반환
        # TODO: 실제 키움 API 연동 시 kiwoom_api.get_current_price() 사용
        mock_result = {
            "rt_cd": "0",
            "msg_cd": "OPSP0000",
            "msg1": "정상처리 되었습니다.",
            "output": {
                "stck_prpr": "71900",  # 현재가
                "prdy_vrss": "-500",    # 전일대비
                "prdy_ctrt": "-0.69",   # 전일대비율
                "stck_oprc": "72400",  # 시가
                "stck_hgpr": "72500",  # 고가
                "stck_lwpr": "71800",  # 저가
                "stck_sdpr": "72400",  # 기준가(전일종가)
                "acml_vol": "1234567",  # 누적거래량
                "stck_mxpr": "93500",  # 상한가
                "stck_llam": "50900"   # 하한가
            }
        }
        
        print(f"[DEBUG] Returning mock data")
        return {
            "success": True,
            "data": mock_result
        }
        
        # 실제 API 호출 코드 (추후 활성화)
        # result = await kiwoom_api.get_current_price(request.stock_code)
        # return {
        #     "success": True,
        #     "data": result
        # }
    except Exception as e:
        print(f"[ERROR] Exception in get_current_price: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trading/order")
async def place_order(order: OrderRequest):
    """주문 실행"""
    try:
        # 사용자 모드 확인
        mode_result = await asyncio.to_thread(
            supabase.rpc("get_current_mode_info", {"p_user_id": order.user_id}).execute
        )
        
        is_test_mode = mode_result.data.get("current_mode", "test") == "test"
        
        result = await kiwoom_api.place_order(order.user_id, order, is_test_mode)
        return {
            "success": True,
            "mode": "test" if is_test_mode else "live",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/account/balance")
async def get_balance(request: BalanceRequest):
    """계좌 잔고 조회"""
    try:
        # 사용자 모드 확인
        mode_result = await asyncio.to_thread(
            supabase.rpc("get_current_mode_info", {"p_user_id": request.user_id}).execute
        )
        
        is_test_mode = mode_result.data.get("current_mode", "test") == "test"
        
        result = await kiwoom_api.get_balance(request.user_id, is_test_mode)
        return {
            "success": True,
            "mode": "test" if is_test_mode else "live",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{user_id}")
async def get_orders(user_id: str, limit: int = 10):
    """주문 내역 조회"""
    try:
        result = await asyncio.to_thread(
            supabase.table("trading_orders")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute
        )
        
        return {
            "success": True,
            "data": result.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# N8N Webhook endpoints
@app.post("/webhook/n8n/signal")
async def n8n_trading_signal(data: Dict[str, Any]):
    """N8N에서 전송한 매매 신호 처리"""
    try:
        # 매매 신호 처리 로직
        signal_type = data.get("signal_type")  # buy/sell
        stock_code = data.get("stock_code")
        user_id = data.get("user_id")
        quantity = data.get("quantity", 1)
        
        if signal_type and stock_code and user_id:
            order = OrderRequest(
                user_id=user_id,
                stock_code=stock_code,
                order_type=signal_type,
                quantity=quantity,
                price=0,  # 시장가
                order_method="01"  # 시장가
            )
            
            result = await place_order(order)
            return {
                "success": True,
                "message": f"Order placed for {stock_code}",
                "result": result
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid signal data")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)