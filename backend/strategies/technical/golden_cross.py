"""
골든크로스 전략
"""

from typing import List, Dict, Any
from ..base import BaseStrategy

class GoldenCrossStrategy(BaseStrategy):
    """
    골든크로스 전략
    - 단기 이동평균이 장기 이동평균을 상향 돌파시 매수
    - RSI 과매수 구간에서 매도
    """

    def __init__(self, strategy_id: str = 'golden_cross'):
        super().__init__(
            strategy_id=strategy_id,
            name="Golden Cross Strategy",
            config={
                'short_period': 20,
                'long_period': 60,
                'rsi_period': 14,
                'rsi_overbought': 70,
                'rsi_oversold': 30
            }
        )

    def get_required_indicators(self) -> List[Dict[str, Any]]:
        """필요한 지표"""
        return [
            {
                'name': 'ma',
                'params': {'period': self.config['short_period']},
                'column_name': f"ma_{self.config['short_period']}"
            },
            {
                'name': 'ma',
                'params': {'period': self.config['long_period']},
                'column_name': f"ma_{self.config['long_period']}"
            },
            {
                'name': 'rsi',
                'params': {'period': self.config['rsi_period']},
                'column_name': 'rsi'
            },
            {
                'name': 'volume',
                'params': {},
                'column_name': 'volume'
            }
        ]

    def get_buy_conditions(self) -> List[Dict[str, Any]]:
        """매수 조건"""
        return [
            {
                'indicator': f"ma_{self.config['short_period']}",
                'operator': 'cross_above',
                'compareTo': f"ma_{self.config['long_period']}",
                'description': '골든크로스 발생'
            },
            {
                'indicator': 'rsi',
                'operator': '<',
                'value': self.config['rsi_overbought'],
                'description': 'RSI 과매수 아님'
            },
            {
                'indicator': 'volume',
                'operator': '>',
                'compareTo': 'volume_ma_20',
                'description': '거래량 평균 이상'
            }
        ]

    def get_sell_conditions(self) -> List[Dict[str, Any]]:
        """매도 조건"""
        return [
            # 데드크로스
            {
                'indicator': f"ma_{self.config['short_period']}",
                'operator': 'cross_below',
                'compareTo': f"ma_{self.config['long_period']}",
                'description': '데드크로스 발생'
            },
            # RSI 과매수
            {
                'indicator': 'rsi',
                'operator': '>',
                'value': self.config['rsi_overbought'],
                'description': 'RSI 과매수'
            },
            # 손절매 (-5%)
            {
                'indicator': 'profit_rate',
                'operator': '<',
                'value': -5,
                'description': '손절매 -5%'
            },
            # 익절매 (15%)
            {
                'indicator': 'profit_rate',
                'operator': '>',
                'value': 15,
                'description': '익절매 15%'
            }
        ]