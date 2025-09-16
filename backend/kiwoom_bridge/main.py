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
import sys
import requests
from dotenv import load_dotenv

# 버전 정보
APP_VERSION = "2.1.0-debug"
BUILD_TIME = datetime.now().isoformat()

print("\n" + "="*70)
print(f"KIWOOM BRIDGE SERVER STARTING")
print(f"Version: {APP_VERSION}")
print(f"Build Time: {BUILD_TIME}")
print(f"Working Dir: {os.getcwd()}")
print(f"Python: {sys.version.split()[0]}")
print("="*70 + "\n")

# Supabase import (있으면 사용)
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# backtest API import
try:
    from backtest_api import router as backtest_router, CODE_VERSION, BacktestRequest, run_backtest
    BACKTEST_AVAILABLE = True
    print(f"[OK] Backtest API loaded (Version: {CODE_VERSION})")
except ImportError as e:
    BACKTEST_AVAILABLE = False
    CODE_VERSION = "N/A"
    print(f"[ERROR] Backtest API not available: {e}")

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
    print(f"[OK] Backtest router registered at /api/backtest")
else:
    print("[WARNING] Backtest router not registered")

# Supabase 클라이언트 초기화
supabase = None
if SUPABASE_AVAILABLE:
    try:
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_KEY', '')

        print(f"[DEBUG] Supabase URL: {supabase_url[:30]}..." if supabase_url else "[ERROR] No SUPABASE_URL")
        print(f"[DEBUG] Supabase KEY: {supabase_key[:20]}..." if supabase_key else "[ERROR] No SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("[ERROR] Supabase credentials missing in .env file!")
            print("[INFO] Running without Supabase (mock data mode)")
        else:
            supabase = create_client(supabase_url, supabase_key)
            print("[OK] Supabase connected successfully")
    except Exception as e:
        print(f"[ERROR] Supabase connection failed: {e}")
        print("[INFO] Running without Supabase (mock data mode)")

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
        "version": APP_VERSION,
        "backtest_version": CODE_VERSION,
        "build_time": BUILD_TIME,
        "timestamp": datetime.now().isoformat(),
        "supabase": "connected" if supabase else "disconnected",
        "backtest_api": "enabled" if BACKTEST_AVAILABLE else "disabled",
        "working_dir": os.getcwd(),
        "python_version": sys.version.split()[0]
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

            # stock_metadata 테이블에서 종목 조회 (오프셋 기반 페이지네이션)
            all_stocks = []
            limit = 1000  # 한 번에 가져올 개수
            offset = 0

            while True:
                query = supabase.table('stock_metadata').select('stock_code, stock_name, market')

                if market:
                    query = query.eq('market', market)

                # limit과 offset 사용
                result = query.limit(limit).offset(offset).execute()

                if not result.data:
                    break

                all_stocks.extend(result.data)
                print(f"[INFO] Fetched {len(result.data)} stocks from offset {offset} (total: {len(all_stocks)})")

                # 다음 페이지가 없으면 중단
                if len(result.data) < limit:
                    break

                offset += limit

            if all_stocks:
                stocks = [
                    {
                        "code": item['stock_code'],
                        "name": item['stock_name'],
                        "market": item['market']
                    }
                    for item in all_stocks
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
    """현재가 조회 - 키움 REST API 토큰 발급 + pykrx 시세"""

    try:
        # 1. 키움 REST API 토큰 발급 (모의투자)
        token_url = "https://mockapi.kiwoom.com/oauth2/token"
        token_data = {
            "grant_type": "client_credentials",
            "appkey": os.getenv('KIWOOM_APP_KEY'),
            "secretkey": os.getenv('KIWOOM_APP_SECRET')  # secretkey 사용!
        }

        headers = {"Content-Type": "application/json"}
        token_response = requests.post(token_url, json=token_data, headers=headers, timeout=10)

        access_token = None
        if token_response.status_code == 200:
            token_info = token_response.json()
            if token_info.get('return_code') == 0:
                access_token = token_info.get('token')
                print(f"[INFO] Kiwoom token issued successfully")
            else:
                print(f"[ERROR] Token failed: {token_info.get('return_msg')}")
        else:
            print(f"[ERROR] Token request failed: {token_response.status_code}")

        # 2. 시세 조회 - pykrx 사용 (키움 API 시세 조회가 500 오류 발생 중)
        # 나중에 키움 API가 정상화되면 아래 코드로 교체
        try:
            from pykrx import stock
            from datetime import datetime, timedelta

            today = datetime.now().strftime('%Y%m%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

            # pykrx로 현재가 조회
            df = stock.get_market_ohlcv_by_date(yesterday, today, request.stock_code)

            if not df.empty:
                latest = df.iloc[-1]
                current_price = int(latest['종가'])

                # 전일 대비 계산
                if len(df) > 1:
                    prev_close = int(df.iloc[-2]['종가'])
                    change_price = current_price - prev_close
                    change_rate = round((change_price / prev_close) * 100, 2)
                else:
                    change_price = 0
                    change_rate = 0

                result = {
                    "success": True,
                    "data": {
                        "stock_code": request.stock_code,
                        "current_price": current_price,
                        "change_price": change_price,
                        "change_rate": change_rate,
                        "volume": int(latest['거래량']),
                        "high_price": int(latest['고가']),
                        "low_price": int(latest['저가']),
                        "open_price": int(latest['시가']),
                        "timestamp": datetime.now().isoformat()
                    },
                    "source": "pykrx",
                    "kiwoom_token": "valid" if access_token else "failed"
                }
                return result
            else:
                return {
                    "success": False,
                    "error": "No price data available",
                    "kiwoom_token": "valid" if access_token else "failed"
                }

        except ImportError:
            # pykrx가 없으면 에러
            return {
                "success": False,
                "error": "pykrx not installed",
                "kiwoom_token": "valid" if access_token else "failed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "kiwoom_token": "valid" if access_token else "failed"
            }

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return {"success": False, "error": str(e)}

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

# Vercel 프론트엔드 호환 라우트
@app.post("/api/backtest-run")
async def backtest_run_vercel(request: BacktestRequest):
    """Vercel에서 사용하는 경로 - /api/backtest/run으로 리다이렉트"""
    print(f"[VERCEL ROUTE] Received request from Vercel frontend")
    print(f"[VERCEL ROUTE] Redirecting to /api/backtest/run")
    # backtest_router의 run_backtest 직접 호출
    if BACKTEST_AVAILABLE:
        return await run_backtest(request)
    else:
        raise HTTPException(status_code=503, detail="Backtest API not available")

print("[OK] Vercel compatibility route added: /api/backtest-run")

if __name__ == "__main__":
    import uvicorn
    print(f"\n[INFO] Starting server on http://0.0.0.0:8001")
    print(f"[INFO] App Version: {APP_VERSION}")
    print(f"[INFO] Backtest Version: {CODE_VERSION}")
    print(f"[INFO] Backtest API: {'Enabled' if BACKTEST_AVAILABLE else 'Disabled'}")
    print(f"[INFO] Supabase: {'Connected' if supabase else 'Not Connected'}")
    print("\n" + "="*70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)