"""
전략 실행 관리자
모의투자 전략을 실행하고 관리
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client
import numpy as np

load_dotenv()

class StrategyExecutionManager:
    """전략 실행 관리 클래스"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        self.active_strategies = {}
        self.indicators = {}
        
    def create_strategy(self, user_id: str, strategy_data: Dict) -> Dict:
        """새 전략 생성"""
        try:
            # 전략 데이터 준비
            strategy = {
                'user_id': user_id,
                'name': strategy_data['name'],
                'description': strategy_data.get('description', ''),
                'is_active': False,  # 생성시에는 비활성
                'conditions': strategy_data.get('conditions', {}),
                'position_size': strategy_data.get('position_size', 10),
                'max_positions': strategy_data.get('max_positions', 5),
                'execution_time': strategy_data.get('execution_time', {
                    'start': '09:00',
                    'end': '15:20'
                }),
                'target_stocks': strategy_data.get('target_stocks', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Supabase에 저장
            result = self.supabase.table('strategies').insert(strategy).execute()
            
            if result.data:
                print(f"[전략생성] {strategy['name']} (ID: {result.data[0]['id']})")
                return result.data[0]
            else:
                raise Exception("전략 생성 실패")
                
        except Exception as e:
            print(f"[에러] 전략 생성 실패: {e}")
            return None
            
    def update_strategy(self, strategy_id: str, update_data: Dict) -> bool:
        """전략 업데이트"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            result = self.supabase.table('strategies').update(
                update_data
            ).eq('id', strategy_id).execute()
            
            if result.data:
                print(f"[전략업데이트] ID: {strategy_id}")
                return True
            return False
            
        except Exception as e:
            print(f"[에러] 전략 업데이트 실패: {e}")
            return False
            
    def activate_strategy(self, strategy_id: str) -> bool:
        """전략 활성화"""
        return self.update_strategy(strategy_id, {'is_active': True})
        
    def deactivate_strategy(self, strategy_id: str) -> bool:
        """전략 비활성화"""
        return self.update_strategy(strategy_id, {'is_active': False})
        
    def get_user_strategies(self, user_id: str) -> List[Dict]:
        """사용자 전략 조회"""
        try:
            result = self.supabase.table('strategies').select('*').eq(
                'user_id', user_id
            ).order('created_at', desc=True).execute()
            
            return result.data
            
        except Exception as e:
            print(f"[에러] 전략 조회 실패: {e}")
            return []
            
    def evaluate_conditions(self, conditions: Dict, market_data: Dict) -> bool:
        """조건 평가"""
        try:
            # 진입 조건 체크
            entry_conditions = conditions.get('entry', {})
            
            # RSI 조건
            if 'rsi' in entry_conditions:
                rsi_condition = entry_conditions['rsi']
                current_rsi = self.calculate_rsi(market_data.get('stock_code'))
                
                if not self._check_condition(current_rsi, rsi_condition):
                    return False
                    
            # 볼륨 조건
            if 'volume' in entry_conditions:
                volume_condition = entry_conditions['volume']
                current_volume = market_data.get('volume', 0)
                avg_volume = self.get_average_volume(market_data.get('stock_code'))
                
                if not self._check_volume_condition(current_volume, avg_volume, volume_condition):
                    return False
                    
            # 가격 조건 (이동평균)
            if 'price' in entry_conditions:
                price_condition = entry_conditions['price']
                current_price = market_data.get('current_price', 0)
                ma20 = self.calculate_ma(market_data.get('stock_code'), 20)
                
                if not self._check_price_condition(current_price, ma20, price_condition):
                    return False
                    
            return True
            
        except Exception as e:
            print(f"[에러] 조건 평가 실패: {e}")
            return False
            
    def _check_condition(self, value: float, condition: Dict) -> bool:
        """단일 조건 체크"""
        operator = condition.get('operator')
        threshold = condition.get('value')
        
        if operator == '<':
            return value < threshold
        elif operator == '>':
            return value > threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '==':
            return value == threshold
        else:
            return False
            
    def _check_volume_condition(self, current: int, average: int, condition: Dict) -> bool:
        """볼륨 조건 체크"""
        operator = condition.get('operator')
        value_str = condition.get('value', '')
        
        # "avg_volume * 2" 같은 형식 파싱
        if 'avg_volume' in value_str:
            multiplier = float(value_str.replace('avg_volume', '').replace('*', '').strip())
            threshold = average * multiplier
        else:
            threshold = float(value_str)
            
        return self._check_condition(current, {'operator': operator, 'value': threshold})
        
    def _check_price_condition(self, current: float, ma: float, condition: Dict) -> bool:
        """가격 조건 체크"""
        operator = condition.get('operator')
        value_str = condition.get('value', '')
        
        # "ma20" 같은 형식 처리
        if 'ma' in value_str:
            threshold = ma
        else:
            threshold = float(value_str)
            
        return self._check_condition(current, {'operator': operator, 'value': threshold})
        
    def calculate_rsi(self, stock_code: str, period: int = 14) -> float:
        """RSI 계산"""
        try:
            # 최근 가격 데이터 조회 (캐시 또는 DB)
            prices = self._get_price_history(stock_code, period + 1)
            
            if len(prices) < period + 1:
                return 50  # 기본값
                
            # RSI 계산
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                diff = prices[i] - prices[i-1]
                if diff > 0:
                    gains.append(diff)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(diff))
                    
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100
                
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            print(f"[에러] RSI 계산 실패: {e}")
            return 50  # 기본값
            
    def calculate_ma(self, stock_code: str, period: int = 20) -> float:
        """이동평균 계산"""
        try:
            prices = self._get_price_history(stock_code, period)
            
            if len(prices) < period:
                return 0
                
            return np.mean(prices)
            
        except Exception as e:
            print(f"[에러] MA 계산 실패: {e}")
            return 0
            
    def get_average_volume(self, stock_code: str, period: int = 20) -> int:
        """평균 거래량 조회"""
        try:
            volumes = self._get_volume_history(stock_code, period)
            
            if not volumes:
                return 0
                
            return int(np.mean(volumes))
            
        except Exception as e:
            print(f"[에러] 평균 거래량 조회 실패: {e}")
            return 0
            
    def _get_price_history(self, stock_code: str, days: int) -> List[float]:
        """가격 히스토리 조회"""
        # 실제로는 DB에서 조회
        # 여기서는 더미 데이터 반환
        return [50000 + i * 100 for i in range(days)]
        
    def _get_volume_history(self, stock_code: str, days: int) -> List[int]:
        """거래량 히스토리 조회"""
        # 실제로는 DB에서 조회
        # 여기서는 더미 데이터 반환
        return [1000000 + i * 10000 for i in range(days)]
        
    def execute_strategy(self, strategy_id: str) -> Dict:
        """전략 실행"""
        try:
            # 전략 조회
            strategy = self.supabase.table('strategies').select('*').eq(
                'id', strategy_id
            ).single().execute()
            
            if not strategy.data:
                raise Exception("전략을 찾을 수 없습니다")
                
            strategy_data = strategy.data
            
            # 실행 로그 생성
            execution = {
                'strategy_id': strategy_id,
                'status': 'running',
                'execution_time': datetime.now().isoformat()
            }
            
            exec_result = self.supabase.table('strategy_executions').insert(
                execution
            ).execute()
            
            execution_id = exec_result.data[0]['id']
            
            # 대상 종목 스캔
            target_stocks = strategy_data.get('target_stocks', [])
            if not target_stocks:
                target_stocks = self.get_default_stocks()
                
            signals_generated = 0
            
            for stock_code in target_stocks:
                # 시장 데이터 조회
                market_data = self.get_market_data(stock_code)
                
                # 조건 평가
                if self.evaluate_conditions(strategy_data['conditions'], market_data):
                    # 신호 생성
                    signal = self.generate_signal(
                        strategy_id, 
                        execution_id,
                        stock_code, 
                        market_data
                    )
                    signals_generated += 1
                    
            # 실행 완료 업데이트
            self.supabase.table('strategy_executions').update({
                'status': 'completed',
                'scanned_stocks': len(target_stocks),
                'signals_generated': signals_generated
            }).eq('id', execution_id).execute()
            
            print(f"[전략실행] {strategy_data['name']} - 스캔: {len(target_stocks)}, 신호: {signals_generated}")
            
            return {
                'execution_id': execution_id,
                'scanned': len(target_stocks),
                'signals': signals_generated
            }
            
        except Exception as e:
            print(f"[에러] 전략 실행 실패: {e}")
            return None
            
    def generate_signal(self, strategy_id: str, execution_id: str, 
                       stock_code: str, market_data: Dict) -> Dict:
        """매매 신호 생성"""
        try:
            # 종목명 조회 (실제로는 API 또는 DB에서)
            stock_name = self.get_stock_name(stock_code)
            
            # 지표 계산
            indicators = {
                'rsi': self.calculate_rsi(stock_code),
                'ma20': self.calculate_ma(stock_code, 20),
                'ma60': self.calculate_ma(stock_code, 60),
                'volume_ratio': market_data['volume'] / self.get_average_volume(stock_code)
            }
            
            # 신호 강도 계산 (0~1)
            signal_strength = self.calculate_signal_strength(indicators)
            
            # 신호 저장
            signal = {
                'strategy_id': strategy_id,
                'execution_id': execution_id,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'signal_type': 'BUY',  # 또는 SELL
                'signal_strength': signal_strength,
                'current_price': market_data.get('current_price'),
                'volume': market_data.get('volume'),
                'indicators': indicators,
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('trading_signals').insert(signal).execute()
            
            print(f"[신호생성] {stock_name}({stock_code}) - {signal['signal_type']} (강도: {signal_strength:.2f})")
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"[에러] 신호 생성 실패: {e}")
            return None
            
    def calculate_signal_strength(self, indicators: Dict) -> float:
        """신호 강도 계산"""
        strength = 0.5  # 기본값
        
        # RSI 기반 강도
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            strength += 0.3
        elif rsi < 40:
            strength += 0.1
            
        # 볼륨 기반 강도
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 2:
            strength += 0.2
        elif volume_ratio > 1.5:
            strength += 0.1
            
        return min(1.0, strength)
        
    def get_market_data(self, stock_code: str) -> Dict:
        """시장 데이터 조회"""
        try:
            # 캐시에서 조회
            result = self.supabase.table('market_data_cache').select('*').eq(
                'stock_code', stock_code
            ).single().execute()
            
            if result.data:
                return result.data
            else:
                # 더미 데이터 반환
                return {
                    'stock_code': stock_code,
                    'current_price': 50000,
                    'volume': 1000000
                }
                
        except Exception as e:
            print(f"[에러] 시장 데이터 조회 실패: {e}")
            return {}
            
    def get_stock_name(self, stock_code: str) -> str:
        """종목명 조회"""
        # 실제로는 DB 또는 API에서 조회
        stock_names = {
            '005930': '삼성전자',
            '000660': 'SK하이닉스',
            '035720': '카카오',
            '035420': 'NAVER'
        }
        return stock_names.get(stock_code, stock_code)
        
    def get_default_stocks(self) -> List[str]:
        """기본 종목 리스트"""
        return ['005930', '000660', '035720', '035420']
        
    def get_strategy_performance(self, strategy_id: str) -> Dict:
        """전략 성과 조회"""
        try:
            # 포지션 조회
            positions = self.supabase.table('positions').select('*').eq(
                'strategy_id', strategy_id
            ).execute()
            
            total_profit = 0
            win_count = 0
            lose_count = 0
            
            for pos in positions.data:
                if not pos['is_active']:  # 청산된 포지션
                    pnl = pos.get('realized_pnl', 0)
                    total_profit += pnl
                    
                    if pnl > 0:
                        win_count += 1
                    elif pnl < 0:
                        lose_count += 1
                        
            total_trades = win_count + lose_count
            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'win_count': win_count,
                'lose_count': lose_count
            }
            
        except Exception as e:
            print(f"[에러] 성과 조회 실패: {e}")
            return {}


# 테스트 코드
if __name__ == "__main__":
    manager = StrategyExecutionManager()
    
    # 테스트 전략 생성
    test_strategy = {
        'name': 'RSI 과매도 전략',
        'description': 'RSI 30 이하에서 매수',
        'conditions': {
            'entry': {
                'rsi': {'operator': '<', 'value': 30},
                'volume': {'operator': '>', 'value': 'avg_volume * 1.5'}
            },
            'exit': {
                'profit_target': 5,
                'stop_loss': -3
            }
        },
        'position_size': 10,
        'max_positions': 3,
        'target_stocks': ['005930', '000660']
    }
    
    # 전략 생성 (실제 사용시 user_id 필요)
    # strategy = manager.create_strategy('user_id_here', test_strategy)
    
    print("전략 실행 관리자 준비 완료")