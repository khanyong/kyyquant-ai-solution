"""
거래 전략 기본 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """모든 거래 전략의 기본 클래스"""
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        self.position = {}  # 현재 포지션
        self.signals = []  # 생성된 신호들
        
    @abstractmethod
    def calculate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        거래 신호 계산
        
        Args:
            data: OHLCV 데이터프레임
            
        Returns:
            신호 딕셔너리 {'type': 'buy/sell/hold', 'strength': 0-1, 'price': float}
        """
        pass
    
    @abstractmethod
    def validate_signal(self, signal: Dict[str, Any], current_position: Dict[str, Any]) -> bool:
        """
        신호 유효성 검증
        
        Args:
            signal: 생성된 신호
            current_position: 현재 포지션
            
        Returns:
            신호가 유효한지 여부
        """
        pass
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """데이터 전처리"""
        # 기본 전처리: 결측값 제거, 정렬
        data = data.dropna()
        data = data.sort_index()
        return data
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        # 기본 지표들
        data['SMA_5'] = data['close'].rolling(window=5).mean()
        data['SMA_20'] = data['close'].rolling(window=20).mean()
        data['SMA_60'] = data['close'].rolling(window=60).mean()
        
        # 볼륨 지표
        data['volume_ratio'] = data['volume'] / data['volume'].rolling(window=20).mean()
        
        # 변동성
        data['volatility'] = data['close'].pct_change().rolling(window=20).std()
        
        # RSI
        data['RSI'] = self.calculate_rsi(data['close'])
        
        # MACD
        data['MACD'], data['MACD_signal'], data['MACD_hist'] = self.calculate_macd(data['close'])
        
        # 볼린저 밴드
        data['BB_upper'], data['BB_middle'], data['BB_lower'] = self.calculate_bollinger_bands(data['close'])
        
        return data
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD 계산"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2):
        """볼린저 밴드 계산"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    def calculate_position_size(self, capital: float, risk_per_trade: float, 
                              entry_price: float, stop_loss: float) -> int:
        """포지션 크기 계산"""
        if stop_loss >= entry_price:  # 매수 포지션
            return 0
        
        risk_amount = capital * risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        position_size = int(risk_amount / risk_per_share)
        
        # 최대 포지션 크기 제한
        max_position = int(capital * 0.3 / entry_price)  # 자본의 30% 제한
        return min(position_size, max_position)
    
    def get_stop_loss(self, entry_price: float, signal_type: str, atr: float = None) -> float:
        """손절가 계산"""
        if atr:
            # ATR 기반 손절
            if signal_type == 'buy':
                return entry_price - (2 * atr)
            else:
                return entry_price + (2 * atr)
        else:
            # 고정 비율 손절
            if signal_type == 'buy':
                return entry_price * 0.95  # 5% 손절
            else:
                return entry_price * 1.05
    
    def get_take_profit(self, entry_price: float, signal_type: str, atr: float = None) -> float:
        """익절가 계산"""
        if atr:
            # ATR 기반 익절
            if signal_type == 'buy':
                return entry_price + (3 * atr)
            else:
                return entry_price - (3 * atr)
        else:
            # 고정 비율 익절
            if signal_type == 'buy':
                return entry_price * 1.1  # 10% 익절
            else:
                return entry_price * 0.9
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 1000000) -> Dict[str, Any]:
        """백테스트 실행"""
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        data = self.preprocess_data(data)
        data = self.calculate_indicators(data)
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            signal = self.calculate_signal(current_data)
            
            if signal['type'] == 'buy' and position == 0:
                # 매수
                position = capital // data.iloc[i]['close']
                capital -= position * data.iloc[i]['close']
                trades.append({
                    'date': data.index[i],
                    'type': 'buy',
                    'price': data.iloc[i]['close'],
                    'quantity': position
                })
            elif signal['type'] == 'sell' and position > 0:
                # 매도
                capital += position * data.iloc[i]['close']
                trades.append({
                    'date': data.index[i],
                    'type': 'sell',
                    'price': data.iloc[i]['close'],
                    'quantity': position
                })
                position = 0
            
            # 자산 가치 계산
            total_value = capital + (position * data.iloc[i]['close'] if position > 0 else 0)
            equity_curve.append(total_value)
        
        # 성과 지표 계산
        returns = pd.Series(equity_curve).pct_change().dropna()
        
        return {
            'total_return': (equity_curve[-1] - initial_capital) / initial_capital,
            'trades': len(trades),
            'win_rate': self._calculate_win_rate(trades),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if len(returns) > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'equity_curve': equity_curve,
            'trades_history': trades
        }
    
    def _calculate_win_rate(self, trades: List[Dict[str, Any]]) -> float:
        """승률 계산"""
        if len(trades) < 2:
            return 0
        
        wins = 0
        for i in range(0, len(trades)-1, 2):
            if i+1 < len(trades):
                buy_price = trades[i]['price']
                sell_price = trades[i+1]['price']
                if sell_price > buy_price:
                    wins += 1
        
        return wins / (len(trades) // 2) if len(trades) >= 2 else 0
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """최대 낙폭 계산"""
        if not equity_curve:
            return 0
        
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd