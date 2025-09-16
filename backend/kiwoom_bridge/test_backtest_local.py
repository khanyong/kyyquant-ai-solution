"""로컬 백테스트 테스트"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backtest_api import router
from fastapi import Request

async def test_backtest():
    """백테스트 테스트"""

    # 테스트 요청 데이터
    request_data = {
        "strategy_id": "fcfbcb90-d074-449e-a60f-a3c2a86fe74f",
        "stock_codes": ["005930"],
        "start_date": "2024-09-14",
        "end_date": "2025-09-12",
        "initial_capital": 10000000,
        "commission": 0.00015,
        "slippage": 0.001,
        "parameters": {}
    }

    # Mock Request 객체 생성
    class MockRequest:
        def __init__(self, data):
            self.data = data

        async def json(self):
            return self.data

    mock_request = MockRequest(request_data)

    try:
        # 백테스트 실행
        print("백테스트 시작...")
        from backtest_api import run_backtest_endpoint
        from pydantic import BaseModel
        from typing import List, Dict, Any

        class BacktestRequest(BaseModel):
            strategy_id: str
            stock_codes: List[str]
            start_date: str
            end_date: str
            initial_capital: float
            commission: float = 0.00015
            slippage: float = 0.001
            parameters: Dict[str, Any] = {}

        request = BacktestRequest(**request_data)
        result = await run_backtest_endpoint(request)
        print("백테스트 완료!")
        print(f"결과 키: {result.keys() if isinstance(result, dict) else 'Not a dict'}")

    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_backtest())