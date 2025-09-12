"""
키움증권 Open API+ Windows 브릿지
PyQt5 기반 키움 API 래퍼 구현
"""

import sys
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication
import pandas as pd
import numpy as np
import websocket
from cryptography.fernet import Fernet
import logging
import requests

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kiwoom_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Order:
    """주문 데이터 클래스"""
    order_id: str
    symbol: str
    side: str  # buy/sell
    quantity: int
    price: float
    order_type: str  # market/limit
    strategy_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class Position:
    """포지션 데이터 클래스"""
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    profit_loss: float
    profit_loss_rate: float

@dataclass
class Balance:
    """계좌 잔고 데이터 클래스"""
    total_cash: float
    available_cash: float
    total_value: float
    stock_value: float
    profit_loss: float
    profit_loss_rate: float

class KiwoomAPI(QAxWidget):
    """키움 Open API+ 래퍼 클래스"""
    
    # 시그널 정의
    connected_signal = pyqtSignal(bool)
    order_signal = pyqtSignal(dict)
    realtime_signal = pyqtSignal(dict)
    
    def __init__(self, mode="paper", nas_url=None):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
        # 설정
        self.mode = mode  # paper or real
        self.nas_url = nas_url or "ws://localhost:8080/kiwoom"
        
        # 상태 관리
        self.connected = False
        self.account_number = ""
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.balance: Optional[Balance] = None
        
        # 이벤트 루프
        self.login_event_loop = None
        self.tr_event_loop = None
        
        # WebSocket 연결
        self.ws = None
        self.ws_thread = None
        
        # 이벤트 연결
        self._connect_events()
        
        # 에러 코드 매핑
        self.error_codes = {
            0: "정상처리",
            -100: "사용자정보교환실패",
            -101: "서버접속실패",
            -102: "버전처리실패",
            -200: "시세조회과부하",
            -201: "전문작성초기화실패",
            -202: "전문작성입력값오류",
            -203: "데이터없음",
            -204: "조회가능한종목수초과",
            -205: "데이터수신실패",
            -206: "조회가능한FID수초과",
            -207: "실시간해제오류",
            -300: "입력값오류",
            -301: "계좌비밀번호없음",
            -302: "타인계좌사용오류",
            -303: "주문가격이상한값입력",
            -304: "주문수량이상한값입력",
            -305: "주문수량300계약초과",
            -306: "주문수량500계약초과",
            -307: "주문전송실패",
            -308: "주문전송과부하",
            -309: "주문수량0계약이하"
        }
        
        logger.info(f"키움 API 초기화 완료 (모드: {self.mode})")
    
    def _connect_events(self):
        """이벤트 핸들러 연결"""
        self.OnEventConnect.connect(self.event_connect)
        self.OnReceiveTrData.connect(self.receive_tr_data)
        self.OnReceiveRealData.connect(self.receive_real_data)
        self.OnReceiveChejanData.connect(self.receive_chejan_data)
        self.OnReceiveMsg.connect(self.receive_msg)
        self.OnReceiveConditionVer.connect(self.receive_condition)
        self.OnReceiveTrCondition.connect(self.receive_tr_condition)
        self.OnReceiveRealCondition.connect(self.receive_real_condition)
    
    def connect_api(self):
        """키움 API 연결"""
        try:
            if self.mode == "paper":
                # 모의투자 서버 설정
                self.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
                
            ret = self.dynamicCall("CommConnect()")
            
            if ret == 0:
                self.login_event_loop = QEventLoop()
                self.login_event_loop.exec_()
                return self.connected
            else:
                logger.error(f"API 연결 실패: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"API 연결 중 오류: {e}")
            return False
    
    def event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            logger.info("키움 API 연결 성공")
            self.connected = True
            self.connected_signal.emit(True)
            
            # 계좌 정보 조회
            self.get_account_info()
            
            # NAS 서버 연결
            if self.nas_url:
                self.connect_to_nas()
        else:
            logger.error(f"키움 API 연결 실패: {self.error_codes.get(err_code, err_code)}")
            self.connected = False
            self.connected_signal.emit(False)
        
        if self.login_event_loop:
            self.login_event_loop.exit()
    
    def get_account_info(self):
        """계좌 정보 조회"""
        try:
            # 계좌 목록
            accounts = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            self.account_number = accounts.split(';')[0] if accounts else ""
            
            # 사용자 정보
            user_id = self.dynamicCall("GetLoginInfo(QString)", "USER_ID")
            user_name = self.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
            
            # 서버 구분
            server = self.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")
            server_type = "모의투자" if server == "1" else "실전투자"
            
            logger.info(f"계좌번호: {self.account_number}")
            logger.info(f"사용자: {user_name} ({user_id})")
            logger.info(f"서버: {server_type}")
            
            return {
                "account_number": self.account_number,
                "user_id": user_id,
                "user_name": user_name,
                "server_type": server_type
            }
            
        except Exception as e:
            logger.error(f"계좌 정보 조회 실패: {e}")
            return None
    
    def connect_to_nas(self):
        """NAS 서버와 WebSocket 연결"""
        try:
            self.ws = websocket.WebSocketApp(
                self.nas_url,
                on_open=self.on_nas_open,
                on_message=self.on_nas_message,
                on_error=self.on_nas_error,
                on_close=self.on_nas_close
            )
            
            # 별도 스레드에서 실행
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            logger.info(f"NAS 서버 연결 시작: {self.nas_url}")
            
        except Exception as e:
            logger.error(f"NAS 서버 연결 실패: {e}")
    
    def on_nas_open(self, ws):
        """NAS 연결 성공"""
        logger.info("NAS 서버 연결 성공")
        
        # 연결 알림
        self.send_to_nas({
            "type": "connection",
            "status": "connected",
            "mode": self.mode,
            "account": self.account_number
        })
    
    def on_nas_message(self, ws, message):
        """NAS로부터 메시지 수신"""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            logger.info(f"NAS 메시지 수신: {action}")
            
            if action == "place_order":
                self.place_order(data)
            elif action == "cancel_order":
                self.cancel_order(data)
            elif action == "modify_order":
                self.modify_order(data)
            elif action == "get_balance":
                self.get_balance()
            elif action == "get_positions":
                self.get_positions()
            elif action == "subscribe_real":
                self.subscribe_realtime(data.get("symbols", []))
            elif action == "unsubscribe_real":
                self.unsubscribe_realtime(data.get("symbols", []))
            elif action == "get_market_data":
                self.get_market_data(data)
                
        except Exception as e:
            logger.error(f"NAS 메시지 처리 오류: {e}")
    
    def on_nas_error(self, ws, error):
        """NAS 연결 에러"""
        logger.error(f"NAS 연결 에러: {error}")
    
    def on_nas_close(self, ws):
        """NAS 연결 종료"""
        logger.warning("NAS 서버 연결 종료")
        
        # 재연결 시도
        time.sleep(5)
        self.connect_to_nas()
    
    def send_to_nas(self, data):
        """NAS 서버로 데이터 전송"""
        try:
            if self.ws and self.ws.sock and self.ws.sock.connected:
                self.ws.send(json.dumps(data))
                logger.debug(f"NAS로 전송: {data.get('type')}")
            else:
                logger.warning("NAS 연결 끊김, 메시지 전송 실패")
                
        except Exception as e:
            logger.error(f"NAS 전송 오류: {e}")
    
    def place_order(self, order_data):
        """주문 실행"""
        try:
            # 주문 파라미터 준비
            rqname = "ORDER"
            screen_no = "0101"
            acc_no = self.account_number
            order_type = 1 if order_data["side"] == "buy" else 2  # 1:매수, 2:매도
            code = order_data["symbol"]
            qty = order_data["quantity"]
            price = int(order_data.get("price", 0))
            hoga = "03" if order_data.get("order_type") == "limit" else "03"  # 00:지정가, 03:시장가
            org_order_no = ""  # 원주문번호 (정정/취소시)
            
            # 주문 전송
            result = self.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                [rqname, screen_no, acc_no, order_type, code, qty, price, hoga, org_order_no]
            )
            
            if result != "":
                # 주문 저장
                order = Order(
                    order_id=order_data.get("order_id", result),
                    symbol=code,
                    side=order_data["side"],
                    quantity=qty,
                    price=price,
                    order_type=order_data.get("order_type", "limit"),
                    strategy_id=order_data.get("strategy_id"),
                    user_id=order_data.get("user_id")
                )
                self.orders[result] = order
                
                # NAS로 결과 전송
                self.send_to_nas({
                    "type": "order_result",
                    "order_id": order_data.get("order_id"),
                    "broker_order_id": result,
                    "status": "submitted",
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"주문 전송 성공: {code} {order_data['side']} {qty}주")
                return result
            else:
                raise Exception("주문 전송 실패")
                
        except Exception as e:
            logger.error(f"주문 실행 오류: {e}")
            
            # 실패 알림
            self.send_to_nas({
                "type": "order_result",
                "order_id": order_data.get("order_id"),
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return None
    
    def cancel_order(self, order_data):
        """주문 취소"""
        try:
            org_order_no = order_data["broker_order_id"]
            code = order_data["symbol"]
            
            # 취소 주문 전송
            result = self.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                ["CANCEL", "0102", self.account_number, 3, code, 0, 0, "00", org_order_no]
            )
            
            if result != "":
                self.send_to_nas({
                    "type": "cancel_result",
                    "order_id": order_data.get("order_id"),
                    "status": "cancelled",
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"주문 취소 성공: {org_order_no}")
                return True
            else:
                raise Exception("주문 취소 실패")
                
        except Exception as e:
            logger.error(f"주문 취소 오류: {e}")
            return False
    
    def get_balance(self):
        """계좌 잔고 조회"""
        try:
            # 입력값 설정
            self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
            self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
            self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
            self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
            
            # TR 요청
            ret = self.dynamicCall(
                "CommRqData(QString, QString, int, QString)",
                "계좌평가잔고내역", "opw00018", 0, "0101"
            )
            
            if ret == 0:
                self.tr_event_loop = QEventLoop()
                self.tr_event_loop.exec_()
                
                logger.info("잔고 조회 완료")
                return self.balance
            else:
                raise Exception(f"잔고 조회 실패: {ret}")
                
        except Exception as e:
            logger.error(f"잔고 조회 오류: {e}")
            return None
    
    def get_positions(self):
        """보유 종목 조회"""
        try:
            # 입력값 설정
            self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
            self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
            self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
            self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
            
            # TR 요청
            ret = self.dynamicCall(
                "CommRqData(QString, QString, int, QString)",
                "계좌평가잔고내역", "opw00018", 0, "0102"
            )
            
            if ret == 0:
                self.tr_event_loop = QEventLoop()
                self.tr_event_loop.exec_()
                
                logger.info(f"보유종목 {len(self.positions)}개 조회 완료")
                return list(self.positions.values())
            else:
                raise Exception(f"보유종목 조회 실패: {ret}")
                
        except Exception as e:
            logger.error(f"보유종목 조회 오류: {e}")
            return []
    
    def subscribe_realtime(self, symbols: List[str]):
        """실시간 데이터 구독"""
        try:
            if not symbols:
                return
            
            # 종목 코드 결합
            codes = ";".join(symbols)
            
            # FID 리스트 (현재가, 전일대비, 등락률, 거래량, 매도호가, 매수호가 등)
            fids = "10;11;12;13;14;15;16;17;18;20;21;22;23;24;25;26;27;28"
            
            # 실시간 등록
            ret = self.dynamicCall(
                "SetRealReg(QString, QString, QString, QString)",
                "0150", codes, fids, "0"
            )
            
            logger.info(f"실시간 구독: {len(symbols)}개 종목")
            
        except Exception as e:
            logger.error(f"실시간 구독 오류: {e}")
    
    def unsubscribe_realtime(self, symbols: List[str]):
        """실시간 데이터 구독 해제"""
        try:
            if not symbols:
                return
            
            codes = ";".join(symbols)
            
            self.dynamicCall("SetRealRemove(QString, QString)", "0150", codes)
            
            logger.info(f"실시간 구독 해제: {len(symbols)}개 종목")
            
        except Exception as e:
            logger.error(f"실시간 구독 해제 오류: {e}")
    
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        try:
            if rqname == "계좌평가잔고내역":
                self._process_balance_data(trcode)
            elif rqname == "주식기본정보":
                self._process_stock_info(trcode)
            elif rqname == "주식분봉차트":
                self._process_chart_data(trcode)
                
        except Exception as e:
            logger.error(f"TR 데이터 처리 오류: {e}")
        finally:
            if self.tr_event_loop:
                self.tr_event_loop.exit()
    
    def _process_balance_data(self, trcode):
        """잔고 데이터 처리"""
        try:
            # 계좌 정보
            total_buy = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                trcode, "", 0, "총매입금액")))
            total_eval = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                 trcode, "", 0, "총평가금액")))
            total_profit = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                   trcode, "", 0, "총평가손익금액")))
            total_profit_rate = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                      trcode, "", 0, "총수익률(%)"))
            available_cash = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                     trcode, "", 0, "예수금")))
            
            # Balance 객체 생성
            self.balance = Balance(
                total_cash=available_cash,
                available_cash=available_cash,
                total_value=total_eval,
                stock_value=total_eval - available_cash,
                profit_loss=total_profit,
                profit_loss_rate=total_profit_rate
            )
            
            # 보유종목 처리
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, "")
            
            self.positions.clear()
            for i in range(cnt):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                      trcode, "", i, "종목번호").strip()[1:]  # A 제거
                name = self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                      trcode, "", i, "종목명").strip()
                qty = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                              trcode, "", i, "보유수량")))
                buy_price = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                    trcode, "", i, "매입가")))
                current_price = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                        trcode, "", i, "현재가")))
                profit = abs(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                 trcode, "", i, "평가손익")))
                profit_rate = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                    trcode, "", i, "수익률(%)"))
                
                position = Position(
                    symbol=code,
                    quantity=qty,
                    avg_price=buy_price,
                    current_price=current_price,
                    profit_loss=profit,
                    profit_loss_rate=profit_rate
                )
                
                self.positions[code] = position
            
            # NAS로 전송
            self.send_to_nas({
                "type": "balance",
                "balance": asdict(self.balance),
                "positions": [asdict(p) for p in self.positions.values()],
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"잔고 데이터 처리 오류: {e}")
    
    def receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신"""
        try:
            if real_type == "주식체결":
                # 체결 데이터 파싱
                current_price = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 10)))
                change = int(self.dynamicCall("GetCommRealData(QString, int)", code, 11))
                change_rate = float(self.dynamicCall("GetCommRealData(QString, int)", code, 12))
                volume = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 15)))
                cumul_volume = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 13)))
                high = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 17)))
                low = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 18)))
                
                # NAS로 전송
                self.send_to_nas({
                    "type": "realtime_price",
                    "symbol": code,
                    "price": current_price,
                    "change": change,
                    "change_rate": change_rate,
                    "volume": volume,
                    "cumul_volume": cumul_volume,
                    "high": high,
                    "low": low,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif real_type == "주식호가잔량":
                # 호가 데이터 파싱
                ask_price1 = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 41)))
                ask_size1 = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 61)))
                bid_price1 = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 51)))
                bid_size1 = abs(int(self.dynamicCall("GetCommRealData(QString, int)", code, 71)))
                
                # NAS로 전송
                self.send_to_nas({
                    "type": "realtime_orderbook",
                    "symbol": code,
                    "ask_price1": ask_price1,
                    "ask_size1": ask_size1,
                    "bid_price1": bid_price1,
                    "bid_size1": bid_size1,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"실시간 데이터 처리 오류: {e}")
    
    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결/잔고 데이터 수신"""
        try:
            if gubun == "0":  # 주문체결
                # 체결 정보 파싱
                order_no = self.dynamicCall("GetChejanData(int)", 9203)
                code = self.dynamicCall("GetChejanData(int)", 9001)
                name = self.dynamicCall("GetChejanData(int)", 302)
                order_qty = abs(int(self.dynamicCall("GetChejanData(int)", 900)))
                order_price = abs(int(self.dynamicCall("GetChejanData(int)", 901)))
                executed_qty = abs(int(self.dynamicCall("GetChejanData(int)", 911)))
                executed_price = abs(int(self.dynamicCall("GetChejanData(int)", 910)))
                order_status = self.dynamicCall("GetChejanData(int)", 913)
                
                # 상태 매핑
                status_map = {
                    "접수": "submitted",
                    "체결": "executed",
                    "확인": "confirmed",
                    "취소": "cancelled",
                    "정정": "modified"
                }
                
                status = status_map.get(order_status, order_status)
                
                # NAS로 전송
                self.send_to_nas({
                    "type": "execution",
                    "order_no": order_no,
                    "symbol": code,
                    "name": name,
                    "order_qty": order_qty,
                    "order_price": order_price,
                    "executed_qty": executed_qty,
                    "executed_price": executed_price,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"체결: {name} {executed_qty}주 @ {executed_price}원")
                
            elif gubun == "1":  # 잔고변경
                # 잔고 업데이트 요청
                self.get_balance()
                
        except Exception as e:
            logger.error(f"체결 데이터 처리 오류: {e}")
    
    def receive_msg(self, screen_no, rqname, trcode, msg):
        """메시지 수신"""
        logger.info(f"메시지: {msg}")
        
        # NAS로 메시지 전송
        self.send_to_nas({
            "type": "message",
            "screen_no": screen_no,
            "rqname": rqname,
            "trcode": trcode,
            "message": msg,
            "timestamp": datetime.now().isoformat()
        })
    
    def receive_condition(self, ret, msg):
        """조건검색식 수신"""
        if ret == 1:
            logger.info("조건검색식 로드 성공")
        else:
            logger.error(f"조건검색식 로드 실패: {msg}")
    
    def receive_tr_condition(self, screen_no, code_list, condition_name, index, next):
        """조건검색 결과 수신"""
        if code_list:
            codes = code_list.split(';')[:-1]
            logger.info(f"조건검색 결과: {condition_name} - {len(codes)}개 종목")
            
            # NAS로 전송
            self.send_to_nas({
                "type": "condition_result",
                "condition_name": condition_name,
                "symbols": codes,
                "timestamp": datetime.now().isoformat()
            })
    
    def receive_real_condition(self, code, type, condition_name, condition_index):
        """실시간 조건검색 결과"""
        event_type = "진입" if type == "I" else "이탈"
        logger.info(f"조건검색 {event_type}: {condition_name} - {code}")
        
        # NAS로 전송
        self.send_to_nas({
            "type": "condition_real",
            "condition_name": condition_name,
            "symbol": code,
            "event": "enter" if type == "I" else "exit",
            "timestamp": datetime.now().isoformat()
        })


class KiwoomService:
    """키움 서비스 메인 클래스"""
    
    def __init__(self, mode="paper", nas_url=None):
        self.app = None
        self.kiwoom = None
        self.mode = mode
        self.nas_url = nas_url
    
    def start(self):
        """서비스 시작"""
        try:
            # Qt 애플리케이션 생성
            self.app = QApplication(sys.argv)
            
            # 키움 API 객체 생성
            self.kiwoom = KiwoomAPI(mode=self.mode, nas_url=self.nas_url)
            
            # API 연결
            if self.kiwoom.connect_api():
                logger.info("키움 서비스 시작")
                
                # 메인 루프 실행
                self.app.exec_()
            else:
                logger.error("키움 API 연결 실패, 서비스 종료")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"서비스 시작 실패: {e}")
            sys.exit(1)
    
    def stop(self):
        """서비스 종료"""
        try:
            if self.kiwoom and self.kiwoom.ws:
                self.kiwoom.ws.close()
            
            if self.app:
                self.app.quit()
            
            logger.info("키움 서비스 종료")
            
        except Exception as e:
            logger.error(f"서비스 종료 오류: {e}")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="키움증권 API 브릿지 서비스")
    parser.add_argument("--mode", choices=["paper", "real"], default="paper",
                       help="실행 모드 (paper: 모의투자, real: 실전투자)")
    parser.add_argument("--nas-url", default="ws://localhost:8080/kiwoom",
                       help="NAS 서버 WebSocket URL")
    
    args = parser.parse_args()
    
    # 서비스 시작
    service = KiwoomService(mode=args.mode, nas_url=args.nas_url)
    
    try:
        service.start()
    except KeyboardInterrupt:
        logger.info("사용자 중단")
        service.stop()
    except Exception as e:
        logger.error(f"예기치 않은 오류: {e}")
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()