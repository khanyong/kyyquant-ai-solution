"""
Production-ready API Server with proper structure
"""
import asyncio
import json
import random
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from models import (
    LoginRequest, LoginResponse,
    OrderRequest, OrderResponse,
    StockInfoRequest, StockInfo,
    BalanceRequest, BalanceResponse,
    Portfolio, MarketStocksResponse,
    HealthResponse, WebSocketMessage, RealTimeData
)

# ==================== Configuration ====================
class Settings:
    """Application settings"""
    APP_NAME = "KyyQuant AI Solution"
    VERSION = "1.0.0"
    DEBUG = True
    
    # CORS settings
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:5173",
        "http://localhost:5174"
    ]
    
    # Mock data for development
    MOCK_MODE = True  # Set to False when using real Kiwoom API

settings = Settings()

# ==================== Mock Data ====================
MOCK_ACCOUNTS = ["12345678", "87654321"]
MOCK_USER = {
    "id": "testuser",
    "name": "테스트 사용자",
}

MOCK_STOCKS = {
    "005930": StockInfo(code="005930", name="삼성전자", price=71000, change=-500, changeRate=-0.7, volume=15234567),
    "000660": StockInfo(code="000660", name="SK하이닉스", price=128500, change=1500, changeRate=1.18, volume=3456789),
    "035720": StockInfo(code="035720", name="카카오", price=45200, change=300, changeRate=0.67, volume=2345678),
    "035420": StockInfo(code="035420", name="NAVER", price=215000, change=-2000, changeRate=-0.92, volume=876543),
}

MOCK_PORTFOLIO = [
    Portfolio(
        stockCode="005930",
        stockName="삼성전자",
        quantity=100,
        avgPrice=70000,
        currentPrice=71000,
        profitLoss=100000,
        profitLossRate=1.43
    ),
    Portfolio(
        stockCode="000660",
        stockName="SK하이닉스",
        quantity=50,
        avgPrice=130000,
        currentPrice=128500,
        profitLoss=-75000,
        profitLossRate=-1.15
    )
]

# ==================== WebSocket Manager ====================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()
        print(f"✅ Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        print(f"❌ Client disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    def subscribe(self, websocket: WebSocket, stock_code: str):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(stock_code)

    def unsubscribe(self, websocket: WebSocket, stock_code: str):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(stock_code)

manager = ConnectionManager()

# ==================== Application Lifespan ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    print(f"\n{'='*50}")
    print(f"{settings.APP_NAME} v{settings.VERSION}")
    print(f"Mode: {'Development (Mock)' if settings.MOCK_MODE else 'Production'}")
    print(f"{'='*50}\n")
    
    # Start background tasks
    asyncio.create_task(generate_mock_real_time_data())
    
    yield
    
    print("\n👋 Shutting down server...")

# ==================== FastAPI Application ====================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Algorithmic Trading Platform API",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Exception Handlers ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# ==================== API Endpoints ====================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "application": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "mode": "mock" if settings.MOCK_MODE else "production",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        kiwoom_api="mock" if settings.MOCK_MODE else "connected",
        timestamp=datetime.now(),
        mode="development" if settings.DEBUG else "production"
    )

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login"""
    if settings.MOCK_MODE:
        # Mock login - always successful
        return LoginResponse(
            success=True,
            message="로그인 성공 (Mock)",
            user_id=MOCK_USER["id"],
            user_name=MOCK_USER["name"],
            accounts=MOCK_ACCOUNTS,
            server_type="모의투자" if request.demo_mode else "실거래"
        )
    else:
        # Real Kiwoom API login would go here
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Real Kiwoom API not implemented"
        )

@app.get("/api/accounts", response_model=dict)
async def get_accounts():
    """Get account list"""
    if settings.MOCK_MODE:
        return {"accounts": MOCK_ACCOUNTS}
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Real Kiwoom API not implemented"
        )

@app.post("/api/balance", response_model=BalanceResponse)
async def get_balance(request: BalanceRequest):
    """Get account balance"""
    if settings.MOCK_MODE:
        total_value = sum(p.currentPrice * p.quantity for p in MOCK_PORTFOLIO)
        total_profit_loss = sum(p.profitLoss for p in MOCK_PORTFOLIO)
        
        return BalanceResponse(
            account_no=request.account_no,
            holdings=MOCK_PORTFOLIO,
            total_value=total_value,
            total_profit_loss=total_profit_loss,
            timestamp=datetime.now()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Real Kiwoom API not implemented"
        )

@app.post("/api/stock-info", response_model=StockInfo)
async def get_stock_info(request: StockInfoRequest):
    """Get stock information"""
    if settings.MOCK_MODE:
        stock = MOCK_STOCKS.get(request.stock_code)
        if not stock:
            # Return default if not found
            return MOCK_STOCKS["005930"]
        return stock
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Real Kiwoom API not implemented"
        )

@app.post("/api/order", response_model=OrderResponse)
async def place_order(request: OrderRequest):
    """Place an order"""
    if settings.MOCK_MODE:
        # Mock order - always successful
        order_no = f"MOCK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return OrderResponse(
            success=True,
            message=f"주문 성공: {request.order_type} {request.quantity}주 @ {request.price}원",
            order_no=order_no,
            order=request
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Real Kiwoom API not implemented"
        )

@app.get("/api/markets/{market}/stocks", response_model=MarketStocksResponse)
async def get_market_stocks(market: str, limit: int = 50):
    """Get stocks by market"""
    if settings.MOCK_MODE:
        stocks_list = list(MOCK_STOCKS.values())[:limit]
        return MarketStocksResponse(
            market=market.upper(),
            count=len(stocks_list),
            total=len(MOCK_STOCKS),
            stocks=stocks_list
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Real Kiwoom API not implemented"
        )

# ==================== WebSocket Endpoint ====================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time data"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            raw_data = await websocket.receive_text()
            
            try:
                data = json.loads(raw_data)
                message = WebSocketMessage(**data)
                
                # Handle different message types
                if message.type == "subscribe" and message.stock_code:
                    manager.subscribe(websocket, message.stock_code)
                    response = WebSocketMessage(
                        type="subscribed",
                        stock_code=message.stock_code,
                        message=f"Subscribed to {message.stock_code}"
                    )
                    await websocket.send_text(response.json())
                    
                elif message.type == "unsubscribe" and message.stock_code:
                    manager.unsubscribe(websocket, message.stock_code)
                    response = WebSocketMessage(
                        type="unsubscribed",
                        stock_code=message.stock_code,
                        message=f"Unsubscribed from {message.stock_code}"
                    )
                    await websocket.send_text(response.json())
                    
                elif message.type == "ping":
                    response = WebSocketMessage(type="pong")
                    await websocket.send_text(response.json())
                    
            except json.JSONDecodeError:
                error_response = WebSocketMessage(
                    type="error",
                    message="Invalid JSON format"
                )
                await websocket.send_text(error_response.json())
            except Exception as e:
                error_response = WebSocketMessage(
                    type="error",
                    message=str(e)
                )
                await websocket.send_text(error_response.json())
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ==================== Background Tasks ====================
async def generate_mock_real_time_data():
    """Generate mock real-time data for subscribed stocks"""
    while True:
        await asyncio.sleep(2)  # Send data every 2 seconds
        
        for websocket, stock_codes in manager.subscriptions.items():
            for stock_code in stock_codes:
                if stock_code in MOCK_STOCKS:
                    stock = MOCK_STOCKS[stock_code]
                    
                    # Generate random price changes
                    price_change = random.randint(-100, 100)
                    new_price = stock.price + price_change
                    
                    real_time_data = RealTimeData(
                        code=stock_code,
                        time=datetime.now(),
                        price=new_price,
                        change=price_change,
                        changeRate=round((price_change / stock.price) * 100, 2),
                        volume=random.randint(1000, 10000),
                        totalVolume=stock.volume + random.randint(0, 100000)
                    )
                    
                    message = WebSocketMessage(
                        type="real_data",
                        stock_code=stock_code,
                        data=real_time_data.dict()
                    )
                    
                    await manager.send_personal_message(message.json(), websocket)

# ==================== Main ====================
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )