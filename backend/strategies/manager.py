"""
전략 관리자
"""

from typing import Dict, Any, Optional
import os
import sys
from supabase import create_client

from .base import BaseStrategy

# 전략 임포트
from .technical.golden_cross import GoldenCrossStrategy
from .technical.rsi_oversold import RSIOversoldStrategy
from .technical.bollinger_band import BollingerBandStrategy

class StrategyManager:
    """전략 관리자"""

    def __init__(self):
        self.strategies = {}
        self._load_builtin_strategies()
        self._init_database()

    def _load_builtin_strategies(self):
        """내장 전략 로드"""
        # 기본 제공 전략들
        self.register_strategy('golden_cross', GoldenCrossStrategy)
        self.register_strategy('rsi_oversold', RSIOversoldStrategy)
        self.register_strategy('bollinger_band', BollingerBandStrategy)
        print(f"Loaded {len(self.strategies)} built-in strategies")

    def _init_database(self):
        """데이터베이스 연결 초기화"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')

            # 디버깅: 환경변수 확인
            print(f"DEBUG: SUPABASE_URL = {url[:30]}..." if url else "DEBUG: SUPABASE_URL is None")
            print(f"DEBUG: SUPABASE_KEY = {key[:30]}..." if key else "DEBUG: SUPABASE_KEY is None")

            if url and key:
                self.supabase = create_client(url, key)
                print("[OK] Supabase connected for strategy management")
            else:
                self.supabase = None
                print(f"[ERROR] Running without database connection - URL: {bool(url)}, KEY: {bool(key)}")
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            self.supabase = None

    def register_strategy(self, strategy_id: str, strategy_class):
        """전략 등록"""
        self.strategies[strategy_id] = strategy_class

    async def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        전략 가져오기
        1. 내장 전략 확인
        2. 데이터베이스에서 사용자 전략 확인
        """
        # 내장 전략 확인
        if strategy_id in self.strategies:
            strategy_class = self.strategies[strategy_id]
            instance = strategy_class(strategy_id)
            return {
                'id': strategy_id,
                'name': instance.name,
                'config': {
                    'indicators': instance.get_required_indicators(),
                    'buyConditions': instance.get_buy_conditions(),
                    'sellConditions': instance.get_sell_conditions()
                }
            }

        # 데이터베이스에서 확인
        if self.supabase:
            try:
                print(f"[DEBUG] Fetching strategy {strategy_id} from database...")
                response = self.supabase.table('strategies').select('*').eq('id', strategy_id).single().execute()
                if response.data:
                    print(f"[OK] Found strategy in database: {response.data.get('name', 'Unknown')}")
                    return response.data
                else:
                    print(f"[WARNING] Strategy {strategy_id} not found in database")
            except Exception as e:
                print(f"[ERROR] Failed to fetch strategy from database: {e}")
        else:
            print(f"[WARNING] Cannot fetch strategy - no database connection")

        return None

    async def save_strategy(self, strategy: Dict[str, Any]) -> bool:
        """전략 저장"""
        if not self.supabase:
            print("Cannot save strategy: No database connection")
            return False

        try:
            response = self.supabase.table('strategies').upsert(strategy).execute()
            return True
        except Exception as e:
            print(f"Failed to save strategy: {e}")
            return False

    async def list_strategies(self, user_id: Optional[str] = None) -> list:
        """전략 목록 조회"""
        strategies = []

        # 내장 전략 추가
        for strategy_id in self.strategies:
            strategies.append({
                'id': strategy_id,
                'name': strategy_id.replace('_', ' ').title(),
                'type': 'builtin'
            })

        # 사용자 전략 추가
        if self.supabase and user_id:
            try:
                response = self.supabase.table('strategies').select('id, name').eq('user_id', user_id).execute()
                for item in response.data:
                    strategies.append({
                        'id': item['id'],
                        'name': item['name'],
                        'type': 'custom'
                    })
            except Exception as e:
                print(f"Failed to list user strategies: {e}")

        return strategies