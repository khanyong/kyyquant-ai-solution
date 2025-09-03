"""
전략 및 신호 저장 테스트
strategies 테이블에 실제 데이터 저장
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import random

load_dotenv()

class StrategyStorageTest:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
    def create_sample_strategy(self):
        """샘플 전략 생성 및 저장"""
        print("\n=== 전략 저장 테스트 ===\n")
        
        # 먼저 사용자 조회 (프로필에서 첫 번째 사용자 가져오기)
        try:
            profiles = self.supabase.table('profiles').select('id').limit(1).execute()
            if profiles.data:
                user_id = profiles.data[0]['id']
                print(f"[정보] 사용자 ID: {user_id}")
            else:
                print("[에러] 사용자를 찾을 수 없습니다")
                return None
        except Exception as e:
            print(f"[에러] 사용자 조회 실패: {e}")
            return None
        
        # 전략 데이터
        strategy = {
            'user_id': user_id,
            'name': f'RSI 오버솔드 전략_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'RSI 30 이하에서 매수, 70 이상에서 매도',
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            # 전략 저장
            result = self.supabase.table('strategies').insert(strategy).execute()
            
            if result.data:
                strategy_id = result.data[0]['id']
                print(f"[성공] 전략 저장 완료")
                print(f"  - ID: {strategy_id}")
                print(f"  - 이름: {strategy['name']}")
                print(f"  - 활성: {strategy['is_active']}")
                return strategy_id
            else:
                print("[실패] 전략 저장 실패")
                return None
                
        except Exception as e:
            print(f"[에러] 전략 저장 중 오류: {e}")
            return None
            
    def create_sample_signal(self, strategy_id):
        """샘플 신호 생성 및 저장"""
        print("\n=== 신호 저장 테스트 ===\n")
        
        if not strategy_id:
            print("[에러] 전략 ID가 없습니다")
            return None
            
        # 샘플 주식 목록
        stocks = [
            {'code': '005930', 'name': '삼성전자'},
            {'code': '000660', 'name': 'SK하이닉스'},
            {'code': '035420', 'name': 'NAVER'}
        ]
        
        stock = random.choice(stocks)
        
        signal = {
            'strategy_id': strategy_id,
            'stock_code': stock['code'],
            'stock_name': stock['name'],
            'signal_type': random.choice(['BUY', 'SELL']),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('trading_signals').insert(signal).execute()
            
            if result.data:
                signal_id = result.data[0]['id']
                print(f"[성공] 신호 저장 완료")
                print(f"  - ID: {signal_id}")
                print(f"  - 종목: {signal['stock_name']}({signal['stock_code']})")
                print(f"  - 신호: {signal['signal_type']}")
                return signal_id
            else:
                print("[실패] 신호 저장 실패")
                return None
                
        except Exception as e:
            print(f"[에러] 신호 저장 중 오류: {e}")
            return None
            
    def create_sample_order(self, strategy_id, signal_id):
        """샘플 주문 생성 및 저장"""
        print("\n=== 주문 저장 테스트 ===\n")
        
        if not strategy_id:
            print("[에러] 전략 ID가 없습니다")
            return None
            
        order = {
            'strategy_id': strategy_id,
            'stock_code': '005930',
            'stock_name': '삼성전자',  
            'order_type': 'BUY',
            'quantity': 10,
            'order_price': 72000,
            'status': 'PENDING',
            'created_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('orders').insert(order).execute()
            
            if result.data:
                order_id = result.data[0]['id']
                print(f"[성공] 주문 저장 완료")
                print(f"  - ID: {order_id}")
                print(f"  - 종목: {order['stock_name']}")
                print(f"  - 수량: {order['quantity']}주")
                print(f"  - 가격: {order['order_price']:,}원")
                return order_id
            else:
                print("[실패] 주문 저장 실패")
                return None
                
        except Exception as e:
            print(f"[에러] 주문 저장 중 오류: {e}")
            return None
            
    def list_all_strategies(self):
        """모든 전략 목록 조회"""
        print("\n=== 저장된 전략 목록 ===\n")
        
        try:
            result = self.supabase.table('strategies').select('*').execute()
            
            if result.data:
                print(f"총 {len(result.data)}개 전략")
                for i, strategy in enumerate(result.data, 1):
                    print(f"\n{i}. {strategy.get('name', 'No name')}")
                    print(f"   - ID: {strategy.get('id')}")
                    print(f"   - 활성: {strategy.get('is_active', False)}")
                    print(f"   - 생성: {strategy.get('created_at', 'Unknown')}")
            else:
                print("저장된 전략이 없습니다")
                
        except Exception as e:
            print(f"[에러] 전략 조회 중 오류: {e}")
            
    def list_recent_signals(self):
        """최근 신호 목록 조회"""
        print("\n=== 최근 신호 목록 ===\n")
        
        try:
            result = self.supabase.table('trading_signals').select('*').limit(10).execute()
            
            if result.data:
                print(f"최근 {len(result.data)}개 신호")
                for i, signal in enumerate(result.data, 1):
                    print(f"\n{i}. {signal.get('signal_type', 'Unknown')} - {signal.get('stock_name', '')}({signal.get('stock_code', '')})")
                    print(f"   - ID: {signal.get('id')}")
                    print(f"   - 시간: {signal.get('timestamp', 'Unknown')}")
            else:
                print("저장된 신호가 없습니다")
                
        except Exception as e:
            print(f"[에러] 신호 조회 중 오류: {e}")
            
    def run_test(self):
        """전체 테스트 실행"""
        print("\n" + "="*50)
        print("전략 및 신호 저장 테스트")
        print("="*50)
        
        # 1. 전략 생성
        strategy_id = self.create_sample_strategy()
        
        # 2. 신호 생성
        signal_id = None
        if strategy_id:
            signal_id = self.create_sample_signal(strategy_id)
        
        # 3. 주문 생성
        if strategy_id:
            self.create_sample_order(strategy_id, signal_id)
        
        # 4. 저장된 데이터 조회
        self.list_all_strategies()
        self.list_recent_signals()
        
        print("\n" + "="*50)
        print("테스트 완료")
        print("="*50)

if __name__ == "__main__":
    tester = StrategyStorageTest()
    tester.run_test()