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
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

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


# ... (existing imports)
import exchange_calendars as ecals
import pytz

# ... (rest of the file)

@router.get("/market-status")
async def get_market_status():
    """
    시장 상태 확인 (exchange_calendars 사용)
    - 공휴일, 수능일 등 특이사항 자동 반영
    - 주말 체크
    """
    # 한국 시간 기준 (Pandas Timestamp 사용이 ecals와 호환성 좋음)
    tz = 'Asia/Seoul'
    now = pd.Timestamp.now(tz=tz)
    
    # XKRX (한국거래소) 캘린더 로드
    xkrx = ecals.get_calendar("XKRX")
    
    # 오늘이 개장일인지 확인 (주말/공휴일 자동 체크)
    is_session = xkrx.is_session(now.strftime('%Y-%m-%d'))
    
    # 현재 장 중인지 확인 (09:00 ~ 15:30, 수능일 등 반영됨)
    # is_open_on_minute는 분 단위로 체크
    is_open = xkrx.is_open_on_minute(now)
    
    market_open_time = None
    market_close_time = None
    
    if is_session:
        # 오늘의 개장/폐장 시간 조회
        try:
            schedule = xkrx.schedule.loc[now.strftime('%Y-%m-%d')]
            # Robust access with fallback keys
            market_open = schedule.get('market_open') if hasattr(schedule, 'get') else schedule['market_open']
            market_close = schedule.get('market_close') if hasattr(schedule, 'get') else schedule['market_close']
            
            market_open_time = market_open.tz_convert(tz)
            market_close_time = market_close.tz_convert(tz)
        except Exception as e:
            print(f"[WARNING] Schedule lookup failed: {e}. Using default hours.")
            # Fallback to default KRX hours (09:00 - 15:30)
            market_open_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # 다음 이벤트 계산
    next_open = xkrx.next_open(now).tz_convert(tz)
    next_close = xkrx.next_close(now).tz_convert(tz)
    
    if is_open:
        next_event = "close"
        next_event_time = next_close
    else:
        next_event = "open"
        next_event_time = next_open

    return {
        'is_open': is_open,
        'is_session': is_session, # 오늘이 개장일인지 (휴장일이면 False)
        'current_time': now.isoformat(),
        'market_open_time': market_open_time.isoformat() if market_open_time else None,
        'market_close_time': market_close_time.isoformat() if market_close_time else None,
        'next_event': next_event,
        'next_event_time': next_event_time.isoformat(),
        'time_to_next_event_minutes': int((next_event_time - now).total_seconds() / 60)
    }

from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime
import json
import os

# Use 'logs' directory which is mounted as volume (- ./logs:/app/logs)
# This ensures data persists even after container rebuild/deploy
DATA_FILE_PATH = "logs/market_data_cache.json"

def get_mock_indices():
    """Fallback mock data to prevent empty UI (Matches 4x4 Layout)"""
    return [
        # Row 1: Core
        {"index_code": "S&P500", "current_value": 4780.25, "change_value": 30.10, "change_rate": 0.63},
        {"index_code": "NASDAQ", "current_value": 15050.60, "change_value": 120.40, "change_rate": 0.81},
        {"index_code": "KOSPI", "current_value": 2600.00, "change_value": 15.50, "change_rate": 0.60},
        {"index_code": "KOSDAQ", "current_value": 850.20, "change_value": -5.20, "change_rate": -0.61},
        
        # Row 2: Global
        {"index_code": "Nikkei225", "current_value": 33400.50, "change_value": 150.00, "change_rate": 0.45},
        {"index_code": "EuroStoxx50", "current_value": 4450.20, "change_value": -10.50, "change_rate": -0.23},
        {"index_code": "DowJones", "current_value": 37600.10, "change_value": 45.30, "change_rate": 0.12},
        {"index_code": "Russell2000", "current_value": 1950.40, "change_value": 12.10, "change_rate": 0.62},

        # Row 3: Money
        {"index_code": "WTI_Oil", "current_value": 72.50, "change_value": -0.80, "change_rate": -1.09},
        {"index_code": "Gold", "current_value": 2045.30, "change_value": 15.20, "change_rate": 0.75},
        {"index_code": "USD/KRW", "current_value": 1320.50, "change_value": 2.50, "change_rate": 0.19},
        {"index_code": "Bitcoin", "current_value": 65000000, "change_value": 1500000, "change_rate": 2.36},

        # Row 4: Risk
        {"index_code": "US10Y", "current_value": 3.95, "change_value": 0.05, "change_rate": 1.28},
        {"index_code": "US2Y_ETF", "current_value": 82.50, "change_value": -0.10, "change_rate": -0.12},
        {"index_code": "VIX", "current_value": 13.50, "change_value": -0.40, "change_rate": -2.88},
        {"index_code": "TLT", "current_value": 98.20, "change_value": 0.50, "change_rate": 0.51}
    ]

def load_cache_from_disk():
    """
    Load cached data from JSON file on server start.
    Performs 'Smart Merge': If disk cache lacks new items (e.g. only 8 items),
    it automatically fills the gaps with Mock Data (16 items).
    """
    loaded_data = []
    if os.path.exists(DATA_FILE_PATH):
        try:
            with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                print(f"[System] Disk Cache Loaded: {len(loaded_data)} items")
        except Exception as e:
            print(f"[Error] Failed to load disk cache: {e}")
    
    # Smart Merge Logic
    # 1. Get full desired list (Mock has all 16 keys)
    full_template = get_mock_indices() # List of dicts
    
    # 2. Convert loaded data to dict for easy lookup
    loaded_map = {item['index_code']: item for item in loaded_data}
    
    # 3. Merge: Prefer loaded data, fall back to mock if missing
    final_cache = []
    for mock_item in full_template:
        code = mock_item['index_code']
        if code in loaded_map:
            final_cache.append(loaded_map[code]) # Keep real/cached data
        else:
            final_cache.append(mock_item) # Fill gap with mock
            print(f"[System] Augmented missing index '{code}' with mock data.")
            
    return final_cache

# --- [Scheduler & Cache Configuration] ---
# In-memory Cache (Initialized from Disk + Smart Merge)
GLOBAL_INDICES_CACHE = load_cache_from_disk()
LAST_UPDATED_TIME = datetime.datetime.now()

# Helper: Create Cached Session for yfinance
def get_yfinance_session():
    session = requests.Session()
    # "Browser-like" User-Agent to avoid AWS IP Blocking
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    return session

def fetch_global_indices_background():
    """
    Background Task: Fetch market data every 10 minutes.
    Updates GLOBAL_INDICES_CACHE in memory.
    """
    global GLOBAL_INDICES_CACHE, LAST_UPDATED_TIME
    print(f"[Market Scheduler] Starting update at {datetime.datetime.now()}...")
    
    # KOSPI, KOSDAQ, USD/KRW (Use FinanceDataReader - Naver Finance source is reliable on AWS)
    import FinanceDataReader as fdr
    
    fdr_indices = {
        "KOSPI": "KS11",
        "KOSDAQ": "KQ11", 
        "USD_KRW": "USD/KRW",
        "SPX": "S&P500",
        "COMP": "IXIC"
    }

    # Bonds (Use yfinance as fallback or specific tickers)
    yf_indices = {
        "IEF": "IEF",
        "TLT": "TLT",
        "LQD": "LQD"
    }

    new_data = []

    try:
        # 1. Fetch from FinanceDataReader
        for name, ticker in fdr_indices.items():
            try:
                # Get last 5 days
                # Use pandas for reliable time handling
                start_date = (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
                df = fdr.DataReader(ticker, start_date)
                
                if df is None or df.empty:
                    print(f"  [Fail] FDR {name}: No data")
                    continue
                
                last_row = df.iloc[-1]
                prev_row = df.iloc[-2] if len(df) > 1 else last_row 
                
                current = float(last_row['Close'])
                prev_close = float(prev_row['Close'])
                
                change = current - prev_close
                change_rate = (change / prev_close * 100) if prev_close != 0 else 0.0

                new_data.append({
                    "index_code": name,
                    "current_value": round(current, 2),
                    "change_value": round(change, 2),
                    "change_rate": round(change_rate, 2),
                    "updated_at": pd.Timestamp.now().isoformat()
                })
                print(f"[Market Scheduler] Fetched {name} (FDR): {current}")

            except Exception as e:
                print(f"[Market Scheduler] FDR fetch failed for {name}: {e}")

        # 2. Fetch from yfinance (for Bonds/others)
        session = requests.Session()
        session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        
        for name, ticker in yf_indices.items():
            try:
                tick = yf.Ticker(ticker, session=session)
                hist = tick.history(period="5d")
                if hist.empty:
                    continue
                
                last_row = hist.iloc[-1]
                prev_row = hist.iloc[-2] if len(hist) > 1 else last_row
                
                current = float(last_row['Close'])
                prev_close = float(prev_row['Close'])
                change = current - prev_close
                change_rate = (change / prev_close) * 100 if prev_close != 0 else 0

                new_data.append({
                    "index_code": name,
                    "current_value": round(current, 2),
                    "change_value": round(change, 2),
                    "change_rate": round(change_rate, 2),
                    "updated_at": pd.Timestamp.now().isoformat()
                })
                print(f"[Market Scheduler] Fetched {name} (YF): {current}")
            except Exception as e:
                print(f"[Market Scheduler] YF fetch failed for {name}: {e}")

        # Update cache if we got data
        if len(new_data) > 0:
            # Upsert into Cache
            current_map = {item['index_code']: item for item in GLOBAL_INDICES_CACHE}
            for item in new_data:
                current_map[item['index_code']] = item
            
            GLOBAL_INDICES_CACHE = list(current_map.values())
            
            # Save to disk
            try:
                with open(DATA_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(GLOBAL_INDICES_CACHE, f, ensure_ascii=False, indent=2)
                print(f"[Market Scheduler] Persisted {len(GLOBAL_INDICES_CACHE)} items to disk.")
            except Exception as e:
                print(f"[Market Scheduler] Failed to save to disk: {e}")
        else:
             print("[Market Scheduler] Fetch returned 0 items. Keeping old cache.")

    except Exception as e:
        print(f"[Market Scheduler] Critical Error: {e}")

class MarketDataPayload(BaseModel):
    data: List[Dict[str, Any]]

# ... existing code ...

@router.post("/update-data")
def update_global_indices(payload: dict):
    """
    Receive data from NAS (Python Fetcher).
    Uses 'Smart Merge': Updates only the items provided, keeping existing data for others.
    """
    global GLOBAL_INDICES_CACHE, LAST_UPDATED_TIME
    
    try:
        new_data_list = payload.get("data", [])
        if not new_data_list:
            return {"status": "ignored", "msg": "No data received"}

        # 1. Convert current cache to Dict {code: item}
        cache_map = {item['index_code']: item for item in GLOBAL_INDICES_CACHE}
        
        # 2. Update with new data
        updated_count = 0
        for new_item in new_data_list:
            code = new_item['index_code']
            # Ensure updated_at exists
            if 'updated_at' not in new_item:
                 new_item['updated_at'] = datetime.datetime.now().isoformat() # Changed datetime.now() to datetime.datetime.now()
            
            cache_map[code] = new_item
            updated_count += 1
            
        # 3. Convert back to List and Save
        GLOBAL_INDICES_CACHE = list(cache_map.values())
        LAST_UPDATED_TIME = datetime.datetime.now() # Changed datetime.now() to datetime.datetime.now()
        
        # Save to Disk
        try:
            with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(GLOBAL_INDICES_CACHE, f, ensure_ascii=False, indent=2)
            print(f"[Market Receiver] Successfully saved {len(GLOBAL_INDICES_CACHE)} items to disk.")
        except Exception as e:
            print(f"[Market Receiver] Failed to save to disk: {e}")

        return {"status": "success", "updated_items": updated_count, "total_items": len(GLOBAL_INDICES_CACHE)}

    except Exception as e:
        print(f"[Market Receiver] Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Call this from main.py @app.on_event("startup")
def start_market_scheduler():
    scheduler = BackgroundScheduler()
    # AWS IP Blocking Issue:
    # Disable internal fetching from AWS. Only listen to NAS push.
    # scheduler.add_job(fetch_global_indices_background, 'interval', minutes=10)
    
    scheduler.start()
    print("[System] Market Data Scheduler Started (Internal Fetch Disabled - Waiting for NAS Push)")
    
    # Run once immediately? No, wait for NAS.
    # try:
    #      fetch_global_indices_background()
    # except:
    #      pass

@router.get("/global-indices")
async def get_global_indices():
    """
    Return InMemory Cached Data immediately.
    Zero latency, no blocking.
    """
    return GLOBAL_INDICES_CACHE


# --- [Backfill & Daily Close Logic] ---
class SyncHistoryRequest(BaseModel):
    stock_codes: List[str]
    days: int = 100

@router.post("/sync-history")
async def sync_history(request: SyncHistoryRequest):
    """
    특정 종목들의 과거 데이터를 백필합니다. (FinanceDataReader 사용)
    - stock_codes: 대상 종목 코드 리스트
    - days: 백필할 기간 (기본 100일)
    """
    import FinanceDataReader as fdr
    import pandas as pd
    
    supabase = get_supabase_client()
    results = {"success": [], "failed": []}
    
    start_date = (datetime.datetime.now() - timedelta(days=request.days)).strftime('%Y-%m-%d')
    
    print(f"[Market] Starting backfill for {len(request.stock_codes)} stocks (since {start_date})...")
    
    for code in request.stock_codes:
        try:
            # Fetch data from Naver Finance via FDR
            df = fdr.DataReader(code, start_date)
            
            if df is None or df.empty:
                results["failed"].append({"code": code, "reason": "No data returned"})
                continue
                
            # Prepare for DB Insert
            records = []
            for date, row in df.iterrows():
                # Ensure date is string
                trade_date = date.strftime('%Y-%m-%d')
                
                records.append({
                    "stock_code": code,
                    "trade_date": trade_date,
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                    "change_rate": float(row['Change']) * 100 if 'Change' in row else 0
                })
            
            if not records:
                continue

            # Upsert to Supabase
            # Note: Supabase bulk upsert matches on Primary Key (assumed: stock_code + trade_date)
            response = supabase.table('kw_price_daily').upsert(records).execute()
            
            results["success"].append({"code": code, "count": len(records)})
            print(f"[Market] Backfilled {code}: {len(records)} rows")
            
        except Exception as e:
            print(f"[Market] Failed backfill for {code}: {e}")
            results["failed"].append({"code": code, "reason": str(e)})
            
    return results


@router.post("/daily-close")
async def daily_close_batch():
    """
    [장 마감 배치]
    모든 활성 전략의 유니버스 종목에 대해 '최근 5일' 데이터를 동기화합니다.
    - 장 마감 후 실행 권장 (15:40 이후)
    - 누락된 데이터 자동 복구
    """
    import FinanceDataReader as fdr
    
    supabase = get_supabase_client()
    
    # 1. Fetch all active stock codes using RPC
    try:
        rpc_response = supabase.rpc('get_active_strategies_with_universe').execute()
        strategies = rpc_response.data if rpc_response.data else []
        
        unique_stocks = set()
        for strategy in strategies:
            stocks = strategy.get('filtered_stocks', [])
            if isinstance(stocks, list):
                for s in stocks:
                    unique_stocks.add(s)
            elif isinstance(stocks, dict):
                 for s in stocks.values():
                    unique_stocks.add(s)
                    
        target_codes = list(unique_stocks)
        print(f"[DailyClose] Found {len(target_codes)} unique stocks to sync.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active universe: {e}")

    # 2. Sync Last 5 Days for all targets
    # We reuse the logic from sync_history but with fixed 5 days
    results = {"success": [], "failed": []}
    days_to_sync = 5
    start_date = (datetime.datetime.now() - timedelta(days=days_to_sync)).strftime('%Y-%m-%d')
    
    for code in target_codes:
        try:
            df = fdr.DataReader(code, start_date)
            
            if df is None or df.empty:
                results["failed"].append(code)
                continue
                
            records = []
            for date, row in df.iterrows():
                trade_date = date.strftime('%Y-%m-%d')
                records.append({
                    "stock_code": code,
                    "trade_date": trade_date,
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                    "change_rate": float(row['Change']) * 100 if 'Change' in row else 0
                })
            
            if records:
                supabase.table('kw_price_daily').upsert(records).execute()
                results["success"].append(code)
                
        except Exception as e:
            print(f"[DailyClose] Error {code}: {e}")
            results["failed"].append(code)
            
    return {
        "status": "completed",
        "total_targets": len(target_codes),
        "success_count": len(results["success"]),
        "fail_count": len(results["failed"]),
        "failed_stocks": results["failed"]
    }
