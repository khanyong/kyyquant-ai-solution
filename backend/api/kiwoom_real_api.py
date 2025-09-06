"""
키움증권(한국투자증권) OpenAPI 실제 연동
"""
import requests
import json
import hashlib
import os
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import time

# 환경변수 로드
load_dotenv()

class KiwoomRealAPI:
    """한국투자증권 OpenAPI 클라이언트"""
    
    def __init__(self):
        # API 설정
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account = os.getenv('KIWOOM_ACCOUNT', '')
        self.base_url = os.getenv('KIWOOM_API_URL', 'https://openapivts.koreainvestment.com:29443')
        
        self.access_token = None
        self.token_expires = None
        
        # 요청 제한 관리
        self.last_request_time = 0
        self.request_count = 0
        
    def _make_hash(self, data: Dict) -> str:
        """해시 생성 (일부 API 요청 시 필요)"""
        data_str = json.dumps(data, ensure_ascii=False).encode()
        hash_obj = hashlib.sha256(data_str)
        return hash_obj.hexdigest()
    
    def _rate_limit(self):
        """API 요청 제한 관리 (초당 20회)"""
        current_time = time.time()
        if current_time - self.last_request_time < 0.05:  # 50ms 간격
            time.sleep(0.05)
        self.last_request_time = time.time()
    
    def authenticate(self) -> bool:
        """API 인증 및 액세스 토큰 발급"""
        try:
            # 이미 유효한 토큰이 있는지 확인
            if self.access_token and self.token_expires:
                if datetime.now() < self.token_expires:
                    return True
            
            url = f"{self.base_url}/oauth2/tokenP"
            headers = {'Content-Type': 'application/json'}
            body = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            self._rate_limit()
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                # 토큰 유효기간 설정 (보통 24시간)
                expires_in = data.get('expires_in', 86400)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                print(f"인증 성공. 토큰 유효기간: {self.token_expires}")
                return True
            else:
                print(f"인증 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"인증 중 오류 발생: {e}")
            return False
    
    def get_current_price(self, stock_code: str) -> Dict:
        """현재가 조회"""
        if not self.authenticate():
            return {}
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            params = {
                "fid_cond_mrkt_div_code": "J",  # 주식
                "fid_input_iscd": stock_code
            }
            
            self._rate_limit()
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('rt_cd') == '0':
                    output = data.get('output', {})
                    return {
                        'stock_code': stock_code,
                        'current_price': int(output.get('stck_prpr', 0)),  # 현재가
                        'change': int(output.get('prdy_vrss', 0)),  # 전일대비
                        'change_rate': float(output.get('prdy_ctrt', 0)),  # 전일대비율
                        'volume': int(output.get('acml_vol', 0)),  # 누적거래량
                        'high': int(output.get('stck_hgpr', 0)),  # 최고가
                        'low': int(output.get('stck_lwpr', 0)),  # 최저가
                        'open': int(output.get('stck_oprc', 0))  # 시가
                    }
            return {}
            
        except Exception as e:
            print(f"현재가 조회 실패: {e}")
            return {}
    
    def get_daily_price(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """일봉 데이터 조회"""
        if not self.authenticate():
            return pd.DataFrame()
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST03010100"
            }
            
            # 날짜 형식: YYYYMMDD
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": stock_code,
                "fid_input_date_1": start_date,
                "fid_input_date_2": end_date,
                "fid_period_div_code": "D",  # 일봉
                "fid_org_adj_prc": "0"  # 수정주가 여부
            }
            
            self._rate_limit()
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('rt_cd') == '0':
                    output2 = data.get('output2', [])
                    
                    if output2:
                        # 데이터프레임 생성
                        df = pd.DataFrame(output2)
                        
                        # 컬럼 이름 변경
                        column_mapping = {
                            'stck_bsop_date': 'date',  # 날짜
                            'stck_oprc': 'open',  # 시가
                            'stck_hgpr': 'high',  # 고가
                            'stck_lwpr': 'low',  # 저가
                            'stck_clpr': 'close',  # 종가
                            'acml_vol': 'volume',  # 거래량
                            'acml_tr_pbmn': 'trading_value'  # 거래대금
                        }
                        
                        df = df.rename(columns=column_mapping)
                        
                        # 필요한 컬럼만 선택
                        columns_to_keep = ['date', 'open', 'high', 'low', 'close', 'volume', 'trading_value']
                        df = df[columns_to_keep]
                        
                        # 데이터 타입 변환
                        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
                        for col in ['open', 'high', 'low', 'close']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').astype('int64')
                        df['trading_value'] = pd.to_numeric(df['trading_value'], errors='coerce').astype('int64')
                        
                        # 날짜로 인덱스 설정
                        df.set_index('date', inplace=True)
                        df.sort_index(inplace=True)
                        
                        return df
                        
                else:
                    print(f"API 오류: {data.get('msg1')}")
                    
            return pd.DataFrame()
            
        except Exception as e:
            print(f"일봉 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_minute_price(self, stock_code: str, interval: int = 1) -> pd.DataFrame:
        """분봉 데이터 조회"""
        if not self.authenticate():
            return pd.DataFrame()
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST03010200"
            }
            
            # 분봉 구분: 1, 3, 5, 10, 15, 30, 60
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": stock_code,
                "fid_hour_cls_code": str(interval),
                "fid_pw_data_incu_yn": "N"
            }
            
            self._rate_limit()
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('rt_cd') == '0':
                    output2 = data.get('output2', [])
                    
                    if output2:
                        df = pd.DataFrame(output2)
                        # 분봉 데이터 처리
                        return df
                        
            return pd.DataFrame()
            
        except Exception as e:
            print(f"분봉 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_balance(self) -> Dict:
        """계좌 잔고 조회"""
        if not self.authenticate():
            return {}
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "TTTC8434R" if 'vts' in self.base_url else "TTTC8434R"
            }
            
            params = {
                "CANO": self.account[:8],  # 계좌번호 앞 8자리
                "ACNT_PRDT_CD": self.account[8:] if len(self.account) > 8 else "01",  # 계좌상품코드
                "AFHR_FLPR_YN": "N",  # 시간외단일가여부
                "OFL_YN": "N",  # 오프라인여부
                "INQR_DVSN": "01",  # 조회구분
                "UNPR_DVSN": "01",  # 단가구분
                "FUND_STTL_ICLD_YN": "N",  # 펀드결제분포함여부
                "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액자동상환여부
                "PRCS_DVSN": "01",  # 처리구분
                "CTX_AREA_FK100": "",  # 연속조회검색조건100
                "CTX_AREA_NK100": ""  # 연속조회키100
            }
            
            self._rate_limit()
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('rt_cd') == '0':
                    output1 = data.get('output1', [])
                    output2 = data.get('output2', [])
                    
                    # 계좌 요약 정보
                    if output2:
                        summary = output2[0]
                        return {
                            'total_evaluation': int(summary.get('tot_evlu_amt', 0)),  # 총평가금액
                            'total_purchase': int(summary.get('pchs_amt_smtl_amt', 0)),  # 총매입금액
                            'total_profit_loss': int(summary.get('evlu_pfls_smtl_amt', 0)),  # 총평가손익
                            'deposit': int(summary.get('dnca_tot_amt', 0)),  # 예수금
                            'stocks': output1  # 보유종목 리스트
                        }
                        
            return {}
            
        except Exception as e:
            print(f"잔고 조회 실패: {e}")
            return {}


# 실제 API 테스트 함수
def test_real_kiwoom_api():
    """실제 키움증권 API 테스트"""
    print("=" * 60)
    print("한국투자증권 OpenAPI 실제 연동 테스트")
    print("=" * 60)
    
    api = KiwoomRealAPI()
    
    if not api.app_key or not api.app_secret:
        print("\n[오류] API 키가 설정되지 않았습니다.")
        print("backend/.env 파일에 다음 정보를 입력하세요:")
        print("  KIWOOM_APP_KEY=발급받은_앱_키")
        print("  KIWOOM_APP_SECRET=발급받은_앱_시크릿")
        print("\n키 발급: https://apiportal.koreainvestment.com")
        return
    
    # 1. 인증 테스트
    print("\n1. API 인증 테스트...")
    if api.authenticate():
        print("   [성공] 액세스 토큰 발급 완료")
    else:
        print("   [실패] 인증 실패 - API 키를 확인하세요")
        return
    
    # 2. 현재가 조회 테스트
    print("\n2. 현재가 조회 테스트...")
    stock_code = "005930"  # 삼성전자
    current_price = api.get_current_price(stock_code)
    
    if current_price:
        print(f"   [성공] {stock_code} 현재가 조회")
        print(f"   - 현재가: {current_price['current_price']:,}원")
        print(f"   - 전일대비: {current_price['change']:+,}원 ({current_price['change_rate']:+.2f}%)")
        print(f"   - 거래량: {current_price['volume']:,}주")
    else:
        print("   [실패] 현재가 조회 실패")
    
    # 3. 일봉 데이터 조회 테스트
    print("\n3. 일봉 데이터 조회 테스트...")
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    daily_data = api.get_daily_price(stock_code, start_date, end_date)
    
    if not daily_data.empty:
        print(f"   [성공] {len(daily_data)}일간 데이터 조회")
        print("\n   최근 5일 데이터:")
        print(daily_data.tail())
    else:
        print("   [실패] 일봉 데이터 조회 실패")
    
    # 4. 계좌 잔고 조회 (계좌번호가 설정된 경우)
    if api.account:
        print("\n4. 계좌 잔고 조회 테스트...")
        balance = api.get_balance()
        
        if balance:
            print("   [성공] 계좌 잔고 조회")
            print(f"   - 총평가금액: {balance.get('total_evaluation', 0):,}원")
            print(f"   - 예수금: {balance.get('deposit', 0):,}원")
            print(f"   - 총손익: {balance.get('total_profit_loss', 0):+,}원")
        else:
            print("   [실패] 계좌 잔고 조회 실패")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    test_real_kiwoom_api()