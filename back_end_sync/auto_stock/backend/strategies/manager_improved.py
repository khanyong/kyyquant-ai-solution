"""
개선된 전략 관리자 - Supabase 우선
"""

from typing import Dict, Any, Optional
import os
from supabase import create_client

from .base import BaseStrategy

class StrategyManager:
    """전략 관리자 - Supabase 우선 버전"""

    def __init__(self, use_supabase_first=True):
        self.strategies = {}
        self.use_supabase_first = use_supabase_first
        self._load_builtin_strategies()
        self._init_database()

    def _load_builtin_strategies(self):
        """내장 전략 로드 (폴백용)"""
        try:
            from .technical.golden_cross import GoldenCrossStrategy
            from .technical.rsi_oversold import RSIOversoldStrategy
            from .technical.bollinger_band import BollingerBandStrategy

            self.register_strategy('golden_cross', GoldenCrossStrategy)
            self.register_strategy('rsi_oversold', RSIOversoldStrategy)
            self.register_strategy('bollinger_band', BollingerBandStrategy)
            print(f"Loaded {len(self.strategies)} fallback strategies")
        except Exception as e:
            print(f"Warning: Could not load builtin strategies: {e}")

    def _init_database(self):
        """데이터베이스 연결 초기화"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            if url and key:
                self.supabase = create_client(url, key)
                print("Supabase connected for strategy management")
            else:
                self.supabase = None
                print("Running without database - using local strategies only")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.supabase = None

    def register_strategy(self, strategy_id: str, strategy_class):
        """전략 등록 (폴백용)"""
        self.strategies[strategy_id] = strategy_class

    async def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        전략 가져오기 - 개선된 버전

        Priority:
        1. Supabase (if use_supabase_first=True)
        2. Local files (fallback)
        """

        # Supabase 우선 모드
        if self.use_supabase_first and self.supabase:
            try:
                # Supabase에서 먼저 확인
                response = self.supabase.table('strategies').select('*').eq('id', strategy_id).single().execute()
                if response.data:
                    print(f"Strategy '{strategy_id}' loaded from Supabase")
                    return self._validate_strategy(response.data)
            except Exception as e:
                print(f"Supabase fetch failed for '{strategy_id}': {e}")
                # 실패 시 로컬로 폴백

        # 로컬 전략 확인 (폴백 또는 Supabase 미사용 시)
        if strategy_id in self.strategies:
            print(f"Strategy '{strategy_id}' loaded from local files")
            strategy_class = self.strategies[strategy_id]
            instance = strategy_class(strategy_id)
            return {
                'id': strategy_id,
                'name': instance.name,
                'config': {
                    'indicators': instance.get_required_indicators(),
                    'buyConditions': instance.get_buy_conditions(),
                    'sellConditions': instance.get_sell_conditions()
                },
                'source': 'local'  # 소스 표시
            }

        print(f"Strategy '{strategy_id}' not found")
        return None

    def _validate_strategy(self, strategy_data: Dict) -> Dict:
        """전략 데이터 검증 및 정규화"""
        # 필수 필드 확인
        required_fields = ['id', 'name', 'config']
        for field in required_fields:
            if field not in strategy_data:
                raise ValueError(f"Missing required field: {field}")

        # config 검증
        config = strategy_data.get('config', {})
        if not config.get('buyConditions') or not config.get('sellConditions'):
            raise ValueError("Strategy must have buy and sell conditions")

        # 소스 표시 추가
        strategy_data['source'] = 'supabase'

        return strategy_data

    async def sync_strategies(self):
        """
        로컬 전략을 Supabase로 동기화
        (초기 설정 시 한 번만 실행)
        """
        if not self.supabase:
            print("Cannot sync: No database connection")
            return

        for strategy_id, strategy_class in self.strategies.items():
            try:
                instance = strategy_class(strategy_id)
                strategy_data = {
                    'id': f'system_{strategy_id}',  # 시스템 전략 구분
                    'name': instance.name,
                    'description': f'System strategy: {instance.name}',
                    'user_id': 'system',  # 시스템 소유
                    'is_public': True,    # 모든 사용자 사용 가능
                    'config': {
                        'indicators': instance.get_required_indicators(),
                        'buyConditions': instance.get_buy_conditions(),
                        'sellConditions': instance.get_sell_conditions()
                    },
                    'created_at': 'now()',
                    'updated_at': 'now()'
                }

                # Upsert (insert or update)
                response = self.supabase.table('strategies').upsert(strategy_data).execute()
                print(f"Synced strategy '{strategy_id}' to Supabase")

            except Exception as e:
                print(f"Failed to sync strategy '{strategy_id}': {e}")

    async def list_strategies(self, user_id: Optional[str] = None) -> list:
        """전략 목록 조회 - 개선된 버전"""
        strategies = []

        # Supabase에서 조회
        if self.supabase:
            try:
                query = self.supabase.table('strategies').select('id, name, user_id, is_public')

                # 사용자 전략 + 공개 전략
                if user_id:
                    # 복잡한 쿼리: (user_id = ? OR is_public = true)
                    response = query.or_(f'user_id.eq.{user_id},is_public.eq.true').execute()
                else:
                    # 공개 전략만
                    response = query.eq('is_public', True).execute()

                for item in response.data:
                    strategies.append({
                        'id': item['id'],
                        'name': item['name'],
                        'type': 'system' if item['user_id'] == 'system' else 'custom',
                        'source': 'supabase'
                    })

            except Exception as e:
                print(f"Failed to list strategies from Supabase: {e}")

        # 로컬 전략 추가 (Supabase 실패 시 폴백)
        if not strategies:
            for strategy_id in self.strategies:
                strategies.append({
                    'id': strategy_id,
                    'name': strategy_id.replace('_', ' ').title(),
                    'type': 'system',
                    'source': 'local'
                })

        return strategies