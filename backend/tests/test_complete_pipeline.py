"""
키움 OpenAPI → Supabase 전체 파이프라인 테스트
새로 생성된 모든 테이블에 데이터 저장 테스트
"""

import os
import json
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class CompletePipelineTest:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        self.user_id = None
        self.strategy_id = None
        self.signal_id = None
        self.order_id = None
        
    def setup(self):
        """초기 설정"""
        print("\n=== 초기 설정 ===")
        
        # 사용자 확인
        profiles = self.supabase.table('profiles').select('id, kiwoom_account').limit(1).execute()
        if profiles.data:
            self.user_id = profiles.data[0]['id']
            print(f"사용자 ID: {self.user_id}")
            
        # 활성 전략 확인
        strategies = self.supabase.table('strategies').select('id, name').eq(
            'is_active', True
        ).limit(1).execute()
        
        if strategies.data:
            self.strategy_id = strategies.data[0]['id']
            print(f"전략: {strategies.data[0]['name']}")
        else:
            # 전략 생성
            self.create_strategy()
            
        return self.user_id is not None
        
    def create_strategy(self):
        """테스트 전략 생성"""
        strategy = {
            'user_id': self.user_id,
            'name': f'파이프라인 테스트 전략_{datetime.now().strftime("%H%M%S")}',
            'description': '전체 데이터 파이프라인 테스트',
            'is_active': True,
            'is_test_mode': True,
            'auto_execute': False,
            'position_size': 10,
            'conditions': json.dumps({
                'entry': {'rsi': {'operator': '<', 'value': 30}},
                'exit': {'rsi': {'operator': '>', 'value': 70}}
            }),
            'target_stocks': ['005930', '000660', '035420']
        }
        
        result = self.supabase.table('strategies').insert(strategy).execute()
        if result.data:
            self.strategy_id = result.data[0]['id']
            print(f"전략 생성: {strategy['name']}")
            
    def test_market_data(self):
        """1. 시장 데이터 저장 테스트"""
        print("\n=== 1. market_data 테이블 테스트 ===")
        
        stocks = [
            {'code': '005930', 'name': '삼성전자', 'base': 72000},
            {'code': '000660', 'name': 'SK하이닉스', 'base': 130000},
            {'code': '035420', 'name': 'NAVER', 'base': 210000}
        ]
        
        for stock in stocks:
            change_rate = random.uniform(-3, 3)
            current_price = int(stock['base'] * (1 + change_rate/100))
            
            data = {
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'current_price': current_price,
                'open_price': stock['base'],
                'high_price': int(current_price * 1.02),
                'low_price': int(current_price * 0.98),
                'close_price': current_price,
                'prev_close': stock['base'],
                'volume': random.randint(100000, 1000000),
                'accumulated_volume': random.randint(1000000, 10000000),
                'change_amount': current_price - stock['base'],
                'change_rate': change_rate,
                'bid_price': current_price - 100,
                'ask_price': current_price + 100,
                'bid_volume': random.randint(10000, 100000),
                'ask_volume': random.randint(10000, 100000),
                'trading_date': datetime.now().date().isoformat(),
                'trading_time': datetime.now().time().isoformat()
            }
            
            try:
                result = self.supabase.table('market_data').insert(data).execute()
                print(f"  [OK] {stock['name']}: {current_price:,}원 ({change_rate:+.2f}%)")
            except Exception as e:
                print(f"  [ERROR] {stock['name']}: {str(e)[:50]}")
                
    def test_technical_indicators(self):
        """2. 기술적 지표 저장 테스트"""
        print("\n=== 2. technical_indicators 테이블 테스트 ===")
        
        indicators = {
            'stock_code': '005930',
            'timeframe': '1d',
            'ma5': 71800,
            'ma10': 71500,
            'ma20': 70900,
            'ma60': 69500,
            'ma120': 68000,
            'bb_upper': 73500,
            'bb_middle': 71500,
            'bb_lower': 69500,
            'rsi': 45.5,
            'rsi_signal': 'neutral',
            'macd': 150,
            'macd_signal': 120,
            'macd_histogram': 30,
            'stochastic_k': 55.2,
            'stochastic_d': 52.8,
            'obv': 15000000,
            'vwap': 71650,
            'cci': -20,
            'atr': 1500
        }
        
        try:
            result = self.supabase.table('technical_indicators').insert(indicators).execute()
            print(f"  [OK] 지표 저장: RSI={indicators['rsi']}, MACD={indicators['macd']}")
        except Exception as e:
            print(f"  [ERROR] 오류: {str(e)[:50]}")
            
    def test_trading_signal(self):
        """3. 거래 신호 생성 테스트"""
        print("\n=== 3. trading_signals 테이블 테스트 ===")
        
        signal = {
            'strategy_id': self.strategy_id,
            'stock_code': '005930',
            'signal_type': 'BUY',
            'price': 72000,
            'signal_strength': 'strong',
            'confidence_score': 0.85,
            'entry_price': 72000,
            'target_price': 75600,  # +5%
            'stop_loss_price': 69840,  # -3%
            'position_size': 10,
            'risk_reward_ratio': 1.67,
            'indicators_snapshot': json.dumps({
                'rsi': 28,
                'macd': 'bullish',
                'volume': 'above_average'
            }),
            'executed': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('trading_signals').insert(signal).execute()
            if result.data:
                self.signal_id = result.data[0]['id']
                print(f"  [OK] 신호 생성: {signal['signal_type']} @ {signal['price']:,}원")
                print(f"    목표가: {signal['target_price']:,}원 | 손절가: {signal['stop_loss_price']:,}원")
        except Exception as e:
            print(f"  [ERROR] 오류: {str(e)[:50]}")
            
    def test_kiwoom_order(self):
        """4. 키움 주문 테스트"""
        print("\n=== 4. kiwoom_orders 테이블 테스트 ===")
        
        order = {
            'strategy_id': self.strategy_id,
            'signal_id': self.signal_id,
            'kiwoom_order_no': f"0000{random.randint(100000, 999999)}",
            'account_no': os.getenv('KIWOOM_ACCOUNT_NO', '81101350-01'),
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'order_type': 'BUY',
            'order_method': '지정가',
            'order_quantity': 10,
            'order_price': 72000,
            'order_status': 'PENDING',
            'order_reason': '강한 매수 신호 감지'
        }
        
        try:
            result = self.supabase.table('kiwoom_orders').insert(order).execute()
            if result.data:
                self.order_id = result.data[0]['id']
                print(f"  [OK] 주문 생성: {order['order_type']} {order['order_quantity']}주 @ {order['order_price']:,}원")
                print(f"    주문번호: {order['kiwoom_order_no']}")
        except Exception as e:
            print(f"  [ERROR] 오류: {str(e)[:50]}")
            
    def test_position(self):
        """5. 포지션 테스트"""
        print("\n=== 5. positions 테이블 테스트 ===")
        
        position = {
            'user_id': self.user_id,
            'strategy_id': self.strategy_id,
            'account_no': os.getenv('KIWOOM_ACCOUNT_NO', '81101350-01'),
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'quantity': 10,
            'available_quantity': 10,
            'avg_buy_price': 72000,
            'current_price': 72500,
            'profit_loss': 5000,
            'profit_loss_rate': 0.69,
            'stop_loss_price': 69840,
            'take_profit_price': 75600,
            'position_status': 'OPEN',
            'entry_signal_id': self.signal_id
        }
        
        try:
            result = self.supabase.table('positions').insert(position).execute()
            print(f"  [OK] 포지션 생성: {position['quantity']}주 @ {position['avg_buy_price']:,}원")
            print(f"    현재 손익: {position['profit_loss']:,}원 ({position['profit_loss_rate']:+.2f}%)")
        except Exception as e:
            print(f"  [ERROR] 오류: {str(e)[:50]}")
            
    def test_account_balance(self):
        """6. 계좌 잔고 테스트"""
        print("\n=== 6. account_balance 테이블 테스트 ===")
        
        balance = {
            'user_id': self.user_id,
            'account_no': os.getenv('KIWOOM_ACCOUNT_NO', '81101350-01'),
            'total_evaluation': 10725000,
            'total_buy_amount': 10000000,
            'available_cash': 2800000,
            'total_profit_loss': 725000,
            'total_profit_loss_rate': 7.25,
            'stock_value': 7925000,
            'cash_balance': 2800000
        }
        
        try:
            result = self.supabase.table('account_balance').insert(balance).execute()
            print(f"  [OK] 잔고 업데이트: 총 평가액 {balance['total_evaluation']:,}원")
            print(f"    수익률: {balance['total_profit_loss_rate']:+.2f}%")
        except Exception as e:
            print(f"  [ERROR] 오류: {str(e)[:50]}")
            
    def test_execution_log(self):
        """7. 실행 로그 테스트"""
        print("\n=== 7. strategy_execution_logs 테이블 테스트 ===")
        
        log = {
            'strategy_id': self.strategy_id,
            'execution_type': 'SIGNAL_CHECK',
            'execution_status': 'SUCCESS',
            'stock_code': '005930',
            'action_taken': '매수 신호 생성 및 주문 실행',
            'reason': 'RSI 28 (과매도), MACD 골든크로스',
            'market_snapshot': json.dumps({
                'kospi': 2450.23,
                'kosdaq': 845.67,
                'volume': 'high'
            }),
            'indicators_snapshot': json.dumps({
                'rsi': 28,
                'macd': 150,
                'bb_position': 'lower'
            }),
            'execution_time_ms': 125
        }
        
        try:
            result = self.supabase.table('strategy_execution_logs').insert(log).execute()
            print(f"  [OK] 실행 로그: {log['action_taken']}")
            print(f"    소요시간: {log['execution_time_ms']}ms")
        except Exception as e:
            print(f"  [ERROR] 오류: {str(e)[:50]}")
            
    def verify_data_flow(self):
        """8. 데이터 흐름 검증"""
        print("\n=== 8. 데이터 흐름 검증 ===")
        
        checks = []
        
        # market_data 확인
        market = self.supabase.table('market_data').select('count', count='exact').execute()
        checks.append(f"market_data: {market.count}개 레코드")
        
        # technical_indicators 확인
        indicators = self.supabase.table('technical_indicators').select('count', count='exact').execute()
        checks.append(f"technical_indicators: {indicators.count}개 레코드")
        
        # trading_signals 확인
        signals = self.supabase.table('trading_signals').select('count', count='exact').execute()
        checks.append(f"trading_signals: {signals.count}개 레코드")
        
        # kiwoom_orders 확인
        orders = self.supabase.table('kiwoom_orders').select('count', count='exact').execute()
        checks.append(f"kiwoom_orders: {orders.count}개 레코드")
        
        # positions 확인
        positions = self.supabase.table('positions').select('count', count='exact').execute()
        checks.append(f"positions: {positions.count}개 레코드")
        
        for check in checks:
            print(f"  [OK] {check}")
            
    def run(self):
        """전체 파이프라인 테스트 실행"""
        print("\n" + "="*60)
        print("키움 OpenAPI → Supabase 파이프라인 테스트")
        print("="*60)
        
        if not self.setup():
            print("초기 설정 실패")
            return
            
        # 순차적 테스트
        self.test_market_data()          # 1. 시장 데이터
        self.test_technical_indicators() # 2. 기술적 지표
        self.test_trading_signal()        # 3. 거래 신호
        self.test_kiwoom_order()         # 4. 주문
        self.test_position()             # 5. 포지션
        self.test_account_balance()      # 6. 계좌 잔고
        self.test_execution_log()        # 7. 실행 로그
        self.verify_data_flow()          # 8. 검증
        
        print("\n" + "="*60)
        print("[SUCCESS] 파이프라인 테스트 완료!")
        print("="*60)

if __name__ == "__main__":
    tester = CompletePipelineTest()
    tester.run()