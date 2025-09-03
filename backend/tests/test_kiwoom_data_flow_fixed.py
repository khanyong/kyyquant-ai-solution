"""
키움 OpenAPI → Supabase 데이터 흐름 완전 테스트 (수정 버전)
데이터 타입 오류 수정
"""

import os
import json
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
from supabase import create_client, Client
import time

load_dotenv()

class KiwoomDataFlowTest:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        # 테스트용 ID 저장
        self.test_ids = {
            'user_id': None,
            'strategy_id': None,
            'signal_ids': [],
            'order_ids': [],
            'position_ids': []
        }
        
        # 테스트 종목
        self.test_stocks = [
            {'code': '005930', 'name': '삼성전자', 'price': 72000},
            {'code': '000660', 'name': 'SK하이닉스', 'price': 130000},
            {'code': '035420', 'name': 'NAVER', 'price': 210000}
        ]
        
    def setup(self):
        """초기 설정 - 사용자와 전략 준비"""
        print("\n" + "="*70)
        print("키움 OpenAPI → Supabase 데이터 흐름 테스트")
        print("="*70)
        
        # 1. 사용자 확인
        profiles = self.supabase.table('profiles').select('*').limit(1).execute()
        if profiles.data:
            self.test_ids['user_id'] = profiles.data[0]['id']
            print(f"\n[설정] 테스트 사용자: {profiles.data[0].get('email', 'Unknown')}")
            print(f"       키움계좌: {profiles.data[0].get('kiwoom_account', '미설정')}")
        
        # 2. 테스트 전략 생성
        strategy = {
            'user_id': self.test_ids['user_id'],
            'name': f'데이터흐름테스트_{datetime.now().strftime("%H%M%S")}',
            'description': '키움 데이터 흐름 테스트용 전략',
            'is_active': True,
            'is_test_mode': True,
            'position_size': 10,
            'conditions': json.dumps({
                'entry': {'rsi': '<30', 'volume': '>average'},
                'exit': {'profit': '>5%', 'loss': '<-3%'}
            }),
            'target_stocks': ['005930', '000660', '035420']
        }
        
        result = self.supabase.table('strategies').insert(strategy).execute()
        if result.data:
            self.test_ids['strategy_id'] = result.data[0]['id']
            print(f"\n[전략] 생성됨: {strategy['name']}")
            
    def test_1_market_data(self):
        """STEP 1: 실시간 시장 데이터 수신 및 저장"""
        print("\n" + "-"*70)
        print("STEP 1: 실시간 시장 데이터 (키움 → market_data)")
        print("-"*70)
        
        saved_data = []
        
        for stock in self.test_stocks:
            # 키움 API에서 받는 실시간 데이터 시뮬레이션
            change_rate = random.uniform(-3, 3)
            current_price = int(stock['price'] * (1 + change_rate/100))
            
            market_data = {
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'current_price': current_price,
                'open_price': stock['price'],
                'high_price': int(current_price * 1.01),
                'low_price': int(current_price * 0.99),
                'close_price': current_price,
                'prev_close': stock['price'],
                'volume': random.randint(100000, 1000000),
                'accumulated_volume': random.randint(5000000, 20000000),
                'trading_value': current_price * random.randint(100000, 1000000),
                'change_amount': current_price - stock['price'],
                'change_rate': change_rate,
                'bid_price': current_price - 100,
                'ask_price': current_price + 100,
                'bid_volume': random.randint(10000, 100000),
                'ask_volume': random.randint(10000, 100000),
                'trading_date': datetime.now().date().isoformat(),
                'trading_time': datetime.now().time().isoformat()
            }
            
            try:
                result = self.supabase.table('market_data').insert(market_data).execute()
                saved_data.append(result.data[0])
                
                print(f"\n[OK] {stock['name']} ({stock['code']})")
                print(f"  현재가: {current_price:,}원 ({change_rate:+.2f}%)")
                print(f"  거래량: {market_data['volume']:,}주")
                
            except Exception as e:
                print(f"[ERROR] {stock['name']}: {e}")
                
        return saved_data
        
    def test_2_technical_indicators(self):
        """STEP 2: 기술적 지표 계산 및 저장"""
        print("\n" + "-"*70)
        print("STEP 2: 기술적 지표 계산 (market_data → technical_indicators)")
        print("-"*70)
        
        saved_indicators = []
        
        for stock in self.test_stocks:
            # 지표 계산 (실제로는 market_data에서 계산)
            indicators = {
                'stock_code': stock['code'],
                'timeframe': '1d',
                'ma5': stock['price'] * 0.99,
                'ma10': stock['price'] * 0.98,
                'ma20': stock['price'] * 0.97,
                'ma60': stock['price'] * 0.95,
                'ma120': stock['price'] * 0.93,
                'bb_upper': stock['price'] * 1.02,
                'bb_middle': stock['price'],
                'bb_lower': stock['price'] * 0.98,
                'rsi': random.uniform(25, 75),
                'rsi_signal': 'oversold' if random.random() < 0.3 else 'neutral',
                'macd': random.uniform(-500, 500),
                'macd_signal': random.uniform(-400, 400),
                'macd_histogram': random.uniform(-100, 100),
                'stochastic_k': random.uniform(20, 80),
                'stochastic_d': random.uniform(20, 80),
                'obv': random.randint(10000000, 50000000),
                'vwap': stock['price'] * random.uniform(0.99, 1.01),
                'cci': random.uniform(-100, 100),
                'atr': stock['price'] * 0.02
            }
            
            try:
                result = self.supabase.table('technical_indicators').insert(indicators).execute()
                saved_indicators.append(result.data[0])
                
                print(f"\n[OK] {stock['name']} 지표")
                print(f"  RSI: {indicators['rsi']:.2f} ({indicators['rsi_signal']})")
                print(f"  MACD: {indicators['macd']:.2f}")
                
            except Exception as e:
                print(f"[ERROR] {stock['name']}: {e}")
                
        return saved_indicators
        
    def test_3_trading_signals(self):
        """STEP 3: 거래 신호 생성"""
        print("\n" + "-"*70)
        print("STEP 3: 거래 신호 생성 (indicators → trading_signals)")
        print("-"*70)
        
        signals = []
        
        # RSI < 30인 종목에 매수 신호
        for stock in self.test_stocks[:1]:  # 첫 번째 종목만
            signal = {
                'strategy_id': self.test_ids['strategy_id'],
                'stock_code': stock['code'],
                'signal_type': 'BUY',
                'price': stock['price'],
                # signal_strength는 문자열이 아닌 제거 또는 다른 필드 사용
                # 'signal_strength': 'strong',  # 제거
                'confidence_score': 0.85,
                'entry_price': stock['price'],
                'target_price': int(stock['price'] * 1.05),  # +5%
                'stop_loss_price': int(stock['price'] * 0.97),  # -3%
                'position_size': 10,
                'risk_reward_ratio': 1.67,
                'indicators_snapshot': json.dumps({
                    'rsi': 28,
                    'macd': 'bullish',
                    'bb_position': 'lower_band'
                }),
                'market_conditions': json.dumps({
                    'market_trend': 'upward',
                    'volume': 'above_average'
                }),
                'timestamp': datetime.now().isoformat()
            }
            
            # signal_strength가 varchar 타입인 경우 추가
            if 'signal_strength' not in signal:
                signal['signal_strength'] = 'strong'  # varchar로 추가
            
            try:
                result = self.supabase.table('trading_signals').insert(signal).execute()
                if result.data:
                    self.test_ids['signal_ids'].append(result.data[0]['id'])
                    signals.append(result.data[0])
                    
                    print(f"\n[OK] {stock['name']} 매수 신호 생성")
                    print(f"  진입가: {signal['entry_price']:,}원")
                    print(f"  목표가: {signal['target_price']:,}원 (+5%)")
                    print(f"  손절가: {signal['stop_loss_price']:,}원 (-3%)")
                    print(f"  신뢰도: {signal['confidence_score']*100:.0f}%")
                    
            except Exception as e:
                print(f"[ERROR] 신호 생성: {str(e)[:100]}")
                
        return signals
        
    def test_4_kiwoom_orders(self):
        """STEP 4: 키움 주문 실행"""
        print("\n" + "-"*70)
        print("STEP 4: 주문 실행 (trading_signals → kiwoom_orders)")
        print("-"*70)
        
        orders = []
        
        if self.test_ids['signal_ids']:
            stock = self.test_stocks[0]
            
            order = {
                'strategy_id': self.test_ids['strategy_id'],
                'signal_id': self.test_ids['signal_ids'][0],
                'kiwoom_order_no': f"TEST{random.randint(100000, 999999)}",
                'account_no': os.getenv('KIWOOM_ACCOUNT_NO', '81101350-01'),
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'order_type': 'BUY',
                'order_method': '지정가',
                'order_quantity': 10,
                'order_price': stock['price'],
                'order_status': 'PENDING',
                'order_reason': 'RSI 과매도 신호'
            }
            
            try:
                result = self.supabase.table('kiwoom_orders').insert(order).execute()
                if result.data:
                    self.test_ids['order_ids'].append(result.data[0]['id'])
                    orders.append(result.data[0])
                    
                    print(f"\n[OK] 키움증권 주문 전송")
                    print(f"  주문번호: {order['kiwoom_order_no']}")
                    print(f"  종목: {order['stock_name']} {order['order_quantity']}주")
                    print(f"  주문가: {order['order_price']:,}원")
                    print(f"  상태: {order['order_status']}")
                    
                    # 체결 시뮬레이션
                    self._simulate_order_execution(result.data[0]['id'])
                    
            except Exception as e:
                print(f"[ERROR] 주문: {e}")
                
        return orders
        
    def _simulate_order_execution(self, order_id):
        """주문 체결 시뮬레이션"""
        update_data = {
            'executed_quantity': 10,
            'executed_price': self.test_stocks[0]['price'],
            'remaining_quantity': 0,
            'order_status': 'FILLED',
            'executed_time': datetime.now().isoformat()
        }
        
        result = self.supabase.table('kiwoom_orders').update(update_data).eq(
            'id', order_id
        ).execute()
        
        print(f"\n[체결] 주문 체결 완료")
        print(f"  체결가: {update_data['executed_price']:,}원")
        print(f"  체결수량: {update_data['executed_quantity']}주")
        
    def test_5_positions(self):
        """STEP 5: 포지션 생성"""
        print("\n" + "-"*70)
        print("STEP 5: 포지션 관리 (kiwoom_orders → positions)")
        print("-"*70)
        
        if self.test_ids['order_ids']:
            stock = self.test_stocks[0]
            
            position = {
                'user_id': self.test_ids['user_id'],
                'strategy_id': self.test_ids['strategy_id'],
                'account_no': os.getenv('KIWOOM_ACCOUNT_NO', '81101350-01'),
                'stock_code': stock['code'],
                'stock_name': stock['name'],
                'quantity': 10,
                'available_quantity': 10,
                'avg_buy_price': stock['price'],
                'current_price': int(stock['price'] * 1.01),  # +1%
                'profit_loss': int(stock['price'] * 0.01 * 10),
                'profit_loss_rate': 1.0,
                'stop_loss_price': int(stock['price'] * 0.97),
                'take_profit_price': int(stock['price'] * 1.05),
                'position_status': 'OPEN',
                'entry_signal_id': self.test_ids['signal_ids'][0] if self.test_ids['signal_ids'] else None
            }
            
            try:
                result = self.supabase.table('positions').insert(position).execute()
                if result.data:
                    self.test_ids['position_ids'].append(result.data[0]['id'])
                    
                    print(f"\n[OK] 새 포지션 생성")
                    print(f"  종목: {position['stock_name']} {position['quantity']}주")
                    print(f"  매입가: {position['avg_buy_price']:,}원")
                    print(f"  현재가: {position['current_price']:,}원")
                    print(f"  손익: {position['profit_loss']:,}원 ({position['profit_loss_rate']:+.1f}%)")
                    
            except Exception as e:
                print(f"[ERROR] 포지션: {e}")
                
    def test_6_account_balance(self):
        """STEP 6: 계좌 잔고 업데이트"""
        print("\n" + "-"*70)
        print("STEP 6: 계좌 잔고 업데이트 (positions → account_balance)")
        print("-"*70)
        
        # account_balance 테이블의 실제 컬럼 확인
        balance = {
            'user_id': self.test_ids['user_id'],
            'account_no': os.getenv('KIWOOM_ACCOUNT_NO', '81101350-01'),
            'total_evaluation': 10720000,
            'total_buy_amount': 10000000,
            'available_cash': 2800000,
            'total_profit_loss': 720000,
            'total_profit_loss_rate': 7.2,
            'stock_value': 7920000,
            # 'cash_balance': 2800000,  # 컬럼이 없으면 제거
            'receivable_amount': 0,
            'invested_amount': 7200000
        }
        
        try:
            result = self.supabase.table('account_balance').insert(balance).execute()
            
            print(f"\n[OK] 계좌 잔고 업데이트")
            print(f"  총평가액: {balance['total_evaluation']:,}원")
            print(f"  주식평가: {balance['stock_value']:,}원")
            print(f"  예수금: {balance['available_cash']:,}원")
            print(f"  총손익: {balance['total_profit_loss']:,}원 ({balance['total_profit_loss_rate']:+.1f}%)")
            
        except Exception as e:
            print(f"[ERROR] 잔고: {str(e)[:100]}")
            
    def test_7_execution_logs(self):
        """STEP 7: 실행 로그 기록"""
        print("\n" + "-"*70)
        print("STEP 7: 실행 로그 (모든 활동 → strategy_execution_logs)")
        print("-"*70)
        
        logs = [
            {
                'execution_type': 'SIGNAL_CHECK',
                'execution_status': 'SUCCESS',
                'action_taken': '매수 신호 감지 및 검증'
            },
            {
                'execution_type': 'ORDER_PLACED',
                'execution_status': 'SUCCESS',
                'action_taken': '매수 주문 실행'
            },
            {
                'execution_type': 'POSITION_OPENED',
                'execution_status': 'SUCCESS',
                'action_taken': '새 포지션 생성'
            }
        ]
        
        for log_data in logs:
            log = {
                'strategy_id': self.test_ids['strategy_id'],
                'execution_type': log_data['execution_type'],
                'execution_status': log_data['execution_status'],
                'stock_code': '005930',
                'action_taken': log_data['action_taken'],
                'market_snapshot': json.dumps({
                    'kospi': 2450.23,
                    'kosdaq': 845.67
                }),
                'execution_time_ms': random.randint(50, 200)
            }
            
            try:
                result = self.supabase.table('strategy_execution_logs').insert(log).execute()
                print(f"\n[OK] {log['execution_type']}")
                print(f"  {log['action_taken']} ({log['execution_time_ms']}ms)")
                
            except Exception as e:
                print(f"[ERROR] 로그: {e}")
                
    def verify_data_flow(self):
        """데이터 흐름 검증"""
        print("\n" + "="*70)
        print("데이터 흐름 검증")
        print("="*70)
        
        # 1. 저장된 데이터 개수 확인
        print("\n[데이터 개수]")
        tables = [
            'market_data',
            'technical_indicators',
            'trading_signals',
            'kiwoom_orders',
            'positions',
            'account_balance',
            'strategy_execution_logs'
        ]
        
        for table in tables:
            result = self.supabase.table(table).select('count', count='exact').execute()
            print(f"  {table}: {result.count}개")
            
        # 2. 관계 확인
        print("\n[데이터 관계]")
        
        # 신호 → 주문 관계
        if self.test_ids['signal_ids']:
            orders = self.supabase.table('kiwoom_orders').select('*').eq(
                'signal_id', self.test_ids['signal_ids'][0]
            ).execute()
            print(f"  신호 → 주문: {len(orders.data)}개 주문 연결됨")
            
        # 주문 → 포지션 관계
        if self.test_ids['strategy_id']:
            positions = self.supabase.table('positions').select('*').eq(
                'strategy_id', self.test_ids['strategy_id']
            ).execute()
            print(f"  전략 → 포지션: {len(positions.data)}개 포지션 연결됨")
            
        # 최신 데이터 샘플 표시
        print("\n[최신 데이터 샘플]")
        
        # 최신 market_data
        latest_market = self.supabase.table('market_data').select('*').order(
            'timestamp', desc=True
        ).limit(1).execute()
        
        if latest_market.data:
            data = latest_market.data[0]
            print(f"\n  최신 시세: {data['stock_name']} - {data['current_price']:,}원")
            
        # 최신 신호
        latest_signal = self.supabase.table('trading_signals').select('*').order(
            'timestamp', desc=True
        ).limit(1).execute()
        
        if latest_signal.data:
            data = latest_signal.data[0]
            print(f"  최신 신호: {data['signal_type']} @ {data.get('price', 0):,}원")
            
    def run(self):
        """전체 테스트 실행"""
        self.setup()
        
        # 데이터 흐름 순서대로 테스트
        self.test_1_market_data()
        self.test_2_technical_indicators()
        self.test_3_trading_signals()
        self.test_4_kiwoom_orders()
        self.test_5_positions()
        self.test_6_account_balance()
        self.test_7_execution_logs()
        
        # 검증
        self.verify_data_flow()
        
        print("\n" + "="*70)
        print("테스트 완료! Supabase Dashboard에서 데이터를 확인하세요.")
        print("="*70)

if __name__ == "__main__":
    tester = KiwoomDataFlowTest()
    tester.run()