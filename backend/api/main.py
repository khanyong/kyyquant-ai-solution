"""
키움 자동매매 시스템 - 메인 서버
Python Backend (FastAPI) + Kiwoom OpenAPI+
"""

import sys
import asyncio
import threading
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal

from scripts.kiwoom.kiwoom_api import KiwoomAPI
from api.backend_api import (
    LoginRequest, OrderRequest, StockInfoRequest, BalanceRequest,
    broadcast_real_data
)

# Global instances
kiwoom_api: Optional[KiwoomAPI] = None
qt_app: Optional[QApplication] = None
qt_thread: Optional[QThread] = None


class KiwoomThread(QThread):
    """키움 API를 별도 스레드에서 실행"""
    data_received = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.kiwoom = None
        
    def run(self):
        """Qt 이벤트 루프 실행"""
        self.kiwoom = KiwoomAPI()
        if self.kiwoom.comm_connect():
            print("키움 API 연결 성공")
            # Qt 이벤트 루프 실행
            self.exec_()
        else:
            print("키움 API 연결 실패")
    
    def get_api(self):
        return self.kiwoom


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    global kiwoom_api, qt_app, qt_thread
    
    print("Starting Kiwoom API in background thread...")
    
    # Qt Application은 메인 스레드에서 실행되어야 함
    # 별도 스레드에서 키움 API 실행
    def run_qt():
        global qt_app, kiwoom_api
        qt_app = QApplication(sys.argv)
        kiwoom_api = KiwoomAPI()
        
        if kiwoom_api.comm_connect():
            print("✓ 키움 API 연결 성공")
        else:
            print("✗ 키움 API 연결 실패")
        
        qt_app.exec_()
    
    # Qt를 별도 스레드에서 실행
    qt_thread = threading.Thread(target=run_qt, daemon=True)
    qt_thread.start()
    
    # Qt 초기화 대기
    await asyncio.sleep(3)
    
    yield
    
    # Shutdown
    print("Shutting down Kiwoom API...")
    if qt_app:
        qt_app.quit()


# FastAPI 앱 생성
app = FastAPI(
    title="키움 자동매매 시스템 API",
    description="Kiwoom OpenAPI+ Backend Server",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
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

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

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
        "message": "키움 자동매매 시스템 API Server",
        "kiwoom_connected": kiwoom_api is not None and kiwoom_api.connected
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "kiwoom_api": "connected" if kiwoom_api and kiwoom_api.connected else "disconnected"
    }


@app.post("/api/login")
async def login(request: LoginRequest):
    """로그인 처리"""
    if not kiwoom_api:
        raise HTTPException(status_code=503, detail="Kiwoom API not initialized")
    
    if not kiwoom_api.connected:
        success = kiwoom_api.comm_connect()
        if not success:
            raise HTTPException(status_code=401, detail="Login failed")
    
    accounts = kiwoom_api.get_account_list()
    user_id = kiwoom_api.get_login_info("USER_ID")
    user_name = kiwoom_api.get_login_info("USER_NAME")
    
    return {
        "success": True,
        "accounts": accounts,
        "user_id": user_id,
        "user_name": user_name,
        "server_type": "모의투자" if request.demo_mode else "실거래"
    }


@app.get("/api/accounts")
async def get_accounts():
    """계좌 목록 조회"""
    if not kiwoom_api or not kiwoom_api.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    accounts = kiwoom_api.get_account_list()
    return {"accounts": accounts}


@app.post("/api/balance")
async def get_balance(request: BalanceRequest):
    """계좌 잔고 조회"""
    if not kiwoom_api or not kiwoom_api.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    try:
        kiwoom_api.request_balance(request.account_no)
        await asyncio.sleep(1)  # 응답 대기
        
        balance = kiwoom_api.tr_data.get('balance', [])
        return {
            "account_no": request.account_no,
            "holdings": balance.to_dict('records') if hasattr(balance, 'to_dict') else [],
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stock-info")
async def get_stock_info(request: StockInfoRequest):
    """주식 정보 조회"""
    if not kiwoom_api or not kiwoom_api.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    try:
        kiwoom_api.request_stock_info(request.stock_code)
        await asyncio.sleep(1)  # 응답 대기
        
        info = kiwoom_api.tr_data.get('stock_info', {})
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/order")
async def place_order(request: OrderRequest):
    """주문 실행"""
    if not kiwoom_api or not kiwoom_api.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    try:
        order_type = 1 if request.order_type == "buy" else 2
        price_type = "00" if request.order_method == "limit" else "03"
        
        result = kiwoom_api.send_order(
            rq_name=f"order_{request.stock_code}",
            screen_no="5000",
            acc_no=request.account_no,
            order_type=order_type,
            code=request.stock_code,
            qty=request.quantity,
            price=request.price,
            hoga_gb=price_type
        )
        
        return {
            "success": result == 0,
            "order": request.dict(),
            "message": "주문 전송 완료" if result == 0 else "주문 실패"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/markets/{market}/stocks")
async def get_market_stocks(market: str, limit: int = 50):
    """시장별 종목 조회"""
    if not kiwoom_api or not kiwoom_api.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    try:
        market_code = "0" if market.upper() == "KOSPI" else "10"
        codes = kiwoom_api.get_code_list_by_market(market_code)
        
        stocks = []
        for code in codes[:limit]:
            name = kiwoom_api.get_master_code_name(code)
            if name:
                stocks.append({
                    "code": code,
                    "name": name,
                    "market": market.upper()
                })
        
        return {
            "market": market.upper(),
            "count": len(stocks),
            "total": len(codes),
            "stocks": stocks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 데이터 WebSocket"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 클라이언트 메시지 수신
            data = await websocket.receive_text()
            
            # 메시지 처리 (구독/구독해제 등)
            import json
            msg = json.loads(data)
            
            if msg.get("type") == "subscribe":
                stock_code = msg.get("stock_code")
                if stock_code and kiwoom_api:
                    # 실시간 데이터 등록
                    kiwoom_api.set_real_reg("1000", stock_code, "10;11;12;13", "0")
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "stock_code": stock_code
                    }))
            
            # 실시간 데이터 전송
            if kiwoom_api and kiwoom_api.real_data:
                await websocket.send_text(json.dumps({
                    "type": "real_data",
                    "data": kiwoom_api.real_data
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Qt와 충돌 방지
        log_level="info"
    )