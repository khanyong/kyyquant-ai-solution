"""
전략 관리 API 엔드포인트
FastAPI 라우터
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from core.strategy_execution_manager import StrategyExecutionManager

load_dotenv()

app = FastAPI(title="키움 자동매매 전략 API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전략 매니저 인스턴스
strategy_manager = StrategyExecutionManager()

# Pydantic 모델
class StrategyCondition(BaseModel):
    operator: str  # '<', '>', '<=', '>=', '=='
    value: float | str

class StrategyEntry(BaseModel):
    rsi: Optional[StrategyCondition] = None
    volume: Optional[StrategyCondition] = None
    price: Optional[StrategyCondition] = None
    macd: Optional[StrategyCondition] = None

class StrategyExit(BaseModel):
    profit_target: float = 5.0  # 수익 목표 (%)
    stop_loss: float = -3.0     # 손절선 (%)
    trailing_stop: Optional[float] = None

class StrategyConditions(BaseModel):
    entry: StrategyEntry
    exit: StrategyExit

class CreateStrategyRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    conditions: StrategyConditions
    position_size: float = 10.0
    max_positions: int = 5
    execution_time: Dict[str, str] = {"start": "09:00", "end": "15:20"}
    target_stocks: List[str] = []
    auto_execute: bool = False

class UpdateStrategyRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[StrategyConditions] = None
    position_size: Optional[float] = None
    max_positions: Optional[int] = None
    execution_time: Optional[Dict[str, str]] = None
    target_stocks: Optional[List[str]] = None
    is_active: Optional[bool] = None
    auto_execute: Optional[bool] = None

class ExecuteStrategyRequest(BaseModel):
    strategy_id: str
    test_mode: bool = True

@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "status": "running",
        "service": "키움 자동매매 전략 API",
        "version": "1.0.0"
    }

@app.post("/api/strategies")
async def create_strategy(request: CreateStrategyRequest, user_id: str = "test_user"):
    """새 전략 생성"""
    try:
        strategy_data = request.dict()
        result = strategy_manager.create_strategy(user_id, strategy_data)
        
        if result:
            return {
                "success": True,
                "strategy": result,
                "message": "전략이 생성되었습니다"
            }
        else:
            raise HTTPException(status_code=400, detail="전략 생성 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies")
async def get_strategies(user_id: str = "test_user"):
    """사용자 전략 목록 조회"""
    try:
        strategies = strategy_manager.get_user_strategies(user_id)
        
        return {
            "success": True,
            "strategies": strategies,
            "count": len(strategies)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """특정 전략 상세 조회"""
    try:
        # 전략 조회 로직
        return {
            "success": True,
            "strategy": {
                "id": strategy_id,
                # 전략 상세 정보
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/strategies/{strategy_id}")
async def update_strategy(strategy_id: str, request: UpdateStrategyRequest):
    """전략 수정"""
    try:
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if strategy_manager.update_strategy(strategy_id, update_data):
            return {
                "success": True,
                "message": "전략이 업데이트되었습니다"
            }
        else:
            raise HTTPException(status_code=400, detail="전략 업데이트 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies/{strategy_id}/activate")
async def activate_strategy(strategy_id: str):
    """전략 활성화"""
    try:
        if strategy_manager.activate_strategy(strategy_id):
            return {
                "success": True,
                "message": "전략이 활성화되었습니다"
            }
        else:
            raise HTTPException(status_code=400, detail="전략 활성화 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies/{strategy_id}/deactivate")
async def deactivate_strategy(strategy_id: str):
    """전략 비활성화"""
    try:
        if strategy_manager.deactivate_strategy(strategy_id):
            return {
                "success": True,
                "message": "전략이 비활성화되었습니다"
            }
        else:
            raise HTTPException(status_code=400, detail="전략 비활성화 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies/execute")
async def execute_strategy(request: ExecuteStrategyRequest):
    """전략 실행 (백테스트 또는 실거래)"""
    try:
        result = strategy_manager.execute_strategy(request.strategy_id)
        
        if result:
            return {
                "success": True,
                "execution": result,
                "message": f"전략 실행 완료 - 스캔: {result['scanned']}, 신호: {result['signals']}"
            }
        else:
            raise HTTPException(status_code=400, detail="전략 실행 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies/{strategy_id}/performance")
async def get_strategy_performance(strategy_id: str):
    """전략 성과 조회"""
    try:
        performance = strategy_manager.get_strategy_performance(strategy_id)
        
        return {
            "success": True,
            "performance": performance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies/{strategy_id}/signals")
async def get_strategy_signals(strategy_id: str, limit: int = 10):
    """전략 신호 조회"""
    try:
        # 최근 신호 조회 로직
        return {
            "success": True,
            "signals": [],
            "count": 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
async def get_positions(user_id: str = "test_user"):
    """현재 포지션 조회"""
    try:
        positions = strategy_manager.get_positions()
        
        return {
            "success": True,
            "positions": positions,
            "count": len(positions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/stocks")
async def get_available_stocks():
    """거래 가능한 종목 목록"""
    try:
        stocks = [
            {"code": "005930", "name": "삼성전자"},
            {"code": "000660", "name": "SK하이닉스"},
            {"code": "035720", "name": "카카오"},
            {"code": "035420", "name": "NAVER"},
            {"code": "051910", "name": "LG화학"},
            {"code": "006400", "name": "삼성SDI"},
            {"code": "068270", "name": "셀트리온"},
            {"code": "005380", "name": "현대차"},
            {"code": "012330", "name": "현대모비스"},
            {"code": "066570", "name": "LG전자"}
        ]
        
        return {
            "success": True,
            "stocks": stocks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indicators")
async def get_available_indicators():
    """사용 가능한 기술적 지표 목록"""
    return {
        "success": True,
        "indicators": [
            {
                "name": "RSI",
                "key": "rsi",
                "description": "상대강도지수",
                "default_period": 14,
                "range": [0, 100]
            },
            {
                "name": "이동평균",
                "key": "ma",
                "description": "단순이동평균",
                "periods": [5, 20, 60, 120]
            },
            {
                "name": "MACD",
                "key": "macd",
                "description": "이동평균수렴발산",
                "fast": 12,
                "slow": 26,
                "signal": 9
            },
            {
                "name": "볼륨비율",
                "key": "volume_ratio",
                "description": "평균 거래량 대비 비율",
                "default_period": 20
            },
            {
                "name": "볼린저밴드",
                "key": "bollinger",
                "description": "볼린저밴드",
                "period": 20,
                "std": 2
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)