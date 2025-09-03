import sys
import time
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication
import pandas as pd


class KiwoomAPI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.connected = False
        self.login_event_loop = QEventLoop()
        
        # Event handlers
        self.ocx.OnEventConnect.connect(self._on_event_connect)
        self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
        self.ocx.OnReceiveMsg.connect(self._on_receive_msg)
        self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan_data)
        
        # Data storage
        self.tr_data = {}
        self.real_data = {}
        self.order_data = {}
        
    def comm_connect(self):
        """로그인"""
        self.ocx.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()
        return self.connected
    
    def _on_event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            print("로그인 성공")
            self.connected = True
        else:
            print(f"로그인 실패: 에러코드 {err_code}")
            self.connected = False
        self.login_event_loop.exit()
    
    def get_login_info(self, tag):
        """로그인 정보 조회"""
        return self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
    
    def set_input_value(self, id, value):
        """TR 입력값 설정"""
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)
    
    def comm_rq_data(self, rq_name, tr_code, prev_next, screen_no):
        """TR 요청"""
        return self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", 
                                   rq_name, tr_code, prev_next, screen_no)
    
    def get_comm_data(self, tr_code, record_name, index, item_name):
        """TR 수신 데이터 조회"""
        data = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                   tr_code, record_name, index, item_name)
        return data.strip()
    
    def get_repeat_cnt(self, tr_code, record_name):
        """TR 수신 데이터 반복 개수"""
        return self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, record_name)
    
    def _on_receive_tr_data(self, screen_no, rq_name, tr_code, record_name, prev_next):
        """TR 데이터 수신 이벤트"""
        print(f"TR 데이터 수신: {rq_name}")
        
        # 예시: 계좌평가잔고내역 요청 처리
        if rq_name == "계좌평가잔고내역요청":
            self._process_balance_data(tr_code, record_name)
        elif rq_name == "주식기본정보요청":
            self._process_stock_info(tr_code, record_name)
            
    def _on_receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신 이벤트"""
        if real_type == "주식체결":
            self._process_real_stock_data(code, real_data)
    
    def _on_receive_msg(self, screen_no, rq_name, tr_code, msg):
        """메시지 수신 이벤트"""
        print(f"[{rq_name}] {msg}")
    
    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결/잔고 데이터 수신 이벤트"""
        if gubun == "0":  # 주문체결
            self._process_order_execution()
        elif gubun == "1":  # 잔고변경
            self._process_balance_change()
    
    def _process_balance_data(self, tr_code, record_name):
        """계좌평가잔고 데이터 처리"""
        cnt = self.get_repeat_cnt(tr_code, record_name)
        balance_list = []
        
        for i in range(cnt):
            data = {
                '종목코드': self.get_comm_data(tr_code, record_name, i, "종목번호"),
                '종목명': self.get_comm_data(tr_code, record_name, i, "종목명"),
                '보유수량': int(self.get_comm_data(tr_code, record_name, i, "보유수량")),
                '평균단가': int(self.get_comm_data(tr_code, record_name, i, "매입가")),
                '현재가': int(self.get_comm_data(tr_code, record_name, i, "현재가")),
                '평가손익': int(self.get_comm_data(tr_code, record_name, i, "평가손익")),
                '수익률': float(self.get_comm_data(tr_code, record_name, i, "수익률(%)"))
            }
            balance_list.append(data)
        
        self.tr_data['balance'] = pd.DataFrame(balance_list)
        print(f"잔고 데이터 {len(balance_list)}건 수신 완료")
    
    def _process_stock_info(self, tr_code, record_name):
        """주식 기본정보 처리"""
        stock_info = {
            '종목코드': self.get_comm_data(tr_code, record_name, 0, "종목코드"),
            '종목명': self.get_comm_data(tr_code, record_name, 0, "종목명"),
            '현재가': abs(int(self.get_comm_data(tr_code, record_name, 0, "현재가"))),
            '전일대비': int(self.get_comm_data(tr_code, record_name, 0, "전일대비")),
            '거래량': int(self.get_comm_data(tr_code, record_name, 0, "거래량")),
            '시가': abs(int(self.get_comm_data(tr_code, record_name, 0, "시가"))),
            '고가': abs(int(self.get_comm_data(tr_code, record_name, 0, "고가"))),
            '저가': abs(int(self.get_comm_data(tr_code, record_name, 0, "저가")))
        }
        self.tr_data['stock_info'] = stock_info
        print(f"주식 정보 수신: {stock_info['종목명']}")
    
    def _process_real_stock_data(self, code, real_data):
        """실시간 주식 체결 데이터 처리"""
        self.real_data[code] = {
            '체결시간': self.get_comm_real_data(code, 20),
            '현재가': abs(int(self.get_comm_real_data(code, 10))),
            '전일대비': int(self.get_comm_real_data(code, 11)),
            '등락율': float(self.get_comm_real_data(code, 12)),
            '거래량': int(self.get_comm_real_data(code, 15)),
            '누적거래량': int(self.get_comm_real_data(code, 13))
        }
    
    def _process_order_execution(self):
        """주문체결 처리"""
        order_no = self.get_chejan_data(9203)  # 주문번호
        stock_code = self.get_chejan_data(9001)  # 종목코드
        stock_name = self.get_chejan_data(302)  # 종목명
        order_qty = int(self.get_chejan_data(900))  # 주문수량
        order_price = int(self.get_chejan_data(901))  # 주문가격
        
        self.order_data[order_no] = {
            '종목코드': stock_code,
            '종목명': stock_name,
            '주문수량': order_qty,
            '주문가격': order_price,
            '체결시간': time.strftime('%Y%m%d%H%M%S')
        }
        print(f"주문체결: {stock_name} {order_qty}주 @ {order_price}원")
    
    def _process_balance_change(self):
        """잔고변경 처리"""
        stock_code = self.get_chejan_data(9001)
        current_qty = int(self.get_chejan_data(930))  # 보유수량
        available_qty = int(self.get_chejan_data(933))  # 주문가능수량
        
        print(f"잔고변경: {stock_code} 보유 {current_qty}주, 주문가능 {available_qty}주")
    
    def get_comm_real_data(self, code, fid):
        """실시간 데이터 조회"""
        return self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid).strip()
    
    def get_chejan_data(self, fid):
        """체결/잔고 데이터 조회"""
        return self.ocx.dynamicCall("GetChejanData(int)", fid).strip()
    
    def send_order(self, rq_name, screen_no, acc_no, order_type, code, qty, price, hoga_gb, org_order_no=""):
        """주문 전송
        
        order_type: 1(신규매수), 2(신규매도), 3(매수취소), 4(매도취소), 5(매수정정), 6(매도정정)
        hoga_gb: 00(지정가), 03(시장가)
        """
        return self.ocx.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [rq_name, screen_no, acc_no, order_type, code, qty, price, hoga_gb, org_order_no]
        )
    
    def set_real_reg(self, screen_no, code_list, fid_list, opt_type):
        """실시간 데이터 등록"""
        return self.ocx.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            screen_no, code_list, fid_list, opt_type
        )
    
    def disconnect_real_data(self, screen_no):
        """실시간 데이터 해제"""
        self.ocx.dynamicCall("DisconnectRealData(QString)", screen_no)
    
    def get_code_list_by_market(self, market):
        """시장별 종목코드 리스트 조회
        market: 0(코스피), 10(코스닥)
        """
        code_list = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        return code_list.split(';')[:-1]
    
    def get_master_code_name(self, code):
        """종목코드로 종목명 조회"""
        return self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
    
    def get_account_list(self):
        """계좌 리스트 조회"""
        account_list = self.get_login_info("ACCNO")
        return account_list.split(';')[:-1]
    
    def request_balance(self, account_no):
        """계좌평가잔고내역 요청"""
        self.set_input_value("계좌번호", account_no)
        self.set_input_value("비밀번호", "")
        self.set_input_value("비밀번호입력매체구분", "00")
        self.set_input_value("조회구분", "2")
        return self.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")
    
    def request_stock_info(self, code):
        """주식기본정보 요청"""
        self.set_input_value("종목코드", code)
        return self.comm_rq_data("주식기본정보요청", "opt10001", 0, "0101")
    
    def request_minute_data(self, code, tick="1"):
        """분봉 데이터 요청"""
        self.set_input_value("종목코드", code)
        self.set_input_value("틱범위", tick)
        self.set_input_value("수정주가구분", "1")
        return self.comm_rq_data("주식분봉차트조회요청", "opt10080", 0, "0200")


if __name__ == "__main__":
    # 사용 예시
    api = KiwoomAPI()
    
    # 로그인
    if api.comm_connect():
        # 계좌 리스트 조회
        accounts = api.get_account_list()
        print(f"계좌 리스트: {accounts}")
        
        if accounts:
            # 첫 번째 계좌의 잔고 조회
            api.request_balance(accounts[0])
            
            # 삼성전자 정보 조회
            api.request_stock_info("005930")
            
            # 실시간 데이터 등록 (삼성전자)
            api.set_real_reg("1000", "005930", "10;11;12;13;14;15", "0")
        
        # 이벤트 루프 실행
        api.app.exec_()