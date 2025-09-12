"""
키움증권 REST API Bridge Server (Mock Version)
Supabase 없이 Mock 데이터만 반환
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
from backtest_api import router as backtest_router

app = FastAPI(
    title="키움증권 REST API Bridge",
    description="Kiwoom Securities REST API Bridge for Auto Trading (Mock)",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 백테스트 라우터 등록
app.include_router(backtest_router)

# === Models ===
class CurrentPriceRequest(BaseModel):
    """현재가 조회 요청"""
    stock_code: str

class OrderRequest(BaseModel):
    """주문 요청 모델"""
    user_id: str
    stock_code: str
    order_type: str  # buy/sell
    quantity: int
    price: int
    order_method: str = "00"

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
    """테스트 엔드포인트"""
    return {
        "success": True,
        "message": "Test endpoint working",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/market/current-price")
async def get_current_price(request: CurrentPriceRequest):
    """현재가 조회 - Mock 데이터 반환"""
    
    # Mock 데이터
    mock_data = {
        "success": True,
        "data": {
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
    }
    
    print(f"[INFO] Current price request for {request.stock_code}")
    return mock_data

@app.post("/api/trading/order")
async def place_order(order: OrderRequest):
    """주문 실행 - Mock 응답"""
    
    mock_response = {
        "success": True,
        "mode": "test",
        "data": {
            "rt_cd": "0",
            "msg1": "모의투자 주문이 접수되었습니다.",
            "output": {
                "odno": "0000123456",  # 주문번호
                "ord_tmd": datetime.now().strftime("%H%M%S"),  # 주문시각
                "ord_qty": str(order.quantity),  # 주문수량
                "ord_unpr": str(order.price)  # 주문단가
            }
        }
    }
    
    print(f"[INFO] Order placed: {order.order_type} {order.quantity} shares of {order.stock_code}")
    return mock_response

@app.post("/webhook/n8n/signal")
async def n8n_trading_signal(data: Dict[str, Any]):
    """N8N에서 전송한 매매 신호 처리"""
    
    signal_type = data.get("signal_type", "unknown")
    stock_code = data.get("stock_code", "000000")
    
    print(f"[INFO] N8N signal received: {signal_type} for {stock_code}")
    
    return {
        "success": True,
        "message": f"Signal processed: {signal_type}",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)