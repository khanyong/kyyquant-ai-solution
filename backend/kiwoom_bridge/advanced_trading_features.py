"""
고급 거래 기능 구현
- 분할 매수/매도
- 트레일링 스탑
- 피라미딩
- 켈리 기준 포지션 사이징
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Position:
    """포지션 정보"""
    stock_code: str
    entry_date: datetime
    entry_price: float
    quantity: int
    current_price: float = 0
    highest_price: float = 0  # 트레일링 스탑용
    lowest_price: float = float('inf')  # 추가 매수 판단용
    pyramid_level: int = 0  # 피라미딩 레벨
    partial_exits: List[Dict] = field(default_factory=list)  # 분할 매도 기록

    @property
    def profit_pct(self) -> float:
        """수익률 계산"""
        if self.entry_price == 0:
            return 0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100

    @property
    def market_value(self) -> float:
        """현재 시가 평가액"""
        return self.quantity * self.current_price

    def update_price(self, price: float):
        """가격 업데이트 및 최고/최저가 추적"""
        self.current_price = price
        self.highest_price = max(self.highest_price, price)
        self.lowest_price = min(self.lowest_price, price)


class SplitTradingManager:
    """분할 매수/매도 관리"""

    def __init__(self, config: Dict):
        self.config = config.get('splitTrading', {})
        self.enabled = self.config.get('enabled', False)
        self.buy_levels = self.config.get('buyLevels', [])
        self.sell_levels = self.config.get('sellLevels', [])

    def get_buy_signal(self, position: Optional[Position], current_price: float,
                      base_signal: bool) -> Tuple[bool, float]:
        """분할 매수 신호 및 비율 반환"""
        if not self.enabled or not base_signal:
            return base_signal, 1.0

        if position is None:
            # 첫 매수
            if self.buy_levels:
                return True, self.buy_levels[0].get('percentage', 100) / 100
            return True, 1.0

        # 추가 매수 체크
        price_drop_pct = ((current_price - position.entry_price) / position.entry_price) * 100

        for i, level in enumerate(self.buy_levels[1:], 1):
            if price_drop_pct <= level.get('priceLevel', 0):
                if i > position.pyramid_level:
                    position.pyramid_level = i
                    return True, level.get('percentage', 0) / 100

        return False, 0

    def get_sell_signal(self, position: Position, base_signal: bool) -> Tuple[bool, float]:
        """분할 매도 신호 및 비율 반환"""
        if not self.enabled or not position:
            return base_signal, 1.0

        profit_pct = position.profit_pct

        # 단계별 매도 체크
        for level in self.sell_levels:
            profit_target = level.get('profitLevel', 0)
            if profit_pct >= profit_target:
                # 이미 이 레벨에서 매도했는지 체크
                if not any(e.get('level') == profit_target for e in position.partial_exits):
                    position.partial_exits.append({
                        'level': profit_target,
                        'percentage': level.get('percentage', 0)
                    })
                    return True, level.get('percentage', 0) / 100

        return base_signal, 1.0


class TrailingStopManager:
    """트레일링 스탑 관리"""

    def __init__(self, config: Dict):
        self.config = config.get('trailingStop', {})
        self.enabled = self.config.get('enabled', False)
        self.activation = self.config.get('activation', 5.0)  # 활성화 수익률
        self.distance = self.config.get('distance', 2.0)  # 최고점 대비 하락률

    def check_trailing_stop(self, position: Position) -> bool:
        """트레일링 스탑 체크"""
        if not self.enabled or not position:
            return False

        profit_pct = position.profit_pct

        # 활성화 조건 체크
        if profit_pct < self.activation:
            return False

        # 최고점 대비 하락률 계산
        drop_from_high = ((position.highest_price - position.current_price) /
                         position.highest_price) * 100

        return drop_from_high >= self.distance


class PyramidingManager:
    """피라미딩 전략 관리"""

    def __init__(self, config: Dict):
        self.config = config.get('pyramiding', {})
        self.enabled = self.config.get('enabled', False)
        self.max_positions = self.config.get('maxPositions', 3)
        self.interval = self.config.get('interval', {})
        self.size_ratio = self.config.get('sizeRatio', [1, 0.5, 0.25])

    def get_pyramid_signal(self, position: Optional[Position], current_price: float,
                          base_signal: bool) -> Tuple[bool, float]:
        """피라미딩 신호 및 사이즈 반환"""
        if not self.enabled or not base_signal:
            return base_signal, 1.0

        if position is None:
            # 첫 진입
            return True, self.size_ratio[0] if self.size_ratio else 1.0

        # 최대 포지션 체크
        if position.pyramid_level >= self.max_positions - 1:
            return False, 0

        interval_type = self.interval.get('type', 'price')
        interval_value = self.interval.get('value', 2)

        if interval_type == 'price':
            # 가격 기준 피라미딩
            price_rise_pct = ((current_price - position.entry_price) /
                            position.entry_price) * 100

            if price_rise_pct >= interval_value * (position.pyramid_level + 1):
                position.pyramid_level += 1
                size = self.size_ratio[position.pyramid_level] if \
                       position.pyramid_level < len(self.size_ratio) else 0.25
                return True, size

        return False, 0


class PositionSizingManager:
    """포지션 사이징 관리"""

    def __init__(self, config: Dict, initial_capital: float):
        self.config = config.get('positionSizing', {})
        self.method = self.config.get('method', 'fixed')
        self.max_size = self.config.get('maxPositionSize', 1.0)
        self.min_size = self.config.get('minPositionSize', 0.1)
        self.initial_capital = initial_capital

    def calculate_position_size(self, win_rate: float, avg_win: float,
                               avg_loss: float, current_capital: float) -> float:
        """포지션 사이즈 계산"""

        if self.method == 'kelly':
            # 켈리 기준
            if avg_loss == 0:
                return self.min_size

            b = avg_win / abs(avg_loss)  # 승리/패배 비율
            p = win_rate / 100  # 승률
            q = 1 - p  # 패율

            kelly_pct = (p * b - q) / b if b > 0 else 0
            kelly_pct = max(0, min(kelly_pct, self.max_size))

            # 보수적 적용 (1/4 켈리)
            return max(self.min_size, min(kelly_pct / 4, self.max_size))

        elif self.method == 'volatility_based':
            # 변동성 기반 (구현 필요)
            return 0.2

        else:
            # 고정 비율
            return min(self.max_size, 1.0)


class RiskManager:
    """리스크 관리"""

    def __init__(self, config: Dict):
        self.config = config.get('riskManagement', {})
        self.max_drawdown = self.config.get('maxDrawdown', 20)
        self.daily_loss_limit = self.config.get('dailyLossLimit', 5)
        self.consecutive_loss_stop = self.config.get('consecutiveLossStop', 5)

        self.peak_value = 0
        self.daily_start_value = 0
        self.consecutive_losses = 0
        self.is_stopped = False

    def update_metrics(self, portfolio_value: float, trade_result: Optional[str] = None):
        """메트릭 업데이트"""
        self.peak_value = max(self.peak_value, portfolio_value)

        if trade_result == 'loss':
            self.consecutive_losses += 1
        elif trade_result == 'win':
            self.consecutive_losses = 0

    def check_risk_limits(self, portfolio_value: float) -> bool:
        """리스크 한도 체크"""
        if self.is_stopped:
            return True

        # 최대 낙폭 체크
        if self.peak_value > 0:
            drawdown = ((self.peak_value - portfolio_value) / self.peak_value) * 100
            if drawdown >= self.max_drawdown:
                self.is_stopped = True
                print(f"[리스크 관리] 최대 낙폭 {drawdown:.2f}% 도달 - 거래 중단")
                return True

        # 일일 손실 한도 체크
        if self.daily_start_value > 0:
            daily_loss = ((self.daily_start_value - portfolio_value) /
                         self.daily_start_value) * 100
            if daily_loss >= self.daily_loss_limit:
                print(f"[리스크 관리] 일일 손실 {daily_loss:.2f}% 도달 - 당일 거래 중단")
                return True

        # 연속 손실 체크
        if self.consecutive_losses >= self.consecutive_loss_stop:
            self.is_stopped = True
            print(f"[리스크 관리] {self.consecutive_losses}연패 - 거래 중단")
            return True

        return False

    def reset_daily(self, portfolio_value: float):
        """일일 리셋"""
        self.daily_start_value = portfolio_value


class SteppedTargetProfitManager:
    """단계별 목표 수익률 관리"""

    def __init__(self, config: Dict):
        self.config = config.get('targetProfit', {})
        self.enabled = self.config.get('enabled', False)
        self.type = self.config.get('type', 'simple')
        self.levels = self.config.get('levels', [])

    def check_target_profit(self, position: Position) -> Tuple[bool, float]:
        """목표 수익률 체크"""
        if not self.enabled or not position:
            return False, 0

        profit_pct = position.profit_pct

        if self.type == 'stepped':
            # 단계별 목표
            for level in self.levels:
                target = level.get('profit', 0)
                if profit_pct >= target:
                    # 이미 이 레벨에서 매도했는지 체크
                    if not any(e.get('profit_level') == target for e in position.partial_exits):
                        ratio = level.get('sellRatio', 1.0)
                        position.partial_exits.append({
                            'profit_level': target,
                            'sell_ratio': ratio
                        })
                        return True, ratio
        else:
            # 단순 목표
            target = self.config.get('value', 5.0)
            if profit_pct >= target:
                return True, 1.0

        return False, 0


class MeanReversionManager:
    """평균회귀 전략 관리"""

    def __init__(self, config: Dict):
        self.config = config.get('meanReversion', {})
        self.enabled = self.config.get('enabled', False)
        self.target_return = self.config.get('targetReturn', 'bb_middle')
        self.max_holding_days = self.config.get('maxHoldingDays', 10)

    def check_mean_reversion(self, position: Position, current_data: pd.Series,
                            days_held: int) -> bool:
        """평균회귀 매도 체크"""
        if not self.enabled or not position:
            return False

        # 최대 보유 기간 체크
        if days_held >= self.max_holding_days:
            print(f"[평균회귀] 최대 보유 기간 {days_held}일 도달 - 청산")
            return True

        # 목표 가격 도달 체크
        if self.target_return in current_data.index:
            target_price = current_data[self.target_return]
            if position.current_price >= target_price:
                print(f"[평균회귀] 목표 가격 {target_price:.0f} 도달")
                return True

        return False


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """샤프 비율 계산"""
    if len(returns) < 2:
        return 0

    excess_returns = returns - risk_free_rate / 252  # 일일 무위험 수익률
    if excess_returns.std() == 0:
        return 0

    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """소르티노 비율 계산 (하방 리스크만 고려)"""
    if len(returns) < 2:
        return 0

    excess_returns = returns - risk_free_rate / 252
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0

    return np.sqrt(252) * excess_returns.mean() / downside_returns.std()


def calculate_calmar_ratio(returns: pd.Series, max_drawdown: float) -> float:
    """칼마 비율 계산 (연간 수익률 / 최대 낙폭)"""
    if max_drawdown == 0:
        return 0

    annual_return = (1 + returns.mean()) ** 252 - 1
    return annual_return / abs(max_drawdown)