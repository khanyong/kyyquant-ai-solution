"""
키움 OpenAPI+ 데이터를 로컬 PC에 다운로드
CSV 파일과 SQLite DB로 저장
"""
import sys
import os
import time
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any

# PyQt5 imports
from PyQt5.QWidgets import QApplication
from PyQt5.QtCore import QEventLoop

# pykiwoom imports
from pykiwoom.kiwoom import Kiwoom

class LocalDataDownloader:
    def __init__(self):
        """로컬 데이터 다운로더 초기화"""
        # 데이터 저장 경로
        self.data_dir = "D:/Dev/auto_stock/data"
        self.csv_dir = f"{self.data_dir}/csv"
        self.db_path = f"{self.data_dir}/kiwoom_data.db"
        
        # 디렉토리 생성
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(f"{self.csv_dir}/daily", exist_ok=True)
        os.makedirs(f"{self.csv_dir}/minute", exist_ok=True)
        os.makedirs(f"{self.csv_dir}/financial", exist_ok=True)
        
        # SQLite 연결
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
        
        # PyQt 앱 생성
        self.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # 키움 API 연결
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect()
        
        print("✅ 키움 OpenAPI+ 연결 완료")
        print(f"📁 데이터 저장 경로: {self.data_dir}")
        print(f"🗄️ SQLite DB: {self.db_path}")
        
    def create_tables(self):
        """SQLite 테이블 생성"""
        cursor = self.conn.cursor()
        
        # 종목 마스터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_master (
                stock_code TEXT PRIMARY KEY,
                stock_name TEXT NOT NULL,
                market TEXT,
                sector_name TEXT,
                listing_date TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 일봉 데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                trade_date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                trading_value INTEGER,
                UNIQUE(stock_code, trade_date)
            )
        ''')
        
        # 분봉 데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_minute (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                trade_time TIMESTAMP NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(stock_code, trade_time)
            )
        ''')
        
        # 재무 정보
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_ratio (
                stock_code TEXT PRIMARY KEY,
                per REAL,
                pbr REAL,
                roe REAL,
                roa REAL,
                eps INTEGER,
                bps INTEGER,
                dividend_yield REAL,
                debt_ratio REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✅ SQLite 테이블 생성 완료")
    
    def get_stock_list(self, market: str = "0") -> List[Dict]:
        """종목 리스트 조회"""
        print(f"\n📊 {'코스피' if market == '0' else '코스닥'} 종목 리스트 다운로드 중...")
        
        code_list = self.kiwoom.GetCodeListByMarket(market)
        stock_list = []
        
        for i, code in enumerate(code_list):
            name = self.kiwoom.GetMasterCodeName(code)
            
            # ETF, 우선주 제외
            if name and not any(x in name for x in ['KODEX', 'TIGER', 'KBSTAR', '우', '스팩']):
                stock_info = {
                    'stock_code': code,
                    'stock_name': name,
                    'market': 'KOSPI' if market == "0" else 'KOSDAQ',
                    'listing_date': self.kiwoom.GetMasterListedStockDate(code)
                }
                stock_list.append(stock_info)
                
                if i % 100 == 0:
                    print(f"  {i}/{len(code_list)} 처리 중...")
                    
        print(f"✅ {len(stock_list)}개 종목 조회 완료")
        return stock_list
    
    def save_stock_master(self, stock_list: List[Dict]):
        """종목 마스터 저장"""
        print("\n💾 종목 마스터 저장 중...")
        
        # DataFrame 생성
        df = pd.DataFrame(stock_list)
        
        # CSV 저장
        csv_path = f"{self.csv_dir}/stock_master.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV 저장: {csv_path}")
        
        # SQLite 저장
        df.to_sql('stock_master', self.conn, if_exists='replace', index=False)
        print(f"✅ SQLite 저장 완료")
        
        return df
    
    def download_daily_prices(self, code: str, years: int = 10) -> pd.DataFrame:
        """일봉 데이터 다운로드 (10년치)"""
        print(f"📈 {code} 일봉 다운로드 중... ({years}년)")
        
        all_data = []
        
        # 10년 데이터를 받기 위해 연속조회
        for i in range(20):  # 최대 20번 조회 (1회당 약 600일)
            # TR: opt10081 (주식일봉차트조회)
            df = self.kiwoom.block_request("opt10081",
                종목코드=code,
                기준일자=datetime.now().strftime("%Y%m%d") if i == 0 else "",
                수정주가구분=1,
                output="주식일봉차트",
                next=0 if i == 0 else 2  # 연속조회
            )
            
            if df is None or df.empty:
                break
                
            all_data.append(df)
            
            # 10년 이전 데이터면 중단
            if len(df) > 0:
                oldest_date = pd.to_datetime(df.iloc[-1]['일자'])
                target_date = datetime.now() - timedelta(days=years*365)
                if oldest_date < target_date:
                    break
                    
            print(f"  - {i+1}번째 조회 완료 (누적 {sum(len(d) for d in all_data)}일)")
            time.sleep(0.2)  # API 제한 방지
        
        # 데이터 합치기
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
        
        if df is not None and not df.empty:
            # 데이터 정리
            df = df.rename(columns={
                '일자': 'trade_date',
                '현재가': 'close',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'
            })
            
            # 절대값 처리
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = df[col].abs()
            
            df['stock_code'] = code
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y-%m-%d')
            
            # 필요한 컬럼만
            return df[['stock_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def download_minute_prices(self, code: str, interval: int = 1) -> pd.DataFrame:
        """분봉 데이터 다운로드"""
        print(f"📊 {code} {interval}분봉 다운로드 중...")
        
        # TR에 따라 다른 코드 사용
        tr_code = {
            1: "opt10080",   # 1분봉
            3: "opt10081",   # 3분봉
            5: "opt10082",   # 5분봉
            10: "opt10083",  # 10분봉
            15: "opt10084",  # 15분봉
            30: "opt10085",  # 30분봉
            60: "opt10086",  # 60분봉
        }.get(interval, "opt10080")
        
        df = self.kiwoom.block_request(tr_code,
            종목코드=code,
            틱범위=interval,
            수정주가구분=1,
            output="주식분봉차트조회",
            next=0
        )
        
        if df is not None and not df.empty:
            # 컬럼 정리
            df = df.rename(columns={
                '체결시간': 'trade_time',
                '현재가': 'close',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'
            })
            
            df['stock_code'] = code
            
            # 최근 2일치만
            df = df.head(800)  
            
            return df[['stock_code', 'trade_time', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def download_financial_data(self, code: str) -> Dict:
        """재무 데이터 다운로드"""
        print(f"💰 {code} 재무 데이터 다운로드 중...")
        
        # TR: opt10001 (주식기본정보)
        df = self.kiwoom.block_request("opt10001",
            종목코드=code,
            output="주식기본정보",
            next=0
        )
        
        if df is not None and not df.empty:
            row = df.iloc[0]
            return {
                'stock_code': code,
                'per': float(row.get('PER', 0)),
                'pbr': float(row.get('PBR', 0)),
                'roe': float(row.get('ROE', 0)),
                'eps': int(row.get('EPS', 0)),
                'bps': int(row.get('BPS', 0)),
                'dividend_yield': float(row.get('배당수익률', 0))
            }
        return None
    
    def save_price_data(self, df: pd.DataFrame, stock_code: str, data_type: str = "daily"):
        """가격 데이터 저장"""
        if df.empty:
            return
            
        # CSV 저장
        csv_path = f"{self.csv_dir}/{data_type}/{stock_code}_{data_type}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  ✅ CSV: {csv_path}")
        
        # SQLite 저장
        table_name = f"price_{data_type}"
        df.to_sql(table_name, self.conn, if_exists='append', index=False)
        print(f"  ✅ SQLite: {table_name} 테이블")
    
    def save_financial_data(self, data: Dict, stock_code: str):
        """재무 데이터 저장"""
        if not data:
            return
            
        # DataFrame 변환
        df = pd.DataFrame([data])
        
        # CSV 저장
        csv_path = f"{self.csv_dir}/financial/{stock_code}_financial.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  ✅ CSV: {csv_path}")
        
        # SQLite 저장
        df.to_sql('financial_ratio', self.conn, if_exists='append', index=False)
        print(f"  ✅ SQLite: financial_ratio 테이블")
    
    def download_all(self, limit: int = None):
        """전체 데이터 다운로드"""
        print("\n" + "="*60)
        print("🚀 키움 데이터 로컬 다운로드 시작")
        print("="*60)
        
        # 1. 종목 마스터 다운로드
        kospi_stocks = self.get_stock_list("0")
        kosdaq_stocks = self.get_stock_list("10")
        all_stocks = kospi_stocks[:limit] if limit else kospi_stocks
        all_stocks += kosdaq_stocks[:limit//2] if limit else kosdaq_stocks[:100]
        
        master_df = self.save_stock_master(all_stocks)
        
        # 2. 주요 종목 선택
        major_codes = [
            '005930',  # 삼성전자
            '000660',  # SK하이닉스
            '035720',  # 카카오
            '035420',  # 네이버
            '005380',  # 현대차
            '051910',  # LG화학
            '006400',  # 삼성SDI
            '003550',  # LG
            '105560',  # KB금융
            '055550',  # 신한지주
        ]
        
        # 3. 가격 데이터 다운로드
        for i, code in enumerate(major_codes):
            print(f"\n[{i+1}/{len(major_codes)}] {code} 처리 중...")
            
            try:
                # 일봉 (10년)
                daily_df = self.download_daily_prices(code, years=10)
                self.save_price_data(daily_df, code, "daily")
                time.sleep(0.5)
                
                # 분봉 (1분봉)
                minute_df = self.download_minute_prices(code, interval=1)
                self.save_price_data(minute_df, code, "minute")
                time.sleep(0.5)
                
                # 재무
                financial = self.download_financial_data(code)
                self.save_financial_data(financial, code)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ 에러: {e}")
                continue
        
        print("\n" + "="*60)
        print("✅ 다운로드 완료!")
        print("="*60)
        
        self.print_summary()
    
    def print_summary(self):
        """다운로드 요약"""
        cursor = self.conn.cursor()
        
        print("\n📊 다운로드 요약:")
        print(f"📁 저장 위치: {self.data_dir}")
        
        # 종목 수
        cursor.execute("SELECT COUNT(*) FROM stock_master")
        count = cursor.fetchone()[0]
        print(f"- 종목 마스터: {count}개")
        
        # 일봉 데이터
        cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM price_daily")
        stocks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM price_daily")
        records = cursor.fetchone()[0]
        print(f"- 일봉 데이터: {stocks}개 종목, {records}개 레코드")
        
        # 분봉 데이터
        cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM price_minute")
        stocks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM price_minute")
        records = cursor.fetchone()[0]
        print(f"- 분봉 데이터: {stocks}개 종목, {records}개 레코드")
        
        # 재무 데이터
        cursor.execute("SELECT COUNT(*) FROM financial_ratio")
        count = cursor.fetchone()[0]
        print(f"- 재무 데이터: {count}개 종목")
        
        # 파일 크기
        db_size = os.path.getsize(self.db_path) / (1024*1024)
        print(f"\n💾 DB 크기: {db_size:.2f} MB")

def main():
    """메인 실행"""
    downloader = LocalDataDownloader()
    
    try:
        # 전체 다운로드 (테스트는 limit=10)
        downloader.download_all(limit=None)
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
    finally:
        downloader.conn.close()
        print("\n프로그램 종료")

if __name__ == "__main__":
    main()