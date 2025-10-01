"""
전략 기본 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd

class BaseStrategy(ABC):
    """모든 전략의 기본 클래스"""

    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any] = None):
        self.strategy_id = strategy_id
        self.name = name
        self.config = config or {}

    @abstractmethod
    def get_buy_conditions(self) -> List[Dict[str, Any]]:
        """매수 조건 반환"""
        pass

    @abstractmethod
    def get_sell_conditions(self) -> List[Dict[str, Any]]:
        """매도 조건 반환"""
        pass

    @abstractmethod
    def get_required_indicators(self) -> List[Dict[str, Any]]:
        """필요한 지표 목록 반환"""
        pass

    def validate_signal(self, signal: Dict[str, Any], current_position: Optional[Dict] = None) -> bool:
        """신호 유효성 검증"""
        # 기본 검증 로직
        if signal['type'] == 'buy' and current_position:
            return False  # 이미 포지션이 있으면 추가 매수 안함
        if signal['type'] == 'sell' and not current_position:
            return False  # 포지션이 없으면 매도 안함
        return True

    def calculate_position_size(self, capital: float, price: float, risk_ratio: float = 0.3) -> int:
        """포지션 크기 계산"""
        max_amount = capital * risk_ratio
        return int(max_amount / price)

    def format_signal_reason(self, conditions: List[Dict], values: Dict) -> str:
        """신호 이유 포맷팅"""
        reasons = []
        for condition in conditions:
            indicator = condition.get('indicator')
            operator = condition.get('operator')
            value = values.get(indicator, 'N/A')
            reasons.append(f"{indicator}={value}")
        return ", ".join(reasons)