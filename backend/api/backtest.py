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
from backtest.preflight import preflight_check
from indicators.calculator import IndicatorCalculator

router = APIRouter()

@router.get("/version")
async def get_version():
    """백테스트 API 버전 확인"""
    return {
        "version": "3.1.0",
        "features": [
            "staged_trading",
            "sell_conditions",
            "multi_strategy",
            "real_time_data",
            "preflight_validation",
            "version_tracking"
        ]
    }


@router.post("/preflight")
async def validate_strategy(request: Dict[str, Any]):
    """
    전략 프리플라이트 검증 (실행 없이 검증만)

    Args:
        request: {
            "strategy_id": "uuid",  # 또는
            "strategy_config": {...},  # 직접 config 제공
            "stock_codes": ["005930"],
            "date_range": ["2023-01-01", "2023-12-31"]
        }

    Returns:
        {
            "passed": true/false,
            "errors": [...],
            "warnings": [...],
            "info": [...]
        }
    """
    try:
        calculator = IndicatorCalculator()

        # 전략 로드 또는 config 직접 사용
        if 'strategy_id' in request:
            engine = BacktestEngine()
            strategy = await engine.strategy_manager.get_strategy(request['strategy_id'])
            if not strategy:
                raise HTTPException(status_code=404, detail="Strategy not found")
            strategy_config = strategy.get('config', {})
        elif 'strategy_config' in request:
            strategy_config = request['strategy_config']
        else:
            raise HTTPException(status_code=400, detail="Provide either strategy_id or strategy_config")

        # 검증 실행
        report = await preflight_check(
            strategy_config=strategy_config,
            calculator=calculator,
            stock_codes=request.get('stock_codes'),
            date_range=tuple(request['date_range']) if 'date_range' in request else None,
            raise_on_error=False  # 에러를 raise하지 않고 리포트 반환
        )

        return {
            "passed": report.passed,
            "errors": [{"level": "error", "message": r.message, "details": r.details} for r in report.errors],
            "warnings": [{"level": "warning", "message": r.message, "details": r.details} for r in report.warnings],
            "info": [{"level": "info", "message": r.message} for r in report.info]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

        # 1. 전략 로드
        engine = BacktestEngine()
        strategy = await engine.strategy_manager.get_strategy(request.strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_id} not found")

        # 2. 프리플라이트 검증 (실행 전 차단)
        print("[API] Running preflight validation...")
        try:
            calculator = IndicatorCalculator()
            report = await preflight_check(
                strategy_config=strategy.get('config', {}),
                calculator=calculator,
                stock_codes=request.stock_codes,
                date_range=(request.start_date, request.end_date),
                raise_on_error=True
            )
            print(f"[API] Preflight passed: {len(report.warnings)} warnings, {len(report.info)} info")
        except ValueError as e:
            # 프리플라이트 실패 → 422 Unprocessable Entity
            raise HTTPException(
                status_code=422,
                detail=f"Preflight validation failed:\n{str(e)}"
            )

        # 3. 백테스트 실행
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