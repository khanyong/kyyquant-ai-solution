"""
배치 다운로드 매니저
중단/재시작 가능한 안전한 데이터 수집
"""
import sys
import os
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
from pykiwoom.kiwoom import Kiwoom

class BatchDownloadManager:
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect()
        
        # 진행 상황 파일
        self.progress_file = "download_progress.json"
        self.batch_size = 10  # 한 번에 처리할 종목 수
        
        # 로컬 DB
        self.db_path = "D:/Dev/auto_stock/data/kiwoom_data.db"
        self.conn = sqlite3.connect(self.db_path)
        
        # 진행 상황 로드
        self.progress = self.load_progress()
        
    def load_progress(self) -> Dict:
        """진행 상황 로드"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "completed_stocks": [],
                "failed_stocks": [],
                "current_batch": 0,
                "total_processed": 0,
                "last_update": None
            }
    
    def save_progress(self):
        """진행 상황 저장"""
        self.progress["last_update"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_all_stocks(self) -> List[str]:
        """전체 종목 리스트"""
        kospi = self.kiwoom.GetCodeListByMarket('0').split(';')[:-1]
        kosdaq = self.kiwoom.GetCodeListByMarket('10').split(';')[:-1]
        
        all_stocks = []
        for code in kospi + kosdaq:
            if code and code not in self.progress["completed_stocks"]:
                name = self.kiwoom.GetMasterCodeName(code)
                # ETF, 스팩 제외
                if name and not any(x in name for x in ['ETF', 'ETN', '스팩', '리츠', 'KODEX', 'TIGER']):
                    all_stocks.append(code)
        
        return all_stocks
    
    def download_stock_data(self, stock_code: str) -> bool:
        """한 종목 데이터 다운로드"""
        try:
            stock_name = self.kiwoom.GetMasterCodeName(stock_code)
            print(f"  📊 {stock_name} ({stock_code}) 다운로드 중...")
            
            # 일봉 데이터 (10년)
            success = self.download_daily_data(stock_code)
            
            if success:
                self.progress["completed_stocks"].append(stock_code)
                print(f"    ✅ 완료")
                return True
            else:
                self.progress["failed_stocks"].append(stock_code)
                print(f"    ❌ 실패")
                return False
                
        except Exception as e:
            print(f"    ❌ 오류: {e}")
            self.progress["failed_stocks"].append(stock_code)
            return False
    
    def download_daily_data(self, stock_code: str) -> bool:
        """10년 일봉 데이터 다운로드"""
        all_data = []
        target_date = datetime.now() - timedelta(days=3650)
        
        for i in range(20):  # 최대 20번 연속조회
            try:
                df = self.kiwoom.block_request("opt10081",
                    종목코드=stock_code,
                    기준일자=datetime.now().strftime("%Y%m%d") if i == 0 else "",
                    수정주가구분=1,
                    output="주식일봉차트",
                    next=0 if i == 0 else 2
                )
                
                if df is None or df.empty:
                    break
                
                all_data.append(df)
                
                # 10년치 확인
                if len(df) > 0:
                    oldest = pd.to_datetime(df.iloc[-1]['일자'])
                    if oldest < target_date:
                        break
                
                time.sleep(0.2)  # API 제한
                
            except:
                break
        
        if all_data:
            # 데이터 저장
            import pandas as pd
            df = pd.concat(all_data, ignore_index=True)
            
            # SQLite 저장
            cursor = self.conn.cursor()
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO price_daily 
                    (stock_code, trade_date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock_code,
                    row['일자'],
                    abs(int(row.get('시가', 0))),
                    abs(int(row.get('고가', 0))),
                    abs(int(row.get('저가', 0))),
                    abs(int(row.get('현재가', 0))),
                    int(row.get('거래량', 0))
                ))
            
            self.conn.commit()
            return True
        
        return False
    
    def run_batch(self):
        """배치 실행"""
        print("\n" + "="*60)
        print("📦 배치 다운로드 시작")
        print("="*60)
        
        # 남은 종목 리스트
        remaining_stocks = self.get_all_stocks()
        total = len(remaining_stocks) + len(self.progress["completed_stocks"])
        
        print(f"전체: {total}개")
        print(f"완료: {len(self.progress['completed_stocks'])}개")
        print(f"남은: {len(remaining_stocks)}개")
        print(f"배치 크기: {self.batch_size}개씩")
        
        # 배치 처리
        batch_count = 0
        for i in range(0, len(remaining_stocks), self.batch_size):
            batch = remaining_stocks[i:i+self.batch_size]
            batch_count += 1
            
            print(f"\n[배치 {batch_count}] {len(batch)}개 종목 처리")
            print("-" * 40)
            
            for stock_code in batch:
                self.download_stock_data(stock_code)
                self.progress["total_processed"] += 1
                time.sleep(1)  # API 제한
            
            # 진행 상황 저장
            self.save_progress()
            
            # 배치 간 휴식
            if i + self.batch_size < len(remaining_stocks):
                print(f"\n⏸️  10초 휴식 (API 제한)...")
                time.sleep(10)
        
        print("\n" + "="*60)
        print("✅ 배치 다운로드 완료!")
        print(f"성공: {len(self.progress['completed_stocks'])}개")
        print(f"실패: {len(self.progress['failed_stocks'])}개")
        
    def show_status(self):
        """현재 상태 표시"""
        print("\n📊 다운로드 현황")
        print("-" * 40)
        print(f"완료: {len(self.progress['completed_stocks'])}개")
        print(f"실패: {len(self.progress['failed_stocks'])}개")
        print(f"마지막 업데이트: {self.progress.get('last_update', 'N/A')}")
        
        if self.progress['failed_stocks']:
            print(f"\n실패 종목: {self.progress['failed_stocks'][:5]}...")
    
    def retry_failed(self):
        """실패한 종목 재시도"""
        failed = self.progress["failed_stocks"].copy()
        self.progress["failed_stocks"] = []
        
        print(f"\n🔄 {len(failed)}개 실패 종목 재시도")
        
        for stock_code in failed:
            if self.download_stock_data(stock_code):
                print(f"  ✅ {stock_code} 성공")
            else:
                print(f"  ❌ {stock_code} 재실패")
            time.sleep(1)
        
        self.save_progress()

def main():
    """메인 실행"""
    manager = BatchDownloadManager()
    
    while True:
        print("\n" + "="*60)
        print("배치 다운로드 매니저")
        print("="*60)
        print("1. 새로 시작")
        print("2. 이어서 다운로드")
        print("3. 현재 상태 확인")
        print("4. 실패 종목 재시도")
        print("5. 종료")
        
        choice = input("\n선택: ")
        
        if choice == "1":
            # 초기화
            manager.progress = {
                "completed_stocks": [],
                "failed_stocks": [],
                "current_batch": 0,
                "total_processed": 0,
                "last_update": None
            }
            manager.save_progress()
            manager.run_batch()
            
        elif choice == "2":
            # 이어서
            manager.run_batch()
            
        elif choice == "3":
            # 상태 확인
            manager.show_status()
            
        elif choice == "4":
            # 재시도
            manager.retry_failed()
            
        elif choice == "5":
            print("\n종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()