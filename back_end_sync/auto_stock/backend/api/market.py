"""
시장 데이터 API 엔드포인트
현재가, 과거 데이터, 차트 데이터 제공
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import os
from supabase import create_client

# 키움 API 클라이언트
from .kiwoom_client import get_kiwoom_client

router = APIRouter()

# Supabase 클라이언트 초기화
def get_supabase_client():
    """Supabase 클라이언트 가져오기"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")

    return create_client(url, key)


class CurrentPriceResponse(BaseModel):
    """현재가 응답"""
    stock_code: str
    stock_name: Optional[str] = None
    current_price: float
    change_amount: float
    change_rate: float
    volume: int
    high: Optional[float] = None
    low: Optional[float] = None
    open_price: Optional[float] = None
    prev_close: Optional[float] = None
    timestamp: datetime
    market_status: str = "open"  # open, closed, pre_market, after_market


class HistoricalDataResponse(BaseModel):
    """과거 데이터 응답"""
    stock_code: str
    interval: str  # 1m, 5m, 15m, 1h, 1d
    data: List[Dict[str, Any]]  # [{date, open, high, low, close, volume}, ...]
    count: int


class MultiStockPriceRequest(BaseModel):
    """복수 종목 현재가 요청"""
    stock_codes: List[str] = Field(..., description="종목 코드 리스트", example=["005930", "000660"])


@router.get("/price/{stock_code}", response_model=CurrentPriceResponse)
async def get_current_price(stock_code: str):
    """
    현재가 조회

    Args:
        stock_code: 종목 코드 (예: 005930)

    Returns:
        CurrentPriceResponse: 현재가 정보
    """
    try:
        # 키움 API에서 실시간 시세 조회 (필수)
        kiwoom_client = get_kiwoom_client()
        price_data = kiwoom_client.get_current_price(stock_code)

        if not price_data or price_data['current_price'] <= 0:
            raise HTTPException(
                status_code=503,
                detail=f"실시간 시세 조회 실패 - 키움 API 연결 필요 (종목: {stock_code})"
            )

        # 키움 API 데이터 사용
        current_price = float(price_data['current_price'])
        prev_close = current_price - price_data['change']
        change_amount = float(price_data['change'])
        change_rate = float(price_data['change_rate'])

        print(f"[Market] 키움 API 현재가: {stock_code} = {current_price:,}원")

        # 시장 상태 확인 (09:00-15:30)
        now = datetime.now()
        market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        market_status = "open" if market_open <= now <= market_close else "closed"

        return CurrentPriceResponse(
            stock_code=stock_code,
            stock_name=price_data.get('stock_name') if isinstance(price_data, dict) else None,
            current_price=current_price,
            change_amount=change_amount,
            change_rate=change_rate,
            volume=int(price_data.get('volume', 0)) if isinstance(price_data, dict) else 0,
            high=float(price_data.get('high', 0)) if isinstance(price_data, dict) else None,
            low=float(price_data.get('low', 0)) if isinstance(price_data, dict) else None,
            open_price=float(price_data.get('open', 0)) if isinstance(price_data, dict) else None,
            prev_close=prev_close,
            timestamp=datetime.fromisoformat(price_data.get('timestamp', datetime.now().isoformat())) if isinstance(price_data, dict) and 'timestamp' in price_data else datetime.now(),
            market_status=market_status
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price: {str(e)}")


@router.post("/prices", response_model=List[CurrentPriceResponse])
async def get_multiple_prices(request: MultiStockPriceRequest):
    """
    복수 종목 현재가 조회

    Args:
        request: 종목 코드 리스트

    Returns:
        List[CurrentPriceResponse]: 현재가 정보 리스트
    """
    results = []

    for stock_code in request.stock_codes:
        try:
            price_data = await get_current_price(stock_code)
            results.append(price_data)
        except HTTPException:
            # 개별 종목 실패는 무시하고 계속 진행
            continue

    if not results:
        raise HTTPException(status_code=404, detail="No valid stock data found")

    return results


@router.get("/historical/{stock_code}", response_model=HistoricalDataResponse)
async def get_historical_data(
    stock_code: str,
    interval: str = Query("1d", description="시간 간격 (1m, 5m, 15m, 1h, 1d)", regex="^(1m|5m|15m|1h|1d)$"),
    limit: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    start_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)")
):
    """
    과거 데이터 조회 (기술적 지표 계산용)

    Args:
        stock_code: 종목 코드
        interval: 시간 간격 (1d만 지원, 추후 분봉 추가 예정)
        limit: 조회할 데이터 개수 (기본 100개, 최대 1000개)
        start_date: 시작일 (선택)
        end_date: 종료일 (선택)

    Returns:
        HistoricalDataResponse: 과거 데이터
    """
    try:
        supabase = get_supabase_client()

        # 기본 쿼리
        query = supabase.table('kw_price_daily') \
            .select('trade_date,open,high,low,close,volume') \
            .eq('stock_code', stock_code) \
            .order('trade_date', desc=False)

        # 날짜 필터
        if start_date:
            query = query.gte('trade_date', start_date)
        if end_date:
            query = query.lte('trade_date', end_date)

        # 제한
        query = query.limit(limit)

        response = query.execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"No historical data for {stock_code}")

        # 데이터 정제
        data = []
        for row in response.data:
            data.append({
                'date': row['trade_date'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume'])
            })

        return HistoricalDataResponse(
            stock_code=stock_code,
            interval=interval,
            data=data,
            count=len(data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")


@router.get("/candles/{stock_code}")
async def get_candles(
    stock_code: str,
    count: int = Query(100, description="캔들 개수", ge=1, le=500)
):
    """
    차트용 캔들 데이터 (OHLCV)

    Args:
        stock_code: 종목 코드
        count: 캔들 개수

    Returns:
        차트 라이브러리용 캔들 데이터
    """
    try:
        historical = await get_historical_data(stock_code, interval="1d", limit=count)

        # 차트 라이브러리용 포맷
        candles = []
        for item in historical.data:
            candles.append({
                'time': item['trade_date'],
                'open': item['open'],
                'high': item['high'],
                'low': item['low'],
                'close': item['close'],
                'volume': item['volume']
            })

        return {
            'stock_code': stock_code,
            'candles': candles,
            'count': len(candles)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch candles: {str(e)}")


@router.get("/market-status")
async def get_market_status():
    """
    시장 상태 확인

    Returns:
        시장 개장 여부, 현재 시간, 다음 개장/폐장 시간
    """
    now = datetime.now()

    # 한국 시장 시간 (09:00-15:30)
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

    is_open = market_open <= now <= market_close

    # 주말 체크
    is_weekend = now.weekday() >= 5  # 5=토요일, 6=일요일

    # 다음 이벤트 시간
    if is_open and not is_weekend:
        next_event = "close"
        next_event_time = market_close
    else:
        next_event = "open"
        # 다음 평일 09:00
        next_day = now + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        next_event_time = next_day.replace(hour=9, minute=0, second=0, microsecond=0)

    return {
        'is_open': is_open and not is_weekend,
        'is_weekend': is_weekend,
        'current_time': now.isoformat(),
        'market_open_time': market_open.isoformat(),
        'market_close_time': market_close.isoformat(),
        'next_event': next_event,
        'next_event_time': next_event_time.isoformat(),
        'time_to_next_event_minutes': int((next_event_time - now).total_seconds() / 60)
    }
