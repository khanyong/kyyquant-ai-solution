"""
키움 OpenAPI+ 데이터 다운로드 (핸들 오류 수정)
"""
import sys
import os
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
from PyQt5.QAxContainer import QAxWidget

class KiwoomDownloader:
    def __init__(self):
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.connected = False
        
        # 이벤트 루프
        self.login_event_loop = QEventLoop()
        self.request_loop = None
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self.on_event_connect)
        self.ocx.OnReceiveTrData.connect(self.on_receive_tr_data)
        
        self.data = []
        
    def comm_connect(self):
        """로그인"""
        self.ocx.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()
        
    def on_event_connect(self, err_code):
        """로그인 이벤트"""
        if err_code == 0:
            print("✅ 로그인 성공!")
            self.connected = True
        else:
            print(f"❌ 로그인 실패: {err_code}")
            self.connected = False
        
        self.login_event_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        print(f"데이터 수신: {rqname}")
        
        if self.request_loop is not None and self.request_loop.isRunning():
            self.request_loop.exit()
    
    def get_login_info(self, tag):
        """로그인 정보"""
        ret = self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
        return ret
    
    def get_code_list_by_market(self, market):
        """시장별 종목 코드"""
        ret = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        stock_list = ret.split(';')
        return stock_list[:-1]
    
    def get_master_code_name(self, code):
        """종목명"""
        ret = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return ret
    
    def set_input_value(self, id, value):
        """입력값 설정"""
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)
    
    def comm_rq_data(self, rqname, trcode, prev_next, screen_no):
        """TR 요청"""
        self.request_loop = QEventLoop()
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", 
                            rqname, trcode, prev_next, screen_no)
        self.request_loop.exec_()
    
    def get_comm_data(self, trcode, field_name, index, item_name):
        """수신 데이터 조회"""
        ret = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                  trcode, field_name, index, item_name)
        return ret.strip()
    
    def get_repeat_cnt(self, trcode, record_name):
        """반복 개수"""
        ret = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, record_name)
        return ret
    
    def download_daily_price(self, code):
        """일봉 데이터 다운로드"""
        print(f"\n📊 {code} 일봉 다운로드...")
        
        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", datetime.now().strftime("%Y%m%d"))
        self.set_input_value("수정주가구분", "1")
        
        self.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        
        # 데이터 수신 대기
        time.sleep(0.5)
        
        # 데이터 파싱
        data_cnt = self.get_repeat_cnt("opt10081", "주식일봉차트조회")
        
        result = []
        for i in range(min(data_cnt, 100)):  # 최근 100일만
            date = self.get_comm_data("opt10081", "주식일봉차트조회", i, "일자")
            open = self.get_comm_data("opt10081", "주식일봉차트조회", i, "시가")
            high = self.get_comm_data("opt10081", "주식일봉차트조회", i, "고가")
            low = self.get_comm_data("opt10081", "주식일봉차트조회", i, "저가")
            close = self.get_comm_data("opt10081", "주식일봉차트조회", i, "현재가")
            volume = self.get_comm_data("opt10081", "주식일봉차트조회", i, "거래량")
            
            result.append({
                'date': date,
                'open': abs(int(open)) if open else 0,
                'high': abs(int(high)) if high else 0,
                'low': abs(int(low)) if low else 0,
                'close': abs(int(close)) if close else 0,
                'volume': int(volume) if volume else 0
            })
        
        return result

def main():
    """메인 실행"""
    print("="*60)
    print("키움 OpenAPI+ 다운로드 (핸들 오류 수정)")
    print("="*60)
    
    # QApplication
    app = QApplication(sys.argv)
    
    # 다운로더
    downloader = KiwoomDownloader()
    
    # 로그인
    print("로그인 중...")
    downloader.comm_connect()
    
    if not downloader.connected:
        print("로그인 실패! 프로그램 종료")
        sys.exit(1)
    
    # 계좌 정보
    accounts = downloader.get_login_info("ACCNO")
    user_name = downloader.get_login_info("USER_NAME")
    print(f"사용자: {user_name}")
    print(f"계좌: {accounts}")
    
    # 주요 종목
    stocks = [
        ('005930', '삼성전자'),
        ('000660', 'SK하이닉스'),
        ('035720', '카카오'),
    ]
    
    # 저장 폴더
    output_dir = "D:/Dev/auto_stock/data/csv"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{len(stocks)}개 종목 다운로드 시작")
    print("-"*40)
    
    for code, name in stocks:
        try:
            print(f"\n[{code}] {name}")
            
            # 일봉 다운로드
            data = downloader.download_daily_price(code)
            
            if data:
                # CSV 저장
                import csv
                csv_file = f"{output_dir}/{code}_{name}.csv"
                
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
                    writer.writeheader()
                    writer.writerows(data)
                
                print(f"  ✓ 저장: {csv_file}")
                print(f"  ✓ 데이터: {len(data)}일")
            else:
                print(f"  ✗ 데이터 없음")
            
            time.sleep(1)  # API 제한
            
        except Exception as e:
            print(f"  ✗ 오류: {e}")
    
    print("\n" + "="*60)
    print("다운로드 완료!")
    print(f"저장 위치: {output_dir}")
    print("="*60)

if __name__ == "__main__":
    main()