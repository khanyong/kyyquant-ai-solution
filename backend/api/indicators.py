"""
지표 계산 API 엔드포인트
n8n workflow에서 호출하여 기술적 지표를 계산합니다.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

from backend.indicators.calculator import IndicatorCalculator
from backend.data.provider import DataProvider

router = APIRouter(prefix="/api/indicators", tags=["indicators"])
logger = logging.getLogger(__name__)


class IndicatorRequest(BaseModel):
    """지표 계산 요청"""
    name: str  # ma, bollinger, rsi 등
    params: Optional[Dict] = {}  # {"period": 20} 등


class CalculateRequest(BaseModel):
    """지표 계산 요청 모델"""
    stock_code: str
    indicators: List[IndicatorRequest]
    days: int = 60  # 과거 데이터 일수


class CalculateResponse(BaseModel):
    """지표 계산 응답 모델"""
    stock_code: str
    indicators: Dict[str, float]  # {"ma_20": 75000, "rsi": 45.5, ...}
    calculated_at: str


@router.post("/calculate", response_model=CalculateResponse)
async def calculate_indicators(request: CalculateRequest):
    """
    주식 종목에 대한 기술적 지표를 계산합니다.

    n8n workflow에서 호출하여 실시간 거래 신호 생성에 사용됩니다.

    Args:
        request: 종목 코드, 계산할 지표 목록, 과거 데이터 일수

    Returns:
        계산된 지표 값들

    Example:
        POST /api/indicators/calculate
        {
            "stock_code": "005930",
            "indicators": [
                {"name": "ma", "params": {"period": 20}},
                {"name": "ma", "params": {"period": 12}},
                {"name": "bollinger", "params": {"period": 20}},
                {"name": "rsi", "params": {"period": 14}}
            ],
            "days": 60
        }

        Response:
        {
            "stock_code": "005930",
            "indicators": {
                "ma_20": 75000,
                "ma_12": 76500,
                "bollinger_upper": 78000,
                "bollinger_middle": 75000,
                "bollinger_lower": 72000,
                "rsi": 45.5,
                "close": 75500
            },
            "calculated_at": "2025-10-26T15:30:00"
        }
    """
    try:
        logger.info(f"🔄 Calculating indicators for {request.stock_code}")

        # 1. 과거 데이터 조회 (kw_price_daily)
        data_provider = DataProvider()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)

        df = await data_provider.get_historical_data(
            stock_code=request.stock_code,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        if df is None or len(df) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {request.stock_code}"
            )

        logger.info(f"📊 Loaded {len(df)} days of historical data")

        # 2. 지표 계산
        calculator = IndicatorCalculator()
        result_indicators = {}

        for indicator_req in request.indicators:
            indicator_name = indicator_req.name
            params = indicator_req.params or {}

            try:
                # IndicatorCalculator는 config 딕셔너리를 받음
                config = {
                    'name': indicator_name,
                    'params': params
                }

                # 지표 계산 (Supabase indicators 테이블 사용)
                result = calculator.calculate(
                    df=df.copy(),
                    config=config,
                    stock_code=request.stock_code
                )

                # IndicatorResult 객체에서 데이터 추출
                if result and result.columns:
                    # columns는 Dict[str, pd.Series]
                    for col_name, col_series in result.columns.items():
                        if col_name not in ['trade_date', 'open', 'high', 'low', 'close', 'volume']:
                            # ma의 경우 period를 붙임: ma_20
                            if indicator_name == 'ma' and 'period' in params:
                                key = f"{indicator_name}_{params['period']}"
                            else:
                                key = col_name

                            # Series의 마지막 값 추출
                            latest_value = col_series.iloc[-1] if len(col_series) > 0 else None
                            if latest_value is not None and not pd.isna(latest_value):
                                result_indicators[key] = float(latest_value)

                    logger.info(f"✅ Calculated {indicator_name}: {list(result_indicators.keys())}")
                else:
                    logger.warning(f"⚠️ {indicator_name} returned no data")

            except Exception as e:
                logger.error(f"❌ Error calculating {indicator_name}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # 개별 지표 실패 시 계속 진행
                continue

        # 3. close 값 추가 (현재가)
        if 'close' in df.columns:
            result_indicators['close'] = float(df.iloc[-1]['close'])

        logger.info(f"✅ Calculated {len(result_indicators)} indicators for {request.stock_code}")

        return CalculateResponse(
            stock_code=request.stock_code,
            indicators=result_indicators,
            calculated_at=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error calculating indicators: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate indicators: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """API 상태 확인"""
    return {
        "status": "healthy",
        "service": "indicators-api",
        "timestamp": datetime.now().isoformat()
    }
