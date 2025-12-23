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
import asyncio

from indicators.calculator import IndicatorCalculator
from data.provider import DataProvider

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
    days: int = 200  # 과거 데이터 일수 (정확도 향상을 위해 60 -> 200일로 증량)


class CalculateResponse(BaseModel):
    """지표 계산 응답 모델"""
    stock_code: str
    stock_name: Optional[str] = None
    indicators: Dict[str, float]  # {"ma_20": 75000, "rsi": 45.5, ...}
    calculated_at: str


# Global instance (Lazy initialization)
calculator_instance = None

def get_calculator():
    global calculator_instance
    if calculator_instance is None:
        try:
            calculator_instance = IndicatorCalculator()
        except Exception as e:
            logger.error(f"Failed to initialize IndicatorCalculator: {e}")
            # Return None or raise, but logging is good for now.
            # If we return None, the route handler should handle it.
            raise
    return calculator_instance

@router.post("/calculate", response_model=CalculateResponse)
async def calculate_indicators(request: CalculateRequest):
    """
    주식 종목에 대한 기술적 지표를 계산합니다.
    
    ... (docstring omitted for brevity) ...
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

        # 1.5 현재가 병합 (frontend logic과 동일하게 맞춤)
        # kw_price_current 테이블에서 최신 가격 조회
        try:
             # run_in_executor for sync supabase call
            loop = asyncio.get_event_loop()
            curr_resp = await loop.run_in_executor(None, lambda: data_provider.supabase.table('kw_price_current').select('*').eq('stock_code', request.stock_code).execute())
            
            if curr_resp.data and len(curr_resp.data) > 0:
                row = curr_resp.data[0]
                current_price = float(row.get('current_price') or 0)
                
                if current_price > 0:
                    now = datetime.now()
                    last_date = df.index[-1]
                    # 오늘 날짜의 데이터가 없으면 추가
                    if last_date.date() < now.date():
                        new_row = pd.DataFrame([{
                            'open': current_price, 'high': current_price, 
                            'low': current_price, 'close': current_price, 
                            'volume': 0 
                        }], index=[pd.Timestamp(now)])
                        df = pd.concat([df, new_row])
                        logger.info(f"➕ Appended current price {current_price} for {request.stock_code}")
                    # 오늘 날짜 데이터가 있으면 업데이트 (종가=현재가)
                    elif last_date.date() == now.date():
                        df.iloc[-1, df.columns.get_loc('close')] = current_price
                        logger.info(f"🔄 Updated today's close to {current_price} for {request.stock_code}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to merge current price: {e}")
            # 실패해도 과거 데이터로 계산 계속 진행


        # 2. 지표 계산
        # Use lazy initialization
        calculator = get_calculator()
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

        # 4. 종목명 조회
        stock_name = await data_provider.get_stock_name(request.stock_code)

        return CalculateResponse(
            stock_code=request.stock_code,
            stock_name=stock_name,
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
