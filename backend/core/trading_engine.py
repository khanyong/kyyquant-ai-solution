"""
자동매매 핵심 엔진
- 전략 실행
- 신호 생성
- 리스크 관리
- 백테스팅
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import json


# ==================== 전략 신호 ====================
class Signal(Enum):
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class TradingSignal:
    """매매 신호"""
    timestamp: datetime
    stock_code: str
    signal: Signal
    price: float
    quantity: int
    confidence: float  # 0.0 ~ 1.0
    strategy_name: str
    reason: str


@dataclass
class Position:
    """포지션 정보"""
    stock_code: str
    quantity: int
    avg_price: float
    current_price: float
    entry_time: datetime
    unrealized_pnl: float
    realized_pnl: float = 0


# ==================== 기술적 지표 계산 ====================
class TechnicalIndicators:
    """기술적 지표 계산"""
    
    @staticmethod
    def sma(prices: pd.Series, period: int) -> pd.Series:
        """단순 이동평균"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def ema(prices: pd.Series, period: int) -> pd.Series:
        """지수 이동평균"""
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2):
        """볼린저 밴드"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram


# ==================== 전략 베이스 클래스 ====================
class BaseStrategy:
    """전략 베이스 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.indicators = TechnicalIndicators()
        
    def analyze(self, data: pd.DataFrame) -> TradingSignal:
        """데이터 분석 및 신호 생성"""
        raise NotImplementedError
    
    def calculate_position_size(self, capital: float, risk_per_trade: float) -> int:
        """포지션 크기 계산"""
        # Kelly Criterion 또는 고정 비율
        return int(capital * risk_per_trade / 100)


# ==================== 전략 구현 예시 ====================
class MomentumStrategy(BaseStrategy):
    """모멘텀 전략"""
    
    def __init__(self):
        super().__init__("Momentum Strategy")
        
    def analyze(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        if len(data) < 50:
            return None
            
        # 지표 계산
        prices = data['close']
        rsi = self.indicators.rsi(prices)
        sma20 = self.indicators.sma(prices, 20)
        sma50 = self.indicators.sma(prices, 50)
        
        current_price = prices.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # 매수 신호: RSI < 30 and 가격이 SMA20 돌파
        if current_rsi < 30 and current_price > sma20.iloc[-1]:
            return TradingSignal(
                timestamp=datetime.now(),
                stock_code=data['code'].iloc[-1] if 'code' in data else 'UNKNOWN',
                signal=Signal.BUY,
                price=current_price,
                quantity=10,
                confidence=0.7,
                strategy_name=self.name,
                reason=f"RSI oversold ({current_rsi:.1f}) + Price above SMA20"
            )
        
        # 매도 신호: RSI > 70 or 가격이 SMA50 하향 돌파
        elif current_rsi > 70 or current_price < sma50.iloc[-1]:
            return TradingSignal(
                timestamp=datetime.now(),
                stock_code=data['code'].iloc[-1] if 'code' in data else 'UNKNOWN',
                signal=Signal.SELL,
                price=current_price,
                quantity=10,
                confidence=0.6,
                strategy_name=self.name,
                reason=f"RSI overbought ({current_rsi:.1f}) or below SMA50"
            )
        
        return None


class MeanReversionStrategy(BaseStrategy):
    """평균 회귀 전략"""
    
    def __init__(self):
        super().__init__("Mean Reversion Strategy")
        
    def analyze(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        if len(data) < 20:
            return None
            
        prices = data['close']
        upper, middle, lower = self.indicators.bollinger_bands(prices)
        current_price = prices.iloc[-1]
        
        # 매수: 하단 밴드 터치
        if current_price <= lower.iloc[-1]:
            return TradingSignal(
                timestamp=datetime.now(),
                stock_code=data['code'].iloc[-1] if 'code' in data else 'UNKNOWN',
                signal=Signal.BUY,
                price=current_price,
                quantity=10,
                confidence=0.75,
                strategy_name=self.name,
                reason="Price touched lower Bollinger Band"
            )
        
        # 매도: 상단 밴드 터치
        elif current_price >= upper.iloc[-1]:
            return TradingSignal(
                timestamp=datetime.now(),
                stock_code=data['code'].iloc[-1] if 'code' in data else 'UNKNOWN',
                signal=Signal.SELL,
                price=current_price,
                quantity=10,
                confidence=0.75,
                strategy_name=self.name,
                reason="Price touched upper Bollinger Band"
            )
        
        return None


# ==================== 리스크 관리 ====================
class RiskManager:
    """리스크 관리 시스템"""
    
    def __init__(self, 
                 max_position_size: float = 0.1,  # 종목당 최대 10%
                 max_daily_loss: float = 0.02,    # 일일 최대 손실 2%
                 max_drawdown: float = 0.1,       # 최대 낙폭 10%
                 stop_loss: float = 0.03,         # 손절 3%
                 take_profit: float = 0.05):      # 익절 5%
        
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
        self.daily_pnl = 0
        self.peak_value = 0
        self.current_drawdown = 0
        
    def check_position_limit(self, position_value: float, total_capital: float) -> bool:
        """포지션 한도 체크"""
        return (position_value / total_capital) <= self.max_position_size
    
    def check_daily_loss_limit(self) -> bool:
        """일일 손실 한도 체크"""
        return self.daily_pnl > -self.max_daily_loss
    
    def check_stop_loss(self, position: Position) -> bool:
        """손절 체크"""
        loss_pct = (position.current_price - position.avg_price) / position.avg_price
        return loss_pct <= -self.stop_loss
    
    def check_take_profit(self, position: Position) -> bool:
        """익절 체크"""
        profit_pct = (position.current_price - position.avg_price) / position.avg_price
        return profit_pct >= self.take_profit
    
    def update_drawdown(self, current_value: float):
        """드로우다운 업데이트"""
        if current_value > self.peak_value:
            self.peak_value = current_value
        
        self.current_drawdown = (self.peak_value - current_value) / self.peak_value
        return self.current_drawdown < self.max_drawdown


# ==================== 백테스팅 엔진 ====================
class BacktestEngine:
    """백테스팅 엔진"""
    
    def __init__(self, initial_capital: float = 10000000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades = []
        self.equity_curve = []
        
    def run(self, 
            data: pd.DataFrame, 
            strategy: BaseStrategy,
            risk_manager: RiskManager) -> Dict:
        """백테스트 실행"""
        
        for i in range(50, len(data)):
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']
            current_date = data.iloc[i]['date'] if 'date' in data else i
            
            # 포지션 업데이트
            for code, position in self.positions.items():
                position.current_price = current_price
                position.unrealized_pnl = (current_price - position.avg_price) * position.quantity
                
                # 리스크 체크
                if risk_manager.check_stop_loss(position):
                    self._close_position(code, current_price, "Stop Loss")
                elif risk_manager.check_take_profit(position):
                    self._close_position(code, current_price, "Take Profit")
            
            # 전략 신호 생성
            signal = strategy.analyze(current_data)
            
            if signal:
                if signal.signal in [Signal.BUY, Signal.STRONG_BUY]:
                    if risk_manager.check_daily_loss_limit():
                        self._open_position(signal)
                elif signal.signal in [Signal.SELL, Signal.STRONG_SELL]:
                    if signal.stock_code in self.positions:
                        self._close_position(signal.stock_code, signal.price, signal.reason)
            
            # 자산 기록
            total_value = self._calculate_total_value()
            self.equity_curve.append({
                'date': current_date,
                'value': total_value,
                'return': (total_value - self.initial_capital) / self.initial_capital
            })
        
        return self._calculate_metrics()
    
    def _open_position(self, signal: TradingSignal):
        """포지션 오픈"""
        cost = signal.price * signal.quantity
        if cost <= self.capital:
            self.capital -= cost
            self.positions[signal.stock_code] = Position(
                stock_code=signal.stock_code,
                quantity=signal.quantity,
                avg_price=signal.price,
                current_price=signal.price,
                entry_time=signal.timestamp,
                unrealized_pnl=0
            )
            self.trades.append({
                'time': signal.timestamp,
                'type': 'BUY',
                'code': signal.stock_code,
                'price': signal.price,
                'quantity': signal.quantity
            })
    
    def _close_position(self, stock_code: str, price: float, reason: str):
        """포지션 종료"""
        if stock_code in self.positions:
            position = self.positions[stock_code]
            revenue = price * position.quantity
            self.capital += revenue
            
            realized_pnl = (price - position.avg_price) * position.quantity
            
            self.trades.append({
                'time': datetime.now(),
                'type': 'SELL',
                'code': stock_code,
                'price': price,
                'quantity': position.quantity,
                'pnl': realized_pnl,
                'reason': reason
            })
            
            del self.positions[stock_code]
    
    def _calculate_total_value(self) -> float:
        """총 자산 계산"""
        positions_value = sum(p.current_price * p.quantity for p in self.positions.values())
        return self.capital + positions_value
    
    def _calculate_metrics(self) -> Dict:
        """성과 지표 계산"""
        if not self.equity_curve:
            return {}
        
        returns = pd.Series([e['return'] for e in self.equity_curve])
        
        # Sharpe Ratio (연환산)
        sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win Rate
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        return {
            'total_return': returns.iloc[-1] if len(returns) > 0 else 0,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'equity_curve': self.equity_curve
        }


# ==================== 자동매매 실행 엔진 ====================
class AutoTradingEngine:
    """자동매매 실행 엔진"""
    
    def __init__(self):
        self.strategies: List[BaseStrategy] = []
        self.risk_manager = RiskManager()
        self.positions: Dict[str, Position] = {}
        self.is_running = False
        self.signals_queue = asyncio.Queue()
        
    def add_strategy(self, strategy: BaseStrategy):
        """전략 추가"""
        self.strategies.append(strategy)
        print(f"✅ Strategy added: {strategy.name}")
    
    async def start(self):
        """자동매매 시작"""
        self.is_running = True
        print("🚀 Auto trading engine started")
        
        # 동시 실행
        await asyncio.gather(
            self._monitor_market(),
            self._execute_signals(),
            self._risk_monitoring()
        )
    
    async def stop(self):
        """자동매매 중지"""
        self.is_running = False
        print("🛑 Auto trading engine stopped")
    
    async def _monitor_market(self):
        """시장 모니터링 및 신호 생성"""
        while self.is_running:
            # 실시간 데이터 수신 (Mock)
            await asyncio.sleep(5)
            
            # 각 전략에서 신호 생성
            for strategy in self.strategies:
                # Mock 데이터로 테스트
                mock_data = self._generate_mock_data()
                signal = strategy.analyze(mock_data)
                
                if signal:
                    await self.signals_queue.put(signal)
                    print(f"📊 Signal generated: {signal.signal.name} for {signal.stock_code}")
    
    async def _execute_signals(self):
        """신호 실행"""
        while self.is_running:
            try:
                signal = await asyncio.wait_for(self.signals_queue.get(), timeout=1)
                
                # 리스크 체크
                if self._validate_signal(signal):
                    # 주문 실행 (실제로는 API 호출)
                    print(f"📈 Executing: {signal.signal.name} {signal.quantity} shares of {signal.stock_code} @ {signal.price}")
                    
                    # 포지션 업데이트
                    if signal.signal in [Signal.BUY, Signal.STRONG_BUY]:
                        self.positions[signal.stock_code] = Position(
                            stock_code=signal.stock_code,
                            quantity=signal.quantity,
                            avg_price=signal.price,
                            current_price=signal.price,
                            entry_time=signal.timestamp,
                            unrealized_pnl=0
                        )
                else:
                    print(f"⚠️ Signal rejected by risk manager")
                    
            except asyncio.TimeoutError:
                continue
    
    async def _risk_monitoring(self):
        """리스크 모니터링"""
        while self.is_running:
            await asyncio.sleep(10)
            
            for code, position in self.positions.items():
                # 손절/익절 체크
                if self.risk_manager.check_stop_loss(position):
                    print(f"🔴 Stop loss triggered for {code}")
                    # 매도 주문
                elif self.risk_manager.check_take_profit(position):
                    print(f"🟢 Take profit triggered for {code}")
                    # 매도 주문
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """신호 검증"""
        # 신뢰도 체크
        if signal.confidence < 0.5:
            return False
        
        # 리스크 한도 체크
        if not self.risk_manager.check_daily_loss_limit():
            return False
        
        return True
    
    def _generate_mock_data(self) -> pd.DataFrame:
        """Mock 데이터 생성"""
        dates = pd.date_range(end=datetime.now(), periods=100)
        prices = np.random.randn(100).cumsum() + 70000
        
        return pd.DataFrame({
            'date': dates,
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 100),
            'code': '005930'
        })


# ==================== 사용 예시 ====================
if __name__ == "__main__":
    # 백테스팅
    print("="*50)
    print("백테스팅 시작")
    print("="*50)
    
    # 데이터 준비
    data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=252),
        'close': np.random.randn(252).cumsum() + 70000,
        'volume': np.random.randint(1000000, 10000000, 252)
    })
    
    # 백테스트 실행
    backtest = BacktestEngine(initial_capital=10000000)
    strategy = MomentumStrategy()
    risk_manager = RiskManager()
    
    results = backtest.run(data, strategy, risk_manager)
    
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print(f"Total Trades: {results['total_trades']}")
    
    print("\n" + "="*50)
    print("자동매매 엔진 테스트")
    print("="*50)
    
    # 자동매매 실행
    async def run_auto_trading():
        engine = AutoTradingEngine()
        engine.add_strategy(MomentumStrategy())
        engine.add_strategy(MeanReversionStrategy())
        
        # 30초 실행
        task = asyncio.create_task(engine.start())
        await asyncio.sleep(30)
        await engine.stop()
    
    # asyncio.run(run_auto_trading())