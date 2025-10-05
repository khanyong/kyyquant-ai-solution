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

# 지표 계산기 임포트 (실제 사용 파일)
from indicators.calculator import IndicatorCalculator, ExecOptions

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


@router.post("/check-signal", response_model=StrategySignalResponse)
async def check_strategy_signal(request: StrategySignalRequest):
    """
    전략 신호 확인 (n8n 워크플로우에서 호출)

    실시간 데이터를 기반으로 전략의 진입/청산 조건을 평가하고 매매 신호 생성

    Args:
        request: 전략 ID, 종목 코드

    Returns:
        StrategySignalResponse: 매매 신호 (BUY/SELL/HOLD)
    """
    try:
        supabase = get_supabase_client()

        # 1. 전략 정보 조회
        strategy_response = supabase.table('strategies') \
            .select('*') \
            .eq('id', request.strategy_id) \
            .single() \
            .execute()

        if not strategy_response.data:
            raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_id} not found")

        strategy = strategy_response.data

        # 스키마 호환성: 구 스키마(conditions) + 신규 스키마(entry_conditions, exit_conditions)
        conditions = strategy.get('conditions')
        if conditions:
            # 구 스키마
            entry_conditions = conditions.get('entry', {})
            exit_conditions = conditions.get('exit', {})
        else:
            # 신규 스키마
            entry_data = strategy.get('entry_conditions', {})
            exit_data = strategy.get('exit_conditions', {})
            entry_conditions = {}
            exit_conditions = {}

            # buyConditions를 entry_conditions로 변환
            buy_conditions = entry_data.get('buy', [])
            for condition in buy_conditions:
                indicator_name = condition.get('left')  # 'rsi', 'macd' 등
                if indicator_name:
                    entry_conditions[indicator_name] = {
                        'operator': condition.get('operator'),
                        'value': condition.get('right'),
                        'period': 14  # 기본값, config에서 가져올 수도 있음
                    }

        # 2. 과거 데이터 조회 (지표 계산용)
        required_bars = _calculate_required_bars_from_conditions(entry_conditions, exit_conditions)

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

        # 3. 지표 계산
        indicators_result = {}

        # 진입 조건에서 사용하는 지표 계산
        for indicator_name, condition in entry_conditions.items():
            if indicator_name in ['rsi', 'macd', 'bb', 'sma', 'ema', 'stochastic']:
                indicator_values = _calculate_indicator(df, indicator_name, condition)
                indicators_result[indicator_name] = indicator_values

        # 4. 현재가 확인 (키움 REST API 필수 - 실시간 데이터만 사용)
        current_price = request.current_price
        if current_price is None:
            kiwoom_client = get_kiwoom_client()
            price_data = kiwoom_client.get_current_price(request.stock_code)

            if not price_data or price_data['current_price'] <= 0:
                raise HTTPException(
                    status_code=503,
                    detail=f"실시간 시세 조회 실패 - 키움 API 연결 필요 (종목: {request.stock_code})"
                )

            current_price = float(price_data['current_price'])
            print(f"[Strategy] 키움 API 현재가: {request.stock_code} = {current_price:,}원")

        # 5. 진입 조건 평가
        entry_met = {}
        for indicator_name, condition in entry_conditions.items():
            met = _evaluate_condition(
                indicator_name,
                indicators_result.get(indicator_name),
                condition,
                current_price,
                df
            )
            entry_met[indicator_name] = met

        # 6. 청산 조건 평가
        exit_met = {}
        for indicator_name, condition in exit_conditions.items():
            met = _evaluate_condition(
                indicator_name,
                indicators_result.get(indicator_name),
                condition,
                current_price,
                df
            )
            exit_met[indicator_name] = met

        # 7. 신호 결정
        signal_type = "HOLD"
        signal_strength = 0.0

        # 모든 진입 조건 충족 시 BUY
        if entry_conditions and all(entry_met.values()):
            signal_type = "BUY"
            signal_strength = sum(entry_met.values()) / len(entry_met) if entry_met else 0.0

        # 청산 조건 충족 시 SELL
        if exit_conditions and any(exit_met.values()):
            signal_type = "SELL"
            signal_strength = sum(exit_met.values()) / len(exit_met) if exit_met else 0.0

        return StrategySignalResponse(
            strategy_id=request.strategy_id,
            strategy_name=strategy.get('name', 'Unknown'),
            stock_code=request.stock_code,
            stock_name=None,  # TODO: 종목명 조회
            signal_type=signal_type,
            signal_strength=signal_strength,
            current_price=current_price,
            indicators=indicators_result,
            entry_conditions_met=entry_met,
            exit_conditions_met=exit_met,
            timestamp=datetime.now(),
            debug_info={
                'data_points': len(df),
                'latest_date': df.index[-1].isoformat() if len(df) > 0 else None
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check signal: {str(e)}")


@router.post("/batch-check", response_model=List[StrategySignalResponse])
async def batch_check_signals(request: BatchSignalRequest):
    """
    배치 신호 확인 (여러 종목 동시 처리)

    Args:
        request: 전략 ID, 종목 코드 리스트

    Returns:
        List[StrategySignalResponse]: 종목별 신호 리스트
    """
    results = []

    for stock_code in request.stock_codes:
        try:
            signal_request = StrategySignalRequest(
                strategy_id=request.strategy_id,
                stock_code=stock_code
            )
            signal = await check_strategy_signal(signal_request)
            results.append(signal)
        except Exception as e:
            # 개별 종목 실패는 무시하고 계속
            continue

    return results


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
