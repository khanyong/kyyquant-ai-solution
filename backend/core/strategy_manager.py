"""
전략을 Supabase에 저장하고 관리하는 모듈
"""
import json
import importlib.util
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
from database.database_supabase import SupabaseDatabase

class CloudStrategyManager:
    """클라우드 기반 전략 관리자"""
    
    def __init__(self):
        self.db = SupabaseDatabase()
        self.init_strategy_table()
        self.loaded_strategies = {}
    
    def init_strategy_table(self):
        """전략 저장용 테이블 생성 SQL (Supabase에서 실행)"""
        init_sql = """
        -- 전략 저장 테이블
        CREATE TABLE IF NOT EXISTS strategies (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            code TEXT NOT NULL,  -- 전략 Python 코드
            parameters JSONB,     -- 전략 파라미터
            description TEXT,
            is_active BOOLEAN DEFAULT FALSE,
            performance_metrics JSONB,  -- 백테스트 결과 등
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            user_id UUID REFERENCES auth.users(id),
            UNIQUE(name, version, user_id)
        );
        
        -- 전략 실행 히스토리
        CREATE TABLE IF NOT EXISTS strategy_executions (
            id SERIAL PRIMARY KEY,
            strategy_id INTEGER REFERENCES strategies(id),
            start_time TIMESTAMPTZ NOT NULL,
            end_time TIMESTAMPTZ,
            status TEXT NOT NULL,  -- running, completed, failed
            signals_generated INTEGER DEFAULT 0,
            orders_placed INTEGER DEFAULT 0,
            profit_loss DECIMAL(15, 2),
            execution_log JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- 전략 백테스트 결과
        CREATE TABLE IF NOT EXISTS backtests (
            id SERIAL PRIMARY KEY,
            strategy_id INTEGER REFERENCES strategies(id),
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            initial_capital DECIMAL(15, 2),
            final_capital DECIMAL(15, 2),
            total_return DECIMAL(10, 4),
            sharpe_ratio DECIMAL(10, 4),
            max_drawdown DECIMAL(10, 4),
            win_rate DECIMAL(5, 2),
            total_trades INTEGER,
            parameters JSONB,
            detailed_results JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX idx_strategies_user_active ON strategies(user_id, is_active);
        CREATE INDEX idx_executions_strategy ON strategy_executions(strategy_id);
        """
        print("Strategy tables SQL ready. Execute in Supabase Dashboard.")
    
    def save_strategy(self, name: str, code: str, parameters: Dict[str, Any] = None, 
                     description: str = None) -> Dict[str, Any]:
        """
        전략을 Supabase에 저장
        
        Args:
            name: 전략 이름
            code: Python 전략 코드
            parameters: 전략 파라미터
            description: 전략 설명
        """
        # 버전 생성 (코드 해시 기반)
        version = hashlib.md5(code.encode()).hexdigest()[:8]
        
        strategy_data = {
            'name': name,
            'version': version,
            'code': code,
            'parameters': parameters or {},
            'description': description,
            'updated_at': datetime.now().isoformat()
        }
        
        # 사용자 ID 추가 (인증된 경우)
        if hasattr(self.db.client.auth, 'user') and self.db.client.auth.user:
            strategy_data['user_id'] = self.db.client.auth.user.id
        
        try:
            # Upsert (동일 이름/버전이 있으면 업데이트)
            response = self.db.client.table('strategies').upsert(
                strategy_data,
                on_conflict='name,version,user_id'
            ).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving strategy: {e}")
            return None
    
    def load_strategy(self, strategy_id: int = None, name: str = None, 
                     version: str = None) -> Any:
        """
        Supabase에서 전략 로드 및 실행
        
        Args:
            strategy_id: 전략 ID
            name: 전략 이름
            version: 전략 버전
        """
        try:
            # 전략 조회
            query = self.db.client.table('strategies').select('*')
            
            if strategy_id:
                query = query.eq('id', strategy_id)
            elif name:
                query = query.eq('name', name)
                if version:
                    query = query.eq('version', version)
                else:
                    # 최신 버전 가져오기
                    query = query.order('created_at', desc=True).limit(1)
            
            response = query.execute()
            
            if not response.data:
                raise ValueError(f"Strategy not found")
            
            strategy_data = response.data[0]
            
            # 코드를 동적으로 로드
            strategy_module = self._load_code_as_module(
                strategy_data['code'],
                strategy_data['name']
            )
            
            # 전략 클래스 인스턴스 생성
            if hasattr(strategy_module, 'Strategy'):
                strategy_class = strategy_module.Strategy
            else:
                # 기본 전략 클래스 찾기
                for name, obj in strategy_module.__dict__.items():
                    if 'Strategy' in name:
                        strategy_class = obj
                        break
                else:
                    raise ValueError("No Strategy class found in code")
            
            # 파라미터와 함께 인스턴스 생성
            strategy_instance = strategy_class(parameters=strategy_data['parameters'])
            
            # 캐시에 저장
            self.loaded_strategies[strategy_data['id']] = strategy_instance
            
            return strategy_instance
            
        except Exception as e:
            print(f"Error loading strategy: {e}")
            return None
    
    def _load_code_as_module(self, code: str, module_name: str):
        """Python 코드 문자열을 모듈로 동적 로드"""
        # 모듈 스펙 생성
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        
        # 코드 실행
        exec(code, module.__dict__)
        
        # sys.modules에 추가 (임포트 가능하게)
        sys.modules[module_name] = module
        
        return module
    
    def get_all_strategies(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """모든 전략 목록 조회"""
        try:
            query = self.db.client.table('strategies').select('*')
            
            if active_only:
                query = query.eq('is_active', True)
            
            if hasattr(self.db.client.auth, 'user') and self.db.client.auth.user:
                query = query.eq('user_id', self.db.client.auth.user.id)
            
            response = query.order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting strategies: {e}")
            return []
    
    def activate_strategy(self, strategy_id: int):
        """전략 활성화"""
        try:
            # 먼저 모든 전략 비활성화
            self.db.client.table('strategies').update(
                {'is_active': False}
            ).execute()
            
            # 선택한 전략만 활성화
            response = self.db.client.table('strategies').update(
                {'is_active': True}
            ).eq('id', strategy_id).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error activating strategy: {e}")
            return None
    
    def save_backtest_result(self, strategy_id: int, results: Dict[str, Any]):
        """백테스트 결과 저장"""
        try:
            backtest_data = {
                'strategy_id': strategy_id,
                'start_date': results['start_date'],
                'end_date': results['end_date'],
                'initial_capital': results['initial_capital'],
                'final_capital': results['final_capital'],
                'total_return': results['total_return'],
                'sharpe_ratio': results.get('sharpe_ratio', 0),
                'max_drawdown': results.get('max_drawdown', 0),
                'win_rate': results.get('win_rate', 0),
                'total_trades': results.get('trades', 0),
                'parameters': results.get('parameters', {}),
                'detailed_results': results
            }
            
            response = self.db.client.table('backtests').insert(backtest_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving backtest: {e}")
            return None
    
    def start_execution(self, strategy_id: int) -> int:
        """전략 실행 시작 기록"""
        try:
            execution_data = {
                'strategy_id': strategy_id,
                'start_time': datetime.now().isoformat(),
                'status': 'running'
            }
            
            response = self.db.client.table('strategy_executions').insert(
                execution_data
            ).execute()
            
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Error starting execution: {e}")
            return None
    
    def update_execution(self, execution_id: int, **kwargs):
        """전략 실행 상태 업데이트"""
        try:
            self.db.client.table('strategy_executions').update(
                kwargs
            ).eq('id', execution_id).execute()
        except Exception as e:
            print(f"Error updating execution: {e}")


# 전략 코드 템플릿
STRATEGY_TEMPLATE = '''
"""
전략 이름: {name}
설명: {description}
생성일: {created_at}
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

class Strategy:
    """사용자 정의 전략"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.name = "{name}"
        self.parameters = parameters or {{}}
        
    def calculate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        거래 신호 계산
        
        Args:
            data: OHLCV 데이터프레임
            
        Returns:
            신호 딕셔너리 {{'type': 'buy/sell/hold', 'strength': 0-1, 'price': float}}
        """
        # 여기에 전략 로직 구현
        if len(data) < 20:
            return {{'type': 'hold', 'strength': 0}}
        
        # 예시: 단순 이동평균 크로스
        sma_short = data['close'].rolling(window=5).mean().iloc[-1]
        sma_long = data['close'].rolling(window=20).mean().iloc[-1]
        current_price = data['close'].iloc[-1]
        
        if sma_short > sma_long:
            return {{
                'type': 'buy',
                'strength': 0.8,
                'price': current_price
            }}
        elif sma_short < sma_long:
            return {{
                'type': 'sell',
                'strength': 0.8,
                'price': current_price
            }}
        else:
            return {{'type': 'hold', 'strength': 0}}
'''


# 사용 예시
def example_usage():
    """전략 저장 및 로드 예시"""
    manager = CloudStrategyManager()
    
    # 1. 새 전략 생성 및 저장
    strategy_code = STRATEGY_TEMPLATE.format(
        name="MA_Cross_Strategy",
        description="이동평균선 교차 전략",
        created_at=datetime.now().isoformat()
    )
    
    saved_strategy = manager.save_strategy(
        name="MA_Cross_Strategy",
        code=strategy_code,
        parameters={
            'short_period': 5,
            'long_period': 20,
            'threshold': 0.02
        },
        description="5일/20일 이동평균선 교차 전략"
    )
    
    print(f"Strategy saved with ID: {saved_strategy['id']}")
    
    # 2. 전략 로드 및 실행
    strategy = manager.load_strategy(name="MA_Cross_Strategy")
    
    # 3. 시뮬레이션 데이터로 신호 생성
    sample_data = pd.DataFrame({
        'close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 3,
        'volume': [1000] * 30
    })
    
    signal = strategy.calculate_signal(sample_data)
    print(f"Generated signal: {signal}")
    
    # 4. 백테스트 결과 저장
    backtest_results = {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 1000000,
        'final_capital': 1150000,
        'total_return': 0.15,
        'sharpe_ratio': 1.5,
        'max_drawdown': 0.08,
        'win_rate': 60,
        'trades': 50
    }
    
    manager.save_backtest_result(saved_strategy['id'], backtest_results)
    
    # 5. 전략 활성화
    manager.activate_strategy(saved_strategy['id'])
    
    print("Strategy management complete!")

if __name__ == "__main__":
    example_usage()