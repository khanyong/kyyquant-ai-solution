"""
키움 API와 Supabase 연동 브릿지
실시간 데이터를 Supabase에 저장하고 전략 실행
"""

import sys
import os
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal, QObject
import time
from datetime import datetime
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import threading
import queue

load_dotenv()

class KiwoomSupabaseBridge(QObject):
    """키움 API와 Supabase를 연결하는 브릿지 클래스"""
    
    # 시그널 정의
    data_received = pyqtSignal(dict)
    order_completed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.app = None
        self.ocx = None
        self.event_loop = QEventLoop()
        self.login_success = False
        self.account_no = ""
        
        # Supabase 클라이언트
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        # 데이터 큐
        self.data_queue = queue.Queue()
        self.order_queue = queue.Queue()
        
        # 화면번호
        self.screen_no = 5000
        
        # 실행중인 전략
        self.active_strategies = {}
        
    def initialize(self):
        """초기화"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        try:
            self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        except Exception as e:
            print(f"[에러] 키움 OpenAPI 초기화 실패: {e}")
            print("[정보] 키움증권 OpenAPI가 설치되어 있는지 확인하세요")
            return False
        
        # 이벤트 연결
        try:
            self.ocx.OnEventConnect.connect(self._on_event_connect)
            self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
            self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
            self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan_data)
            self.ocx.OnReceiveMsg.connect(self._on_receive_msg)
        except AttributeError as e:
            print(f"[에러] 이벤트 연결 실패: {e}")
            print("[정보] 키움 OpenAPI OCX가 제대로 등록되지 않았습니다")
            return False
        
        print("[초기화] 키움 API 연결 준비 완료")
        return True
        
    def _on_event_connect(self, err_code):
        """로그인 이벤트"""
        if err_code == 0:
            print("[로그인] 성공")
            self.login_success = True
            
            # 계좌 정보 가져오기
            account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            self.account_no = account_list.split(';')[0]
            print(f"[계좌] {self.account_no}")
            
            # Supabase에 로그인 기록
            self._log_to_supabase("LOGIN", {"account": self.account_no})
        else:
            print(f"[로그인] 실패 (코드: {err_code})")
            self.login_success = False
        self.event_loop.exit()
        
    def _on_receive_real_data(self, jongmok_code, real_type, real_data):
        """실시간 데이터 수신"""
        if real_type == "주식체결":
            data = {
                "stock_code": jongmok_code,
                "timestamp": datetime.now().isoformat(),
                "current_price": abs(int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 10))),
                "change": int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 11)),
                "change_rate": float(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 12)),
                "volume": int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 15)),
                "accumulated_volume": int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 13)),
            }
            
            # 데이터 큐에 추가
            self.data_queue.put(data)
            
            # 시장 데이터 캐시 업데이트
            self._update_market_cache(data)
            
            # 전략 체크
            self._check_strategies(data)
            
    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결/잔고 데이터 수신"""
        if gubun == "0":  # 주문체결
            order_data = {
                "kiwoom_order_id": self.ocx.dynamicCall("GetChejanData(int)", 9203),
                "stock_code": self.ocx.dynamicCall("GetChejanData(int)", 9001),
                "stock_name": self.ocx.dynamicCall("GetChejanData(int)", 302),
                "order_status": self.ocx.dynamicCall("GetChejanData(int)", 913),
                "quantity": int(self.ocx.dynamicCall("GetChejanData(int)", 900)),
                "price": int(self.ocx.dynamicCall("GetChejanData(int)", 901)),
                "executed_quantity": int(self.ocx.dynamicCall("GetChejanData(int)", 911)),
                "executed_price": int(self.ocx.dynamicCall("GetChejanData(int)", 910))
            }
            
            # 주문 상태 업데이트
            self._update_order_status(order_data)
            
    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """메시지 수신"""
        print(f"[메시지] {msg}")
        
    def _on_receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        print(f"[TR수신] {rqname}")
        
    def login(self):
        """로그인"""
        if self.ocx.dynamicCall("GetConnectState()") == 0:
            print("[로그인] 시도중...")
            self.ocx.dynamicCall("CommConnect()")
            QTimer.singleShot(30000, self.event_loop.exit)
            self.event_loop.exec_()
        else:
            self.login_success = True
        return self.login_success
        
    def _update_market_cache(self, data):
        """시장 데이터 캐시 업데이트"""
        try:
            # 기존 캐시 검색
            existing = self.supabase.table('market_data_cache').select('*').eq(
                'stock_code', data['stock_code']
            ).execute()
            
            cache_data = {
                'stock_code': data['stock_code'],
                'current_price': data['current_price'],
                'volume': data['volume'],
                'fetched_at': datetime.now().isoformat(),
                'expires_at': (datetime.now().timestamp() + 60)  # 60초 후 만료
            }
            
            if existing.data:
                # 업데이트
                self.supabase.table('market_data_cache').update(cache_data).eq(
                    'stock_code', data['stock_code']
                ).execute()
            else:
                # 삽입
                self.supabase.table('market_data_cache').insert(cache_data).execute()
                
        except Exception as e:
            print(f"[에러] 캐시 업데이트 실패: {e}")
            
    def _check_strategies(self, market_data):
        """전략 조건 체크"""
        try:
            # 활성 전략 조회
            strategies = self.supabase.table('strategies').select('*').eq(
                'is_active', True
            ).execute()
            
            for strategy in strategies.data:
                self._evaluate_strategy(strategy, market_data)
                
        except Exception as e:
            print(f"[에러] 전략 체크 실패: {e}")
            
    def _evaluate_strategy(self, strategy, market_data):
        """전략 평가 및 신호 생성"""
        try:
            conditions = strategy.get('conditions', {})
            entry_conditions = conditions.get('entry', {})
            
            # 간단한 조건 체크 예시 (RSI < 30)
            # 실제로는 더 복잡한 로직 필요
            if self._check_entry_conditions(entry_conditions, market_data):
                signal = {
                    'strategy_id': strategy['id'],
                    'stock_code': market_data['stock_code'],
                    'signal_type': 'BUY',
                    'current_price': market_data['current_price'],
                    'volume': market_data['volume'],
                    'created_at': datetime.now().isoformat()
                }
                
                # 신호 저장
                result = self.supabase.table('trading_signals').insert(signal).execute()
                
                # 자동 주문 실행 (설정된 경우)
                if strategy.get('auto_execute', False):
                    self._execute_order(signal, strategy)
                    
        except Exception as e:
            print(f"[에러] 전략 평가 실패: {e}")
            
    def _check_entry_conditions(self, conditions, market_data):
        """진입 조건 체크"""
        # 여기에 실제 조건 체크 로직 구현
        # 예시로 항상 False 반환
        return False
        
    def _execute_order(self, signal, strategy):
        """주문 실행"""
        try:
            # 포지션 크기 계산
            position_size = strategy.get('position_size', 10)
            quantity = self._calculate_quantity(signal['current_price'], position_size)
            
            # 주문 전송
            order_result = self.send_order(
                code=signal['stock_code'],
                qty=quantity,
                price=signal['current_price'],
                order_type="1",  # 매수
                hoga_type="00"   # 지정가
            )
            
            if order_result == 0:
                # 주문 기록 저장
                order_data = {
                    'signal_id': signal.get('id'),
                    'strategy_id': strategy['id'],
                    'stock_code': signal['stock_code'],
                    'order_type': 'BUY',
                    'quantity': quantity,
                    'order_price': signal['current_price'],
                    'status': 'PENDING',
                    'order_time': datetime.now().isoformat()
                }
                
                self.supabase.table('orders').insert(order_data).execute()
                print(f"[주문] {signal['stock_code']} {quantity}주 매수 주문 전송")
                
        except Exception as e:
            print(f"[에러] 주문 실행 실패: {e}")
            
    def _calculate_quantity(self, price, position_size_percent):
        """주문 수량 계산"""
        # 간단한 계산 예시
        # 실제로는 계좌 잔고 조회 후 계산 필요
        total_balance = 10000000  # 1천만원 가정
        position_value = total_balance * (position_size_percent / 100)
        quantity = int(position_value / price)
        return max(1, quantity)
        
    def send_order(self, code, qty, price, order_type="1", hoga_type="00"):
        """주문 전송"""
        if not self.account_no:
            print("[에러] 계좌번호가 없습니다")
            return -1
            
        order_result = self.ocx.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            ["신규주문", self._get_screen_no(), self.account_no, int(order_type), 
             code, int(qty), int(price), hoga_type, ""]
        )
        
        return order_result
        
    def _update_order_status(self, order_data):
        """주문 상태 업데이트"""
        try:
            status_map = {
                "체결": "EXECUTED",
                "확인": "CONFIRMED",
                "접수": "PENDING",
                "취소": "CANCELLED"
            }
            
            status = status_map.get(order_data['order_status'], "UNKNOWN")
            
            # Supabase 업데이트
            self.supabase.table('orders').update({
                'status': status,
                'executed_quantity': order_data['executed_quantity'],
                'executed_price': order_data['executed_price'],
                'updated_at': datetime.now().isoformat()
            }).eq('kiwoom_order_id', order_data['kiwoom_order_id']).execute()
            
            print(f"[주문업데이트] {order_data['stock_name']} {status}")
            
        except Exception as e:
            print(f"[에러] 주문 상태 업데이트 실패: {e}")
            
    def _log_to_supabase(self, event_type, data):
        """이벤트 로깅"""
        try:
            log_data = {
                'event_type': event_type,
                'data': json.dumps(data),
                'timestamp': datetime.now().isoformat()
            }
            # 로그 테이블이 있다면 저장
            # self.supabase.table('system_logs').insert(log_data).execute()
        except Exception as e:
            print(f"[에러] 로깅 실패: {e}")
            
    def register_real_data(self, code_list: List[str]):
        """실시간 데이터 등록"""
        codes = ";".join(code_list)
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                           self._get_screen_no(), codes, "10;11;12;13;15;20", "0")
        print(f"[실시간등록] {codes}")
        
    def load_active_strategies(self):
        """활성 전략 로드"""
        try:
            result = self.supabase.table('strategies').select('*').eq(
                'is_active', True
            ).execute()
            
            for strategy in result.data:
                self.active_strategies[strategy['id']] = strategy
                print(f"[전략로드] {strategy['name']}")
                
                # 대상 종목 실시간 등록
                target_stocks = strategy.get('target_stocks', [])
                if target_stocks:
                    self.register_real_data(target_stocks)
                    
        except Exception as e:
            print(f"[에러] 전략 로드 실패: {e}")
            
    def get_positions(self):
        """현재 포지션 조회"""
        try:
            result = self.supabase.table('positions').select('*').eq(
                'is_active', True
            ).execute()
            
            print(f"\n[포지션 현황]")
            for pos in result.data:
                print(f"- {pos['stock_name']}: {pos['quantity']}주 @ {pos['avg_price']:,}원")
                
            return result.data
            
        except Exception as e:
            print(f"[에러] 포지션 조회 실패: {e}")
            return []
            
    def _get_screen_no(self):
        """화면번호 관리"""
        self.screen_no += 1
        if self.screen_no > 9999:
            self.screen_no = 5000
        return str(self.screen_no)
        
    def run(self):
        """메인 실행"""
        if not self.login():
            print("[에러] 로그인 실패")
            return
            
        print("\n=== 키움-Supabase 브릿지 실행 ===\n")
        
        # 활성 전략 로드
        self.load_active_strategies()
        
        # 현재 포지션 확인
        self.get_positions()
        
        print("\n실시간 모니터링 시작... (Ctrl+C로 종료)")
        
        try:
            while True:
                QApplication.processEvents()
                
                # 큐 처리
                while not self.data_queue.empty():
                    data = self.data_queue.get()
                    # 데이터 처리
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n종료 중...")
            
    def disconnect(self):
        """연결 종료"""
        if self.ocx:
            self.ocx.dynamicCall("CommTerminate()")
            print("[연결종료]")


if __name__ == "__main__":
    bridge = KiwoomSupabaseBridge()
    if bridge.initialize():
        bridge.run()
        bridge.disconnect()
    else:
        print("[에러] 초기화 실패로 프로그램을 종료합니다")
    sys.exit(0)