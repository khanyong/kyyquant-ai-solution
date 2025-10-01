"""
RSI 과매도 전략
"""

from typing import List, Dict, Any
from ..base import BaseStrategy

class RSIOversoldStrategy(BaseStrategy):
    """
    RSI 과매도 전략
    - RSI가 과매도 구간에서 반등시 매수
    - RSI가 과매수 구간 도달시 매도
    """

    def __init__(self, strategy_id: str = 'rsi_oversold'):
        super().__init__(
            strategy_id=strategy_id,
            name="RSI Oversold Strategy",
            config={
                'rsi_period': 14,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'volume_ma_period': 20
            }
        )

    def get_required_indicators(self) -> List[Dict[str, Any]]:
        """필요한 지표"""
        return [
            {
                'name': 'rsi',
                'params': {'period': self.config['rsi_period']},
                'column_name': 'rsi'
            },
            {
                'name': 'ma',
                'params': {'period': 20},
                'column_name': 'ma_20'
            },
            {
                'name': 'ma',
                'params': {'period': 60},
                'column_name': 'ma_60'
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
                'indicator': 'rsi',
                'operator': 'cross_above',
                'value': self.config['rsi_oversold'],
                'description': 'RSI 과매도 구간 탈출'
            },
            {
                'indicator': 'close',
                'operator': '>',
                'compareTo': 'ma_20',
                'description': '20일 이평선 위'
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
                'indicator': 'rsi',
                'operator': '>',
                'value': self.config['rsi_overbought'],
                'description': 'RSI 과매수'
            },
            {
                'indicator': 'close',
                'operator': 'cross_below',
                'compareTo': 'ma_20',
                'description': '20일 이평선 하향 돌파'
            },
            {
                'indicator': 'profit_rate',
                'operator': '<',
                'value': -3,
                'description': '손절매 -3%'
            },
            {
                'indicator': 'profit_rate',
                'operator': '>',
                'value': 10,
                'description': '익절매 10%'
            }
        ]