"""
볼린저 밴드 전략
"""

from typing import List, Dict, Any
from ..base import BaseStrategy

class BollingerBandStrategy(BaseStrategy):
    """
    볼린저 밴드 전략
    - 하단 밴드 터치 후 반등시 매수
    - 상단 밴드 터치시 매도
    """

    def __init__(self, strategy_id: str = 'bollinger_band'):
        super().__init__(
            strategy_id=strategy_id,
            name="Bollinger Band Strategy",
            config={
                'bb_period': 20,
                'bb_std': 2,
                'rsi_period': 14,
                'volume_ma_period': 20
            }
        )

    def get_required_indicators(self) -> List[Dict[str, Any]]:
        """필요한 지표"""
        return [
            {
                'name': 'bollinger',
                'params': {
                    'period': self.config['bb_period'],
                    'std': self.config['bb_std']
                },
                'column_name': 'bb'
            },
            {
                'name': 'rsi',
                'params': {'period': self.config['rsi_period']},
                'column_name': 'rsi'
            },
            {
                'name': 'volume_ma',
                'params': {'period': self.config['volume_ma_period']},
                'column_name': 'volume_ma_20'
            }
        ]

    def get_buy_conditions(self) -> List[Dict[str, Any]]:
        """매수 조건"""
        return [
            {
                'indicator': 'close',
                'operator': 'cross_above',
                'compareTo': 'bb_lower',
                'description': '볼린저 밴드 하단 반등'
            },
            {
                'indicator': 'rsi',
                'operator': '<',
                'value': 50,
                'description': 'RSI 50 미만'
            },
            {
                'indicator': 'volume',
                'operator': '>',
                'compareTo': 'volume_ma_20',
                'description': '거래량 증가'
            }
        ]

    def get_sell_conditions(self) -> List[Dict[str, Any]]:
        """매도 조건"""
        return [
            {
                'indicator': 'close',
                'operator': '>',
                'compareTo': 'bb_upper',
                'description': '볼린저 밴드 상단 터치'
            },
            {
                'indicator': 'rsi',
                'operator': '>',
                'value': 70,
                'description': 'RSI 과매수'
            },
            {
                'indicator': 'profit_rate',
                'operator': '<',
                'value': -5,
                'description': '손절매 -5%'
            },
            {
                'indicator': 'profit_rate',
                'operator': '>',
                'value': 20,
                'description': '익절매 20%'
            }
        ]