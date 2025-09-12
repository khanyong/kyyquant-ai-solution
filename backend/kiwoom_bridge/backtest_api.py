"""
백테스트 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import numpy as np

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

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
    trades: List[Dict]

class Strategy:
    """전략 실행 클래스"""
    
    @staticmethod
    async def moving_average_crossover(data: pd.DataFrame, params: dict):
        """이동평균 교차 전략"""
        short_window = params.get('short_window', 5)
        long_window = params.get('long_window', 20)
        
        data['MA_short'] = data['close'].rolling(window=short_window).mean()
        data['MA_long'] = data['close'].rolling(window=long_window).mean()
        
        # 매수/매도 신호 생성
        data['signal'] = 0
        data.loc[data['MA_short'] > data['MA_long'], 'signal'] = 1  # 매수
        data.loc[data['MA_short'] < data['MA_long'], 'signal'] = -1  # 매도
        
        return data
    
    @staticmethod
    async def rsi_strategy(data: pd.DataFrame, params: dict):
        """RSI 전략"""
        period = params.get('period', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)
        
        # RSI 계산
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # 매수/매도 신호
        data['signal'] = 0
        data.loc[data['RSI'] < oversold, 'signal'] = 1  # 과매도 → 매수
        data.loc[data['RSI'] > overbought, 'signal'] = -1  # 과매수 → 매도
        
        return data
    
    @staticmethod
    async def bollinger_bands(data: pd.DataFrame, params: dict):
        """볼린저 밴드 전략"""
        window = params.get('window', 20)
        num_std = params.get('num_std', 2)
        
        data['MA'] = data['close'].rolling(window=window).mean()
        data['STD'] = data['close'].rolling(window=window).std()
        data['Upper'] = data['MA'] + (data['STD'] * num_std)
        data['Lower'] = data['MA'] - (data['STD'] * num_std)
        
        # 매수/매도 신호
        data['signal'] = 0
        data.loc[data['close'] < data['Lower'], 'signal'] = 1  # 하단 터치 → 매수
        data.loc[data['close'] > data['Upper'], 'signal'] = -1  # 상단 터치 → 매도
        
        return data

class BacktestEngine:
    """백테스트 엔진"""
    
    @staticmethod
    async def run_backtest(data: pd.DataFrame, initial_capital: float) -> BacktestResult:
        """백테스트 실행"""
        capital = initial_capital
        position = 0
        trades = []
        entry_price = 0
        
        for i in range(1, len(data)):
            signal = data.iloc[i]['signal']
            price = data.iloc[i]['close']
            date = data.iloc[i]['date']
            
            # 매수 신호
            if signal == 1 and position == 0:
                shares = int(capital / price)
                position = shares
                entry_price = price
                capital -= shares * price
                
                trades.append({
                    'date': date,
                    'type': 'buy',
                    'price': price,
                    'shares': shares
                })
            
            # 매도 신호
            elif signal == -1 and position > 0:
                capital += position * price
                profit = (price - entry_price) * position
                profit_pct = ((price - entry_price) / entry_price) * 100
                
                trades.append({
                    'date': date,
                    'type': 'sell',
                    'price': price,
                    'shares': position,
                    'profit': profit,
                    'profit_pct': profit_pct
                })
                
                position = 0
        
        # 마지막 포지션 정리
        if position > 0:
            final_price = data.iloc[-1]['close']
            capital += position * final_price
        
        # 성과 계산
        total_return = ((capital - initial_capital) / initial_capital) * 100
        winning_trades = [t for t in trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit', 0) < 0]
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
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
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            trades=trades
        )

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """백테스트 실행 - 여러 종목 지원"""
    try:
        all_results = []
        total_stocks = min(len(request.stock_codes), 10)  # 최대 10개 종목
        
        # 진행 상황을 로그로 출력
        print(f"[백테스트 시작] 총 {total_stocks}개 종목 처리 예정")
        
        # 각 종목에 대해 백테스트 실행
        for idx, stock_code in enumerate(request.stock_codes[:total_stocks], 1):
            print(f"[진행중] {idx}/{total_stocks} - 종목코드: {stock_code} 처리 중...")
            # TODO: Supabase에서 과거 가격 데이터 조회
            # 여기서는 Mock 데이터 사용
            dates = pd.date_range(start=request.start_date, end=request.end_date, freq='D')
            base_price = 50000 + np.random.randint(0, 50000)  # 종목별 다른 기준가
            mock_prices = np.random.randn(len(dates)) * (base_price * 0.02) + base_price
            
            data = pd.DataFrame({
                'date': dates,
                'close': mock_prices,
                'volume': np.random.randint(1000000, 10000000, len(dates))
            })
            
            # 전략 실행
            strategy = Strategy()
            if request.parameters.get('strategy_type') == 'ma_crossover':
                data = await strategy.moving_average_crossover(data, request.parameters)
            elif request.parameters.get('strategy_type') == 'rsi':
                data = await strategy.rsi_strategy(data, request.parameters)
            elif request.parameters.get('strategy_type') == 'bollinger':
                data = await strategy.bollinger_bands(data, request.parameters)
            else:
                # 기본: 이동평균 교차
                data = await strategy.moving_average_crossover(data, {'short_window': 5, 'long_window': 20})
            
            # 백테스트 실행
            engine = BacktestEngine()
            result = await engine.run_backtest(data, request.initial_capital / len(request.stock_codes))
            
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
        
        print(f"[결과] 평균 수익률: {total_return:.2f}%, 평균 승률: {avg_win_rate:.2f}%")
        
        return {
            "success": True,
            "summary": {
                "total_return": total_return,
                "average_win_rate": avg_win_rate,
                "average_sharpe_ratio": avg_sharpe,
                "max_drawdown": max_dd,
                "stock_count": len(request.stock_codes),
                "processed_count": len(all_results)
            },
            "individual_results": all_results,
            "request": request.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_strategies():
    """사용 가능한 전략 목록"""
    return {
        "strategies": [
            {
                "id": "ma_crossover",
                "name": "이동평균 교차",
                "parameters": ["short_window", "long_window"]
            },
            {
                "id": "rsi",
                "name": "RSI",
                "parameters": ["period", "oversold", "overbought"]
            },
            {
                "id": "bollinger",
                "name": "볼린저 밴드",
                "parameters": ["window", "num_std"]
            }
        ]
    }

@router.get("/results/{user_id}")
async def get_backtest_results(user_id: str):
    """사용자의 백테스트 결과 조회"""
    # TODO: Supabase에서 결과 조회
    return {
        "success": True,
        "results": []
    }