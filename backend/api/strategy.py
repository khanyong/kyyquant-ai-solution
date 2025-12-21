"""
전략 실행 및 신호 생성 API 엔드포인트
n8n 워크플로우에서 호출하여 매매 신호 생성
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import os
from supabase import create_client
import asyncio
import math

# 지표 계산기 임포트 (실제 사용 파일)
from indicators.calculator import IndicatorCalculator, ExecOptions

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


# 지표 계산기 (Lazy initialization)
_indicator_calculator = None

def get_indicator_calculator():
    """지표 계산기 싱글톤"""
    global _indicator_calculator
    if _indicator_calculator is None:
        _indicator_calculator = IndicatorCalculator()
    return _indicator_calculator


class StrategySignalRequest(BaseModel):
    """전략 신호 확인 요청"""
    strategy_id: str = Field(..., description="전략 ID (UUID)")
    stock_code: str = Field(..., description="종목 코드", example="005930")
    current_price: Optional[float] = Field(None, description="현재가 (선택)")


class StrategySignalResponse(BaseModel):
    """전략 신호 응답"""
    strategy_id: str
    strategy_name: str
    stock_code: str
    stock_name: Optional[str] = None
    signal_type: str  # BUY, SELL, HOLD
    signal_strength: float  # 0.0 ~ 1.0
    current_price: float
    indicators: Dict[str, Any]  # 계산된 지표 값
    entry_conditions_met: Dict[str, bool]  # 진입 조건별 충족 여부
    exit_conditions_met: Dict[str, bool]  # 청산 조건별 충족 여부
    timestamp: datetime
    debug_info: Optional[Dict[str, Any]] = None


class BatchSignalRequest(BaseModel):
    """배치 신호 확인 요청"""
    strategy_id: str
    stock_codes: List[str] = Field(..., description="종목 코드 리스트")


class PositionExitRequest(BaseModel):
    """포지션 청산 확인 요청"""
    position_id: str = Field(..., description="포지션 ID")
    stock_code: str = Field(..., description="종목 코드")
    entry_price: float = Field(..., description="진입가")
    current_quantity: int = Field(..., description="현재 보유 수량")
    strategy_id: str = Field(..., description="전략 ID")


class PositionExitResponse(BaseModel):
    """포지션 청산 응답"""
    position_id: str
    should_exit: bool
    exit_type: str  # stop_loss, profit_target, trailing_stop, strategy_signal, none
    exit_percentage: float  # 청산 비율 (0.2 = 20%, 1.0 = 100%)
    exit_quantity: int
    current_price: float
    entry_price: float
    profit_loss: float
    profit_loss_rate: float
    reason: str


class StrategyVerificationResult(BaseModel):
    strategy_name: str
    stock_code: str
    stock_name: str
    current_price: float
    signal_type: str
    score: float
    details: Dict[str, Any]

class VerificationTarget(BaseModel):
    strategy_id: str
    strategy_name: str
    stock_codes: List[str]

@router.get("/verification-targets", response_model=List[VerificationTarget])
async def get_verification_targets():
    """
    검증 대상 전략 및 종목 리스트 조회 (클라이언트 사이드 배치 처리용)
    """
    try:
        supabase = get_supabase_client()
        
        # 1. 활성 전략 + 유니버스 조회 (RPC 사용)
        rpc_response = supabase.rpc('get_active_strategies_with_universe', {}).execute()
        strategies_data = rpc_response.data
        
        if not strategies_data:
            return []
            
        targets = []
        for item in strategies_data:
            strategy_name = item.get('strategy_name', 'Unknown')
            target_stocks = []
            
            # 1. Top-Level filtered_stocks
            f_stocks_top = item.get('filtered_stocks')
            if f_stocks_top:
                for s in f_stocks_top:
                    if isinstance(s, dict) and 'stock_code' in s:
                        target_stocks.append(s['stock_code'])
                    elif isinstance(s, str):
                        target_stocks.append(s)
            
            # 2. 'universes' 키 확인
            if item.get('universes'):
                for u in item['universes']:
                    f_stocks = u.get('filtered_stocks')
                    if f_stocks:
                        for s in f_stocks:
                            if isinstance(s, dict) and 'stock_code' in s:
                                target_stocks.append(s['stock_code'])
                            elif isinstance(s, str):
                                target_stocks.append(s)
            
            # 중복 제거 및 정렬
            target_stocks = sorted(list(set(target_stocks)))
            
            if target_stocks:
                targets.append(VerificationTarget(
                    strategy_id=item['strategy_id'],
                    strategy_name=strategy_name,
                    stock_codes=target_stocks
                ))
                
        return targets

    except Exception as e:
        print(f"[Targets] Failed to fetch targets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch verification targets: {str(e)}")


@router.post("/verify-all", response_model=List[StrategyVerificationResult])
async def verify_all_strategies():
    """
    모든 활성 전략에 대해 유니버스 종목 검증
    (자동매매 탭의 '검증' 버튼용)
    """
    results = []
    try:
        print("[VerifyAll] Starting verification process...")
        supabase = get_supabase_client()
        import math # NaN 체크용
        
        # n8n 워크플로우와 동일한 엔진 로직 사용
        print("[VerifyAll] Importing BacktestEngine...")
        from backtest.engine import BacktestEngine
        
        # 1. 활성 전략 + 유니버스 조회 (RPC 사용)
        print("[VerifyAll] Calling RPC: get_active_strategies_with_universe")
        rpc_response = supabase.rpc('get_active_strategies_with_universe', {}).execute()
        print(f"[VerifyAll] RPC Response: {rpc_response}")
        strategies_data = rpc_response.data
        
        if not strategies_data:
            return []
            
        # 전략별로 종목 그룹화 to avoid multiple strategy fetches
        # RPC returns flattened list: strategy info + 1 filtered_stocks array per filter
        
        # 2. 검증 루프
        engine = BacktestEngine()
        
        # 성능을 위해 전체 대상 종목의 현재가 한 번에 조회? 
        # API 구조상 275개 조회는 루프로 처리하되, 너무 느리면 최적화 필요.
        # 일단 순차 처리 (안정성 우선).
        
        engine = BacktestEngine()
        
        # 동시성 제어 (Supabase 연결 제한 고려: 50 -> 20으로 감소)
        # 너무 많은 동시 연결은 DB Pool 고갈을 유발할 수 있음 (총 550개 쿼리 발생)
        sem = asyncio.Semaphore(20)

        async def process_single_stock(stock_code: str, strategy_name: str, strategy_config: dict) -> Optional[StrategyVerificationResult]:
            async with sem:
                try:
                    # 1. 과거 데이터 조회 (Blocking I/O - Worker Thread 실행)
                    def fetch_data():
                        # 200일 치 데이터 조회
                        p_resp = supabase.table('kw_price_daily').select('trade_date,open,high,low,close,volume').eq('stock_code', stock_code).order('trade_date', desc=False).limit(200).execute()
                        # 실시간 현재가 조회
                        c_resp = supabase.table('kw_price_current').select('*').eq('stock_code', stock_code).limit(1).execute()
                        return p_resp, c_resp
                        
                    price_response, curr_resp = await asyncio.to_thread(fetch_data)

                    if not price_response.data or len(price_response.data) < 20:
                        return None

                    # DataFrame 변환
                    df = pd.DataFrame(price_response.data)
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                    # 현재가 병합 로직
                    current_price = 0.0
                    stock_name = stock_code
                    
                    if curr_resp.data and len(curr_resp.data) > 0:
                        row = curr_resp.data[0]
                        current_price = float(row.get('current_price') or 0)
                        stock_name = row.get('stock_name', stock_code)
                        
                        if current_price > 0:
                            try:
                                now = datetime.now()
                                last_date = df.index[-1]
                                if last_date.date() < now.date():
                                    new_row = pd.DataFrame([{
                                        'open': current_price, 'high': current_price, 'low': current_price, 
                                        'close': current_price, 'volume': 0
                                    }], index=[pd.Timestamp(now)])
                                    df = pd.concat([df, new_row])
                                elif last_date.date() == now.date():
                                    df.iloc[-1, df.columns.get_loc('close')] = current_price
                            except Exception as e:
                                # print(f"DF Error {stock_code}: {e}")
                                pass
                    
                    # Fallback Price
                    if current_price <= 0:
                        if not df.empty:
                            current_price = df.iloc[-1]['close']
                        else:
                            return None
                            
                    # 엔진 평가 (Async)
                    eval_result = await engine.evaluate_snapshot(stock_code, df, strategy_config)
                    
                    # 결과 포맷팅 (Safety Checks)
                    score = eval_result.get('score', 0)
                    if not isinstance(score, (int, float)) or isinstance(score, float) and (math.isnan(score) or math.isinf(score)):
                        score = 0.0
                        
                    signal = eval_result.get('signal', 'hold').upper()
                    if signal == 'CONFLICT': signal = 'HOLD'
                    
                    # 데이터 정제
                    safe_stock_name = stock_name or stock_code or "Unknown"
                    if not isinstance(current_price, (int, float)) or isinstance(current_price, float) and (math.isnan(current_price) or math.isinf(current_price)):
                        current_price = 0.0
                    
                    return StrategyVerificationResult(
                        strategy_name=strategy_name or "Unknown Strategy",
                        stock_code=stock_code,
                        stock_name=safe_stock_name,
                        current_price=float(current_price),
                        signal_type=signal,
                        score=float(score),
                        details={
                            'reasons': eval_result.get('reasons', []),
                            'indicators': _sanitize_for_json(eval_result.get('indicators', {}))
                        }
                    )
                except Exception as e:
                    print(f"[Verify] Error processing {stock_code}: {e}")
                    return None

            
        # 디버깅: 파일로 데이터 구조 저장
        try:
            with open("debug_strategy_data.log", "w", encoding="utf-8") as f:
                f.write(str(strategies_data))
                f.write("\n\nKeys of first item:\n")
                if len(strategies_data) > 0:
                    f.write(str(strategies_data[0].keys()))
        except Exception as e:
            print(f"[VerifyAll] Failed to write debug log: {e}")

        # 모든 작업 생성
        tasks = []
        for item in strategies_data:
            strategy_name = item.get('strategy_name', 'Unknown')
            print(f"[VerifyAll] Processing strategy: {strategy_name}")
            
            # DB 'strategies' 테이블을 다시 조회하여 전체 config를 가져옴
            try:
                full_strategy_resp = supabase.table('strategies').select('*').eq('id', item['strategy_id']).single().execute()
                full_strategy = full_strategy_resp.data
                strategy_config = full_strategy.get('config') or full_strategy
            except Exception as e:
                print(f"[VerifyAll] Failed to fetch full config for {strategy_name}: {e}")
                continue
            
            target_stocks = []
            
            # 1. Top-Level filtered_stocks 확인 (RPC 반환 구조에 따라 다름)
            f_stocks_top = item.get('filtered_stocks')
            if f_stocks_top:
                print(f"[VerifyAll] Found {len(f_stocks_top)} stocks in top-level 'filtered_stocks'.")
                for s in f_stocks_top:
                    if isinstance(s, dict) and 'stock_code' in s:
                        target_stocks.append(s['stock_code'])
                    elif isinstance(s, str):
                        target_stocks.append(s)
            
            # 2. 'universes' 키 확인 (Nested 구조일 경우)
            if item.get('universes'):
                print(f"[VerifyAll] Universes found: {len(item['universes'])}")
                for u in item['universes']:
                    u_name = u.get('universe_name', 'Unknown')
                    f_stocks = u.get('filtered_stocks')
                    
                    if f_stocks:
                        print(f"[VerifyAll] Universe {u_name} has {len(f_stocks)} stocks.")
                        for s in f_stocks:
                            if isinstance(s, dict) and 'stock_code' in s:
                                target_stocks.append(s['stock_code'])
                            elif isinstance(s, str):
                                target_stocks.append(s)
                            else:
                                print(f"[VerifyAll] Unknown stock format in universe: {s}")
            
            if not target_stocks:
                print(f"[VerifyAll] Strategy {strategy_name} has NO stocks found (checked top-level and universes).")
            
            # 중복 제거
            target_stocks = list(set(target_stocks))
            print(f"[VerifyAll] Target stocks (unique): {len(target_stocks)}")
            
            for stock_code in target_stocks:
                # process_single_stock 호출 (비동기 엔진 사용, 내부에서 to_thread)
                tasks.append(process_single_stock(stock_code, strategy_name, strategy_config))
                
        print(f"[VerifyAll] processing {len(tasks)} items concurrently...")
        
        # 병렬 실행
        if tasks:
            results_raw = await asyncio.gather(*tasks)
            # None 제외 (타임아웃 등 고려)
            results = [r for r in results_raw if r is not None]
        
        print(f"[VerifyAll] Completed. Total results: {len(results)}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
        
    return results

def _sanitize_for_json(data: Any) -> Any:
    """JSON 직렬화를 위해 NaN, Infinity 등을 None으로 변환"""
    import math
    if isinstance(data, dict):
        return {k: _sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_sanitize_for_json(v) for v in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    return data
async def check_strategy_signal(request: StrategySignalRequest):
    """
    전략 신호 확인 (n8n 워크플로우에서 호출)

    실시간 데이터를 기반으로 전략의 진입/청산 조건을 평가하고 매매 신호 생성
    BacktestEngine의 로직을 재사용하여 일관된 신호 생성 보장

    Args:
        request: 전략 ID, 종목 코드

    Returns:
        StrategySignalResponse: 매매 신호 (BUY/SELL/HOLD)
    """
    try:
        supabase = get_supabase_client()
        from backtest.engine import BacktestEngine

        # 1. 전략 정보 조회
        strategy_response = supabase.table('strategies') \
            .select('*') \
            .eq('id', request.strategy_id) \
            .single() \
            .execute()

        if not strategy_response.data:
            raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_id} not found")

        strategy = strategy_response.data
        
        # 전략 설정 추출 (BacktestEngine 호환성)
        # 1. 'config' 필드가 있으면 사용
        # 2. 없으면 strategy 전체를 사용 (구버전 호환)
        strategy_config = strategy.get('config') or strategy

        # 2. 과거 데이터 조회 (충분한 기간 확보)
        # 지표 계산을 위해 최소 200일 이상 권장
        required_bars = 200 # 넉넉하게 고정

        price_response = supabase.table('kw_price_daily') \
            .select('trade_date,open,high,low,close,volume') \
            .eq('stock_code', request.stock_code) \
            .order('trade_date', desc=False) \
            .limit(required_bars) \
            .execute()

        if not price_response.data or len(price_response.data) < 20:
            raise HTTPException(status_code=400, detail=f"Insufficient historical data for {request.stock_code}")

        # DataFrame 생성
        df = pd.DataFrame(price_response.data)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        df = df.astype(float)

        # 3. 현재가 확인 및 데이터 추가
        current_price = request.current_price
        stock_name = None
        is_realtime_price = False
        
        if current_price is None:
            kiwoom_client = get_kiwoom_client()
            try:
                price_data = kiwoom_client.get_current_price(request.stock_code)
                if price_data and price_data.get('current_price') and float(price_data['current_price']) > 0:
                    current_price = float(price_data['current_price'])
                    stock_name = price_data.get('stock_name')
                    is_realtime_price = True
                    print(f"[Strategy] 키움 API 현재가: {request.stock_code} ({stock_name}) = {current_price:,}원")
            except Exception as e:
                print(f"[Strategy] 키움 API 조회 에러 (Fallback 시도): {e}")

            # Fallback: 실시간 조회 실패 시 DB 최신 종가 사용
            if current_price is None:
                if not df.empty:
                    current_price = float(df.iloc[-1]['close'])
                    print(f"[Strategy] 경고: 실시간 시세 실패, DB 최신 종가 사용: {request.stock_code} = {current_price:,}원 ({df.index[-1].date()})")
                else:
                    raise HTTPException(
                        status_code=503,
                        detail=f"실시간 시세 조회 실패 및 DB 데이터 부재 (종목: {request.stock_code})"
                    )
            
        # Ensure stock name is present (for N8N / Reporting)
        if not stock_name:
            try:
                # 1. Try kw_stock_master
                name_resp = supabase.table('kw_stock_master').select('stock_name').eq('stock_code', request.stock_code).execute()
                if name_resp.data and len(name_resp.data) > 0:
                    stock_name = name_resp.data[0].get('stock_name')
                
                # 2. Try kw_price_current as fallback
                if not stock_name:
                    price_resp = supabase.table('kw_price_current').select('stock_name').eq('stock_code', request.stock_code).execute()
                    if price_resp.data and len(price_resp.data) > 0:
                        stock_name = price_resp.data[0].get('stock_name')
            except Exception as e:
                print(f"[Strategy] 종목명 조회 실패: {e}")

        # 최신 데이터 행 추가 (Real-time Evaluation용)
        # 마지막 데이터 날짜 확인
        last_date = df.index[-1]
        now = datetime.now()
        
        # 만약 마지막 데이터가 오늘 날짜가 아니라면 추가 (장중/장마감 후)
        # 이미 오늘자 데이터가 있으면 업데이트 (덮어쓰기)
        if last_date.date() < now.date():
            new_row = pd.DataFrame([{
                'open': current_price, 
                'high': current_price, 
                'low': current_price, 
                'close': current_price, 
                'volume': 0 # 거래량은 알 수 없으므로 0 또는 직전값
            }], index=[pd.Timestamp(now)])
            df = pd.concat([df, new_row])
        elif last_date.date() == now.date():
            # 오늘 데이터가 이미 있으면 종가(close)를 현재가로 업데이트
            df.iloc[-1, df.columns.get_loc('close')] = current_price
            # 고가/저가 업데이트
            if current_price > df.iloc[-1]['high']:
                 df.iloc[-1, df.columns.get_loc('high')] = current_price
            if current_price < df.iloc[-1]['low']:
                 df.iloc[-1, df.columns.get_loc('low')] = current_price

        # 4. BacktestEngine을 이용한 신호 평가
        engine = BacktestEngine()
        result = await engine.evaluate_snapshot(request.stock_code, df, strategy_config)

        # 5. 응답 구성
        # result 구조: {'signal': 'buy'/'sell'/'hold', 'reasons': [], 'indicators': {}, ...}
        
        signal_type = result.get('signal', 'hold').upper()
        if signal_type == 'CONFLICT': signal_type = 'HOLD' # 충돌 시 보수적 접근
        
        # 진입/청산 조건 충족 여부 (상세 정보 매핑)
        entry_met = {}
        if signal_type == 'BUY':
            for r in result.get('reasons', []):
                entry_met[str(r)] = True
                
        exit_met = {}
        if signal_type == 'SELL':
             for r in result.get('reasons', []):
                exit_met[str(r)] = True

        # [PERSISTENCE FIX] DB에 신호 저장 (프론트엔드 '실시간 매매신호' 표시용)
        if signal_type in ['BUY', 'SELL']:
            try:
                # DB에는 소문자로 저장 (기존 데이터 일관성)
                db_signal_type = signal_type.lower()
                
                signal_record = {
                    'strategy_id': request.strategy_id,
                    'stock_code': request.stock_code,
                    'stock_name': stock_name or request.stock_code,
                    'signal_type': db_signal_type,
                    'signal_strength': result.get('score', 0),
                    'current_price': current_price,
                    'strategy_name': strategy.get('name', 'Unknown'),
                    'conditions_met': entry_met if signal_type == 'BUY' else exit_met,
                    'status': 'new',
                    'created_at': datetime.now().isoformat()
                }
                
                # 비동기 상황이지만 supabase-py는 동기 호출이므로 바로 실행
                # (성능 영향이 클 경우 background task로 분리 고려)
                supabase.table('trading_signals').insert(signal_record).execute()
                print(f"[Strategy] Signal saved to DB: {request.stock_code} {signal_type}")
                
            except Exception as e:
                print(f"[Strategy] Failed to save signal to DB: {e}")

        return StrategySignalResponse(
            strategy_id=request.strategy_id,
            strategy_name=strategy.get('name', 'Unknown'),
            stock_code=request.stock_code,
            stock_name=stock_name,
            signal_type=signal_type,
            signal_strength=result.get('score', 0) / 100.0 if result.get('score') else 0.0,
            current_price=current_price,
            indicators=result.get('indicators', {}),
            entry_conditions_met=entry_met,
            exit_conditions_met=exit_met,
            timestamp=datetime.now(),
            debug_info={
                'data_points': len(df),
                'latest_date': df.index[-1].isoformat(),
                'engine_result': result
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to check signal: {str(e)}")


@router.post("/batch-check", response_model=List[StrategyVerificationResult])
async def batch_check_strategies(request: BatchSignalRequest):
    """
    배치 신호 확인 (여러 종목 동시 처리)
    클라이언트 사이드 배치 처리를 지원하기 위한 엔드포인트
    """
    try:
        supabase = get_supabase_client()
        import math
        from backtest.engine import BacktestEngine
        
        # 1. 전략 정보 조회
        strategy_response = supabase.table('strategies') \
            .select('*') \
            .eq('id', request.strategy_id) \
            .single() \
            .execute()

        if not strategy_response.data:
            raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_id} not found")
        
        strategy = strategy_response.data
        strategy_id = strategy.get('id')
        strategy_name = strategy.get('name', 'Unknown')
        strategy_config = strategy.get('config') or strategy
        
        stock_codes = request.stock_codes
        if not stock_codes:
            return []
            
        # 2. 검증 엔진 초기화
        engine = BacktestEngine()
        sem = asyncio.Semaphore(20) # 동시성 제어

        # 3. 개별 종목 처리 함수 (Internal Helper)
        async def process_single_stock(stock_code: str) -> Optional[StrategyVerificationResult]:
            async with sem:
                try:
                    # 1. 과거 데이터 조회
                    def fetch_data():
                        p_resp = supabase.table('kw_price_daily').select('trade_date,open,high,low,close,volume').eq('stock_code', stock_code).order('trade_date', desc=False).limit(200).execute()
                        c_resp = supabase.table('kw_price_current').select('*').eq('stock_code', stock_code).limit(1).execute()
                        return p_resp, c_resp
                        
                    price_response, curr_resp = await asyncio.to_thread(fetch_data)

                    if not price_response.data or len(price_response.data) < 20:
                        return None

                    # DataFrame 변환
                    df = pd.DataFrame(price_response.data)
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                    # 현재가 병합
                    current_price = 0.0
                    stock_name = stock_code
                    
                    if curr_resp.data and len(curr_resp.data) > 0:
                        row = curr_resp.data[0]
                        current_price = float(row.get('current_price') or 0)
                        stock_name = row.get('stock_name', stock_code)
                        
                        if current_price > 0:
                            try:
                                now = datetime.now()
                                last_date = df.index[-1]
                                if last_date.date() < now.date():
                                    new_row = pd.DataFrame([{
                                        'open': current_price, 'high': current_price, 'low': current_price, 
                                        'close': current_price, 'volume': 0
                                    }], index=[pd.Timestamp(now)])
                                    df = pd.concat([df, new_row])
                                elif last_date.date() == now.date():
                                    df.iloc[-1, df.columns.get_loc('close')] = current_price
                            except Exception:
                                pass
                    
                    # Fallback Price
                    if current_price <= 0:
                        if not df.empty:
                            current_price = df.iloc[-1]['close']
                        else:
                            return None
                            
                    # 엔진 평가
                    eval_result = await engine.evaluate_snapshot(stock_code, df, strategy_config)
                    
                    # 결과 포맷팅
                    score = eval_result.get('score', 0)
                    if not isinstance(score, (int, float)) or isinstance(score, float) and (math.isnan(score) or math.isinf(score)):
                        score = 0.0
                        
                    signal = eval_result.get('signal', 'hold').upper()
                    if signal == 'CONFLICT': signal = 'HOLD'
                    
                    safe_stock_name = stock_name or stock_code or "Unknown"
                    if not isinstance(current_price, (int, float)) or isinstance(current_price, float) and (math.isnan(current_price) or math.isinf(current_price)):
                        current_price = 0.0
                    
                    return StrategyVerificationResult(
                        strategy_name=strategy_name,
                        stock_code=stock_code,
                        stock_name=safe_stock_name,
                        current_price=float(current_price),
                        signal_type=signal,
                        score=float(score),
                        details={
                            'reasons': eval_result.get('reasons', []),
                            'indicators': _sanitize_for_json(eval_result.get('indicators', {}))
                        }
                    )
                except Exception as e:
                    print(f"[Batch] Error processing {stock_code}: {e}")
                    return None

        # 4. 병렬 실행
        tasks = [process_single_stock(code) for code in stock_codes]
        results_raw = await asyncio.gather(*tasks)
        results = [r for r in results_raw if r is not None]
        
        return results

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Batch verification failed: {str(e)}")


@router.post("/check-signal", response_model=StrategySignalResponse)
async def check_signal_endpoint(request: StrategySignalRequest):
    """
    단일 종목 전략 신호 확인 (n8n 호환용)
    """
    return await check_strategy_signal(request)


@router.post("/check-position-exit", response_model=PositionExitResponse)
async def check_position_exit(request: PositionExitRequest):
    """
    포지션 청산 확인 (손절/익절/trailing stop)

    Args:
        request: 포지션 정보

    Returns:
        PositionExitResponse: 청산 여부 및 수량
    """
    try:
        supabase = get_supabase_client()

        # 전략 정보 조회
        strategy_response = supabase.table('strategies') \
            .select('*') \
            .eq('id', request.strategy_id) \
            .single() \
            .execute()

        if not strategy_response.data:
            raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_id} not found")

        strategy = strategy_response.data

        # 현재가 조회 (키움 REST API 필수 - 실시간 데이터만 사용)
        kiwoom_client = get_kiwoom_client()
        price_data = kiwoom_client.get_current_price(request.stock_code)

        if not price_data or price_data['current_price'] <= 0:
            raise HTTPException(
                status_code=503,
                detail=f"실시간 시세 조회 실패 - 키움 API 연결 필요 (종목: {request.stock_code})"
            )

        current_price = float(price_data['current_price'])
        print(f"[PositionExit] 키움 API 현재가: {request.stock_code} = {current_price:,}원")

        # 수익률 계산
        profit_loss = (current_price - request.entry_price) * request.current_quantity
        profit_loss_rate = (current_price - request.entry_price) / request.entry_price

        # 청산 조건 체크
        exit_conditions = strategy.get('conditions', {}).get('exit', {})

        # 손절 체크
        stop_loss = exit_conditions.get('stop_loss', {})
        if stop_loss and stop_loss.get('enabled'):
            stop_loss_rate = stop_loss.get('rate', -0.05)  # 기본 -5%
            if profit_loss_rate <= stop_loss_rate:
                return PositionExitResponse(
                    position_id=request.position_id,
                    should_exit=True,
                    exit_type="stop_loss",
                    exit_percentage=1.0,  # 전량 청산
                    exit_quantity=request.current_quantity,
                    current_price=current_price,
                    entry_price=request.entry_price,
                    profit_loss=profit_loss,
                    profit_loss_rate=profit_loss_rate,
                    reason=f"Stop loss triggered: {profit_loss_rate:.2%} <= {stop_loss_rate:.2%}"
                )

        # 익절 체크 (단계별)
        profit_target = exit_conditions.get('profit_target', {})
        if profit_target and profit_target.get('enabled'):
            targets = profit_target.get('targets', [])
            for target in targets:
                target_rate = target.get('rate', 0.1)  # 목표 수익률
                sell_percentage = target.get('percentage', 0.3)  # 청산 비율

                if profit_loss_rate >= target_rate:
                    exit_quantity = int(request.current_quantity * sell_percentage)
                    return PositionExitResponse(
                        position_id=request.position_id,
                        should_exit=True,
                        exit_type="profit_target",
                        exit_percentage=sell_percentage,
                        exit_quantity=exit_quantity,
                        current_price=current_price,
                        entry_price=request.entry_price,
                        profit_loss=profit_loss,
                        profit_loss_rate=profit_loss_rate,
                        reason=f"Profit target reached: {profit_loss_rate:.2%} >= {target_rate:.2%}"
                    )

        # 청산 신호 없음
        return PositionExitResponse(
            position_id=request.position_id,
            should_exit=False,
            exit_type="none",
            exit_percentage=0.0,
            exit_quantity=0,
            current_price=current_price,
            entry_price=request.entry_price,
            profit_loss=profit_loss,
            profit_loss_rate=profit_loss_rate,
            reason="No exit conditions met"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check position exit: {str(e)}")


@router.get("/evaluate/{strategy_id}")
async def evaluate_strategy(strategy_id: str):
    """
    전략 성과 평가

    Args:
        strategy_id: 전략 ID

    Returns:
        전략 성과 지표 (승률, 평균 수익률, 샤프 비율 등)
    """
    try:
        supabase = get_supabase_client()

        # 전략의 모든 주문 조회
        orders_response = supabase.table('orders') \
            .select('*') \
            .eq('strategy_id', strategy_id) \
            .order('created_at', desc=False) \
            .execute()

        if not orders_response.data:
            return {
                'strategy_id': strategy_id,
                'total_trades': 0,
                'message': 'No trading history found'
            }

        orders = orders_response.data

        # 성과 계산 (간단 버전)
        total_trades = len(orders)
        buy_orders = [o for o in orders if o.get('order_type') == 'BUY']
        sell_orders = [o for o in orders if o.get('order_type') == 'SELL']

        return {
            'strategy_id': strategy_id,
            'total_trades': total_trades,
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'latest_trade': orders[-1].get('created_at') if orders else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate strategy: {str(e)}")


# =============================================================================
# 헬퍼 함수
# =============================================================================

def _calculate_required_bars(conditions: Dict[str, Any]) -> int:
    """전략 조건에서 필요한 과거 데이터 개수 계산 (구 스키마용)"""
    max_period = 20  # 기본값

    entry_conditions = conditions.get('entry', {})
    for indicator_name, condition in entry_conditions.items():
        period = condition.get('period', 14)
        if indicator_name == 'macd':
            period = max(condition.get('fast', 12), condition.get('slow', 26))
        max_period = max(max_period, period)

    # 충분한 여유를 위해 5배
    return max_period * 5


def _calculate_required_bars_from_conditions(entry_conditions: Dict[str, Any], exit_conditions: Dict[str, Any]) -> int:
    """전략 조건에서 필요한 과거 데이터 개수 계산 (신규 스키마용)"""
    max_period = 20  # 기본값

    # 진입 조건
    for indicator_name, condition in entry_conditions.items():
        period = condition.get('period', 14)
        if indicator_name == 'macd':
            period = max(condition.get('fast', 12), condition.get('slow', 26))
        max_period = max(max_period, period)

    # 청산 조건
    for indicator_name, condition in exit_conditions.items():
        period = condition.get('period', 14)
        max_period = max(max_period, period)

    # 충분한 여유를 위해 5배
    return max_period * 5


def _calculate_indicator(df: pd.DataFrame, indicator_name: str, params: Dict[str, Any]) -> Dict[str, float]:
    """지표 계산"""
    try:
        calculator = get_indicator_calculator()
        options = ExecOptions(
            period=params.get('period', 14),
            realtime=True  # 현재 봉 제외
        )

        config = {
            'name': indicator_name,
            'calculation_type': 'builtin',
            'params': params
        }

        result = calculator.calculate(df, config, options)

        # 최신 값만 추출
        latest_values = {}
        for col_name, series in result.columns.items():
            if len(series) > 0:
                latest_values[col_name] = float(series.iloc[-1])

        return latest_values

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate {indicator_name}: {str(e)}")


def _evaluate_condition(
    indicator_name: str,
    indicator_values: Optional[Dict[str, float]],
    condition: Dict[str, Any],
    current_price: float,
    df: pd.DataFrame
) -> bool:
    """조건 평가"""
    if not indicator_values:
        return False

    operator = condition.get('operator', '>')
    threshold = condition.get('value', 0)

    # 지표별 평가
    if indicator_name == 'rsi':
        value = indicator_values.get('rsi', 50)
        if operator == '<':
            return value < threshold
        elif operator == '>':
            return value > threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '>=':
            return value >= threshold

    elif indicator_name == 'macd':
        macd_line = indicator_values.get('macd', 0)
        signal_line = indicator_values.get('signal', 0)
        if operator == 'cross_above':
            return macd_line > signal_line
        elif operator == 'cross_below':
            return macd_line < signal_line

    elif indicator_name == 'bb':
        bb_lower = indicator_values.get('bb_lower', 0)
        bb_upper = indicator_values.get('bb_upper', 0)
        if operator == 'below_lower':
            return current_price < bb_lower
        elif operator == 'above_upper':
            return current_price > bb_upper

    return False
