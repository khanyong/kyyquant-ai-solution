"""
간단한 이동평균 전략 예제
"""
from typing import Dict, Any
import pandas as pd
from .base_strategy import BaseStrategy

class SimpleMovingAverageStrategy(BaseStrategy):
    """이동평균선 교차 전략"""
    
    def __init__(self, name: str = "SMA Cross", parameters: Dict[str, Any] = None):
        default_params = {
            'short_window': 20,  # 단기 이동평균 기간
            'long_window': 60,   # 장기 이동평균 기간
            'volume_filter': True,  # 거래량 필터 사용 여부
            'volume_threshold': 1.5  # 평균 거래량 대비 임계값
        }
        
        if parameters:
            default_params.update(parameters)
        
        super().__init__(name, default_params)
    
    def calculate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        이동평균선 교차 신호 계산
        - 골든크로스: 단기선이 장기선을 상향 돌파 → 매수
        - 데드크로스: 단기선이 장기선을 하향 돌파 → 매도
        """
        if len(data) < self.parameters['long_window']:
            return {'type': 'hold', 'strength': 0, 'price': 0}
        
        # 이동평균 계산
        data = data.copy()
        data['SMA_short'] = data['close'].rolling(window=self.parameters['short_window']).mean()
        data['SMA_long'] = data['close'].rolling(window=self.parameters['long_window']).mean()
        
        # 현재와 이전 값
        current_short = data['SMA_short'].iloc[-1]
        current_long = data['SMA_long'].iloc[-1]
        prev_short = data['SMA_short'].iloc[-2]
        prev_long = data['SMA_long'].iloc[-2]
        current_price = data['close'].iloc[-1]
        
        # 거래량 필터
        if self.parameters['volume_filter']:
            avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
            current_volume = data['volume'].iloc[-1]
            
            if current_volume < avg_volume * self.parameters['volume_threshold']:
                return {'type': 'hold', 'strength': 0, 'price': current_price}
        
        # 골든크로스 (매수 신호)
        if prev_short <= prev_long and current_short > current_long:
            strength = min((current_short - current_long) / current_long, 1.0)
            return {
                'type': 'buy',
                'strength': strength,
                'price': current_price,
                'reason': '골든크로스 발생'
            }
        
        # 데드크로스 (매도 신호)
        elif prev_short >= prev_long and current_short < current_long:
            strength = min((current_long - current_short) / current_long, 1.0)
            return {
                'type': 'sell',
                'strength': strength,
                'price': current_price,
                'reason': '데드크로스 발생'
            }
        
        # 보유
        else:
            return {'type': 'hold', 'strength': 0, 'price': current_price}
    
    def validate_signal(self, signal: Dict[str, Any], current_position: Dict[str, Any]) -> bool:
        """신호 유효성 검증"""
        # 이미 포지션이 있는데 같은 방향의 신호면 무시
        if current_position.get('quantity', 0) > 0 and signal['type'] == 'buy':
            return False
        
        # 포지션이 없는데 매도 신호면 무시
        if current_position.get('quantity', 0) == 0 and signal['type'] == 'sell':
            return False
        
        # 신호 강도가 너무 약하면 무시
        if signal['strength'] < 0.1:
            return False
        
        return True