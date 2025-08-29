"""
키움 자동매매 시스템 - 개발용 서버 (키움 API 없이 실행)
"""

import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Mock data for development
MOCK_ACCOUNTS = ["12345678", "87654321"]
MOCK_USER = {
    "id": "testuser",
    "name": "테스트 사용자",
}

MOCK_STOCKS = [
    {"code": "005930", "name": "삼성전자", "price": 71000, "change": -500, "changeRate": -0.7, "volume": 15234567},
    {"code": "000660", "name": "SK하이닉스", "price": 128500, "change": 1500, "changeRate": 1.18, "volume": 3456789},
    {"code": "035720", "name": "카카오", "price": 45200, "change": 300, "changeRate": 0.67, "volume": 2345678},
]

MOCK_PORTFOLIO = [
    {
        "stockCode": "005930",
        "stockName": "삼성전자",
        "quantity": 100,
        "avgPrice": 70000,
        "currentPrice": 71000,
        "profitLoss": 100000,
        "profitLossRate": 1.43
    },
    {
        "stockCode": "000660",
        "stockName": "SK하이닉스",
        "quantity": 50,
        "avgPrice": 130000,
        "currentPrice": 128500,
        "profitLoss": -75000,
        "profitLossRate": -1.15
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    print("Starting development server (no Kiwoom API)...")
    yield
    print("Shutting down development server...")

# FastAPI 앱 생성
app = FastAPI(
    title="키움 자동매매 시스템 API (Dev)",
    description="Development Server - Mock Data",
    version="1.0.0-dev",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# REST API Endpoints
@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "status": "running",
        "message": "키움 자동매매 시스템 API Server (Development Mode)",
        "kiwoom_connected": False,
        "mode": "development"
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "kiwoom_api": "mock",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/login")
async def login(request: dict):
    """로그인 처리 (Mock)"""
    return {
        "success": True,
        "accounts": MOCK_ACCOUNTS,
        "user_id": MOCK_USER["id"],
        "user_name": MOCK_USER["name"],
        "server_type": "모의투자(개발)"
    }

@app.get("/api/accounts")
async def get_accounts():
    """계좌 목록 조회 (Mock)"""
    return {"accounts": MOCK_ACCOUNTS}

@app.post("/api/balance")
async def get_balance(request: dict):
    """계좌 잔고 조회 (Mock)"""
    return {
        "account_no": request.get("account_no", MOCK_ACCOUNTS[0]),
        "holdings": MOCK_PORTFOLIO,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/stock-info")
async def get_stock_info(request: dict):
    """주식 정보 조회 (Mock)"""
    stock_code = request.get("stock_code", "005930")
    
    # Find mock stock or return default
    for stock in MOCK_STOCKS:
        if stock["code"] == stock_code:
            return stock
    
    return MOCK_STOCKS[0]

@app.post("/api/order")
async def place_order(request: dict):
    """주문 실행 (Mock)"""
    return {
        "success": True,
        "order": request,
        "message": "주문이 정상적으로 접수되었습니다 (개발 모드)",
        "order_no": f"DEV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }

@app.get("/api/markets/{market}/stocks")
async def get_market_stocks(market: str, limit: int = 50):
    """시장별 종목 조회 (Mock)"""
    return {
        "market": market.upper(),
        "count": len(MOCK_STOCKS),
        "total": 100,
        "stocks": MOCK_STOCKS
    }

# WebSocket Endpoint with mock real-time data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 데이터 WebSocket (Mock)"""
    await manager.connect(websocket)
    
    try:
        # Send mock real-time data periodically
        async def send_mock_data():
            while True:
                await asyncio.sleep(2)  # Send data every 2 seconds
                
                # Generate random price changes
                for stock in MOCK_STOCKS:
                    mock_data = {
                        "type": "real_data",
                        "data": {
                            "code": stock["code"],
                            "time": datetime.now().isoformat(),
                            "price": stock["price"] + random.randint(-100, 100),
                            "change": random.randint(-1000, 1000),
                            "changeRate": round(random.uniform(-3, 3), 2),
                            "volume": random.randint(1000, 10000),
                            "totalVolume": stock["volume"] + random.randint(0, 100000)
                        }
                    }
                    
                    import json
                    await websocket.send_text(json.dumps(mock_data))
        
        # Start sending mock data
        asyncio.create_task(send_mock_data())
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            
            # Echo back subscription confirmations
            import json
            msg = json.loads(data)
            
            if msg.get("type") == "subscribe":
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "stock_code": msg.get("stock_code")
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("키움 자동매매 시스템 - 개발 서버")
    print("="*50)
    print("Mode: Development (Mock Data)")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("="*50 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )