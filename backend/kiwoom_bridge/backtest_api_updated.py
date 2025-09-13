"""
백테스트 API 엔드포인트 (수정 버전)
strategy_engine 통합
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import os
import asyncio
import aiohttp
from supabase import create_client, Client

# 새로운 전략 엔진 import
from strategy_engine import strategy_engine

try:
    from backtest_engine_advanced import AdvancedBacktestEngine, TechnicalIndicators, SignalGenerator
    USE_ADVANCED_ENGINE = True
except ImportError:
    USE_ADVANCED_ENGINE = False
    print("[INFO] 고급 백테스트 엔진을 사용할 수 없습니다. 기본 엔진 사용.")

try:
    from strategy_analyzer import StrategyAnalyzer
    USE_ANALYZER = True
except ImportError:
    USE_ANALYZER = False
    print("[INFO] 전략 분석기를 사용할 수 없습니다.")

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

# Supabase 클라이언트 초기화
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("[경고] Supabase 환경변수가 설정되지 않았습니다. Mock 데이터를 사용합니다.")

class BacktestRequest(BaseModel):
    """백테스트 요청 모델"""
    strategy_id: str
    stock_codes: List[str]  # 여러 종목 지원
    start_date: str
    end_date: str
    initial_capital: float = 10000000  # 1천만원
    commission: float = 0.00015
    slippage: float = 0.001
    data_interval: str = "1d"
    filtering_mode: str = "pre-filter"
    use_cached_data: bool = True
    filter_id: str = None
    parameters: Dict[str, Any] = {}

class BacktestResult(BaseModel):
    """백테스트 결과 모델"""
    total_return: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    buy_count: int = 0  # 매수 횟수
    sell_count: int = 0  # 매도 횟수
    trades: List[Dict]

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """백테스트 실행"""
    print(f"[백테스트 시작] 전략: {request.strategy_id}")

    try:
        # 전략 데이터 가져오기
        strategy_data = await get_strategy_data(request.strategy_id)

        if not strategy_data:
            # Mock 전략 데이터 사용
            strategy_data = {
                'id': request.strategy_id,
                'name': 'Test Strategy',
                'custom_parameters': request.parameters
            }

        # 주가 데이터 로드
        stock_data = await load_stock_data(
            request.stock_codes,
            request.start_date,
            request.end_date
        )

        if not stock_data:
            print("[INFO] 실제 데이터 없음. Mock 데이터 생성")
            stock_data = generate_mock_data(
                request.stock_codes,
                request.start_date,
                request.end_date
            )

        # 백테스트 실행
        result = await execute_backtest(
            strategy_data,
            stock_data,
            request
        )

        # 결과 저장
        if supabase:
            try:
                await save_backtest_result(result, request, strategy_data)
            except Exception as e:
                print(f"[경고] 결과 저장 실패: {e}")

        return {
            "status": "completed",
            "results": result
        }

    except Exception as e:
        print(f"[ERROR] 백테스트 실행 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_strategy_data(strategy_id: str) -> Optional[Dict]:
    """전략 데이터 가져오기"""
    if not supabase:
        return None

    try:
        response = supabase.table('strategies').select("*").eq('id', strategy_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"[경고] 전략 데이터 로드 실패: {e}")

    return None

async def load_stock_data(stock_codes: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """주가 데이터 로드"""
    stock_data = {}

    # 로컬 캐시 확인
    cache_dir = "D:/Dev/auto_stock/data/cache"
    if os.path.exists(cache_dir):
        for code in stock_codes:
            cache_file = os.path.join(cache_dir, f"{code}_{start_date}_{end_date}.csv")
            if os.path.exists(cache_file):
                try:
                    df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                    stock_data[code] = df
                    print(f"[INFO] 캐시에서 로드: {code}")
                except Exception as e:
                    print(f"[경고] 캐시 로드 실패 ({code}): {e}")

    # Supabase에서 로드
    if supabase:
        for code in stock_codes:
            if code not in stock_data:
                try:
                    response = supabase.table('kw_price_daily').select("*").eq('stock_code', code).gte('trade_date', start_date).lte('trade_date', end_date).execute()
                    if response.data:
                        df = pd.DataFrame(response.data)
                        df['date'] = pd.to_datetime(df['trade_date'])
                        df.set_index('date', inplace=True)

                        # 필수 컬럼 확인 및 매핑
                        column_mapping = {
                            'stck_oprc': 'open',
                            'stck_hgpr': 'high',
                            'stck_lwpr': 'low',
                            'stck_clpr': 'close',
                            'acml_vol': 'volume'
                        }

                        for old_col, new_col in column_mapping.items():
                            if old_col in df.columns:
                                df[new_col] = df[old_col]

                        stock_data[code] = df
                        print(f"[INFO] Supabase에서 로드: {code}")
                except Exception as e:
                    print(f"[경고] Supabase 로드 실패 ({code}): {e}")

    return stock_data

def generate_mock_data(stock_codes: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """Mock 데이터 생성"""
    stock_data = {}
    dates = pd.date_range(start=start_date, end=end_date, freq='B')

    for code in stock_codes:
        np.random.seed(hash(code) % 2**32)
        initial_price = np.random.uniform(10000, 100000)
        daily_returns = np.random.normal(0.001, 0.02, len(dates))
        prices = initial_price * np.exp(np.cumsum(daily_returns))

        df = pd.DataFrame({
            'open': prices * np.random.uniform(0.99, 1.01, len(dates)),
            'high': prices * np.random.uniform(1.01, 1.03, len(dates)),
            'low': prices * np.random.uniform(0.97, 0.99, len(dates)),
            'close': prices,
            'volume': np.random.uniform(100000, 1000000, len(dates))
        }, index=dates)

        stock_data[code] = df
        print(f"[INFO] Mock 데이터 생성: {code}")

    return stock_data

async def execute_backtest(strategy_data: Dict, stock_data: Dict[str, pd.DataFrame], request: BacktestRequest) -> Dict:
    """백테스트 실행 (strategy_engine 사용)"""

    # 전략 파라미터 준비
    strategy_params = strategy_data.get('custom_parameters', {})

    # 초기 자본
    capital = request.initial_capital
    initial_capital = request.initial_capital

    # 포트폴리오
    portfolio = {
        'cash': capital,
        'positions': {},
        'trades': []
    }

    # 모든 날짜 수집
    all_dates = set()
    for df in stock_data.values():
        all_dates.update(df.index)
    all_dates = sorted(list(all_dates))

    # 각 종목에 대해 지표 계산
    prepared_stock_data = {}
    for code, df in stock_data.items():
        # strategy_engine을 사용하여 지표 계산
        prepared_df = strategy_engine.prepare_data(df, strategy_params)
        prepared_stock_data[code] = prepared_df
        print(f"[INFO] {code} 지표 계산 완료")

    # 거래 기록
    trades = []
    equity_curve = []

    # 백테스트 실행
    for date in all_dates:
        daily_value = portfolio['cash']

        for code, df in prepared_stock_data.items():
            if date in df.index:
                price = df.loc[date, 'close']

                # strategy_engine을 사용하여 신호 생성
                signal = strategy_engine.generate_signal(df, date, strategy_params)

                # 매수 신호
                if signal == 'buy' and code not in portfolio['positions']:
                    # 자본의 일부만 사용 (예: 종목당 20%)
                    position_size = portfolio['cash'] * 0.2
                    if position_size > price * 10:  # 최소 10주
                        shares = int(position_size / price)
                        cost = shares * price * (1 + request.commission + request.slippage)

                        if cost <= portfolio['cash']:
                            portfolio['cash'] -= cost
                            portfolio['positions'][code] = {
                                'shares': shares,
                                'avg_price': price * (1 + request.slippage),
                                'entry_date': date
                            }

                            trades.append({
                                'date': date.strftime('%Y-%m-%d'),
                                'code': code,
                                'type': 'buy',
                                'shares': shares,
                                'price': price,
                                'value': cost
                            })

                # 매도 신호
                elif signal == 'sell' and code in portfolio['positions']:
                    position = portfolio['positions'][code]
                    shares = position['shares']
                    proceeds = shares * price * (1 - request.commission - request.slippage)

                    portfolio['cash'] += proceeds
                    profit = proceeds - (shares * position['avg_price'])
                    profit_pct = (profit / (shares * position['avg_price'])) * 100

                    trades.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'code': code,
                        'type': 'sell',
                        'shares': shares,
                        'price': price,
                        'value': proceeds,
                        'profit': profit,
                        'profit_pct': profit_pct
                    })

                    del portfolio['positions'][code]

                # 현재 포지션 가치 계산
                if code in portfolio['positions']:
                    position = portfolio['positions'][code]
                    daily_value += position['shares'] * price

        # 일별 자산 기록
        equity_curve.append({
            'date': date.strftime('%Y-%m-%d'),
            'value': daily_value
        })

    # 최종 포지션 정리 (모두 매도)
    final_date = all_dates[-1] if all_dates else datetime.now()
    for code, position in portfolio['positions'].items():
        if code in prepared_stock_data and final_date in prepared_stock_data[code].index:
            price = prepared_stock_data[code].loc[final_date, 'close']
            shares = position['shares']
            proceeds = shares * price * (1 - request.commission - request.slippage)

            portfolio['cash'] += proceeds
            profit = proceeds - (shares * position['avg_price'])
            profit_pct = (profit / (shares * position['avg_price'])) * 100

            trades.append({
                'date': final_date.strftime('%Y-%m-%d'),
                'code': code,
                'type': 'sell',
                'shares': shares,
                'price': price,
                'value': proceeds,
                'profit': profit,
                'profit_pct': profit_pct,
                'reason': 'final_cleanup'
            })

    # 성과 계산
    final_capital = portfolio['cash']
    total_return = ((final_capital - initial_capital) / initial_capital) * 100

    # 거래 통계
    sell_trades = [t for t in trades if t['type'] == 'sell' and 'profit' in t]
    winning_trades = len([t for t in sell_trades if t.get('profit', 0) > 0])
    losing_trades = len([t for t in sell_trades if t.get('profit', 0) <= 0])
    win_rate = (winning_trades / max(1, len(sell_trades))) * 100

    # 최대 낙폭 계산
    max_drawdown = calculate_max_drawdown(equity_curve)

    # 샤프 비율 계산
    sharpe_ratio = calculate_sharpe_ratio(equity_curve)

    return {
        'total_return': total_return,
        'win_rate': win_rate,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'total_trades': len(trades),
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'buy_count': len([t for t in trades if t['type'] == 'buy']),
        'sell_count': len([t for t in trades if t['type'] == 'sell']),
        'final_capital': final_capital,
        'trades': trades[-20:],  # 최근 20개 거래
        'equity_curve': equity_curve[-100:],  # 최근 100일
        'trade_history': trades
    }

def calculate_max_drawdown(equity_curve: List[Dict]) -> float:
    """최대 낙폭 계산"""
    if not equity_curve:
        return 0

    values = [e['value'] for e in equity_curve]
    peak = values[0]
    max_dd = 0

    for value in values:
        if value > peak:
            peak = value
        dd = ((peak - value) / peak) * 100
        max_dd = max(max_dd, dd)

    return max_dd

def calculate_sharpe_ratio(equity_curve: List[Dict], risk_free_rate: float = 0.02) -> float:
    """샤프 비율 계산"""
    if len(equity_curve) < 2:
        return 0

    values = [e['value'] for e in equity_curve]
    returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]

    if not returns:
        return 0

    avg_return = np.mean(returns)
    std_return = np.std(returns)

    if std_return == 0:
        return 0

    # 연율화
    annual_return = avg_return * 252
    annual_std = std_return * np.sqrt(252)

    return (annual_return - risk_free_rate) / annual_std

async def save_backtest_result(result: Dict, request: BacktestRequest, strategy_data: Dict):
    """백테스트 결과 저장"""
    if not supabase:
        return

    try:
        # 결과 저장 로직
        pass
    except Exception as e:
        print(f"[경고] 결과 저장 실패: {e}")