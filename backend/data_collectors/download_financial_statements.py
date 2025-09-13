"""
키움 OpenAPI+ 재무제표 다운로드
- 분기별, 연도별 재무제표
- 손익계산서, 재무상태표, 현금흐름표
"""
import sys
import os
import time
import json
import csv
from datetime import datetime, timedelta
import platform

# 32비트 Python 확인
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 32비트 Python 필요!")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

class FinancialStatementDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Statement Downloader")
        self.setGeometry(100, 100, 400, 300)
        
        # OCX 생성
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.setParent(self.central_widget)
        self.ocx.setGeometry(10, 10, 380, 280)
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self.on_event_connect)
        self.ocx.OnReceiveTrData.connect(self.on_receive_tr_data)
        
        # 이벤트 루프
        self.login_loop = QEventLoop()
        self.data_loop = QEventLoop()
        
        # 데이터 저장
        self.financial_data = {}
        self.quarterly_data = []
        self.yearly_data = []
        
        # 디렉토리
        self.financial_dir = "D:/Dev/auto_stock/data/financial_statements"
        self.quarterly_dir = f"{self.financial_dir}/quarterly"
        self.yearly_dir = f"{self.financial_dir}/yearly"
        self.progress_file = "financial_progress.json"
        
        # 진행 상태
        self.total_stocks = 0
        self.current_stock_idx = 0
        self.completed_stocks = []
        
        # 디렉토리 생성
        os.makedirs(self.quarterly_dir, exist_ok=True)
        os.makedirs(self.yearly_dir, exist_ok=True)
    
    def on_event_connect(self, err_code):
        """로그인 결과"""
        if err_code == 0:
            print("[OK] 로그인 성공")
        else:
            print(f"[FAIL] 로그인 실패: {err_code}")
        self.login_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rqname, trcode, recordname, 
                          prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        print(f"  데이터 수신: {rqname} ({trcode})")
        
        if trcode == "opt10015":  # 일별매매일지
            self.process_financial_summary(trcode, recordname)
        elif trcode == "opt10001":  # 주식기본정보
            self.process_basic_info(trcode, recordname)
        elif trcode == "OPT10056":  # 분기별 재무
            self.process_quarterly_financial(trcode, recordname)
        elif trcode == "OPT10057":  # 연도별 재무
            self.process_yearly_financial(trcode, recordname)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_basic_info(self, trcode, recordname):
        """주식 기본정보 처리"""
        try:
            # 기본 재무 정보
            fields = {
                "종목코드": "종목코드",
                "종목명": "종목명",
                "시가총액": "시가총액",
                "매출액": "매출액",
                "영업이익": "영업이익", 
                "당기순이익": "당기순이익",
                "PER": "PER",
                "PBR": "PBR",
                "ROE": "ROE",
                "EPS": "EPS",
                "BPS": "BPS",
                "매출액증가율": "매출액증가율",
                "영업이익증가율": "영업이익증가율",
                "순이익증가율": "순이익증가율",
                "부채비율": "부채비율",
                "유보율": "유보율",
                "유동비율": "유동비율",
                "배당수익률": "배당수익률"
            }
            
            for key, field in fields.items():
                value = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, 0, field).strip()
                self.financial_data[key] = value
                
        except Exception as e:
            print(f"  기본정보 처리 오류: {e}")
    
    def process_quarterly_financial(self, trcode, recordname):
        """분기별 재무제표 처리"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(min(cnt, 20)):  # 최근 20개 분기 (5년)
                quarter_data = {}
                
                # 분기 정보
                quarter_data['결산월'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "결산월").strip()
                
                # 손익계산서 항목
                quarter_data['매출액'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "매출액").strip()
                
                quarter_data['영업이익'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "영업이익").strip()
                
                quarter_data['당기순이익'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "당기순이익").strip()
                
                # 재무상태표 항목
                quarter_data['자산총계'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "자산총계").strip()
                
                quarter_data['부채총계'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "부채총계").strip()
                
                quarter_data['자본총계'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "자본총계").strip()
                
                quarter_data['유동자산'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "유동자산").strip()
                
                quarter_data['유동부채'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "유동부채").strip()
                
                # 재무비율
                quarter_data['ROE'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "ROE(%)").strip()
                
                quarter_data['ROA'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "ROA(%)").strip()
                
                quarter_data['부채비율'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "부채비율").strip()
                
                quarter_data['유동비율'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "유동비율").strip()
                
                quarter_data['영업이익률'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "영업이익률").strip()
                
                quarter_data['순이익률'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "순이익률").strip()
                
                # 주당지표
                quarter_data['EPS'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "EPS(원)").strip()
                
                quarter_data['BPS'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "BPS(원)").strip()
                
                if quarter_data['결산월']:
                    self.quarterly_data.append(quarter_data)
                    
        except Exception as e:
            print(f"  분기 재무 처리 오류: {e}")
    
    def process_yearly_financial(self, trcode, recordname):
        """연도별 재무제표 처리"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(min(cnt, 10)):  # 최근 10년
                yearly_data = {}
                
                # 연도 정보
                yearly_data['회계연도'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "회계연도").strip()
                
                # 손익계산서 (연간)
                yearly_data['매출액'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "매출액").strip()
                
                yearly_data['매출원가'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "매출원가").strip()
                
                yearly_data['매출총이익'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "매출총이익").strip()
                
                yearly_data['판관비'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "판관비").strip()
                
                yearly_data['영업이익'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "영업이익").strip()
                
                yearly_data['당기순이익'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "당기순이익").strip()
                
                # 재무상태표 (연간)
                yearly_data['자산총계'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "자산총계").strip()
                
                yearly_data['부채총계'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "부채총계").strip()
                
                yearly_data['자본총계'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "자본총계").strip()
                
                # 현금흐름표
                yearly_data['영업활동현금흐름'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "영업활동현금흐름").strip()
                
                yearly_data['투자활동현금흐름'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "투자활동현금흐름").strip()
                
                yearly_data['재무활동현금흐름'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "재무활동현금흐름").strip()
                
                # 성장률
                yearly_data['매출액증가율'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "매출액증가율").strip()
                
                yearly_data['영업이익증가율'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "영업이익증가율").strip()
                
                yearly_data['순이익증가율'] = self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", 
                    trcode, recordname, i, "순이익증가율").strip()
                
                if yearly_data['회계연도']:
                    self.yearly_data.append(yearly_data)
                    
        except Exception as e:
            print(f"  연도별 재무 처리 오류: {e}")
    
    def process_financial_summary(self, trcode, recordname):
        """재무 요약 정보 처리"""
        try:
            # 최신 재무 요약
            self.financial_data['매출액'] = self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)", 
                trcode, recordname, 0, "매출액").strip()
            
            self.financial_data['영업이익'] = self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)", 
                trcode, recordname, 0, "영업이익").strip()
            
            self.financial_data['당기순이익'] = self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)", 
                trcode, recordname, 0, "당기순이익").strip()
                
        except Exception as e:
            print(f"  재무 요약 처리 오류: {e}")
    
    def login(self):
        """로그인"""
        print("\n로그인 중...")
        self.ocx.dynamicCall("CommConnect()")
        QTimer.singleShot(30000, self.login_loop.quit)
        self.login_loop.exec_()
        
        state = self.ocx.dynamicCall("GetConnectState()")
        return state == 1
    
    def get_all_stocks(self):
        """전체 종목 리스트"""
        stocks = []
        
        # KOSPI
        kospi = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "0")
        kospi_list = kospi.split(';')[:-1]
        
        for code in kospi_list:
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            if name and not any(x in name for x in ['ETF', 'ETN', '리츠', '스팩']):
                stocks.append({'code': code, 'name': name, 'market': 'KOSPI'})
        
        # KOSDAQ  
        kosdaq = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "10")
        kosdaq_list = kosdaq.split(';')[:-1]
        
        for code in kosdaq_list:
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            if name and not any(x in name for x in ['ETF', 'ETN', '리츠', '스팩']):
                stocks.append({'code': code, 'name': name, 'market': 'KOSDAQ'})
        
        return stocks
    
    def load_progress(self):
        """진행 상태 로드"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                self.completed_stocks = progress.get('completed', [])
                return progress.get('last_index', 0)
        return 0
    
    def save_progress(self):
        """진행 상태 저장"""
        progress = {
            'last_index': self.current_stock_idx,
            'completed': self.completed_stocks,
            'total': self.total_stocks,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def download_stock_financial_statements(self, code, name, market):
        """종목별 재무제표 다운로드"""
        self.financial_data = {}
        self.quarterly_data = []
        self.yearly_data = []
        
        # 1. 주식 기본정보 조회
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "주식기본정보", "opt10001", 0, "0101")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
        
        time.sleep(0.3)
        
        # 2. 재무정보 조회 (opt10015)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "결산월", "")
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "재무정보", "opt10015", 0, "0102")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
        
        # 3. 분기별 재무 데이터 저장
        if self.quarterly_data:
            csv_file = f"{self.quarterly_dir}/{code}_{name}_{market}_quarterly.csv"
            
            fieldnames = ['결산월', '매출액', '영업이익', '당기순이익', 
                         '자산총계', '부채총계', '자본총계',
                         '유동자산', '유동부채', 'ROE', 'ROA', 
                         '부채비율', '유동비율', '영업이익률', '순이익률',
                         'EPS', 'BPS']
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(self.quarterly_data)
            
            print(f"    분기별: {len(self.quarterly_data)}개 분기 저장")
        
        # 4. 연도별 재무 데이터 저장
        if self.yearly_data:
            csv_file = f"{self.yearly_dir}/{code}_{name}_{market}_yearly.csv"
            
            fieldnames = ['회계연도', '매출액', '매출원가', '매출총이익', '판관비',
                         '영업이익', '당기순이익', '자산총계', '부채총계', '자본총계',
                         '영업활동현금흐름', '투자활동현금흐름', '재무활동현금흐름',
                         '매출액증가율', '영업이익증가율', '순이익증가율']
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(self.yearly_data)
            
            print(f"    연도별: {len(self.yearly_data)}개년 저장")
        
        # 5. 최신 요약 정보 저장
        if self.financial_data:
            csv_file = f"{self.financial_dir}/{code}_{name}_{market}_summary.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['항목', '값', '날짜'])
                for key, value in self.financial_data.items():
                    writer.writerow([key, value, datetime.now().strftime("%Y%m%d")])
            
            print(f"    요약: 최신 재무정보 저장")
        
        return bool(self.quarterly_data or self.yearly_data or self.financial_data)
    
    def download_all_financial_statements(self):
        """전체 재무제표 다운로드"""
        print("\n종목 리스트 조회 중...")
        all_stocks = self.get_all_stocks()
        self.total_stocks = len(all_stocks)
        
        print(f"전체 종목: {self.total_stocks}개")
        
        # 이전 진행 상태 로드
        start_idx = self.load_progress()
        if start_idx > 0:
            print(f"이전 진행: {start_idx}/{self.total_stocks}")
            print(f"완료된 종목: {len(self.completed_stocks)}개")
        
        print("\n재무제표 다운로드 시작...")
        print("="*60)
        
        # 다운로드 실행 (테스트용 100개만)
        for idx in range(start_idx, min(self.total_stocks, start_idx + 100)):
            stock = all_stocks[idx]
            code = stock['code']
            name = stock['name']
            market = stock['market']
            
            # 이미 완료된 종목 스킵
            if code in self.completed_stocks:
                continue
            
            self.current_stock_idx = idx
            
            # 진행률 표시
            percent = (idx / self.total_stocks) * 100
            print(f"\n[{idx+1}/{self.total_stocks}] {percent:.1f}% - {code} {name} ({market})")
            
            try:
                # 재무제표 다운로드
                if self.download_stock_financial_statements(code, name, market):
                    print(f"  [OK] 재무제표 저장 완료")
                    self.completed_stocks.append(code)
                else:
                    print(f"  [SKIP] 재무 데이터 없음")
                
                # 진행 상태 저장 (10개마다)
                if idx % 10 == 0:
                    self.save_progress()
                
                # API 제한 대응
                time.sleep(0.5)
                
                # 1분에 60건 제한
                if (idx + 1) % 60 == 0:
                    print("\n[대기] API 제한 - 60초 대기...")
                    time.sleep(60)
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
            
            # 중단 확인
            QApplication.processEvents()
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*60)
        print(f"재무제표 다운로드 완료!")
        print(f"완료: {len(self.completed_stocks)}개")
        print(f"분기별: {self.quarterly_dir}")
        print(f"연도별: {self.yearly_dir}")
        print("="*60)

def main():
    """메인 실행"""
    print("="*60)
    print("키움 재무제표 다운로드")
    print("="*60)
    print("\n다운로드 항목:")
    print("【분기별 재무제표】")
    print("  - 최근 5년 (20개 분기)")
    print("  - 손익계산서: 매출액, 영업이익, 당기순이익")
    print("  - 재무상태표: 자산, 부채, 자본")
    print("  - 재무비율: ROE, ROA, 부채비율 등")
    print("\n【연도별 재무제표】")
    print("  - 최근 10년")
    print("  - 손익계산서 (연간 전체)")
    print("  - 재무상태표 (연말 기준)")
    print("  - 현금흐름표")
    print("  - 성장률 지표")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    downloader = FinancialStatementDownloader()
    downloader.show()
    
    # 로그인
    if downloader.login():
        user_name = downloader.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        print(f"사용자: {user_name}")
        
        # 다운로드 실행
        downloader.download_all_financial_statements()
    else:
        print("로그인 실패")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()