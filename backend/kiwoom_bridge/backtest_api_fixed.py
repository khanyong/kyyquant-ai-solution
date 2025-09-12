"""
백테스트 API 엔드포인트 - 수정된 버전
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
    trades: List[Dict[str, Any]]

class Strategy:
    """전략 구현"""
    
    @staticmethod
    async def moving_average_crossover(data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """이동평균 교차 전략"""
        short_window = params.get('short_window', 5)
        long_window = params.get('long_window', 20)
        
        data['ma_short'] = data['close'].rolling(window=short_window).mean()
        data['ma_long'] = data['close'].rolling(window=long_window).mean()
        
        # 신호 생성
        data['signal'] = 0
        data.loc[data['ma_short'] > data['ma_long'], 'signal'] = 1
        data.loc[data['ma_short'] < data['ma_long'], 'signal'] = -1
        
        return data
    
    @staticmethod
    async def rsi_strategy(data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """RSI 전략"""
        period = params.get('rsi_period', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)
        
        # RSI 계산
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        data['rsi'] = rsi
        data['signal'] = 0
        data.loc[rsi < oversold, 'signal'] = 1
        data.loc[rsi > overbought, 'signal'] = -1
        
        return data
    
    @staticmethod
    async def bollinger_bands(data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """볼린저 밴드 전략"""
        window = params.get('bb_window', 20)
        num_std = params.get('bb_std', 2)
        
        data['bb_middle'] = data['close'].rolling(window=window).mean()
        data['bb_std'] = data['close'].rolling(window=window).std()
        data['bb_upper'] = data['bb_middle'] + (data['bb_std'] * num_std)
        data['bb_lower'] = data['bb_middle'] - (data['bb_std'] * num_std)
        
        data['signal'] = 0
        data.loc[data['close'] < data['bb_lower'], 'signal'] = 1
        data.loc[data['close'] > data['bb_upper'], 'signal'] = -1
        
        return data

class BacktestEngine:
    """백테스트 엔진 - 수정된 버전"""
    
    @staticmethod
    async def run_backtest(data: pd.DataFrame, initial_capital: float, commission: float = 0.00015, slippage: float = 0.001) -> BacktestResult:
        """백테스트 실행 - 수정된 로직"""
        capital = initial_capital
        position = 0
        trades = []
        entry_price = 0
        portfolio_values = []  # 포트폴리오 가치 추적
        
        for i in range(1, len(data)):
            signal = data.iloc[i]['signal']
            price = data.iloc[i]['close']
            date = data.iloc[i]['date']
            
            # 현재 포트폴리오 가치 계산
            current_value = capital + (position * price if position > 0 else 0)
            portfolio_values.append(current_value)
            
            # 매수 신호
            if signal == 1 and position == 0:
                # 슬리피지 적용
                actual_price = price * (1 + slippage)
                # 수수료 계산
                available_capital = capital / (1 + commission)
                shares = int(available_capital / actual_price)
                
                if shares > 0:
                    cost = shares * actual_price * (1 + commission)
                    position = shares
                    entry_price = actual_price
                    capital -= cost
                    
                    trades.append({
                        'date': date,
                        'type': 'buy',
                        'price': actual_price,
                        'shares': shares,
                        'cost': cost
                    })
            
            # 매도 신호
            elif signal == -1 and position > 0:
                # 슬리피지 적용
                actual_price = price * (1 - slippage)
                # 수수료 계산
                proceeds = position * actual_price * (1 - commission)
                
                # 수익 계산
                cost_basis = entry_price * position * (1 + commission)
                profit = proceeds - cost_basis
                profit_pct = (profit / cost_basis) * 100 if cost_basis > 0 else 0
                
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
        
        # 마지막 포지션 정리
        if position > 0:
            final_price = data.iloc[-1]['close'] * (1 - slippage)
            proceeds = position * final_price * (1 - commission)
            capital += proceeds
            
            cost_basis = entry_price * position * (1 + commission)
            profit = proceeds - cost_basis
            profit_pct = (profit / cost_basis) * 100 if cost_basis > 0 else 0
            
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
        
        # 최종 포트폴리오 가치
        final_value = capital
        portfolio_values.append(final_value)
        
        # 성과 계산
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        # 매수/매도 쌍으로 승률 계산
        sell_trades = [t for t in trades if t['type'] == 'sell']
        if sell_trades:
            winning_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
            losing_trades = [t for t in sell_trades if t.get('profit', 0) <= 0]
            win_rate = (len(winning_trades) / len(sell_trades)) * 100
        else:
            winning_trades = []
            losing_trades = []
            win_rate = 0
        
        # 최대 낙폭 계산 (포트폴리오 가치 기준)
        if portfolio_values:
            portfolio_values = np.array(portfolio_values)
            peak = np.maximum.accumulate(portfolio_values)
            drawdown = ((peak - portfolio_values) / peak) * 100
            max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        else:
            max_drawdown = 0
        
        # Sharpe Ratio 계산 (일일 수익률 기준)
        if len(portfolio_values) > 1:
            daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
            if len(daily_returns) > 0 and np.std(daily_returns) > 0:
                sharpe_ratio = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(252)  # 연간화
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        return BacktestResult(
            total_return=total_return,
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_trades=len([t for t in trades if t['type'] == 'buy']),  # 매수 횟수
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
            
            # Mock 데이터 생성
            dates = pd.date_range(start=request.start_date, end=request.end_date, freq='D')
            base_price = 50000 + np.random.randint(0, 50000)  # 종목별 다른 기준가
            
            # 더 현실적인 가격 변동 (브라운 운동)
            returns = np.random.randn(len(dates)) * 0.02  # 일일 변동성 2%
            price_series = base_price * np.exp(np.cumsum(returns))
            
            data = pd.DataFrame({
                'date': dates,
                'close': price_series,
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
            
            # 백테스트 실행 (수수료와 슬리피지 포함)
            engine = BacktestEngine()
            capital_per_stock = request.initial_capital / total_stocks
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
        
        print(f"[결과] 평균 수익률: {total_return:.2f}%, 평균 승률: {avg_win_rate:.2f}%")
        
        return {
            "success": True,
            "data": {
                "overall": {
                    "total_return": total_return,
                    "win_rate": avg_win_rate,
                    "sharpe_ratio": avg_sharpe,
                    "max_drawdown": max_dd,
                    "total_stocks": len(all_results)
                },
                "individual_results": all_results
            }
        }
        
    except Exception as e:
        print(f"[오류] 백테스트 실행 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))