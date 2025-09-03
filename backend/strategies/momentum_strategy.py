"""
모멘텀 전략 구현
"""
from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    """모멘텀 기반 거래 전략"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        default_params = {
            'lookback_period': 20,  # 모멘텀 계산 기간
            'threshold': 0.05,  # 모멘텀 임계값 (5%)
            'volume_filter': True,  # 거래량 필터 사용
            'volume_ratio_min': 1.5,  # 최소 거래량 비율
            'rsi_oversold': 30,  # RSI 과매도
            'rsi_overbought': 70,  # RSI 과매수
            'use_confirmation': True  # 추가 확인 신호 사용
        }
        if parameters:
            default_params.update(parameters)
        super().__init__("Momentum", default_params)
    
    def calculate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """모멘텀 신호 계산"""
        if len(data) < self.parameters['lookback_period']:
            return {'type': 'hold', 'strength': 0, 'reason': 'Insufficient data'}
        
        # 지표 계산
        data = self.calculate_indicators(data)
        
        # 최근 데이터
        current = data.iloc[-1]
        prev = data.iloc[-2]
        
        # 모멘텀 계산
        momentum = self._calculate_momentum(data)
        
        # 거래량 확인
        volume_ok = self._check_volume(data) if self.parameters['volume_filter'] else True
        
        # RSI 확인
        rsi = current['RSI']
        
        # 신호 생성
        signal = {'type': 'hold', 'strength': 0}
        
        # 매수 신호
        if (momentum > self.parameters['threshold'] and 
            volume_ok and 
            rsi < self.parameters['rsi_overbought']):
            
            strength = min(momentum / (self.parameters['threshold'] * 2), 1.0)
            
            if self.parameters['use_confirmation']:
                if self._check_buy_confirmation(data):
                    signal = {
                        'type': 'buy',
                        'strength': strength,
                        'price': current['close'],
                        'reason': f'Momentum: {momentum:.2%}, RSI: {rsi:.1f}'
                    }
            else:
                signal = {
                    'type': 'buy',
                    'strength': strength,
                    'price': current['close'],
                    'reason': f'Momentum: {momentum:.2%}, RSI: {rsi:.1f}'
                }
        
        # 매도 신호
        elif (momentum < -self.parameters['threshold'] or 
              rsi > self.parameters['rsi_overbought']):
            
            strength = min(abs(momentum) / (self.parameters['threshold'] * 2), 1.0)
            
            signal = {
                'type': 'sell',
                'strength': strength,
                'price': current['close'],
                'reason': f'Momentum: {momentum:.2%}, RSI: {rsi:.1f}'
            }
        
        return signal
    
    def _calculate_momentum(self, data: pd.DataFrame) -> float:
        """모멘텀 계산"""
        period = self.parameters['lookback_period']
        if len(data) < period:
            return 0
        
        current_price = data['close'].iloc[-1]
        past_price = data['close'].iloc[-period]
        
        return (current_price - past_price) / past_price
    
    def _check_volume(self, data: pd.DataFrame) -> bool:
        """거래량 체크"""
        if len(data) < 20:
            return False
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].iloc[-20:].mean()
        
        return current_volume > avg_volume * self.parameters['volume_ratio_min']
    
    def _check_buy_confirmation(self, data: pd.DataFrame) -> bool:
        """매수 신호 확인"""
        if len(data) < 3:
            return False
        
        current = data.iloc[-1]
        prev = data.iloc[-2]
        
        # MACD 골든크로스
        macd_cross = (current['MACD'] > current['MACD_signal'] and 
                     prev['MACD'] <= prev['MACD_signal'])
        
        # 이동평균선 정배열
        ma_alignment = current['SMA_5'] > current['SMA_20']
        
        # 가격이 볼린저 밴드 하단 근처에서 반등
        bb_bounce = (current['close'] > current['BB_lower'] and 
                    prev['close'] <= prev['BB_lower'])
        
        return macd_cross or ma_alignment or bb_bounce
    
    def validate_signal(self, signal: Dict[str, Any], current_position: Dict[str, Any]) -> bool:
        """신호 유효성 검증"""
        # 이미 포지션이 있는 경우
        if current_position and current_position.get('quantity', 0) > 0:
            # 매수 신호는 무시
            if signal['type'] == 'buy':
                return False
        
        # 포지션이 없는 경우
        else:
            # 매도 신호는 무시
            if signal['type'] == 'sell':
                return False
        
        # 신호 강도가 너무 약한 경우
        if signal.get('strength', 0) < 0.3:
            return False
        
        return True