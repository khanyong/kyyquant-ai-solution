from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Import the Kiwoom API wrapper
from scripts.kiwoom.kiwoom_api import KiwoomAPI

# Data models
class LoginRequest(BaseModel):
    account_no: Optional[str] = None
    password: Optional[str] = None
    demo_mode: bool = True

class OrderRequest(BaseModel):
    account_no: str
    stock_code: str
    order_type: str  # buy/sell
    quantity: int
    price: int
    order_method: str = "limit"  # limit/market

class StockInfoRequest(BaseModel):
    stock_code: str

class BalanceRequest(BaseModel):
    account_no: str

# Global variables
kiwoom: Optional[KiwoomAPI] = None
connected_clients: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global kiwoom
    print("Initializing Kiwoom API...")
    # Note: Kiwoom API requires Qt event loop, handled separately
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API Endpoints
@app.get("/")
async def root():
    return {"message": "Kiwoom Trading API Server", "status": "running"}

@app.post("/api/login")
async def login(request: LoginRequest):
    """로그인 및 API 연결"""
    try:
        if not kiwoom:
            return {"success": False, "message": "Kiwoom API not initialized"}
        
        # Perform login
        success = kiwoom.comm_connect()
        
        if success:
            accounts = kiwoom.get_account_list()
            return {
                "success": True,
                "message": "Login successful",
                "accounts": accounts,
                "user_id": kiwoom.get_login_info("USER_ID"),
                "user_name": kiwoom.get_login_info("USER_NAME")
            }
        else:
            return {"success": False, "message": "Login failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts")
async def get_accounts():
    """계좌 목록 조회"""
    try:
        if not kiwoom or not kiwoom.connected:
            raise HTTPException(status_code=401, detail="Not connected to Kiwoom API")
        
        accounts = kiwoom.get_account_list()
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/balance")
async def get_balance(request: BalanceRequest):
    """계좌 잔고 조회"""
    try:
        if not kiwoom or not kiwoom.connected:
            raise HTTPException(status_code=401, detail="Not connected to Kiwoom API")
        
        kiwoom.request_balance(request.account_no)
        # Wait for response (implement proper async handling)
        await asyncio.sleep(1)
        
        balance_data = kiwoom.tr_data.get('balance', [])
        return {
            "account_no": request.account_no,
            "balance": balance_data.to_dict('records') if hasattr(balance_data, 'to_dict') else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock-info")
async def get_stock_info(request: StockInfoRequest):
    """주식 기본 정보 조회"""
    try:
        if not kiwoom or not kiwoom.connected:
            raise HTTPException(status_code=401, detail="Not connected to Kiwoom API")
        
        kiwoom.request_stock_info(request.stock_code)
        # Wait for response
        await asyncio.sleep(1)
        
        stock_info = kiwoom.tr_data.get('stock_info', {})
        return stock_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/order")
async def place_order(request: OrderRequest):
    """주문 실행"""
    try:
        if not kiwoom or not kiwoom.connected:
            raise HTTPException(status_code=401, detail="Not connected to Kiwoom API")
        
        # Convert order type
        order_type_code = 1 if request.order_type == "buy" else 2
        hoga_gb = "00" if request.order_method == "limit" else "03"
        
        result = kiwoom.send_order(
            rq_name=f"{request.order_type}_{request.stock_code}",
            screen_no="5000",
            acc_no=request.account_no,
            order_type=order_type_code,
            code=request.stock_code,
            qty=request.quantity,
            price=request.price,
            hoga_gb=hoga_gb
        )
        
        return {
            "success": result == 0,
            "message": "Order placed successfully" if result == 0 else "Order failed",
            "order_details": request.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-codes/{market}")
async def get_market_codes(market: str):
    """시장별 종목 코드 조회"""
    try:
        if not kiwoom or not kiwoom.connected:
            raise HTTPException(status_code=401, detail="Not connected to Kiwoom API")
        
        market_code = "0" if market.lower() == "kospi" else "10"
        codes = kiwoom.get_code_list_by_market(market_code)
        
        # Get names for each code
        stocks = []
        for code in codes[:100]:  # Limit to first 100 for performance
            name = kiwoom.get_master_code_name(code)
            if name:
                stocks.append({"code": code, "name": name})
        
        return {"market": market, "stocks": stocks, "total": len(codes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for real-time data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                stock_code = message.get("stock_code")
                if stock_code and kiwoom:
                    # Register for real-time data
                    kiwoom.set_real_reg("1000", stock_code, "10;11;12;13;14;15", "0")
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "stock_code": stock_code
                    }))
            
            elif message.get("type") == "unsubscribe":
                stock_code = message.get("stock_code")
                # Handle unsubscribe logic
                await websocket.send_text(json.dumps({
                    "type": "unsubscribed",
                    "stock_code": stock_code
                }))
            
            # Send real-time data if available
            if kiwoom and kiwoom.real_data:
                await websocket.send_text(json.dumps({
                    "type": "real_data",
                    "data": kiwoom.real_data
                }))
                
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_real_data(data: dict):
    """Broadcast real-time data to all connected clients"""
    message = json.dumps({"type": "real_data", "data": data})
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            connected_clients.remove(client)

# Run with: uvicorn backend_api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)