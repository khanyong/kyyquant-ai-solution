"""
백테스트 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# 백테스트 엔진 임포트
from backtest.engine import BacktestEngine
from backtest.models import BacktestRequest, BacktestResult

router = APIRouter()

@router.get("/version")
async def get_version():
    """백테스트 API 버전 확인"""
    return {
        "version": "3.0.0",
        "features": [
            "staged_trading",
            "sell_conditions",
            "multi_strategy",
            "real_time_data"
        ]
    }

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """
    백테스트 실행

    Args:
        request: 백테스트 요청 파라미터

    Returns:
        BacktestResult: 백테스트 결과
    """
    try:
        print(f"[API] Backtest request received for strategy: {request.strategy_id}")
        engine = BacktestEngine()
        result = await engine.run(
            strategy_id=request.strategy_id,
            stock_codes=request.stock_codes,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            **request.dict(exclude={'strategy_id', 'stock_codes', 'start_date', 'end_date', 'initial_capital'})
        )

        # API 응답 형식 맞추기 - 프론트엔드가 기대하는 형식
        print(f"[API] Backtest completed. Preparing response...")
        api_response = {
            'success': True,
            'status': result.get('status', 'completed'),
            'backtest_id': result.get('backtest_id'),
            'summary': {
                'total_return': result.get('total_return_rate', 0),
                'average_win_rate': result.get('win_rate', 0),
                'max_drawdown': result.get('max_drawdown', 0),
                'total_trades': result.get('total_trades', 0),
                'winning_trades': result.get('winning_trades', 0),
                'losing_trades': result.get('losing_trades', 0),
                'processed_count': result.get('total_trades', 0)
            },
            'individual_results': [
                {
                    'stock_code': code,
                    'result': {
                        'trades': [t for t in result.get('trades', []) if t.get('stock_code') == code],
                        'total_trades': len([t for t in result.get('trades', []) if t.get('stock_code') == code and t.get('type') == 'sell']),
                        'winning_trades': len([t for t in result.get('trades', []) if t.get('stock_code') == code and t.get('type') == 'sell' and t.get('profit', 0) > 0]),
                        'losing_trades': len([t for t in result.get('trades', []) if t.get('stock_code') == code and t.get('type') == 'sell' and t.get('profit', 0) <= 0])
                    }
                } for code in request.stock_codes
            ] if request.stock_codes else []
        }

        print(f"[API] Response prepared. Total return: {api_response['summary']['total_return']:.2f}%")
        return api_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick")
async def quick_backtest(request: Dict[str, Any]):
    """
    빠른 백테스트 (전략 저장 없이)
    """
    try:
        engine = BacktestEngine()

        # 임시 전략으로 실행
        result = await engine.run_with_config(
            strategy_config=request.get('strategy'),
            stock_codes=request.get('stock_codes', ['005930']),  # 기본값: 삼성전자
            **request
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{user_id}")
async def get_user_results(user_id: str, limit: int = 10):
    """
    사용자의 백테스트 결과 조회
    """
    try:
        # TODO: 데이터베이스에서 결과 조회
        return {
            "user_id": user_id,
            "results": [],
            "count": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/results/{result_id}")
async def delete_result(result_id: str):
    """
    백테스트 결과 삭제
    """
    try:
        # TODO: 데이터베이스에서 결과 삭제
        return {"message": f"Result {result_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))