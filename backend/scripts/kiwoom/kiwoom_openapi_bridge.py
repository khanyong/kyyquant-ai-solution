"""
키움 OpenAPI Bridge Server
32비트 Python 환경에서 실행되며, REST API와 WebSocket을 제공
"""

import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
import pythoncom
import win32com.client
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="키움 OpenAPI Bridge Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 모델 정의
class LoginRequest(BaseModel):
    mock_trading: bool = True

class OrderRequest(BaseModel):
    account: str
    stock_code: str
    order_type: int  # 1:매수, 2:매도
    quantity: int
    price: int
    price_type: str = "00"  # 00:지정가, 03:시장가

class StockRequest(BaseModel):
    stock_code: str

class RealtimeSubscribe(BaseModel):
    stock_codes: List[str]
    subscribe: bool = True

# 키움 OpenAPI 래퍼 클래스
class KiwoomOpenAPI:
    def __init__(self):
        self.ocx = None
        self.connected = False
        self.account_list = []
        self.realtime_stocks = set()
        
    def initialize(self):
        """COM 객체 초기화"""
        try:
            pythoncom.CoInitialize()
            self.ocx = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
            logger.info("키움 OpenAPI OCX 초기화 성공")
            return True
        except Exception as e:
            logger.error(f"OCX 초기화 실패: {e}")
            return False
    
    def connect(self):
        """로그인"""
        if not self.ocx:
            return False
        
        try:
            ret = self.ocx.CommConnect()
            if ret == 0:
                # 로그인 창이 뜨고 사용자가 로그인하기를 기다림
                import time
                time.sleep(5)  # 로그인 대기
                
                # 계좌 정보 가져오기
                account_str = self.ocx.GetLoginInfo("ACCLIST")
                if account_str:
                    self.account_list = [acc for acc in account_str.split(';') if acc]
                    self.connected = True
                    logger.info(f"로그인 성공. 계좌: {self.account_list}")
                    return True
            return False
        except Exception as e:
            logger.error(f"로그인 실패: {e}")
            return False
    
    def get_account_info(self):
        """계좌 정보 조회"""
        if not self.connected:
            return None
        
        return {
            "accounts": self.account_list,
            "user_id": self.ocx.GetLoginInfo("USER_ID"),
            "user_name": self.ocx.GetLoginInfo("USER_NAME"),
            "server": "모의투자" if self.ocx.GetLoginInfo("GetServerGubun") == "1" else "실거래"
        }
    
    def get_stock_info(self, stock_code: str):
        """종목 정보 조회"""
        if not self.connected:
            return None
        
        try:
            # 종목명
            stock_name = self.ocx.GetMasterCodeName(stock_code)
            
            # 현재가 조회 (opt10001)
            self.ocx.SetInputValue("종목코드", stock_code)
            ret = self.ocx.CommRqData("주식기본정보", "opt10001", 0, "0101")
            
            if ret == 0:
                # 데이터 수신 대기 (실제로는 이벤트 처리 필요)
                import time
                time.sleep(0.5)
                
                return {
                    "code": stock_code,
                    "name": stock_name,
                    "market": self.ocx.GetMasterStockState(stock_code)
                }
        except Exception as e:
            logger.error(f"종목 정보 조회 실패: {e}")
            return None
    
    def send_order(self, order: OrderRequest):
        """주문 전송"""
        if not self.connected:
            return {"success": False, "message": "Not connected"}
        
        try:
            ret = self.ocx.SendOrder(
                "주문",  # 사용자 구분명
                "0101",  # 화면번호
                order.account,  # 계좌번호
                order.order_type,  # 주문유형
                order.stock_code,  # 종목코드
                order.quantity,  # 수량
                order.price,  # 가격
                order.price_type,  # 호가구분
                ""  # 원주문번호 (정정/취소시 사용)
            )
            
            if ret == 0:
                return {"success": True, "message": "주문 전송 성공"}
            else:
                return {"success": False, "message": f"주문 전송 실패: {ret}"}
        except Exception as e:
            logger.error(f"주문 전송 오류: {e}")
            return {"success": False, "message": str(e)}
    
    def subscribe_realtime(self, stock_codes: List[str]):
        """실시간 시세 구독"""
        if not self.connected:
            return False
        
        try:
            for code in stock_codes:
                if code not in self.realtime_stocks:
                    # FID: 현재가(10), 전일대비(11), 등락율(12), 거래량(13)
                    self.ocx.SetRealReg(
                        f"1000{len(self.realtime_stocks)}",
                        code,
                        "10;11;12;13;14;15;16;17;18;20;21",
                        "0" if len(self.realtime_stocks) == 0 else "1"
                    )
                    self.realtime_stocks.add(code)
                    logger.info(f"실시간 구독: {code}")
            return True
        except Exception as e:
            logger.error(f"실시간 구독 실패: {e}")
            return False

# 전역 키움 API 인스턴스
kiwoom = KiwoomOpenAPI()

# API 엔드포인트
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    if kiwoom.initialize():
        logger.info("키움 OpenAPI Bridge Server 시작")
    else:
        logger.error("키움 OpenAPI 초기화 실패")

@app.get("/")
async def root():
    """헬스 체크"""
    return {
        "status": "running",
        "connected": kiwoom.connected,
        "server": "Kiwoom OpenAPI Bridge Server"
    }

@app.post("/login")
async def login(request: LoginRequest):
    """로그인"""
    if kiwoom.connected:
        return {"success": True, "message": "Already connected"}
    
    if kiwoom.connect():
        return {
            "success": True,
            "account_info": kiwoom.get_account_info()
        }
    else:
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/accounts")
async def get_accounts():
    """계좌 정보 조회"""
    if not kiwoom.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    return kiwoom.get_account_info()

@app.post("/order")
async def send_order(order: OrderRequest):
    """주문 전송"""
    if not kiwoom.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    result = kiwoom.send_order(order)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/stock/info")
async def get_stock_info(request: StockRequest):
    """종목 정보 조회"""
    if not kiwoom.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    info = kiwoom.get_stock_info(request.stock_code)
    if not info:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return info

@app.post("/realtime/subscribe")
async def subscribe_realtime(request: RealtimeSubscribe):
    """실시간 데이터 구독"""
    if not kiwoom.connected:
        raise HTTPException(status_code=401, detail="Not connected")
    
    if request.subscribe:
        success = kiwoom.subscribe_realtime(request.stock_codes)
        return {"success": success, "subscribed": list(kiwoom.realtime_stocks)}
    else:
        # 구독 취소 로직
        for code in request.stock_codes:
            kiwoom.realtime_stocks.discard(code)
        return {"success": True, "subscribed": list(kiwoom.realtime_stocks)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 (실시간 데이터 스트리밍)"""
    await websocket.accept()
    logger.info("WebSocket 클라이언트 연결")
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 메시지 처리
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "subscribe":
                stock_codes = message.get("codes", [])
                kiwoom.subscribe_realtime(stock_codes)
                await websocket.send_json({
                    "type": "subscribed",
                    "codes": stock_codes
                })
    except WebSocketDisconnect:
        logger.info("WebSocket 클라이언트 연결 종료")

if __name__ == "__main__":
    # QApplication 필요 (PyQt5)
    qt_app = QApplication(sys.argv)
    
    # 서버 실행
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8100,
        log_level="info"
    )