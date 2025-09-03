"""
키움증권 OpenAPI 트레이딩 API
실시간 데이터, 주문, 잔고 조회 기능
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

class KiwoomTradingAPI(QObject):
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
        self.request_data = {}
        self.real_data = {}
        self.screen_no = 5000  # 화면번호
        
    def initialize(self):
        """API 초기화"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self._on_event_connect)
        self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
        self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan_data)
        self.ocx.OnReceiveMsg.connect(self._on_receive_msg)
        
    def _on_event_connect(self, err_code):
        """로그인 이벤트"""
        if err_code == 0:
            print("[로그인] 성공")
            self.login_success = True
            
            # 계좌 정보 가져오기
            account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            self.account_no = account_list.split(';')[0]
            print(f"[계좌] {self.account_no}")
        else:
            print(f"[로그인] 실패 (코드: {err_code})")
            self.login_success = False
        self.event_loop.exit()
        
    def _on_receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        print(f"[TR수신] {rqname}")
        
        if rqname == "주식기본정보":
            self._process_stock_info(trcode)
        elif rqname == "계좌잔고":
            self._process_account_balance(trcode)
        elif rqname == "당일실현손익":
            self._process_daily_profit(trcode)
            
        self.request_data[rqname] = True
        
    def _on_receive_real_data(self, jongmok_code, real_type, real_data):
        """실시간 데이터 수신"""
        if real_type == "주식체결":
            data = {
                "종목코드": jongmok_code,
                "시간": self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 20),
                "현재가": abs(int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 10))),
                "전일대비": int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 11)),
                "등락율": float(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 12)),
                "거래량": int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 15)),
                "누적거래량": int(self.ocx.dynamicCall("GetCommRealData(QString, int)", jongmok_code, 13)),
            }
            print(f"[실시간] {jongmok_code} 현재가: {data['현재가']:,}원 ({data['등락율']:+.2f}%)")
            self.real_data[jongmok_code] = data
            self.data_received.emit(data)
            
    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결/잔고 데이터 수신"""
        if gubun == "0":  # 주문체결
            order_no = self.ocx.dynamicCall("GetChejanData(int)", 9203)
            종목코드 = self.ocx.dynamicCall("GetChejanData(int)", 9001)
            주문상태 = self.ocx.dynamicCall("GetChejanData(int)", 913)
            종목명 = self.ocx.dynamicCall("GetChejanData(int)", 302)
            주문수량 = int(self.ocx.dynamicCall("GetChejanData(int)", 900))
            주문가격 = int(self.ocx.dynamicCall("GetChejanData(int)", 901))
            
            print(f"[체결] {종목명} {주문상태} 수량:{주문수량} 가격:{주문가격}")
            
            self.order_completed.emit({
                "주문번호": order_no,
                "종목코드": 종목코드,
                "종목명": 종목명,
                "주문상태": 주문상태,
                "주문수량": 주문수량,
                "주문가격": 주문가격
            })
            
    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """메시지 수신"""
        print(f"[메시지] {msg}")
        
    def login(self):
        """로그인"""
        if self.ocx.dynamicCall("GetConnectState()") == 0:
            self.ocx.dynamicCall("CommConnect()")
            QTimer.singleShot(30000, self.event_loop.exit)
            self.event_loop.exec_()
        else:
            self.login_success = True
        return self.login_success
        
    def get_stock_info(self, code):
        """종목 기본정보 조회"""
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", 
                           "주식기본정보", "opt10001", 0, "0101")
        
    def _process_stock_info(self, trcode):
        """종목정보 처리"""
        종목코드 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                    trcode, "", 0, "종목코드").strip()
        종목명 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                  trcode, "", 0, "종목명").strip()
        현재가 = abs(int(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, "", 0, "현재가").strip()))
        전일대비 = int(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                        trcode, "", 0, "전일대비").strip())
        거래량 = int(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                      trcode, "", 0, "거래량").strip())
        
        print(f"\n[종목정보]")
        print(f"종목: {종목명}({종목코드})")
        print(f"현재가: {현재가:,}원")
        print(f"전일대비: {전일대비:+,}원")
        print(f"거래량: {거래량:,}")
        
    def register_real_data(self, code_list: List[str], fid_list="10;11;12;13;15;20"):
        """실시간 데이터 등록"""
        codes = ";".join(code_list)
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                           self._get_screen_no(), codes, fid_list, "0")
        print(f"[실시간등록] {codes}")
        
    def unregister_real_data(self, code_list: List[str]):
        """실시간 데이터 해제"""
        for code in code_list:
            self.ocx.dynamicCall("SetRealRemove(QString, QString)", 
                               self._get_screen_no(), code)
        print(f"[실시간해제] {';'.join(code_list)}")
        
    def send_order(self, code, qty, price, order_type="1", hoga_type="00"):
        """
        주문 전송
        order_type: 1-신규매수, 2-신규매도, 3-매수취소, 4-매도취소
        hoga_type: 00-지정가, 03-시장가
        """
        if not self.account_no:
            print("[에러] 계좌번호가 없습니다")
            return
            
        order_result = self.ocx.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            ["신규주문", "0101", self.account_no, int(order_type), code, 
             int(qty), int(price), hoga_type, ""]
        )
        
        if order_result == 0:
            print(f"[주문성공] {code} 수량:{qty} 가격:{price}")
        else:
            print(f"[주문실패] 에러코드:{order_result}")
            
        return order_result
        
    def get_balance(self):
        """계좌 잔고 조회"""
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_no)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", 
                           "계좌잔고", "opw00018", 0, "0102")
                           
    def _process_account_balance(self, trcode):
        """잔고 처리"""
        총매입 = int(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                      trcode, "", 0, "총매입금액").strip())
        총평가 = int(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                      trcode, "", 0, "총평가금액").strip())
        총손익 = int(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                      trcode, "", 0, "총평가손익금액").strip())
        수익률 = float(self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                        trcode, "", 0, "총수익률(%)").strip())
        
        print(f"\n[계좌잔고]")
        print(f"총매입: {총매입:,}원")
        print(f"총평가: {총평가:,}원")
        print(f"총손익: {총손익:+,}원")
        print(f"수익률: {수익률:+.2f}%")
        
    def _get_screen_no(self):
        """화면번호 관리"""
        self.screen_no += 1
        if self.screen_no > 9999:
            self.screen_no = 5000
        return str(self.screen_no)
        
    def disconnect(self):
        """연결 종료"""
        if self.ocx:
            self.ocx.dynamicCall("CommTerminate()")
            print("[연결종료]")


# 테스트 코드
if __name__ == "__main__":
    api = KiwoomTradingAPI()
    api.initialize()
    
    if api.login():
        print("\n=== 키움 트레이딩 API 준비 완료 ===\n")
        
        # 1. 종목정보 조회 (삼성전자)
        api.get_stock_info("005930")
        time.sleep(1)
        
        # 2. 실시간 데이터 등록
        api.register_real_data(["005930", "000660"])  # 삼성전자, SK하이닉스
        
        # 3. 계좌잔고 조회
        api.get_balance()
        
        # 4. 매수 주문 예시 (주석처리)
        # api.send_order("005930", 1, 60000, "1", "00")  # 삼성전자 1주 60,000원 지정가 매수
        
        print("\n실시간 데이터 수신 중... (Ctrl+C로 종료)")
        
        try:
            # 실시간 데이터 수신 대기
            while True:
                QApplication.processEvents()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n종료 중...")
            api.unregister_real_data(["005930", "000660"])
            api.disconnect()
    else:
        print("로그인 실패")
        
    sys.exit(0)