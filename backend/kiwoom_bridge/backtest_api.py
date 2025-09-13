"""
백테스트 API 엔드포인트
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

# Import StrategyEngine for indicator calculations
try:
    from strategy_engine import StrategyEngine
    USE_STRATEGY_ENGINE = True
    print("[INFO] strategy_engine.py를 사용합니다.")
except ImportError:
    USE_STRATEGY_ENGINE = False
    print("[WARNING] strategy_engine.py를 찾을 수 없습니다. 기본 Strategy 클래스 사용.")

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

class Strategy:
    """전략 실행 클래스"""

    @staticmethod
    async def calculate_indicators(data: pd.DataFrame, indicators: List[Dict]) -> pd.DataFrame:
        """여러 기술적 지표 계산"""
        # Use StrategyEngine if available
        if USE_STRATEGY_ENGINE:
            try:
                # Create StrategyEngine instance
                engine = StrategyEngine()

                # Calculate all indicators using strategy_engine
                data = engine.calculate_all_indicators(data)

                # Ensure PRICE column exists for compatibility
                if 'PRICE' not in data.columns:
                    data['PRICE'] = data['close']

                print(f"[INFO] StrategyEngine에서 지표 계산 완료. 컬럼: {list(data.columns)[:20]}...")
                return data
            except Exception as e:
                print(f"[WARNING] StrategyEngine 사용 실패: {e}. 기본 방법으로 전환.")

        # Original indicator calculation logic as fallback
        for indicator in indicators:
            ind_type = indicator.get('type', '')
            params = indicator.get('params', {})
            
            if ind_type == 'MA':
                period = params.get('period', 20)
                data[f'MA_{period}'] = data['close'].rolling(window=period).mean()
            
            elif ind_type == 'EMA':
                period = params.get('period', 20)
                data[f'EMA_{period}'] = data['close'].ewm(span=period, adjust=False).mean()
            
            elif ind_type == 'RSI':
                period = params.get('period', 14)
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                data[f'RSI_{period}'] = 100 - (100 / (1 + rs))
            
            elif ind_type == 'MACD':
                fast = params.get('fast', 12)
                slow = params.get('slow', 26)
                signal = params.get('signal', 9)
                data['MACD'] = data['close'].ewm(span=fast, adjust=False).mean() - data['close'].ewm(span=slow, adjust=False).mean()
                data['MACD_signal'] = data['MACD'].ewm(span=signal, adjust=False).mean()
                data['MACD_hist'] = data['MACD'] - data['MACD_signal']
            
            elif ind_type == 'BB':
                period = params.get('period', 20)
                std = params.get('std', 2)
                ma = data['close'].rolling(window=period).mean()
                std_dev = data['close'].rolling(window=period).std()
                data['BB_upper'] = ma + (std_dev * std)
                data['BB_lower'] = ma - (std_dev * std)
                data['BB_middle'] = ma
            
            elif ind_type == 'Stochastic':
                k_period = params.get('k_period', 14)
                d_period = params.get('d_period', 3)
                low_min = data['low'].rolling(window=k_period).min()
                high_max = data['high'].rolling(window=k_period).max()
                data['Stoch_K'] = 100 * ((data['close'] - low_min) / (high_max - low_min))
                data['Stoch_D'] = data['Stoch_K'].rolling(window=d_period).mean()
            
            elif ind_type == 'ATR':
                period = params.get('period', 14)
                high_low = data['high'] - data['low']
                high_close = np.abs(data['high'] - data['close'].shift())
                low_close = np.abs(data['low'] - data['close'].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = np.max(ranges, axis=1)
                data[f'ATR_{period}'] = true_range.rolling(window=period).mean()
            
            elif ind_type == 'OBV':
                data['OBV'] = (np.sign(data['close'].diff()) * data['volume']).fillna(0).cumsum()
            
            elif ind_type == 'Volume':
                period = params.get('period', 20)
                data[f'Volume_MA_{period}'] = data['volume'].rolling(window=period).mean()
        
        return data
    
    @staticmethod
    async def evaluate_conditions(data: pd.DataFrame, conditions: List[Dict], condition_type: str) -> pd.DataFrame:
        """매수/매도 조건 평가"""
        data[f'{condition_type}_signal'] = 0
        
        if not conditions:
            return data
        
        # 각 조건 평가
        condition_results = []
        for condition in conditions:
            indicator = condition.get('indicator', '')
            operator = condition.get('operator', '')
            value = condition.get('value', 0)
            combine = condition.get('combineWith', 'AND')
            
            # 지표값 가져오기
            if indicator in data.columns:
                ind_values = data[indicator]
            else:
                continue
            
            # 조건 평가
            if operator == '>':
                result = ind_values > value
            elif operator == '<':
                result = ind_values < value
            elif operator == '>=':
                result = ind_values >= value
            elif operator == '<=':
                result = ind_values <= value
            elif operator == '==':
                result = ind_values == value
            elif operator == 'cross_above':
                result = (ind_values > value) & (ind_values.shift(1) <= value)
            elif operator == 'cross_below':
                result = (ind_values < value) & (ind_values.shift(1) >= value)
            else:
                continue
            
            condition_results.append((result, combine))
        
        # 조건 결합
        if condition_results:
            final_result = condition_results[0][0]
            for i in range(1, len(condition_results)):
                if condition_results[i][1] == 'AND':
                    final_result = final_result & condition_results[i][0]
                else:  # OR
                    final_result = final_result | condition_results[i][0]
            
            # 신호 생성 (진입 시점만)
            data.loc[final_result & ~final_result.shift(1).fillna(False), f'{condition_type}_signal'] = 1 if condition_type == 'buy' else -1
        
        return data
    
    @staticmethod
    async def execute_strategy(data: pd.DataFrame, strategy_config: Dict[str, Any]) -> pd.DataFrame:
        """Supabase에서 로드한 전략 설정을 사용하여 전략 실행
        
        모든 전략은 Supabase에 저장된 설정을 기반으로 동적으로 실행됩니다.
        하드코딩된 전략 구현은 사용하지 않습니다.
        """
        # 지표 계산 (설정에서 가져온 indicators 사용)
        indicators = strategy_config.get('indicators', [])
        if indicators:
            data = await Strategy.calculate_indicators(data, indicators)
        
        # 매수 조건 평가 (설정에서 가져온 buyConditions 사용)
        buy_conditions = strategy_config.get('buyConditions', [])
        if buy_conditions:
            data = await Strategy.evaluate_conditions(data, buy_conditions, 'buy')
        
        # 매도 조건 평가 (설정에서 가져온 sellConditions 사용)
        sell_conditions = strategy_config.get('sellConditions', [])
        if sell_conditions:
            data = await Strategy.evaluate_conditions(data, sell_conditions, 'sell')
        
        # 최종 신호 결합
        data['signal'] = 0
        if 'buy_signal' in data.columns:
            data.loc[data['buy_signal'] == 1, 'signal'] = 1
        if 'sell_signal' in data.columns:
            data.loc[data['sell_signal'] == -1, 'signal'] = -1
        
        return data

class BacktestEngine:
    """백테스트 엔진"""
    
    @staticmethod
    async def run_backtest(data: pd.DataFrame, initial_capital: float, commission: float = 0.00015, slippage: float = 0.001) -> BacktestResult:
        """백테스트 실행"""
        capital = initial_capital
        position = 0
        trades = []
        entry_price = 0
        entry_cost = 0  # 실제 매수 비용 저장
        
        for i in range(1, len(data)):
            signal = data.iloc[i]['signal']
            price = data.iloc[i]['close']
            date = data.iloc[i]['date']
            
            # 매수 신호
            if signal == 1 and position == 0:
                # 슬리피지와 수수료 적용
                actual_price = price * (1 + slippage)
                available_capital = capital / (1 + commission)
                shares = int(available_capital / actual_price)
                
                if shares > 0:
                    total_cost = shares * actual_price * (1 + commission)
                    position = shares
                    entry_price = actual_price
                    entry_cost = total_cost  # 실제 지불 비용 저장
                    capital -= total_cost
                    
                    trades.append({
                        'date': date,
                        'type': 'buy',
                        'price': actual_price,
                        'shares': shares,
                        'cost': total_cost
                    })
            
            # 매도 신호
            elif signal == -1 and position > 0:
                # 슬리피지와 수수료 적용
                actual_price = price * (1 - slippage)
                proceeds = position * actual_price * (1 - commission)
                
                # 수익 계산 (실제 비용 대비)
                profit = proceeds - entry_cost
                profit_pct = (profit / entry_cost) * 100 if entry_cost > 0 else 0
                
                trades.append({
                    'date': date,
                    'type': 'sell',
                    'price': actual_price,
                    'shares': position,
                    'proceeds': proceeds,
                    'profit': profit,
                    'profit_pct': profit_pct
                })
                
                capital += proceeds
                position = 0
                entry_cost = 0
        
        # 마지막 포지션 정리
        if position > 0:
            final_price = data.iloc[-1]['close'] * (1 - slippage)
            proceeds = position * final_price * (1 - commission)
            capital += proceeds
            
            # 수익 계산
            profit = proceeds - entry_cost
            profit_pct = (profit / entry_cost) * 100 if entry_cost > 0 else 0
            
            trades.append({
                'date': data.iloc[-1]['date'],
                'type': 'sell',
                'price': final_price,
                'shares': position,
                'proceeds': proceeds,
                'profit': profit,
                'profit_pct': profit_pct,
                'forced': True  # 강제 청산 표시
            })
        
        # 성과 계산
        total_return = ((capital - initial_capital) / initial_capital) * 100
        
        # 매수/매도 횟수 계산
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        
        # 매도 거래만으로 승률 계산
        if sell_trades:
            winning_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
            losing_trades = [t for t in sell_trades if t.get('profit', 0) <= 0]
            win_rate = (len(winning_trades) / len(sell_trades)) * 100
        else:
            winning_trades = []
            losing_trades = []
            win_rate = 0
        
        # 최대 낙폭 계산
        cumulative_returns = []
        current_capital = initial_capital
        for trade in trades:
            if trade['type'] == 'sell':
                current_capital += trade.get('profit', 0)
            cumulative_returns.append(current_capital)
        
        if cumulative_returns:
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = (peak - cumulative_returns) / peak * 100
            max_drawdown = np.max(drawdown)
        else:
            max_drawdown = 0
        
        # Sharpe Ratio (간단 버전)
        if trades:
            returns = [t.get('profit_pct', 0) for t in trades if 'profit_pct' in t]
            if returns:
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        return BacktestResult(
            total_return=total_return,
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_trades=len(sell_trades),  # 완료된 거래(매도) 수만 카운트
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            buy_count=len(buy_trades),  # 매수 횟수
            sell_count=len(sell_trades),  # 매도 횟수
            trades=trades
        )

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """백테스트 실행 - 여러 종목 지원"""
    try:
        # 1. Supabase에서 전략 정보 조회
        strategy_config = {}
        if supabase and request.strategy_id:
            try:
                print(f"[전략 로드] strategy_id: {request.strategy_id}")
                response = supabase.table('strategies').select('*').eq('id', request.strategy_id).single().execute()
                if response.data:
                    strategy_config = response.data.get('config', {})
                    print(f"  ✓ 전략 로드 성공: {response.data.get('name', 'Unknown')}")
                    print(f"  - 지표: {len(strategy_config.get('indicators', []))}개")
                    print(f"  - 매수 조건: {len(strategy_config.get('buyConditions', []))}개")
                    print(f"  - 매도 조건: {len(strategy_config.get('sellConditions', []))}개")
            except Exception as e:
                print(f"  ! 전략 조회 실패: {str(e)}")
        
        # 2. request.parameters와 병합 (request.parameters가 우선)
        merged_parameters = {**strategy_config, **request.parameters}
        
        all_results = []
        total_stocks = min(len(request.stock_codes), 10)  # 최대 10개 종목
        
        # 진행 상황을 로그로 출력
        print(f"[백테스트 시작] 총 {total_stocks}개 종목 처리 예정")
        
        # 각 종목에 대해 백테스트 실행
        for idx, stock_code in enumerate(request.stock_codes[:total_stocks], 1):
            print(f"[진행중] {idx}/{total_stocks} - 종목코드: {stock_code} 처리 중...")
            
            # 실제 주가 데이터 조회 (3-tier 전략: Supabase → API → Mock)
            data = None
            
            # 1. Supabase에서 데이터 조회 시도
            if supabase:
                try:
                    print(f"  - Supabase에서 {stock_code} 데이터 조회 중...")
                    response = supabase.table('kw_price_daily').select('*').eq(
                        'stock_code', stock_code
                    ).gte('trade_date', request.start_date).lte('trade_date', request.end_date).order('trade_date').execute()
                    
                    if response.data and len(response.data) > 0:
                        print(f"  ✓ Supabase에서 {len(response.data)}개 데이터 로드")
                        data = pd.DataFrame(response.data)
                        # trade_date를 date로 변환
                        data['date'] = pd.to_datetime(data['trade_date'])
                        
                        # OHLCV 데이터 확인 및 선택
                        required_cols = ['date', 'close']
                        optional_cols = ['open', 'high', 'low', 'volume']
                        
                        if 'close' in data.columns:
                            cols_to_keep = required_cols.copy()
                            for col in optional_cols:
                                if col in data.columns:
                                    cols_to_keep.append(col)
                            
                            data = data[cols_to_keep]
                            
                            # 누락된 OHLC 데이터 보완
                            if 'open' not in data.columns:
                                data['open'] = data['close']
                            if 'high' not in data.columns:
                                data['high'] = data['close'] * 1.01
                            if 'low' not in data.columns:
                                data['low'] = data['close'] * 0.99
                            if 'volume' not in data.columns:
                                data['volume'] = 1000000
                        else:
                            print(f"  ! 데이터에 close 컬럼이 없습니다")
                            data = None
                except Exception as e:
                    print(f"  ! Supabase 조회 실패: {str(e)}")
                    data = None
            
            # 2. 외부 API에서 데이터 조회 (필요시 구현)
            # if data is None:
            #     data = await fetch_from_external_api(stock_code, request.start_date, request.end_date)
            
            # 3. 데이터가 없으면 Mock 데이터 사용 (개발/테스트용)
            if data is None or data.empty:
                print(f"  ! 실제 데이터 없음. Mock 데이터 생성 중...")
                dates = pd.date_range(start=request.start_date, end=request.end_date, freq='D')
                base_price = 50000 + np.random.randint(0, 50000)
                mock_prices = np.random.randn(len(dates)) * (base_price * 0.02) + base_price
                
                # Mock OHLCV 데이터 생성
                high_prices = mock_prices * (1 + np.random.uniform(0, 0.02, len(dates)))
                low_prices = mock_prices * (1 - np.random.uniform(0, 0.02, len(dates)))
                open_prices = np.roll(mock_prices, 1) * (1 + np.random.uniform(-0.01, 0.01, len(dates)))
                open_prices[0] = mock_prices[0]
                
                data = pd.DataFrame({
                    'date': dates,
                    'open': open_prices,
                    'high': high_prices,
                    'low': low_prices,
                    'close': mock_prices,
                    'volume': np.random.randint(1000000, 10000000, len(dates))
                })
                
                # Mock 데이터를 Supabase에 저장 (선택적)
                # if supabase:
                #     save_to_supabase(stock_code, data)
            
            # 백테스트 실행 - 고급 엔진 또는 기본 엔진 사용
            capital_per_stock = request.initial_capital / total_stocks

            if USE_ADVANCED_ENGINE:
                # 고급 백테스트 엔진 사용
                print(f"  - 고급 백테스트 엔진 사용")
                engine = AdvancedBacktestEngine(
                    initial_capital=capital_per_stock,
                    commission=request.commission,
                    slippage=request.slippage
                )
                result_dict = engine.run(data, merged_parameters)

                # BacktestResult 형식으로 변환
                result = BacktestResult(
                    total_return=result_dict['total_return'],
                    win_rate=result_dict['win_rate'],
                    sharpe_ratio=result_dict['sharpe_ratio'],
                    max_drawdown=result_dict['max_drawdown'],
                    total_trades=result_dict['total_trades'],
                    winning_trades=result_dict['winning_trades'],
                    losing_trades=result_dict['losing_trades'],
                    buy_count=result_dict.get('buy_count', 0),
                    sell_count=result_dict.get('sell_count', 0),
                    trades=result_dict['trades']
                )
            else:
                # 기본 백테스트 엔진 사용
                print(f"  - 기본 백테스트 엔진 사용")
                strategy = Strategy()
                data = await strategy.execute_strategy(data, merged_parameters)

                if 'signal' not in data.columns:
                    print(f"  ! 경고: {stock_code}에 대한 신호가 생성되지 않음")
                    data['signal'] = 0

                engine = BacktestEngine()
                result = await engine.run_backtest(
                    data,
                    capital_per_stock,
                    commission=request.commission,
                    slippage=request.slippage
                )
            
            all_results.append({
                'stock_code': stock_code,
                'result': result.dict()
            })
            print(f"[완료] {idx}/{total_stocks} - 종목코드: {stock_code} 완료")
        
        # 전체 결과 집계
        print(f"[백테스트 완료] 모든 종목 처리 완료. 결과 집계 중...")
        total_return = np.mean([r['result']['total_return'] for r in all_results])
        avg_win_rate = np.mean([r['result']['win_rate'] for r in all_results])
        avg_sharpe = np.mean([r['result']['sharpe_ratio'] for r in all_results])
        max_dd = np.max([r['result']['max_drawdown'] for r in all_results])
        
        # 전체 거래 수와 승리/패배 거래 수, 매수/매도 횟수 집계
        total_trades = sum([r['result']['total_trades'] for r in all_results])
        total_winning = sum([r['result']['winning_trades'] for r in all_results])
        total_losing = sum([r['result']['losing_trades'] for r in all_results])
        total_buy_count = sum([r['result'].get('buy_count', 0) for r in all_results])
        total_sell_count = sum([r['result'].get('sell_count', 0) for r in all_results])
        
        print(f"[결과] 평균 수익률: {total_return:.2f}%, 평균 승률: {avg_win_rate:.2f}%")
        print(f"[결과] 총 거래: {total_trades}회, 승리: {total_winning}회, 패배: {total_losing}회")
        
        return {
            "success": True,
            "summary": {
                "total_return": total_return,
                "average_win_rate": avg_win_rate,
                "average_sharpe_ratio": avg_sharpe,
                "max_drawdown": max_dd,
                "stock_count": len(request.stock_codes),
                "processed_count": len(all_results),
                "total_trades": total_trades,
                "winning_trades": total_winning,
                "losing_trades": total_losing,
                "buy_count": total_buy_count,
                "sell_count": total_sell_count
            },
            "individual_results": all_results,
            "request": request.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_strategies():
    """사용 가능한 전략 목록 - Supabase에서 로드"""
    try:
        if supabase:
            # Supabase에서 전략 목록 가져오기
            response = supabase.table('strategies').select('id, name, description, type, config').execute()
            if response.data:
                return {
                    "success": True,
                    "strategies": response.data
                }
        
        # Supabase가 없거나 실패한 경우 빈 목록 반환
        return {
            "success": False,
            "strategies": [],
            "message": "Supabase에서 전략을 로드할 수 없습니다"
        }
    except Exception as e:
        return {
            "success": False,
            "strategies": [],
            "error": str(e)
        }

@router.get("/results/{user_id}")
async def get_backtest_results(user_id: str):
    """사용자의 백테스트 결과 조회"""
    # TODO: Supabase에서 결과 조회
    return {
        "success": True,
        "results": []
    }

class AnalyzeRequest(BaseModel):
    """전략 분석 요청 모델"""
    strategy_config: Dict[str, Any]
    stock_codes: List[str]  # 다중 종목 지원
    start_date: str
    end_date: str
    save_to_file: bool = False

@router.post("/analyze")
async def analyze_strategy(request: AnalyzeRequest):
    """전략 분석 실행"""
    try:
        if not USE_ANALYZER:
            raise HTTPException(
                status_code=500,
                detail="Strategy analyzer is not available"
            )

        print(f"\n[전략 분석] 종목: {', '.join(request.stock_codes)}")
        print(f"  기간: {request.start_date} ~ {request.end_date}")

        # 각 종목별로 분석 실행
        all_results = {}

        for stock_code in request.stock_codes:
            print(f"\n  분석 중: {stock_code}")

            # 1. 데이터 로드 (백테스트와 동일한 방식)
            data = None

            # Supabase에서 데이터 조회
            if supabase:
                try:
                    response = supabase.table('kw_price_daily').select('*').eq(
                        'stock_code', stock_code
                    ).gte('trade_date', request.start_date).lte('trade_date', request.end_date).order('trade_date').execute()

                    if response.data and len(response.data) > 0:
                        print(f"  [OK] Supabase에서 {len(response.data)}개 데이터 로드")
                        data = pd.DataFrame(response.data)
                        # trade_date를 date로 변환
                        data['date'] = pd.to_datetime(data['trade_date'])

                        # OHLCV 데이터 확인
                        required_cols = ['date', 'close']
                        if 'close' in data.columns:
                            # 누락된 OHLC 데이터 보완
                            if 'open' not in data.columns:
                                data['open'] = data['close']
                            if 'high' not in data.columns:
                                data['high'] = data['close'] * 1.01
                            if 'low' not in data.columns:
                                data['low'] = data['close'] * 0.99
                            if 'volume' not in data.columns:
                                data['volume'] = 1000000
                        else:
                            print(f"  [WARNING] 데이터에 close 컬럼이 없습니다")
                            data = None
                except Exception as e:
                    print(f"  [ERROR] Supabase 조회 실패: {str(e)}")
                    data = None

            # Mock 데이터 생성 (필요시)
            if data is None or data.empty:
                print(f"    [INFO] Mock 데이터 생성 중...")
                dates = pd.date_range(start=request.start_date, end=request.end_date, freq='D')
                base_price = 50000 + np.random.randint(0, 50000)
                mock_prices = np.random.randn(len(dates)) * (base_price * 0.02) + base_price

                high_prices = mock_prices * (1 + np.random.uniform(0, 0.02, len(dates)))
                low_prices = mock_prices * (1 - np.random.uniform(0, 0.02, len(dates)))
                open_prices = np.roll(mock_prices, 1) * (1 + np.random.uniform(-0.01, 0.01, len(dates)))
                open_prices[0] = mock_prices[0]

                data = pd.DataFrame({
                    'date': dates,
                    'open': open_prices,
                    'high': high_prices,
                    'low': low_prices,
                    'close': mock_prices,
                    'volume': np.random.randint(100000, 10000000, len(dates))
                })

            # 2. 전략 분석 실행
            analyzer = StrategyAnalyzer()
            results = analyzer.analyze_strategy(
                data=data,
                strategy_config=request.strategy_config,
                save_to_file=False  # 개별 종목은 파일 저장 안함
            )

            all_results[stock_code] = results

        # 3. 전체 결과 요약 생성
        summary = {
            "total_stocks": len(request.stock_codes),
            "analyzed_stocks": len(all_results),
            "period": f"{request.start_date} ~ {request.end_date}",
            "average_return": np.mean([r['backtest_analysis']['total_return'] for r in all_results.values()]),
            "average_win_rate": np.mean([r['backtest_analysis']['win_rate'] for r in all_results.values()])
        }

        # 4. 결과 반환
        return {
            "success": True,
            "summary": summary,
            "results_by_stock": all_results,
            "data_source": "supabase" if supabase else "mock"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 전략 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))