"""
키움 데이터를 Supabase에 저장하는 실제 구현
실제 테이블 구조에 맞춰 데이터 저장
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import random

load_dotenv()

class KiwoomDataSaver:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        self.user_id = None
        self.strategy_id = None
        
    def initialize(self):
        """초기화 - 사용자 및 전략 확인"""
        # 사용자 확인
        profiles = self.supabase.table('profiles').select('id, kiwoom_account').limit(1).execute()
        if profiles.data:
            self.user_id = profiles.data[0]['id']
            print(f"[초기화] 사용자: {self.user_id}")
            print(f"[초기화] 키움계좌: {profiles.data[0].get('kiwoom_account', '미설정')}")
        else:
            print("[에러] 사용자를 찾을 수 없습니다")
            return False
            
        # 활성 전략 확인 또는 생성
        strategies = self.supabase.table('strategies').select('*').eq(
            'user_id', self.user_id
        ).eq('is_active', True).execute()
        
        if strategies.data:
            self.strategy_id = strategies.data[0]['id']
            print(f"[초기화] 활성 전략: {strategies.data[0]['name']}")
        else:
            # 새 전략 생성
            self.strategy_id = self.create_default_strategy()
            
        return True
        
    def create_default_strategy(self):
        """기본 전략 생성"""
        strategy = {
            'user_id': self.user_id,
            'name': f'키움 실시간 전략_{datetime.now().strftime("%Y%m%d")}',
            'description': '키움 API 실시간 데이터 수집 및 거래',
            'type': 'REALTIME',
            'is_active': True,
            'is_test_mode': True,
            'auto_trade_enabled': False,
            'config': json.dumps({
                'target_stocks': ['005930', '000660', '035420'],
                'indicators': ['RSI', 'MACD', 'BB'],
                'timeframe': '1m'
            }),
            'risk_management': json.dumps({
                'max_position_size': 10,  # 10%
                'stop_loss': 3,  # 3%
                'take_profit': 5  # 5%
            }),
            'created_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('strategies').insert(strategy).execute()
            if result.data:
                print(f"[생성] 전략: {strategy['name']}")
                return result.data[0]['id']
        except Exception as e:
            print(f"[에러] 전략 생성 실패: {e}")
            
        return None
        
    def save_market_data(self, stock_code, stock_name, price, volume, change_rate):
        """실시간 시장 데이터 저장"""
        try:
            # market_data_cache 테이블이 없으므로 trading_signals에 저장
            signal_data = {
                'strategy_id': self.strategy_id,
                'stock_code': stock_code,
                'signal_type': self.determine_signal(price, change_rate),
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.supabase.table('trading_signals').insert(signal_data).execute()
            
            if result.data:
                print(f"[저장] {stock_name}({stock_code}): {price:,}원 ({change_rate:+.2f}%)")
                return result.data[0]['id']
                
        except Exception as e:
            print(f"[에러] 시장 데이터 저장 실패: {e}")
            
        return None
        
    def determine_signal(self, price, change_rate):
        """신호 결정 (간단한 로직)"""
        if change_rate < -2:
            return 'BUY'
        elif change_rate > 2:
            return 'SELL'
        else:
            return 'HOLD'
            
    def save_order(self, stock_code, stock_name, order_type, quantity, price):
        """주문 저장"""
        order_data = {
            'strategy_id': self.strategy_id,
            'stock_code': stock_code,
            'stock_name': stock_name,
            'order_type': order_type,
            'order_status': 'PENDING',  # status 대신 order_status 사용
            'price': price,
            'created_at': datetime.now().isoformat()
        }
        
        # quantity 필드가 있는지 확인
        # orders 테이블의 실제 구조에 맞게 조정 필요
        
        try:
            result = self.supabase.table('orders').insert(order_data).execute()
            
            if result.data:
                print(f"[주문] {order_type} {stock_name}({stock_code}) @ {price:,}원")
                return result.data[0]['id']
                
        except Exception as e:
            print(f"[에러] 주문 저장 실패: {e}")
            # 에러 메시지를 분석하여 필수 필드 확인
            error_msg = str(e)
            if 'null value in column' in error_msg:
                print("[정보] 필수 필드가 누락되었습니다")
            elif 'Could not find the' in error_msg:
                print("[정보] 존재하지 않는 컬럼입니다")
                
        return None
        
    def simulate_realtime_data(self):
        """실시간 데이터 시뮬레이션"""
        print("\n=== 실시간 데이터 시뮬레이션 ===\n")
        
        stocks = [
            {'code': '005930', 'name': '삼성전자', 'base_price': 72000},
            {'code': '000660', 'name': 'SK하이닉스', 'base_price': 130000},
            {'code': '035420', 'name': 'NAVER', 'base_price': 210000}
        ]
        
        for _ in range(3):  # 3번 반복
            for stock in stocks:
                # 랜덤 가격 변동
                change_rate = random.uniform(-3, 3)
                price = int(stock['base_price'] * (1 + change_rate/100))
                volume = random.randint(100000, 1000000)
                
                # 데이터 저장
                signal_id = self.save_market_data(
                    stock['code'],
                    stock['name'],
                    price,
                    volume,
                    change_rate
                )
                
                # 매수/매도 신호가 있으면 주문
                if signal_id and abs(change_rate) > 2:
                    order_type = 'BUY' if change_rate < -2 else 'SELL'
                    self.save_order(
                        stock['code'],
                        stock['name'],
                        order_type,
                        10,  # 10주
                        price
                    )
                    
    def check_saved_data(self):
        """저장된 데이터 확인"""
        print("\n=== 저장된 데이터 확인 ===\n")
        
        # 최근 신호
        signals = self.supabase.table('trading_signals').select('*').eq(
            'strategy_id', self.strategy_id
        ).order('timestamp', desc=True).limit(5).execute()
        
        if signals.data:
            print(f"최근 신호 {len(signals.data)}개:")
            for signal in signals.data:
                print(f"  - {signal['stock_code']}: {signal['signal_type']} @ {signal.get('price', 0):,}원")
                
        # 주문 내역
        orders = self.supabase.table('orders').select('*').eq(
            'strategy_id', self.strategy_id
        ).limit(5).execute()
        
        if orders.data:
            print(f"\n주문 내역 {len(orders.data)}개:")
            for order in orders.data:
                print(f"  - {order.get('stock_code')}: {order.get('order_type')} @ {order.get('price', 0):,}원")
                
    def run(self):
        """메인 실행"""
        print("\n" + "="*50)
        print("키움 데이터 Supabase 저장 테스트")
        print("="*50)
        
        if not self.initialize():
            print("[에러] 초기화 실패")
            return
            
        # 실시간 데이터 시뮬레이션 및 저장
        self.simulate_realtime_data()
        
        # 저장된 데이터 확인
        self.check_saved_data()
        
        print("\n" + "="*50)
        print("테스트 완료")
        print("="*50)


if __name__ == "__main__":
    saver = KiwoomDataSaver()
    saver.run()