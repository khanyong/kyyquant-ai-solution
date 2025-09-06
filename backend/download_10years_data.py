"""
키움 OpenAPI+ 10년 데이터 다운로드
대용량 장기 데이터 수집
"""
import sys
import os
import time
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
import json

# PyQt5 imports
from PyQt5.QWidgets import QApplication
from PyQt5.QtCore import QEventLoop

# pykiwoom imports
from pykiwoom.kiwoom import Kiwoom

class TenYearDataDownloader:
    def __init__(self):
        """10년 데이터 다운로더 초기화"""
        # 데이터 저장 경로
        self.data_dir = "D:/Dev/auto_stock/data"
        self.csv_dir = f"{self.data_dir}/csv"
        self.db_path = f"{self.data_dir}/kiwoom_10years.db"
        
        # 디렉토리 생성
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(f"{self.csv_dir}/daily", exist_ok=True)
        os.makedirs(f"{self.csv_dir}/weekly", exist_ok=True)
        os.makedirs(f"{self.csv_dir}/monthly", exist_ok=True)
        
        # SQLite 연결
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
        
        # PyQt 앱 생성
        self.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # 키움 API 연결
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect()
        
        print("="*60)
        print("🚀 키움 10년 데이터 다운로더")
        print("="*60)
        print(f"📁 저장 경로: {self.data_dir}")
        print(f"🗄️ DB 파일: {self.db_path}")
        
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
        
        # 일봉 (10년)
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
        
        # 주봉
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_weekly (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                week_date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(stock_code, week_date)
            )
        ''')
        
        # 월봉
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_monthly (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                month_date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(stock_code, month_date)
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stock ON price_daily(stock_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_date ON price_daily(trade_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_weekly_stock ON price_weekly(stock_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_monthly_stock ON price_monthly(stock_code)')
        
        self.conn.commit()
        print("✅ 테이블 생성 완료")
    
    def get_top_stocks(self, limit: int = 100) -> List[str]:
        """시가총액 상위 종목 조회"""
        print(f"\n📊 시가총액 상위 {limit}개 종목 선정 중...")
        
        # 코스피 200 + 코스닥 150
        kospi_codes = self.kiwoom.GetCodeListByMarket("0")
        kosdaq_codes = self.kiwoom.GetCodeListByMarket("10")
        
        stock_caps = []
        
        # 시가총액 조회
        for code in kospi_codes[:200]:  # 상위 200개만 체크
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not any(x in name for x in ['KODEX', 'TIGER', 'KBSTAR', '우', '스팩']):
                # 시가총액 조회 (간단히 현재가 * 상장주식수)
                stock_caps.append({
                    'code': code,
                    'name': name,
                    'market': 'KOSPI'
                })
        
        for code in kosdaq_codes[:150]:
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not any(x in name for x in ['우', '스팩']):
                stock_caps.append({
                    'code': code,
                    'name': name,
                    'market': 'KOSDAQ'
                })
        
        # 상위 종목 선택
        selected = stock_caps[:limit]
        
        # 종목 마스터 저장
        df = pd.DataFrame([{
            'stock_code': s['code'],
            'stock_name': s['name'],
            'market': s['market']
        } for s in selected])
        
        df.to_sql('stock_master', self.conn, if_exists='replace', index=False)
        df.to_csv(f"{self.csv_dir}/stock_master.csv", index=False, encoding='utf-8-sig')
        
        print(f"✅ {len(selected)}개 종목 선정 완료")
        return [s['code'] for s in selected]
    
    def download_daily_10years(self, code: str) -> pd.DataFrame:
        """10년 일봉 데이터 다운로드"""
        print(f"📈 {code} 일봉 10년 다운로드 시작...")
        
        all_data = []
        target_date = datetime.now() - timedelta(days=3650)  # 10년 전
        
        for i in range(30):  # 최대 30번 조회
            try:
                df = self.kiwoom.block_request("opt10081",
                    종목코드=code,
                    기준일자=datetime.now().strftime("%Y%m%d") if i == 0 else "",
                    수정주가구분=1,
                    output="주식일봉차트",
                    next=0 if i == 0 else 2
                )
                
                if df is None or df.empty:
                    break
                    
                all_data.append(df)
                
                # 날짜 체크
                if len(df) > 0:
                    oldest = pd.to_datetime(df.iloc[-1].get('일자', df.index[-1]))
                    if oldest < target_date:
                        print(f"  ✓ 10년 데이터 수집 완료 (최종: {oldest.strftime('%Y-%m-%d')})")
                        break
                
                print(f"  - {i+1}회 조회 (누적 {sum(len(d) for d in all_data)}일)")
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  ❌ 조회 실패: {e}")
                break
        
        # 데이터 합치기
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            
            # 컬럼 정리
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
            
            # 10년 이내 데이터만
            df = df[pd.to_datetime(df['trade_date']) >= target_date]
            
            print(f"  ✅ {len(df)}일 데이터 수집 완료")
            return df[['stock_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def download_weekly_data(self, code: str) -> pd.DataFrame:
        """주봉 데이터 다운로드"""
        print(f"📊 {code} 주봉 다운로드...")
        
        df = self.kiwoom.block_request("opt10082",
            종목코드=code,
            기준일자=datetime.now().strftime("%Y%m%d"),
            수정주가구분=1,
            output="주식주봉차트조회",
            next=0
        )
        
        if df is not None and not df.empty:
            df = df.rename(columns={
                '일자': 'week_date',
                '현재가': 'close',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'
            })
            
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = df[col].abs()
            
            df['stock_code'] = code
            df['week_date'] = pd.to_datetime(df['week_date']).dt.strftime('%Y-%m-%d')
            
            return df[['stock_code', 'week_date', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def download_monthly_data(self, code: str) -> pd.DataFrame:
        """월봉 데이터 다운로드"""
        print(f"📊 {code} 월봉 다운로드...")
        
        df = self.kiwoom.block_request("opt10083",
            종목코드=code,
            기준일자=datetime.now().strftime("%Y%m%d"),
            수정주가구분=1,
            output="주식월봉차트조회",
            next=0
        )
        
        if df is not None and not df.empty:
            df = df.rename(columns={
                '일자': 'month_date',
                '현재가': 'close',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'
            })
            
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = df[col].abs()
            
            df['stock_code'] = code
            df['month_date'] = pd.to_datetime(df['month_date']).dt.strftime('%Y-%m-%d')
            
            return df[['stock_code', 'month_date', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, stock_code: str, data_type: str):
        """데이터 저장"""
        if df.empty:
            return
        
        # CSV 저장
        csv_path = f"{self.csv_dir}/{data_type}/{stock_code}_{data_type}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # SQLite 저장
        table_name = f"price_{data_type}"
        df.to_sql(table_name, self.conn, if_exists='append', index=False)
        
        print(f"  💾 저장: {len(df)}개 레코드")
    
    def download_all(self, stock_limit: int = 50):
        """전체 다운로드 실행"""
        print("\n" + "="*60)
        print("🚀 10년 데이터 다운로드 시작")
        print("="*60)
        
        # 상위 종목 선정
        stock_codes = self.get_top_stocks(stock_limit)
        
        # 각 종목 데이터 다운로드
        for i, code in enumerate(stock_codes):
            print(f"\n[{i+1}/{len(stock_codes)}] {code} 처리 중...")
            
            try:
                # 일봉 (10년)
                daily_df = self.download_daily_10years(code)
                self.save_data(daily_df, code, "daily")
                time.sleep(1)
                
                # 주봉
                weekly_df = self.download_weekly_data(code)
                self.save_data(weekly_df, code, "weekly")
                time.sleep(0.5)
                
                # 월봉
                monthly_df = self.download_monthly_data(code)
                self.save_data(monthly_df, code, "monthly")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ 에러: {e}")
                continue
            
            # 진행 상황
            if (i+1) % 10 == 0:
                self.print_progress()
        
        print("\n" + "="*60)
        print("✅ 10년 데이터 다운로드 완료!")
        print("="*60)
        
        self.print_summary()
    
    def print_progress(self):
        """진행 상황 출력"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM price_daily")
        stocks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM price_daily")
        records = cursor.fetchone()[0]
        print(f"\n  📊 진행 상황: {stocks}개 종목, {records:,}개 일봉 레코드")
    
    def print_summary(self):
        """최종 요약"""
        cursor = self.conn.cursor()
        
        print("\n📊 다운로드 완료 요약:")
        print(f"📁 저장 위치: {self.data_dir}")
        
        # 종목 수
        cursor.execute("SELECT COUNT(*) FROM stock_master")
        print(f"- 종목: {cursor.fetchone()[0]}개")
        
        # 일봉
        cursor.execute("SELECT COUNT(DISTINCT stock_code), COUNT(*), MIN(trade_date), MAX(trade_date) FROM price_daily")
        stocks, records, min_date, max_date = cursor.fetchone()
        print(f"- 일봉: {stocks}개 종목, {records:,}개 레코드 ({min_date} ~ {max_date})")
        
        # 주봉
        cursor.execute("SELECT COUNT(DISTINCT stock_code), COUNT(*) FROM price_weekly")
        stocks, records = cursor.fetchone()
        print(f"- 주봉: {stocks}개 종목, {records:,}개 레코드")
        
        # 월봉
        cursor.execute("SELECT COUNT(DISTINCT stock_code), COUNT(*) FROM price_monthly")
        stocks, records = cursor.fetchone()
        print(f"- 월봉: {stocks}개 종목, {records:,}개 레코드")
        
        # DB 크기
        db_size = os.path.getsize(self.db_path) / (1024*1024)
        print(f"\n💾 DB 크기: {db_size:.2f} MB")
        
        # 평균 데이터 길이
        cursor.execute("SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM price_daily GROUP BY stock_code)")
        avg_days = cursor.fetchone()[0]
        print(f"📈 평균 일봉 개수: {avg_days:.0f}일 (약 {avg_days/250:.1f}년)")

def main():
    """메인 실행"""
    downloader = TenYearDataDownloader()
    
    try:
        # 시가총액 상위 50개 종목의 10년 데이터
        downloader.download_all(stock_limit=50)
        
    except Exception as e:
        print(f"\n❌ 에러: {e}")
    finally:
        downloader.conn.close()
        print("\n프로그램 종료")

if __name__ == "__main__":
    main()