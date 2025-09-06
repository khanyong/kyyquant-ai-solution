"""
RSI (Relative Strength Index) 전략
"""
from typing import Dict, Any
import pandas as pd
from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    """RSI 기반 과매수/과매도 전략"""
    
    def __init__(self, name: str = "RSI Strategy", parameters: Dict[str, Any] = None):
        default_params = {
            'rsi_period': 14,        # RSI 계산 기간
            'oversold': 30,          # 과매도 기준선
            'overbought': 70,        # 과매수 기준선
            'use_divergence': True,  # 다이버전스 사용 여부
            'min_volume': 1000000    # 최소 거래량 필터
        }
        
        if parameters:
            default_params.update(parameters)
        
        super().__init__(name, default_params)
    
    def calculate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        RSI 신호 계산
        - RSI < 30: 과매도 → 매수 고려
        - RSI > 70: 과매수 → 매도 고려
        - 다이버전스: 가격과 RSI의 방향이 반대일 때
        """
        if len(data) < self.parameters['rsi_period'] + 5:
            return {'type': 'hold', 'strength': 0, 'price': 0}
        
        data = data.copy()
        
        # RSI 계산
        data['RSI'] = self.calculate_rsi(data['close'], self.parameters['rsi_period'])
        
        current_rsi = data['RSI'].iloc[-1]
        prev_rsi = data['RSI'].iloc[-2]
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        
        # 거래량 필터
        if current_volume < self.parameters['min_volume']:
            return {'type': 'hold', 'strength': 0, 'price': current_price}
        
        # 다이버전스 체크
        if self.parameters['use_divergence']:
            divergence = self._check_divergence(data)
            if divergence:
                return divergence
        
        # 과매도 영역에서 상승 전환 (매수 신호)
        if prev_rsi <= self.parameters['oversold'] and current_rsi > self.parameters['oversold']:
            strength = min((self.parameters['oversold'] - prev_rsi) / self.parameters['oversold'], 1.0)
            return {
                'type': 'buy',
                'strength': abs(strength),
                'price': current_price,
                'reason': f'RSI 과매도 영역 이탈 ({prev_rsi:.1f} → {current_rsi:.1f})'
            }
        
        # 과매수 영역에서 하락 전환 (매도 신호)
        elif prev_rsi >= self.parameters['overbought'] and current_rsi < self.parameters['overbought']:
            strength = min((prev_rsi - self.parameters['overbought']) / (100 - self.parameters['overbought']), 1.0)
            return {
                'type': 'sell',
                'strength': abs(strength),
                'price': current_price,
                'reason': f'RSI 과매수 영역 이탈 ({prev_rsi:.1f} → {current_rsi:.1f})'
            }
        
        return {'type': 'hold', 'strength': 0, 'price': current_price}
    
    def _check_divergence(self, data: pd.DataFrame) -> Dict[str, Any] or None:
        """
        다이버전스 체크
        - 강세 다이버전스: 가격은 하락하나 RSI는 상승
        - 약세 다이버전스: 가격은 상승하나 RSI는 하락
        """
        if len(data) < 20:
            return None
        
        # 최근 10일간의 고점/저점 찾기
        recent_data = data.tail(10)
        price_highs = recent_data['high']
        price_lows = recent_data['low']
        rsi_values = recent_data['RSI']
        
        # 강세 다이버전스 체크 (저점)
        if len(price_lows) >= 2:
            price_low_idx = price_lows.idxmin()
            prev_low_idx = price_lows.drop(price_low_idx).idxmin() if len(price_lows) > 1 else None
            
            if prev_low_idx and price_low_idx > prev_low_idx:
                price_lower = price_lows[price_low_idx] < price_lows[prev_low_idx]
                rsi_higher = rsi_values[price_low_idx] > rsi_values[prev_low_idx]
                
                if price_lower and rsi_higher:
                    return {
                        'type': 'buy',
                        'strength': 0.7,
                        'price': data['close'].iloc[-1],
                        'reason': '강세 다이버전스 발견'
                    }
        
        # 약세 다이버전스 체크 (고점)
        if len(price_highs) >= 2:
            price_high_idx = price_highs.idxmax()
            prev_high_idx = price_highs.drop(price_high_idx).idxmax() if len(price_highs) > 1 else None
            
            if prev_high_idx and price_high_idx > prev_high_idx:
                price_higher = price_highs[price_high_idx] > price_highs[prev_high_idx]
                rsi_lower = rsi_values[price_high_idx] < rsi_values[prev_high_idx]
                
                if price_higher and rsi_lower:
                    return {
                        'type': 'sell',
                        'strength': 0.7,
                        'price': data['close'].iloc[-1],
                        'reason': '약세 다이버전스 발견'
                    }
        
        return None
    
    def validate_signal(self, signal: Dict[str, Any], current_position: Dict[str, Any]) -> bool:
        """신호 유효성 검증"""
        # 기본 검증
        if not super().validate_signal(signal, current_position):
            return False
        
        # RSI 전략 특화 검증
        # 신호 강도가 너무 약하면 무시
        if signal['strength'] < 0.3:
            return False
        
        return True