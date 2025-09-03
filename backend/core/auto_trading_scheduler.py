"""
자동매매 스케줄러
전략을 주기적으로 실행하고 매매 신호를 처리
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Dict, List, Optional
import schedule
import time as time_module
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database.database_supabase import SupabaseDB
from core.strategy_execution_manager import StrategyExecutionManager
from scripts.kiwoom.kiwoom_trading_api import KiwoomTradingAPI

logger = logging.getLogger(__name__)

class AutoTradingScheduler:
    """자동매매 스케줄러"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = SupabaseDB()
        self.execution_manager = StrategyExecutionManager()
        self.kiwoom_api = KiwoomTradingAPI()
        self.active_strategies = {}
        
        # 장 시간 설정
        self.market_open = time(9, 0)  # 오전 9시
        self.market_close = time(15, 30)  # 오후 3시 30분
        
    def initialize(self):
        """스케줄러 초기화"""
        try:
            # 키움 API 연결
            self.kiwoom_api.connect()
            
            # 활성 전략 로드
            self.load_active_strategies()
            
            # 스케줄 설정
            self.setup_schedules()
            
            # 스케줄러 시작
            self.scheduler.start()
            
            logger.info("자동매매 스케줄러 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"스케줄러 초기화 실패: {e}")
            return False
    
    def load_active_strategies(self):
        """활성화된 전략 로드"""
        try:
            # Supabase에서 활성 전략 조회
            result = self.db.supabase.table('strategies')\
                .select('*')\
                .eq('is_active', True)\
                .execute()
            
            self.active_strategies = {
                str(s['id']): s for s in result.data
            }
            
            logger.info(f"{len(self.active_strategies)}개 활성 전략 로드")
            
        except Exception as e:
            logger.error(f"전략 로드 실패: {e}")
    
    def setup_schedules(self):
        """스케줄 설정"""
        # 장 시작 시 실행
        self.scheduler.add_job(
            func=self.on_market_open,
            trigger=CronTrigger(hour=9, minute=0),
            id='market_open',
            name='장 시작 처리'
        )
        
        # 장 종료 시 실행
        self.scheduler.add_job(
            func=self.on_market_close,
            trigger=CronTrigger(hour=15, minute=30),
            id='market_close',
            name='장 종료 처리'
        )
        
        # 1분마다 전략 실행 (장 중에만)
        self.scheduler.add_job(
            func=self.execute_strategies,
            trigger='interval',
            seconds=60,
            id='execute_strategies',
            name='전략 실행'
        )
        
        # 5분마다 포지션 업데이트
        self.scheduler.add_job(
            func=self.update_positions,
            trigger='interval',
            minutes=5,
            id='update_positions',
            name='포지션 업데이트'
        )
    
    def is_market_open(self) -> bool:
        """장 시간 확인"""
        now = datetime.now().time()
        
        # 주말 제외
        if datetime.now().weekday() >= 5:  # 토요일(5), 일요일(6)
            return False
        
        # 장 시간 확인
        return self.market_open <= now <= self.market_close
    
    def on_market_open(self):
        """장 시작 시 실행"""
        logger.info("=== 장 시작 ===")
        
        # 전략 재로드
        self.load_active_strategies()
        
        # 계좌 정보 업데이트
        self.update_account_balance()
        
        # 전략별 초기화
        for strategy_id, strategy in self.active_strategies.items():
            self.initialize_strategy(strategy_id)
    
    def on_market_close(self):
        """장 종료 시 실행"""
        logger.info("=== 장 종료 ===")
        
        # 미체결 주문 취소
        self.cancel_pending_orders()
        
        # 일일 성과 기록
        self.record_daily_performance()
        
        # 리포트 생성
        self.generate_daily_report()
    
    def execute_strategies(self):
        """전략 실행 (메인 로직)"""
        if not self.is_market_open():
            return
        
        logger.info(f"전략 실행 시작: {len(self.active_strategies)}개")
        
        for strategy_id, strategy in self.active_strategies.items():
            try:
                # 전략 실행
                signals = self.execution_manager.execute_strategy(strategy_id)
                
                # 신호가 있으면 주문 실행
                if signals:
                    self.process_signals(strategy_id, signals)
                    
            except Exception as e:
                logger.error(f"전략 {strategy_id} 실행 실패: {e}")
    
    def process_signals(self, strategy_id: str, signals: List[Dict]):
        """매매 신호 처리"""
        for signal in signals:
            try:
                if signal['signal_type'] == 'BUY':
                    self.execute_buy_order(strategy_id, signal)
                elif signal['signal_type'] == 'SELL':
                    self.execute_sell_order(strategy_id, signal)
                    
            except Exception as e:
                logger.error(f"신호 처리 실패: {e}")
    
    def execute_buy_order(self, strategy_id: str, signal: Dict):
        """매수 주문 실행"""
        try:
            # 키움 API로 매수 주문
            order = self.kiwoom_api.buy_order(
                stock_code=signal['stock_code'],
                quantity=signal['position_size'],
                price=signal['entry_price'],
                order_type='limit'  # 지정가 주문
            )
            
            # 주문 정보 저장
            self.save_order(strategy_id, order, signal)
            
            logger.info(f"매수 주문 실행: {signal['stock_code']} {signal['position_size']}주")
            
        except Exception as e:
            logger.error(f"매수 주문 실패: {e}")
    
    def execute_sell_order(self, strategy_id: str, signal: Dict):
        """매도 주문 실행"""
        try:
            # 키움 API로 매도 주문
            order = self.kiwoom_api.sell_order(
                stock_code=signal['stock_code'],
                quantity=signal['position_size'],
                price=signal['exit_price'],
                order_type='limit'
            )
            
            # 주문 정보 저장
            self.save_order(strategy_id, order, signal)
            
            logger.info(f"매도 주문 실행: {signal['stock_code']} {signal['position_size']}주")
            
        except Exception as e:
            logger.error(f"매도 주문 실패: {e}")
    
    def save_order(self, strategy_id: str, order: Dict, signal: Dict):
        """주문 정보 저장"""
        try:
            order_data = {
                'strategy_id': strategy_id,
                'signal_id': signal.get('id'),
                'stock_code': signal['stock_code'],
                'order_type': signal['signal_type'],
                'quantity': signal['position_size'],
                'price': signal.get('entry_price') or signal.get('exit_price'),
                'order_number': order.get('order_number'),
                'status': 'PENDING',
                'created_at': datetime.now().isoformat()
            }
            
            self.db.supabase.table('kiwoom_orders').insert(order_data).execute()
            
        except Exception as e:
            logger.error(f"주문 저장 실패: {e}")
    
    def update_positions(self):
        """포지션 업데이트"""
        if not self.is_market_open():
            return
        
        try:
            # 키움 API에서 현재 포지션 조회
            positions = self.kiwoom_api.get_positions()
            
            for position in positions:
                # 현재가 조회
                current_price = self.kiwoom_api.get_current_price(position['stock_code'])
                
                # 손익 계산
                profit_loss = (current_price - position['avg_price']) * position['quantity']
                profit_loss_rate = ((current_price / position['avg_price']) - 1) * 100
                
                # 포지션 업데이트
                self.db.supabase.table('positions')\
                    .update({
                        'current_price': current_price,
                        'profit_loss': profit_loss,
                        'profit_loss_rate': profit_loss_rate,
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('stock_code', position['stock_code'])\
                    .eq('status', 'OPEN')\
                    .execute()
            
            logger.info(f"{len(positions)}개 포지션 업데이트 완료")
            
        except Exception as e:
            logger.error(f"포지션 업데이트 실패: {e}")
    
    def update_account_balance(self):
        """계좌 잔고 업데이트"""
        try:
            # 키움 API에서 계좌 정보 조회
            balance = self.kiwoom_api.get_account_balance()
            
            # 계좌 정보 저장
            self.db.supabase.table('account_balance')\
                .upsert({
                    'user_id': self.get_user_id(),
                    'account_no': balance['account_no'],
                    'total_assets': balance['total_assets'],
                    'total_evaluation': balance['total_evaluation'],
                    'cash_balance': balance['cash_balance'],
                    'stock_value': balance['stock_value'],
                    'total_profit_loss': balance['total_profit_loss'],
                    'total_profit_loss_rate': balance['total_profit_loss_rate'],
                    'updated_at': datetime.now().isoformat()
                })\
                .execute()
            
            logger.info("계좌 잔고 업데이트 완료")
            
        except Exception as e:
            logger.error(f"계좌 잔고 업데이트 실패: {e}")
    
    def cancel_pending_orders(self):
        """미체결 주문 취소"""
        try:
            # 미체결 주문 조회
            pending_orders = self.db.supabase.table('kiwoom_orders')\
                .select('*')\
                .eq('status', 'PENDING')\
                .execute()
            
            for order in pending_orders.data:
                # 주문 취소
                self.kiwoom_api.cancel_order(order['order_number'])
                
                # 상태 업데이트
                self.db.supabase.table('kiwoom_orders')\
                    .update({'status': 'CANCELLED'})\
                    .eq('id', order['id'])\
                    .execute()
            
            logger.info(f"{len(pending_orders.data)}개 미체결 주문 취소")
            
        except Exception as e:
            logger.error(f"주문 취소 실패: {e}")
    
    def record_daily_performance(self):
        """일일 성과 기록"""
        try:
            # 오늘 실행된 전략들의 성과 집계
            today = datetime.now().date().isoformat()
            
            for strategy_id in self.active_strategies:
                performance = self.calculate_strategy_performance(strategy_id, today)
                
                # 성과 저장
                self.db.supabase.table('strategy_performance')\
                    .insert({
                        'strategy_id': strategy_id,
                        'date': today,
                        'total_trades': performance['total_trades'],
                        'winning_trades': performance['winning_trades'],
                        'losing_trades': performance['losing_trades'],
                        'total_profit': performance['total_profit'],
                        'total_loss': performance['total_loss'],
                        'win_rate': performance['win_rate'],
                        'profit_factor': performance['profit_factor']
                    })\
                    .execute()
            
            logger.info("일일 성과 기록 완료")
            
        except Exception as e:
            logger.error(f"성과 기록 실패: {e}")
    
    def calculate_strategy_performance(self, strategy_id: str, date: str) -> Dict:
        """전략 성과 계산"""
        # TODO: 실제 성과 계산 로직 구현
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'total_loss': 0,
            'win_rate': 0,
            'profit_factor': 0
        }
    
    def generate_daily_report(self):
        """일일 리포트 생성"""
        try:
            # TODO: 일일 리포트 생성 및 이메일 발송
            logger.info("일일 리포트 생성 완료")
            
        except Exception as e:
            logger.error(f"리포트 생성 실패: {e}")
    
    def initialize_strategy(self, strategy_id: str):
        """전략 초기화"""
        logger.info(f"전략 {strategy_id} 초기화")
    
    def get_user_id(self) -> str:
        """사용자 ID 조회"""
        # TODO: 실제 사용자 ID 조회 로직
        return "2ca318c1-34d6-4e6b-b16c-3be494cd0048"
    
    def stop(self):
        """스케줄러 중지"""
        self.scheduler.shutdown()
        logger.info("자동매매 스케줄러 중지")

# 메인 실행
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scheduler = AutoTradingScheduler()
    
    if scheduler.initialize():
        print("자동매매 스케줄러가 시작되었습니다.")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        try:
            # 계속 실행
            while True:
                time_module.sleep(1)
                
        except KeyboardInterrupt:
            print("\n스케줄러를 중지합니다...")
            scheduler.stop()