"""
리스크 관리 모듈
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from config.config import config
from database.database import db

class RiskManager:
    """리스크 관리 클래스"""
    
    def __init__(self):
        self.config = config
        self.db = db
        self.daily_loss = 0
        self.daily_trades = 0
        self.last_reset = datetime.now().date()
    
    def check_trade_allowed(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> tuple[bool, str]:
        """
        거래 가능 여부 확인
        
        Returns:
            (가능 여부, 거부 사유)
        """
        # 날짜 변경 시 카운터 리셋
        if datetime.now().date() != self.last_reset:
            self.reset_daily_counters()
        
        # 1. 시장 시간 체크
        if not config.is_market_open():
            return False, "Market is closed"
        
        # 2. 일일 거래 횟수 제한
        if self.daily_trades >= config.get('risk_management.daily_trade_limit'):
            return False, f"Daily trade limit reached ({self.daily_trades})"
        
        # 3. 일일 손실 제한
        if self.check_daily_loss_limit():
            return False, f"Daily loss limit reached ({self.daily_loss:.2%})"
        
        # 4. 포지션 수 제한
        if signal['type'] == 'buy':
            current_positions = len([p for p in portfolio.values() if p['quantity'] > 0])
            if current_positions >= config.get('trading.max_positions'):
                return False, f"Maximum positions reached ({current_positions})"
        
        # 5. 포지션 크기 제한
        if not self.check_position_size(signal, portfolio):
            return False, "Position size exceeds limit"
        
        # 6. 변동성 필터
        if config.get('risk_management.volatility_filter'):
            if not self.check_volatility(signal.get('stock_code')):
                return False, "Volatility too high"
        
        return True, "OK"
    
    def check_daily_loss_limit(self) -> bool:
        """일일 손실 한도 확인"""
        # 오늘의 실현 손실 계산
        today = datetime.now().strftime('%Y-%m-%d')
        orders = self.db.get_recent_orders(limit=100)
        
        daily_pnl = 0
        for order in orders:
            if order.get('executed_at') and order['executed_at'].startswith(today):
                if order['order_type'] == 'sell':
                    # 매도 주문의 손익 계산
                    # 실제로는 매수 가격과 비교해야 하지만, 여기서는 간단히 구현
                    daily_pnl += (order.get('executed_price', 0) - order['price']) * order['quantity']
        
        total_capital = self.get_total_capital()
        if total_capital > 0:
            self.daily_loss = daily_pnl / total_capital
            return self.daily_loss < -config.get('risk_management.daily_loss_limit')
        
        return False
    
    def check_position_size(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """포지션 크기 제한 확인"""
        if signal['type'] != 'buy':
            return True
        
        total_capital = self.get_total_capital()
        position_value = signal.get('price', 0) * signal.get('quantity', 0)
        max_position_value = total_capital * config.get('trading.max_position_size')
        
        return position_value <= max_position_value
    
    def check_volatility(self, stock_code: str) -> bool:
        """변동성 체크"""
        # 최근 20일 가격 데이터 조회
        price_history = self.db.get_price_history(stock_code, days=20)
        
        if len(price_history) < 10:
            return True  # 데이터 부족 시 통과
        
        # 일일 수익률 계산
        returns = price_history['close'].pct_change().dropna()
        
        # 변동성 계산 (표준편차)
        volatility = returns.std()
        
        return volatility < config.get('risk_management.volatility_threshold')
    
    def calculate_position_size(self, signal: Dict[str, Any], capital: float) -> int:
        """
        적절한 포지션 크기 계산
        Kelly Criterion 변형 사용
        """
        # 기본 포지션 크기 (자본의 일정 비율)
        base_position = capital * config.get('trading.max_position_size')
        
        # 신호 강도에 따른 조정
        signal_strength = signal.get('strength', 0.5)
        adjusted_position = base_position * signal_strength
        
        # 최소 주문 금액 확인
        min_order = config.get('trading.min_order_amount')
        if adjusted_position < min_order:
            return 0
        
        # 주식 수량 계산
        price = signal.get('price', 0)
        if price > 0:
            quantity = int(adjusted_position / price)
            return quantity
        
        return 0
    
    def get_stop_loss_price(self, entry_price: float, signal_type: str) -> float:
        """손절 가격 계산"""
        stop_loss_rate = config.get('trading.stop_loss_rate')
        
        if signal_type == 'buy':
            return entry_price * (1 - stop_loss_rate)
        else:
            return entry_price * (1 + stop_loss_rate)
    
    def get_take_profit_price(self, entry_price: float, signal_type: str) -> float:
        """익절 가격 계산"""
        take_profit_rate = config.get('trading.take_profit_rate')
        
        if signal_type == 'buy':
            return entry_price * (1 + take_profit_rate)
        else:
            return entry_price * (1 - take_profit_rate)
    
    def check_stop_conditions(self, position: Dict[str, Any]) -> Optional[str]:
        """
        손절/익절 조건 확인
        
        Returns:
            'stop_loss', 'take_profit', or None
        """
        current_price = position.get('current_price', 0)
        avg_price = position.get('avg_price', 0)
        
        if current_price == 0 or avg_price == 0:
            return None
        
        profit_rate = (current_price - avg_price) / avg_price
        
        # 손절 확인
        if profit_rate <= -config.get('trading.stop_loss_rate'):
            return 'stop_loss'
        
        # 익절 확인
        if profit_rate >= config.get('trading.take_profit_rate'):
            return 'take_profit'
        
        return None
    
    def calculate_risk_metrics(self, portfolio: List[Dict[str, Any]]) -> Dict[str, float]:
        """포트폴리오 리스크 지표 계산"""
        if not portfolio:
            return {
                'total_value': 0,
                'var_95': 0,
                'cvar_95': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        # 포트폴리오 가치 계산
        total_value = sum(p['quantity'] * p['current_price'] for p in portfolio)
        
        # VaR (Value at Risk) 계산 - 95% 신뢰수준
        returns = []
        for position in portfolio:
            hist = self.db.get_price_history(position['stock_code'], days=30)
            if len(hist) > 1:
                ret = hist['close'].pct_change().dropna()
                returns.extend(ret.tolist())
        
        if returns:
            var_95 = np.percentile(returns, 5) * total_value
            cvar_95 = np.mean([r for r in returns if r <= np.percentile(returns, 5)]) * total_value
            
            # Sharpe Ratio
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (mean_return / std_return * np.sqrt(252)) if std_return > 0 else 0
        else:
            var_95 = 0
            cvar_95 = 0
            sharpe_ratio = 0
        
        return {
            'total_value': total_value,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'sharpe_ratio': sharpe_ratio,
            'positions': len(portfolio)
        }
    
    def get_total_capital(self) -> float:
        """총 자본 계산"""
        # 포트폴리오 가치
        portfolio = self.db.get_portfolio()
        portfolio_value = sum(p['quantity'] * p.get('current_price', 0) for p in portfolio)
        
        # 현금 잔고 (실제로는 API에서 가져와야 함)
        cash_balance = 1000000  # 임시값
        
        return portfolio_value + cash_balance
    
    def reset_daily_counters(self):
        """일일 카운터 리셋"""
        self.daily_loss = 0
        self.daily_trades = 0
        self.last_reset = datetime.now().date()
    
    def update_trade_count(self):
        """거래 횟수 업데이트"""
        self.daily_trades += 1
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """리스크 리포트 생성"""
        portfolio = self.db.get_portfolio()
        metrics = self.calculate_risk_metrics(portfolio)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'portfolio_metrics': metrics,
            'daily_stats': {
                'trades': self.daily_trades,
                'daily_loss': self.daily_loss,
                'trade_limit': config.get('risk_management.daily_trade_limit'),
                'loss_limit': config.get('risk_management.daily_loss_limit')
            },
            'risk_parameters': {
                'max_positions': config.get('trading.max_positions'),
                'max_position_size': config.get('trading.max_position_size'),
                'stop_loss_rate': config.get('trading.stop_loss_rate'),
                'take_profit_rate': config.get('trading.take_profit_rate')
            }
        }

# 전역 리스크 매니저 인스턴스
risk_manager = RiskManager()