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

# API 라우터 등록
try:
    from api.backtest import router as backtest_router
    app.include_router(backtest_router, prefix="/api/backtest", tags=["backtest"])
    print("[OK] Backtest router registered")
except ImportError as e:
    print(f"[ERROR] Failed to import backtest router: {e}")

try:
    from api.market import router as market_router
    app.include_router(market_router, prefix="/api/market", tags=["market"])
    print("[OK] Market router registered")
except ImportError as e:
    print(f"[ERROR] Failed to import market router: {e}")

try:
    from api.strategy import router as strategy_router
    app.include_router(strategy_router, prefix="/api/strategy", tags=["strategy"])
    print("[OK] Strategy router registered")
except ImportError as e:
    print(f"[ERROR] Failed to import strategy router: {e}")

try:
    from api.account import router as account_router
    app.include_router(account_router, prefix="/api/account", tags=["account"])
    print("[OK] Account router registered")
except ImportError as e:
    print(f"[ERROR] Failed to import account router: {e}")

try:
    from api.order import router as order_router
    app.include_router(order_router, prefix="/api/order", tags=["order"])
    print("[OK] Order router registered")
except ImportError as e:
    print(f"[ERROR] Failed to import order router: {e}")

try:
    from api.indicators import router as indicators_router
    app.include_router(indicators_router, tags=["indicators"])
    print("[OK] Indicators router registered")
except ImportError as e:
    print(f"[ERROR] Failed to import indicators router: {e}")

@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "status": "running",
        "version": APP_VERSION,
        "build_time": BUILD_TIME,
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