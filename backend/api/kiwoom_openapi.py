"""
키움증권 OpenAPI+ 실제 연동 (pykiwoom 사용)
"""
import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
import json

# PyQt5와 pykiwoom import
try:
    from PyQt5.QAxContainer import QAxWidget
    from PyQt5.QtCore import QEventLoop, QTimer
    from PyQt5.QtWidgets import QApplication
    from pykiwoom import Kiwoom
except ImportError:
    print("pykiwoom이 설치되어 있지 않습니다.")
    print("설치: pip install pykiwoom PyQt5")
    sys.exit(1)

# 환경변수에서 Supabase 클라이언트 가져오기
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.supabase_client import get_supabase_client


class KiwoomOpenAPI:
    """키움증권 OpenAPI+ 클래스"""
    
    def __init__(self):
        """키움 API 초기화"""
        # QApplication이 없으면 생성
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        self.kiwoom = Kiwoom()
        self.supabase = get_supabase_client()
        
        # 로그인 상태 확인
        self.connected = False
        
    def connect(self) -> bool:
        """키움 서버 접속"""
        try:
            # 자동 로그인 시도
            self.kiwoom.CommConnect()
            
            # 접속 대기 (최대 30초)
            for i in range(30):
                if self.kiwoom.GetConnectState() == 1:
                    self.connected = True
                    print("키움증권 OpenAPI+ 접속 성공")
                    
                    # 계좌 정보 가져오기
                    accounts = self.kiwoom.GetLoginInfo("ACCNO")
                    if accounts:
                        self.account = accounts.split(';')[0]
                        print(f"계좌번호: {self.account}")
                    
                    return True
                time.sleep(1)
                
            print("키움증권 OpenAPI+ 접속 실패 - 시간 초과")
            return False
            
        except Exception as e:
            print(f"접속 중 오류: {e}")
            return False
    
    def get_stock_name(self, code: str) -> str:
        """종목명 조회"""
        if not self.connected:
            return ""
        return self.kiwoom.GetMasterCodeName(code)
    
    def get_current_price(self, code: str) -> Dict:
        """현재가 조회"""
        if not self.connected:
            return {}
        
        try:
            # SetInputValue로 종목코드 설정
            self.kiwoom.SetInputValue("종목코드", code)
            
            # 현재가 조회 TR 요청 (opt10001)
            self.kiwoom.CommRqData("현재가조회", "opt10001", 0, "0101")
            
            # 데이터 수신 대기
            time.sleep(0.5)
            
            # 데이터 가져오기
            data = {
                'code': code,
                'name': self.get_stock_name(code),
                'current_price': abs(int(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "현재가"))),
                'change': int(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "전일대비")),
                'change_rate': float(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "등락율")),
                'volume': int(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "거래량")),
                'high': abs(int(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "고가"))),
                'low': abs(int(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "저가"))),
                'open': abs(int(self.kiwoom.GetCommData("opt10001", "현재가조회", 0, "시가")))
            }
            
            return data
            
        except Exception as e:
            print(f"현재가 조회 실패: {e}")
            return {}
    
    def get_ohlcv(self, code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """일봉 데이터 조회 (OHLCV)
        
        Args:
            code: 종목코드
            start_date: 시작일 (YYYYMMDD or YYYY-MM-DD)
            end_date: 종료일 (기본값: 오늘)
        """
        if not self.connected:
            return pd.DataFrame()
        
        try:
            # 날짜 형식 변환
            if '-' in start_date:
                start_date = start_date.replace('-', '')
            if end_date and '-' in end_date:
                end_date = end_date.replace('-', '')
            
            # 종료일이 없으면 오늘로 설정
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # pykiwoom의 block_request 사용
            df = self.kiwoom.block_request("opt10081",
                                          종목코드=code,
                                          기준일자=end_date,
                                          수정주가구분=1,
                                          output="주식일봉차트조회",
                                          next=0)
            
            if df is not None and not df.empty:
                # 컬럼명 변경
                df = df.rename(columns={
                    '일자': 'date',
                    '시가': 'open',
                    '고가': 'high',
                    '저가': 'low',
                    '현재가': 'close',
                    '거래량': 'volume'
                })
                
                # 날짜 형식 변환
                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
                
                # 시작일 이후 데이터만 필터링
                start_dt = pd.to_datetime(start_date, format='%Y%m%d')
                df = df[df['date'] >= start_dt]
                
                # 절대값 변환 (키움 API는 음수로 반환)
                for col in ['open', 'high', 'low', 'close']:
                    df[col] = df[col].abs()
                
                # 인덱스 설정
                df.set_index('date', inplace=True)
                df.sort_index(inplace=True)
                
                # trading_value 추가 (거래대금)
                df['trading_value'] = df['close'] * df['volume']
                
                return df
                
        except Exception as e:
            print(f"일봉 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_minute_data(self, code: str, interval: int = 1) -> pd.DataFrame:
        """분봉 데이터 조회
        
        Args:
            code: 종목코드
            interval: 분봉 간격 (1, 3, 5, 10, 15, 30, 45, 60)
        """
        if not self.connected:
            return pd.DataFrame()
        
        try:
            # TR 코드 매핑
            tr_map = {
                1: "opt10080",   # 1분봉
                3: "opt10081",   # 3분봉
                5: "opt10082",   # 5분봉
                10: "opt10083",  # 10분봉
                15: "opt10084",  # 15분봉
                30: "opt10085",  # 30분봉
                45: "opt10086",  # 45분봉
                60: "opt10087"   # 60분봉
            }
            
            tr_code = tr_map.get(interval, "opt10080")
            
            # 분봉 데이터 요청
            df = self.kiwoom.block_request(tr_code,
                                          종목코드=code,
                                          틱범위=interval,
                                          수정주가구분=1,
                                          output=f"주식분봉차트조회",
                                          next=0)
            
            if df is not None and not df.empty:
                # 데이터 가공
                df = df.rename(columns={
                    '체결시간': 'datetime',
                    '시가': 'open',
                    '고가': 'high',
                    '저가': 'low',
                    '현재가': 'close',
                    '거래량': 'volume'
                })
                
                # 절대값 변환
                for col in ['open', 'high', 'low', 'close']:
                    if col in df.columns:
                        df[col] = df[col].abs()
                
                return df
                
        except Exception as e:
            print(f"분봉 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_account_balance(self) -> Dict:
        """계좌 잔고 조회"""
        if not self.connected or not hasattr(self, 'account'):
            return {}
        
        try:
            # 계좌평가잔고내역 요청
            df = self.kiwoom.block_request("opw00018",
                                          계좌번호=self.account,
                                          비밀번호="",
                                          비밀번호입력매체구분="00",
                                          조회구분=1,
                                          output="계좌평가결과",
                                          next=0)
            
            if df is not None and not df.empty:
                # 첫 번째 행에서 요약 정보 추출
                summary = df.iloc[0]
                
                balance = {
                    'account_no': self.account,
                    'total_evaluation': int(summary.get('총평가금액', 0)),
                    'total_purchase': int(summary.get('총매입금액', 0)),
                    'total_profit_loss': int(summary.get('총평가손익금액', 0)),
                    'profit_rate': float(summary.get('총수익률(%)', 0)),
                    'deposit': int(summary.get('예수금', 0))
                }
                
                # 보유종목 조회
                stocks_df = self.kiwoom.block_request("opw00018",
                                                     계좌번호=self.account,
                                                     비밀번호="",
                                                     비밀번호입력매체구분="00",
                                                     조회구분=1,
                                                     output="계좌평가잔고개별합산",
                                                     next=0)
                
                if stocks_df is not None and not stocks_df.empty:
                    balance['stocks'] = stocks_df.to_dict('records')
                
                return balance
                
        except Exception as e:
            print(f"계좌 잔고 조회 실패: {e}")
            return {}
    
    def save_to_supabase(self, df: pd.DataFrame, stock_code: str) -> int:
        """주가 데이터를 Supabase에 저장"""
        try:
            records = []
            for index, row in df.iterrows():
                record = {
                    'stock_code': stock_code,
                    'date': index.strftime('%Y-%m-%d') if isinstance(index, pd.Timestamp) else str(index),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']),
                    'trading_value': int(row.get('trading_value', 0))
                }
                records.append(record)
            
            # Supabase에 upsert (중복 시 업데이트)
            result = self.supabase.table('price_data').upsert(records).execute()
            print(f"{len(records)}개 레코드를 Supabase에 저장")
            return len(records)
            
        except Exception as e:
            print(f"Supabase 저장 실패: {e}")
            return 0
    
    def get_from_supabase(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Supabase에서 주가 데이터 조회"""
        try:
            result = self.supabase.table('price_data').select('*')\
                .eq('stock_code', stock_code)\
                .gte('date', start_date)\
                .lte('date', end_date)\
                .order('date', desc=False)\
                .execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Supabase 조회 실패: {e}")
            return pd.DataFrame()


# 테스트 함수
def test_kiwoom_openapi():
    """키움증권 OpenAPI+ 테스트"""
    print("=" * 60)
    print("키움증권 OpenAPI+ 연동 테스트")
    print("=" * 60)
    
    # 키움 API 초기화
    kiwoom = KiwoomOpenAPI()
    
    # 1. 접속 테스트
    print("\n1. 키움증권 접속...")
    if not kiwoom.connect():
        print("   [실패] 키움증권 OpenAPI+ 접속 실패")
        print("   - KOA Studio가 실행 중인지 확인하세요")
        print("   - 키움증권 로그인이 되어있는지 확인하세요")
        return
    print("   [성공] 접속 완료")
    
    # 2. 종목명 조회
    print("\n2. 종목명 조회 테스트...")
    test_codes = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "035720": "카카오"
    }
    
    for code, expected_name in test_codes.items():
        name = kiwoom.get_stock_name(code)
        if name:
            print(f"   {code}: {name} [OK]")
        else:
            print(f"   {code}: 조회 실패 [FAIL]")
    
    # 3. 현재가 조회
    print("\n3. 현재가 조회 테스트...")
    current = kiwoom.get_current_price("005930")
    if current:
        print(f"   종목: {current.get('name')} ({current.get('code')})")
        print(f"   현재가: {current.get('current_price'):,}원")
        print(f"   전일대비: {current.get('change'):+,}원 ({current.get('change_rate'):+.2f}%)")
        print(f"   거래량: {current.get('volume'):,}주")
    else:
        print("   [실패] 현재가 조회 실패")
    
    # 4. 일봉 데이터 조회
    print("\n4. 일봉 데이터 조회 테스트...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    ohlcv = kiwoom.get_ohlcv(
        "005930",
        start_date.strftime('%Y%m%d'),
        end_date.strftime('%Y%m%d')
    )
    
    if not ohlcv.empty:
        print(f"   [성공] {len(ohlcv)}일 데이터 조회")
        print("\n   최근 5일 데이터:")
        print(ohlcv.tail())
        
        # Supabase 저장 테스트
        print("\n5. Supabase 저장 테스트...")
        saved = kiwoom.save_to_supabase(ohlcv, "005930")
        if saved > 0:
            print(f"   [성공] {saved}개 레코드 저장")
        else:
            print("   [실패] 저장 실패")
    else:
        print("   [실패] 일봉 데이터 조회 실패")
    
    # 6. 계좌 잔고 조회
    print("\n6. 계좌 잔고 조회 테스트...")
    balance = kiwoom.get_account_balance()
    if balance:
        print(f"   계좌번호: {balance.get('account_no')}")
        print(f"   총평가금액: {balance.get('total_evaluation'):,}원")
        print(f"   총매입금액: {balance.get('total_purchase'):,}원")
        print(f"   총손익: {balance.get('total_profit_loss'):+,}원")
        print(f"   수익률: {balance.get('profit_rate'):+.2f}%")
        print(f"   예수금: {balance.get('deposit'):,}원")
    else:
        print("   [실패] 계좌 잔고 조회 실패")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    test_kiwoom_openapi()