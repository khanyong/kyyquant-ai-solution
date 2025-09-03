"""
Supabase 데이터 저장 테스트 (키움 API 없이)
실제 키움 API 대신 모의 데이터를 생성하여 Supabase 저장 기능 테스트
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import random
import time

load_dotenv()

class SupabaseStorageTest:
    """Supabase 저장 기능 테스트"""
    
    def __init__(self):
        # Supabase 클라이언트 초기화
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        print(f"[초기화] Supabase URL: {os.getenv('SUPABASE_URL')[:30]}...")
        
    def test_connection(self):
        """연결 테스트"""
        try:
            # 간단한 쿼리로 연결 테스트
            result = self.supabase.table('strategies').select('id').limit(1).execute()
            print("[OK] Supabase 연결 성공")
            return True
        except Exception as e:
            print(f"[ERROR] Supabase 연결 실패: {e}")
            return False
    
    def create_test_tables(self):
        """필요한 테이블이 없으면 생성 (SQL 실행 필요)"""
        print("\n[정보] 필요한 테이블 구조:")
        tables = {
            'market_data_cache': ['stock_code', 'current_price', 'volume', 'fetched_at', 'expires_at'],
            'trading_signals': ['strategy_id', 'stock_code', 'signal_type', 'current_price', 'volume', 'created_at'],
            'orders': ['signal_id', 'strategy_id', 'stock_code', 'order_type', 'quantity', 'order_price', 'status', 'order_time'],
            'positions': ['stock_code', 'stock_name', 'quantity', 'avg_price', 'is_active'],
            'strategies': ['id', 'name', 'is_active', 'conditions', 'target_stocks', 'position_size', 'auto_execute']
        }
        
        for table, columns in tables.items():
            print(f"  - {table}: {', '.join(columns)}")
            
    def save_market_data(self):
        """시장 데이터 저장 테스트"""
        print("\n[테스트] 시장 데이터 저장...")
        
        test_stocks = [
            {'code': '005930', 'name': '삼성전자'},
            {'code': '000660', 'name': 'SK하이닉스'},
            {'code': '035420', 'name': 'NAVER'}
        ]
        
        for stock in test_stocks:
            try:
                # 모의 시장 데이터 생성
                market_data = {
                    'stock_code': stock['code'],
                    'current_price': random.randint(50000, 100000),
                    'volume': random.randint(100000, 1000000),
                    'fetched_at': datetime.now().isoformat(),
                    'expires_at': int(datetime.now().timestamp() + 60)
                }
                
                # 기존 데이터 확인
                existing = self.supabase.table('market_data_cache').select('*').eq(
                    'stock_code', stock['code']
                ).execute()
                
                if existing.data:
                    # 업데이트
                    result = self.supabase.table('market_data_cache').update(market_data).eq(
                        'stock_code', stock['code']
                    ).execute()
                    print(f"  [업데이트] {stock['name']}({stock['code']}): {market_data['current_price']:,}원")
                else:
                    # 신규 삽입
                    result = self.supabase.table('market_data_cache').insert(market_data).execute()
                    print(f"  [삽입] {stock['name']}({stock['code']}): {market_data['current_price']:,}원")
                    
            except Exception as e:
                print(f"  [에러] {stock['name']} 저장 실패: {e}")
                
    def save_test_strategy(self):
        """테스트 전략 저장"""
        print("\n[테스트] 전략 저장...")
        
        test_strategy = {
            'name': 'RSI 오버솔드 전략',
            'description': 'RSI 30 이하에서 매수',
            'is_active': True,
            'conditions': json.dumps({
                'entry': {'rsi': {'operator': '<', 'value': 30}},
                'exit': {'profit_target': 5, 'stop_loss': -3}
            }),
            'target_stocks': ['005930', '000660', '035420'],
            'position_size': 10,  # 10% of portfolio
            'auto_execute': False,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('strategies').insert(test_strategy).execute()
            print(f"  [OK] 전략 저장 성공: {test_strategy['name']}")
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            # 이미 존재하는 경우 조회
            existing = self.supabase.table('strategies').select('*').eq(
                'name', test_strategy['name']
            ).execute()
            if existing.data:
                print(f"  [정보] 전략이 이미 존재함: {test_strategy['name']}")
                return existing.data[0]['id']
            else:
                print(f"  [에러] 전략 저장 실패: {e}")
                return None
                
    def save_test_signal(self, strategy_id):
        """테스트 신호 저장"""
        print("\n[테스트] 거래 신호 저장...")
        
        if not strategy_id:
            print("  [에러] 전략 ID가 없습니다")
            return
            
        test_signal = {
            'strategy_id': strategy_id,
            'stock_code': '005930',
            'signal_type': 'BUY',
            'current_price': 72000,
            'volume': 500000,
            'rsi_value': 28.5,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('trading_signals').insert(test_signal).execute()
            print(f"  [OK] 신호 저장 성공: {test_signal['signal_type']} - 삼성전자 @ {test_signal['current_price']:,}원")
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"  [에러] 신호 저장 실패: {e}")
            return None
            
    def save_test_order(self, signal_id, strategy_id):
        """테스트 주문 저장"""
        print("\n[테스트] 주문 저장...")
        
        test_order = {
            'signal_id': signal_id,
            'strategy_id': strategy_id,
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'order_type': 'BUY',
            'quantity': 10,
            'order_price': 72000,
            'status': 'PENDING',
            'order_time': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('orders').insert(test_order).execute()
            print(f"  [OK] 주문 저장 성공: {test_order['stock_name']} {test_order['quantity']}주 @ {test_order['order_price']:,}원")
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"  [에러] 주문 저장 실패: {e}")
            return None
            
    def check_data_retrieval(self):
        """저장된 데이터 조회 테스트"""
        print("\n[테스트] 데이터 조회...")
        
        try:
            # 활성 전략 조회
            strategies = self.supabase.table('strategies').select('*').eq(
                'is_active', True
            ).execute()
            print(f"  [조회] 활성 전략: {len(strategies.data)}개")
            
            # 최근 신호 조회
            signals = self.supabase.table('trading_signals').select('*').order(
                'created_at', desc=True
            ).limit(5).execute()
            print(f"  [조회] 최근 신호: {len(signals.data)}개")
            
            # 시장 데이터 캐시 조회
            market_data = self.supabase.table('market_data_cache').select('*').execute()
            print(f"  [조회] 시장 데이터: {len(market_data.data)}개")
            
            # 주문 조회
            orders = self.supabase.table('orders').select('*').order(
                'order_time', desc=True
            ).limit(5).execute()
            print(f"  [조회] 최근 주문: {len(orders.data)}개")
            
        except Exception as e:
            print(f"  [에러] 데이터 조회 실패: {e}")
            
    def run_full_test(self):
        """전체 테스트 실행"""
        print("\n" + "="*50)
        print("Supabase 저장 기능 테스트 시작")
        print("="*50)
        
        # 1. 연결 테스트
        if not self.test_connection():
            return
            
        # 2. 테이블 구조 확인
        self.create_test_tables()
        
        # 3. 시장 데이터 저장
        self.save_market_data()
        
        # 4. 전략 저장
        strategy_id = self.save_test_strategy()
        
        # 5. 신호 저장
        signal_id = None
        if strategy_id:
            signal_id = self.save_test_signal(strategy_id)
            
        # 6. 주문 저장
        if signal_id and strategy_id:
            self.save_test_order(signal_id, strategy_id)
            
        # 7. 데이터 조회
        self.check_data_retrieval()
        
        print("\n" + "="*50)
        print("테스트 완료")
        print("="*50)


if __name__ == "__main__":
    tester = SupabaseStorageTest()
    tester.run_full_test()