"""
전략 설정 관리자 - 모든 전략 요소를 체계적으로 관리
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from core.strategy_config_schema import StrategyConfig
from database.database_supabase import SupabaseDatabase

class StrategyConfigManager:
    """전략 설정 통합 관리자"""
    
    def __init__(self):
        self.db = SupabaseDatabase()
    
    def create_strategy(self, config: StrategyConfig) -> Dict[str, Any]:
        """
        새 전략 생성 및 저장
        모든 설정값이 strategies_v2 테이블에 저장됨
        """
        strategy_data = {
            # 기본 정보
            'name': config.name,
            'version': config.version,
            'description': config.description,
            'author': config.author,
            'strategy_type': config.strategy_type,
            'timeframe': config.timeframe,
            'universe': config.universe,
            
            # 상태
            'is_active': config.is_active,
            'is_test_mode': config.is_test_mode,
            'auto_trade_enabled': config.auto_trade_enabled,
            
            # 상세 설정 (JSON으로 저장)
            'indicators': config.indicators.dict(),
            'entry_conditions': config.entry_conditions.dict(),
            'exit_conditions': config.exit_conditions.dict(),
            'risk_management': config.risk_management.dict(),
            'backtest_settings': config.backtest_settings.dict(),
            'notifications': config.notifications.dict(),
            'custom_parameters': config.custom_parameters,
            
            # 성과 메트릭
            'performance_metrics': config.performance_metrics,
            
            # 타임스탬프
            'updated_at': datetime.now().isoformat()
        }
        
        # 사용자 ID 추가
        if hasattr(self.db.client.auth, 'user') and self.db.client.auth.user:
            strategy_data['user_id'] = self.db.client.auth.user.id
        
        try:
            response = self.db.client.table('strategies_v2').insert(strategy_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating strategy: {e}")
            return None
    
    def get_strategy_config(self, strategy_id: int) -> Optional[StrategyConfig]:
        """전략 설정 조회"""
        try:
            response = self.db.client.table('strategies_v2').select('*').eq('id', strategy_id).execute()
            
            if response.data:
                data = response.data[0]
                # JSON 필드를 다시 객체로 변환
                return StrategyConfig(
                    name=data['name'],
                    version=data['version'],
                    description=data['description'],
                    author=data['author'],
                    strategy_type=data['strategy_type'],
                    timeframe=data['timeframe'],
                    universe=data['universe'],
                    is_active=data['is_active'],
                    is_test_mode=data['is_test_mode'],
                    auto_trade_enabled=data['auto_trade_enabled'],
                    indicators=data['indicators'],
                    entry_conditions=data['entry_conditions'],
                    exit_conditions=data['exit_conditions'],
                    risk_management=data['risk_management'],
                    backtest_settings=data['backtest_settings'],
                    notifications=data['notifications'],
                    custom_parameters=data['custom_parameters'],
                    performance_metrics=data['performance_metrics']
                )
            return None
        except Exception as e:
            print(f"Error getting strategy config: {e}")
            return None
    
    def update_strategy_config(self, strategy_id: int, updates: Dict[str, Any]) -> bool:
        """전략 설정 업데이트"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            response = self.db.client.table('strategies_v2').update(updates).eq('id', strategy_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating strategy: {e}")
            return False
    
    def log_execution(self, strategy_id: int, execution_data: Dict[str, Any]):
        """전략 실행 로그 저장"""
        log_data = {
            'strategy_id': strategy_id,
            'execution_time': datetime.now().isoformat(),
            'market_data': execution_data.get('market_data', {}),
            'indicator_values': execution_data.get('indicators', {}),
            'entry_conditions_met': execution_data.get('entry_conditions', {}),
            'exit_conditions_met': execution_data.get('exit_conditions', {}),
            'risk_checks_passed': execution_data.get('risk_checks', {}),
            'signal_generated': execution_data.get('signal', 'hold'),
            'signal_strength': execution_data.get('signal_strength', 0),
            'action_taken': execution_data.get('action', 'none'),
            'action_reason': execution_data.get('reason', ''),
            'order_placed': execution_data.get('order_placed', False),
            'order_details': execution_data.get('order_details', {})
        }
        
        try:
            self.db.client.table('strategy_execution_logs').insert(log_data).execute()
        except Exception as e:
            print(f"Error logging execution: {e}")
    
    def get_all_strategies(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """모든 전략 목록 조회 (설정 포함)"""
        try:
            query = self.db.client.table('strategies_v2').select('*')
            
            if active_only:
                query = query.eq('is_active', True)
            
            if hasattr(self.db.client.auth, 'user') and self.db.client.auth.user:
                query = query.eq('user_id', self.db.client.auth.user.id)
            
            response = query.order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting strategies: {e}")
            return []
    
    def get_strategy_performance(self, strategy_id: int) -> Dict[str, Any]:
        """전략 성과 조회"""
        try:
            # 전략 정보
            strategy_response = self.db.client.table('strategies_v2').select(
                'name, version, performance_metrics'
            ).eq('id', strategy_id).execute()
            
            if not strategy_response.data:
                return {}
            
            strategy = strategy_response.data[0]
            
            # 최근 실행 로그
            logs_response = self.db.client.table('strategy_execution_logs').select(
                'execution_time, signal_generated, action_taken'
            ).eq('strategy_id', strategy_id).order(
                'execution_time', desc=True
            ).limit(100).execute()
            
            # 통계 계산
            logs = logs_response.data if logs_response.data else []
            total_signals = len(logs)
            buy_signals = sum(1 for log in logs if log['signal_generated'] == 'buy')
            sell_signals = sum(1 for log in logs if log['signal_generated'] == 'sell')
            orders_placed = sum(1 for log in logs if log['action_taken'] != 'none')
            
            return {
                'strategy_name': strategy['name'],
                'version': strategy['version'],
                'performance_metrics': strategy['performance_metrics'],
                'recent_activity': {
                    'total_signals': total_signals,
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'orders_placed': orders_placed,
                    'last_execution': logs[0]['execution_time'] if logs else None
                }
            }
        except Exception as e:
            print(f"Error getting performance: {e}")
            return {}
    
    def clone_strategy(self, strategy_id: int, new_name: str) -> Optional[int]:
        """전략 복제"""
        try:
            # 원본 전략 조회
            original = self.get_strategy_config(strategy_id)
            if not original:
                return None
            
            # 새 전략 생성
            original.name = new_name
            original.version = "1.0.0"
            original.is_active = False
            original.created_at = datetime.now()
            original.updated_at = datetime.now()
            
            new_strategy = self.create_strategy(original)
            return new_strategy['id'] if new_strategy else None
        except Exception as e:
            print(f"Error cloning strategy: {e}")
            return None
    
    def export_strategy(self, strategy_id: int) -> str:
        """전략을 JSON으로 내보내기"""
        try:
            config = self.get_strategy_config(strategy_id)
            if config:
                return config.json(indent=2)
            return "{}"
        except Exception as e:
            print(f"Error exporting strategy: {e}")
            return "{}"
    
    def import_strategy(self, json_str: str) -> Optional[int]:
        """JSON에서 전략 가져오기"""
        try:
            config = StrategyConfig.parse_raw(json_str)
            new_strategy = self.create_strategy(config)
            return new_strategy['id'] if new_strategy else None
        except Exception as e:
            print(f"Error importing strategy: {e}")
            return None


# 사용 예시
def example_usage():
    """전략 설정 관리 예시"""
    manager = StrategyConfigManager()
    
    # 1. 새 전략 생성 (모든 설정 포함)
    from core.strategy_config_schema import (
        StrategyConfig, IndicatorConfig, EntryConditions, 
        ExitConditions, RiskManagement, BacktestSettings
    )
    
    config = StrategyConfig(
        name="Advanced Momentum Strategy",
        version="1.0.0",
        description="고급 모멘텀 전략 with 리스크 관리",
        author="트레이더",
        strategy_type="momentum",
        timeframe="1d",
        universe=["005930", "000660", "035720"],  # 삼성전자, SK하이닉스, 카카오
        
        # 지표 설정
        indicators=IndicatorConfig(
            rsi_enabled=True,
            rsi_period=14,
            rsi_oversold=25,
            rsi_overbought=75,
            macd_enabled=True,
            bb_enabled=True,
            volume_enabled=True,
            volume_ratio_threshold=2.0
        ),
        
        # 진입 조건
        entry_conditions=EntryConditions(
            use_trend_confirmation=True,
            buy_signals_required=3,
            buy_rsi_max=65,
            min_volume_ratio=1.5,
            time_filter_enabled=True,
            allowed_hours=[9, 10, 11, 13, 14]
        ),
        
        # 청산 조건  
        exit_conditions=ExitConditions(
            stop_loss_enabled=True,
            stop_loss_percent=3.0,
            take_profit_enabled=True,
            take_profit_percent=10.0,
            trailing_stop_enabled=True,
            trailing_stop_percent=2.0,
            exit_on_signal_reverse=True
        ),
        
        # 리스크 관리
        risk_management=RiskManagement(
            position_sizing_method="fixed_percent",
            fixed_position_percent=10.0,
            max_positions=3,
            daily_loss_limit=2.0,
            daily_trade_limit=5,
            volatility_filter=True,
            max_volatility=0.03
        ),
        
        # 백테스트 설정
        backtest_settings=BacktestSettings(
            initial_capital=10000000,
            start_date="2023-01-01",
            end_date="2024-12-31",
            commission_rate=0.00015
        )
    )
    
    # 전략 저장
    new_strategy = manager.create_strategy(config)
    print(f"Strategy created with ID: {new_strategy['id']}")
    
    # 2. 전략 실행 로그
    execution_log = {
        'market_data': {'price': 70000, 'volume': 1000000},
        'indicators': {
            'rsi': 45,
            'macd': 0.5,
            'volume_ratio': 1.8
        },
        'entry_conditions': {
            'trend_confirmed': True,
            'volume_ok': True,
            'rsi_ok': True
        },
        'signal': 'buy',
        'signal_strength': 0.8,
        'action': 'order_placed',
        'reason': 'All conditions met',
        'order_placed': True,
        'order_details': {
            'type': 'limit',
            'price': 70000,
            'quantity': 10
        }
    }
    
    manager.log_execution(new_strategy['id'], execution_log)
    
    # 3. 전략 성과 조회
    performance = manager.get_strategy_performance(new_strategy['id'])
    print(f"Strategy Performance: {json.dumps(performance, indent=2)}")
    
    # 4. 전략 내보내기
    exported = manager.export_strategy(new_strategy['id'])
    print(f"Exported strategy: {exported[:200]}...")
    
    print("\nAll strategy settings are stored in Supabase!")

if __name__ == "__main__":
    example_usage()