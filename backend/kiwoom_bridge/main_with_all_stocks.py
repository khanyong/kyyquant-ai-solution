"""
키움증권 REST API Bridge Server - 전체 종목 버전
Supabase에서 종목 리스트를 가져오거나 키움 API 사용
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Supabase import (있으면 사용)
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# backtest API import
try:
    from backtest_api import router as backtest_router
    BACKTEST_AVAILABLE = True
except ImportError:
    BACKTEST_AVAILABLE = False

load_dotenv()

app = FastAPI(
    title="키움증권 REST API Bridge",
    description="Kiwoom Securities REST API Bridge for Auto Trading",
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

# 백테스트 라우터 등록
if BACKTEST_AVAILABLE:
    app.include_router(backtest_router)

# Supabase 클라이언트 초기화
supabase = None
if SUPABASE_AVAILABLE:
    try:
        supabase = create_client(
            os.getenv('SUPABASE_URL', ''),
            os.getenv('SUPABASE_KEY', '')
        )
        print("[INFO] Supabase connected")
    except:
        print("[WARNING] Supabase connection failed")

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
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "supabase": "connected" if supabase else "disconnected"
    }

@app.post("/api/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {
        "success": True,
        "message": "Test endpoint working",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market/stock-list")
async def get_stock_list(market: str = None, source: str = "auto"):
    """
    전체 종목 리스트 조회

    Parameters:
    - market: "KOSPI", "KOSDAQ", None (전체)
    - source: "auto" (자동선택), "supabase" (DB), "mock" (테스트)
    """

    stocks = []

    # 1. Supabase에서 가져오기 시도
    if source in ["auto", "supabase"] and supabase:
        try:
            print("[INFO] Fetching stocks from Supabase...")

            # stock_metadata 테이블에서 종목 조회
            query = supabase.table('stock_metadata').select('stock_code, stock_name, market')

            if market:
                query = query.eq('market', market)

            result = query.execute()

            if result.data:
                stocks = [
                    {
                        "code": item['stock_code'],
                        "name": item['stock_name'],
                        "market": item['market']
                    }
                    for item in result.data
                ]
                print(f"[INFO] Found {len(stocks)} stocks from Supabase")

                return {
                    "success": True,
                    "source": "supabase",
                    "data": stocks,
                    "count": len(stocks),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"[ERROR] Supabase query failed: {e}")

    # 2. 키움 API 사용 (구현 필요)
    if source == "kiwoom":
        # TODO: 키움 API GetCodeListByMarket 구현
        return {
            "success": False,
            "message": "Kiwoom API integration not implemented yet",
            "timestamp": datetime.now().isoformat()
        }

    # 3. Mock 데이터 (Fallback)
    print("[INFO] Using mock data...")

    # 대표 종목들 (실제로는 3000+ 종목)
    kospi_stocks = [
        {"code": "005930", "name": "삼성전자", "market": "KOSPI"},
        {"code": "000660", "name": "SK하이닉스", "market": "KOSPI"},
        {"code": "207940", "name": "삼성바이오로직스", "market": "KOSPI"},
        {"code": "005380", "name": "현대차", "market": "KOSPI"},
        {"code": "005935", "name": "삼성전자우", "market": "KOSPI"},
        {"code": "000270", "name": "기아", "market": "KOSPI"},
        {"code": "068270", "name": "셀트리온", "market": "KOSPI"},
        {"code": "035420", "name": "NAVER", "market": "KOSPI"},
        {"code": "051910", "name": "LG화학", "market": "KOSPI"},
        {"code": "006400", "name": "삼성SDI", "market": "KOSPI"},
        {"code": "003670", "name": "포스코퓨처엠", "market": "KOSPI"},
        {"code": "035720", "name": "카카오", "market": "KOSPI"},
        {"code": "012330", "name": "현대모비스", "market": "KOSPI"},
        {"code": "028260", "name": "삼성물산", "market": "KOSPI"},
        {"code": "066570", "name": "LG전자", "market": "KOSPI"},
        {"code": "036570", "name": "NCsoft", "market": "KOSPI"},
        {"code": "033780", "name": "KT&G", "market": "KOSPI"},
        {"code": "003550", "name": "LG", "market": "KOSPI"},
        {"code": "017670", "name": "SK텔레콤", "market": "KOSPI"},
        {"code": "105560", "name": "KB금융", "market": "KOSPI"},
        {"code": "055550", "name": "신한지주", "market": "KOSPI"},
        {"code": "086790", "name": "하나금융지주", "market": "KOSPI"},
        {"code": "316140", "name": "우리금융지주", "market": "KOSPI"},
        {"code": "024110", "name": "기업은행", "market": "KOSPI"},
        {"code": "090430", "name": "아모레퍼시픽", "market": "KOSPI"},
        {"code": "000810", "name": "삼성화재", "market": "KOSPI"},
        {"code": "009150", "name": "삼성전기", "market": "KOSPI"},
        {"code": "096770", "name": "SK이노베이션", "market": "KOSPI"},
        {"code": "018260", "name": "삼성에스디에스", "market": "KOSPI"},
        {"code": "010130", "name": "고려아연", "market": "KOSPI"},
    ]

    kosdaq_stocks = [
        {"code": "247540", "name": "에코프로비엠", "market": "KOSDAQ"},
        {"code": "086520", "name": "에코프로", "market": "KOSDAQ"},
        {"code": "328130", "name": "루닛", "market": "KOSDAQ"},
        {"code": "196170", "name": "알테오젠", "market": "KOSDAQ"},
        {"code": "141080", "name": "레고켐바이오", "market": "KOSDAQ"},
        {"code": "145020", "name": "휴젤", "market": "KOSDAQ"},
        {"code": "112040", "name": "위메이드", "market": "KOSDAQ"},
        {"code": "293490", "name": "카카오게임즈", "market": "KOSDAQ"},
        {"code": "263750", "name": "펄어비스", "market": "KOSDAQ"},
        {"code": "357780", "name": "솔브레인", "market": "KOSDAQ"},
    ]

    # 시장별 필터링
    if market == "KOSPI":
        stocks = kospi_stocks
    elif market == "KOSDAQ":
        stocks = kosdaq_stocks
    else:
        stocks = kospi_stocks + kosdaq_stocks

    print(f"[INFO] Stock list requested: {len(stocks)} stocks (mock)")

    return {
        "success": True,
        "source": "mock",
        "data": stocks,
        "count": len(stocks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market/stock-list-full")
async def get_full_stock_list():
    """
    데이터베이스에서 전체 종목 수 확인
    """
    if supabase:
        try:
            # 전체 종목 수 카운트
            result = supabase.table('stock_metadata').select('stock_code', count='exact').execute()

            return {
                "success": True,
                "total_count": result.count if hasattr(result, 'count') else 0,
                "message": "Use /api/market/stock-list to get actual stock data",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    return {
        "success": False,
        "message": "Database not connected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/market/current-price")
async def get_current_price(request: CurrentPriceRequest):
    """현재가 조회 - Mock 데이터 반환"""

    # Mock 데이터 (실제로는 키움 API 호출)
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