"""
키움증권 REST API Bridge Server
Clean Architecture Version
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 버전 정보
APP_VERSION = "3.0.0"
BUILD_TIME = datetime.now().isoformat()

print("\n" + "="*70)
print(f"KIWOOM BRIDGE SERVER STARTING")
print(f"Version: {APP_VERSION}")
print(f"Build Time: {BUILD_TIME}")
print(f"Working Dir: {os.getcwd()}")
print(f"Python: {sys.version.split()[0]}")
print("="*70 + "\n")

# FastAPI 앱 생성
app = FastAPI(
    title="키움증권 REST API Bridge",
    description="Kiwoom Securities REST API Bridge for Auto Trading",
    version=APP_VERSION
)

# CORS 설정 (Vercel 및 로컬 개발 환경)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://192.168.50.150:3000",
        "https://api.bll-pro.com",
        "https://workflow.bll-pro.com"
    ],
    allow_origin_regex="https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import Status Tracking
import_status = {
    "backtest": "pending",
    "market": "pending",
    "strategy": "pending",
    "account": "pending",
    "order": "pending",
    "indicators": "pending",
    "errors": {}
}

# API 라우터 등록
try:
    from api.backtest import router as backtest_router
    app.include_router(backtest_router, prefix="/api/backtest", tags=["backtest"])
    print("[OK] Backtest router registered")
    import_status["backtest"] = "ok"
except ImportError as e:
    print(f"[ERROR] Failed to import backtest router: {e}")
    import_status["backtest"] = "error"
    import_status["errors"]["backtest"] = str(e)

try:
    from api.market import router as market_router
    app.include_router(market_router, prefix="/api/market", tags=["market"])
    print("[OK] Market router registered")
    import_status["market"] = "ok"
except ImportError as e:
    print(f"[ERROR] Failed to import market router: {e}")
    import_status["market"] = "error"
    import_status["errors"]["market"] = str(e)

try:
    from api.strategy import router as strategy_router
    app.include_router(strategy_router, prefix="/api/strategy", tags=["strategy"])
    print("[OK] Strategy router registered")
    import_status["strategy"] = "ok"
except Exception as e: # Catch ANY exception, not just ImportError
    import  traceback
    tb = traceback.format_exc()
    print(f"[ERROR] Failed to import strategy router: {e}")
    print(tb)
    import_status["strategy"] = "error"
    import_status["errors"]["strategy"] = str(e) + "\n" + tb

try:
    from api.account import router as account_router
    app.include_router(account_router, prefix="/api/account", tags=["account"])
    print("[OK] Account router registered")
    import_status["account"] = "ok"
except ImportError as e:
    print(f"[ERROR] Failed to import account router: {e}")
    import_status["account"] = "error"
    import_status["errors"]["account"] = str(e)

try:
    from api.order import router as order_router
    app.include_router(order_router, prefix="/api/order", tags=["order"])
    print("[OK] Order router registered")
    import_status["order"] = "ok"
except ImportError as e:
    print(f"[ERROR] Failed to import order router: {e}")
    import_status["order"] = "error"
    import_status["errors"]["order"] = str(e)

try:
    from api.indicators import router as indicators_router
    app.include_router(indicators_router, tags=["indicators"])
    print("[OK] Indicators router registered")
    import_status["indicators"] = "ok"
except ImportError as e:
    print(f"[ERROR] Failed to import indicators router: {e}")
    import_status["indicators"] = "error"
    import_status["errors"]["indicators"] = str(e)

@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "status": "running",
        "version": APP_VERSION,
        "build_time": BUILD_TIME,
        "import_status": import_status,
        "endpoints": {
            "backtest": "/api/backtest",
            "market": "/api/market",
            "strategy": "/api/strategy",
            "account": "/api/account",
            "order": "/api/order",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """헬스체크"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)