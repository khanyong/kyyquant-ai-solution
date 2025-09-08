"""
하이브리드 자동매매 시스템 메인
Windows: OpenAPI+ 우선 사용
Linux/NAS: REST API 사용
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 하이브리드 매니저
from kiwoom_hybrid_manager import get_kiwoom_manager
from kiwoom_api_interface import KiwoomAPIInterface

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱
app = FastAPI(
    title="Kiwoom Hybrid Trading API",
    description="OpenAPI+와 REST API를 지원하는 하이브리드 자동매매 시스템",
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

# 전역 변수
manager = None
trading_system = None

class HybridTradingSystem:
    """하이브리드 자동매매 시스템"""
    
    def __init__(self, api: KiwoomAPIInterface):
        self.api = api
        self.is_running = False
        self.strategies = []
        self.monitoring_task = None
        
    async def start(self):
        """시스템 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info(f"자동매매 시스템 시작 - API: {self.api.api_type}")
        
        # 모니터링 태스크 시작
        self.monitoring_task = asyncio.create_task(self.monitor_market())
        
    async def stop(self):
        """시스템 중지"""
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("자동매매 시스템 중지")
    
    async def monitor_market(self):
        """시장 모니터링"""
        watch_list = ['005930', '000660', '035720']  # 삼성전자, SK하이닉스, 카카오
        
        while self.is_running:
            try:
                for stock_code in watch_list:
                    price = await self.api.get_current_price(stock_code)
                    if price:
                        logger.info(
                            f"{stock_code} - {price.name}: "
                            f"{price.price:,}원 ({price.change_rate:+.2f}%)"
                        )
                
                # 전략 실행
                await self.execute_strategies()
                
                # 대기
                await asyncio.sleep(60)  # 1분
                
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                await asyncio.sleep(10)
    
    async def execute_strategies(self):
        """전략 실행"""
        # 전략 로직 구현
        pass
    
    def add_strategy(self, strategy):
        """전략 추가"""
        self.strategies.append(strategy)
        logger.info(f"전략 추가: {strategy.get('name', 'Unknown')}")
    
    def get_status(self):
        """시스템 상태"""
        return {
            'is_running': self.is_running,
            'api_type': self.api.api_type,
            'platform': self.api.platform,
            'strategies_count': len(self.strategies),
            'timestamp': datetime.now().isoformat()
        }

# FastAPI 이벤트 핸들러
@app.on_event("startup")
async def startup_event():
    """서버 시작시 실행"""
    global manager, trading_system
    
    try:
        # 하이브리드 매니저 초기화
        manager = get_kiwoom_manager()
        
        # API 초기화 (환경에 따라 자동 선택)
        prefer_api = os.getenv('KIWOOM_API_TYPE')  # 환경변수로 강제 지정 가능
        success = await manager.initialize(force_api=prefer_api)
        
        if not success:
            logger.error("API 초기화 실패")
            sys.exit(1)
        
        # API 정보 출력
        status = manager.get_status()
        logger.info(f"API 초기화 성공")
        logger.info(f"- 플랫폼: {status['platform']}")
        logger.info(f"- 사용 API: {status['current_api']}")
        logger.info(f"- 연결 상태: {status['is_connected']}")
        
        # 자동매매 시스템 생성
        api = manager.get_api()
        trading_system = HybridTradingSystem(api)
        
        # 자동으로 시작 (옵션)
        if os.getenv('AUTO_START', 'false').lower() == 'true':
            await trading_system.start()
        
    except Exception as e:
        logger.error(f"시작 오류: {e}")
        sys.exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료시 실행"""
    global manager, trading_system
    
    try:
        # 자동매매 중지
        if trading_system:
            await trading_system.stop()
        
        # API 연결 해제
        if manager:
            api = manager.get_api()
            if api:
                await api.disconnect()
        
        logger.info("서버 종료 완료")
        
    except Exception as e:
        logger.error(f"종료 오류: {e}")

# API 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Kiwoom Hybrid Trading API",
        "version": "2.0.0",
        "status": "running",
        "api_type": manager.get_status()['current_api'] if manager else "not initialized"
    }

@app.get("/health")
async def health_check():
    """헬스체크"""
    if not manager or not manager.get_api():
        raise HTTPException(status_code=503, detail="API not initialized")
    
    api = manager.get_api()
    is_healthy = await api.health_check()
    
    if not is_healthy:
        raise HTTPException(status_code=503, detail="API not healthy")
    
    return {"status": "healthy", "api_type": api.api_type}

@app.get("/api/status")
async def get_status():
    """시스템 상태 조회"""
    if not manager:
        raise HTTPException(status_code=503, detail="Manager not initialized")
    
    manager_status = manager.get_status()
    system_status = trading_system.get_status() if trading_system else {}
    
    return {
        "manager": manager_status,
        "trading_system": system_status
    }

@app.post("/api/switch/{api_type}")
async def switch_api(api_type: str):
    """API 전환"""
    global trading_system  # global 선언을 먼저
    
    if api_type not in ['openapi', 'rest']:
        raise HTTPException(status_code=400, detail="Invalid API type")
    
    # 자동매매 중지
    if trading_system and trading_system.is_running:
        await trading_system.stop()
    
    # API 전환
    success = await manager.switch_api(api_type)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to switch to {api_type}")
    
    # 새 API로 자동매매 시스템 재생성
    api = manager.get_api()
    trading_system = HybridTradingSystem(api)
    
    return {"message": f"Switched to {api_type}", "status": manager.get_status()}

@app.get("/api/price/{stock_code}")
async def get_price(stock_code: str):
    """현재가 조회"""
    if not manager or not manager.get_api():
        raise HTTPException(status_code=503, detail="API not initialized")
    
    api = manager.get_api()
    price = await api.get_current_price(stock_code)
    
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    
    return {
        "code": price.code,
        "name": price.name,
        "price": price.price,
        "change": price.change,
        "change_rate": price.change_rate,
        "volume": price.volume,
        "high": price.high,
        "low": price.low,
        "timestamp": price.timestamp.isoformat()
    }

@app.get("/api/balance")
async def get_balance():
    """잔고 조회"""
    if not manager or not manager.get_api():
        raise HTTPException(status_code=503, detail="API not initialized")
    
    api = manager.get_api()
    balance = await api.get_balance()
    
    if not balance:
        raise HTTPException(status_code=500, detail="Failed to get balance")
    
    return {
        "total_eval": balance.total_eval,
        "total_purchase": balance.total_purchase,
        "total_profit": balance.total_profit,
        "cash": balance.cash,
        "holdings": balance.holdings,
        "timestamp": balance.timestamp.isoformat()
    }

@app.post("/api/order")
async def place_order(
    stock_code: str,
    quantity: int,
    price: int,
    order_type: str = "buy",
    order_method: str = "limit"
):
    """주문 실행"""
    if not manager or not manager.get_api():
        raise HTTPException(status_code=503, detail="API not initialized")
    
    api = manager.get_api()
    result = await api.place_order(stock_code, quantity, price, order_type, order_method)
    
    if not result:
        raise HTTPException(status_code=500, detail="Order failed")
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return {
        "success": result.success,
        "order_no": result.order_no,
        "message": result.message,
        "timestamp": result.timestamp.isoformat(),
        "details": result.details
    }

@app.post("/api/trading/start")
async def start_trading():
    """자동매매 시작"""
    if not trading_system:
        raise HTTPException(status_code=503, detail="Trading system not initialized")
    
    await trading_system.start()
    return {"message": "Trading started", "status": trading_system.get_status()}

@app.post("/api/trading/stop")
async def stop_trading():
    """자동매매 중지"""
    if not trading_system:
        raise HTTPException(status_code=503, detail="Trading system not initialized")
    
    await trading_system.stop()
    return {"message": "Trading stopped", "status": trading_system.get_status()}

@app.post("/api/strategy/add")
async def add_strategy(strategy: dict):
    """전략 추가"""
    if not trading_system:
        raise HTTPException(status_code=503, detail="Trading system not initialized")
    
    trading_system.add_strategy(strategy)
    return {"message": "Strategy added", "strategy": strategy}

# Windows에서 직접 실행시
def run_windows():
    """Windows에서 OpenAPI+ 우선 실행"""
    logger.info("Windows 환경 감지 - OpenAPI+ 우선 모드")
    os.environ['KIWOOM_API_TYPE'] = 'openapi'  # OpenAPI+ 우선
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Linux/Docker에서 실행시
def run_linux():
    """Linux/Docker에서 REST API 실행"""
    logger.info("Linux/Docker 환경 감지 - REST API 모드")
    os.environ['KIWOOM_API_TYPE'] = 'rest'  # REST API 강제
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import platform
    
    # 플랫폼에 따라 자동 실행
    if platform.system() == 'Windows':
        run_windows()
    else:
        run_linux()