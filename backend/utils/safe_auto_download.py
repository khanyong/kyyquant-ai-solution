"""
안전한 자동 다운로드
- 50개씩 끊어서 다운로드
- 자동 재시작
- 진행 상황 저장
"""
import os
import json
import time
import sys
from datetime import datetime
from PyQt5.QWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom

class SafeAutoDownloader:
    def __init__(self):
        # PyQt5 앱 생성 (필수)
        self.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect()
        
        # 설정
        self.BATCH_SIZE = 50  # 한 번에 처리할 종목 수
        self.REST_TIME = 30   # 배치 간 휴식 시간(초)
        self.PROGRESS_FILE = "auto_download_progress.json"
        
        print("="*60)
        print("🤖 안전한 자동 다운로드")
        print("="*60)
        print(f"• 배치 크기: {self.BATCH_SIZE}개")
        print(f"• 휴식 시간: {self.REST_TIME}초")
        print("• Ctrl+C로 중단 (자동 저장)")
        print("="*60)
        
    def load_completed(self):
        """완료된 종목 로드"""
        if os.path.exists(self.PROGRESS_FILE):
            with open(self.PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('completed', []))
        return set()
    
    def save_completed(self, completed_set):
        """완료 목록 저장"""
        data = {
            'completed': list(completed_set),
            'updated': datetime.now().isoformat(),
            'count': len(completed_set)
        }
        with open(self.PROGRESS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_remaining_stocks(self, completed):
        """남은 종목 리스트"""
        kospi = self.kiwoom.GetCodeListByMarket('0').split(';')[:-1]
        kosdaq = self.kiwoom.GetCodeListByMarket('10').split(';')[:-1]
        
        remaining = []
        for code in kospi + kosdaq:
            if code and code not in completed:
                name = self.kiwoom.GetMasterCodeName(code)
                if name and not any(x in name for x in ['ETF', 'ETN', '스팩', '리츠']):
                    remaining.append(code)
        
        return remaining
    
    def download_single(self, stock_code):
        """한 종목 간단 다운로드 (일봉만)"""
        try:
            # opt10081: 일봉 조회
            df = self.kiwoom.block_request("opt10081",
                종목코드=stock_code,
                기준일자=datetime.now().strftime("%Y%m%d"),
                수정주가구분=1,
                output="주식일봉차트",
                next=0
            )
            
            if df is not None and not df.empty:
                # 간단히 첫 페이지만 (약 600일)
                # 실제 저장은 여기서 처리
                print(f"    ✓ {stock_code}: {len(df)}일")
                return True
                
        except Exception as e:
            print(f"    ✗ {stock_code}: 실패")
        
        return False
    
    def run(self):
        """자동 실행"""
        completed = self.load_completed()
        
        while True:
            remaining = self.get_remaining_stocks(completed)
            
            if not remaining:
                print("\n✅ 모든 종목 완료!")
                break
            
            print(f"\n📊 현황: {len(completed)}/{len(completed)+len(remaining)} 완료")
            print(f"📦 다음 배치: {min(self.BATCH_SIZE, len(remaining))}개")
            
            # 배치 처리
            batch = remaining[:self.BATCH_SIZE]
            
            for i, code in enumerate(batch):
                try:
                    name = self.kiwoom.GetMasterCodeName(code)
                    print(f"[{i+1}/{len(batch)}] {name} ({code})")
                    
                    if self.download_single(code):
                        completed.add(code)
                    
                    # 매 10개마다 저장
                    if (i+1) % 10 == 0:
                        self.save_completed(completed)
                    
                    time.sleep(0.5)  # API 제한
                    
                except KeyboardInterrupt:
                    print("\n\n⏸️  중단! 진행상황 저장됨")
                    self.save_completed(completed)
                    print(f"완료: {len(completed)}개")
                    print("다시 실행하면 이어서 진행됩니다.")
                    sys.exit(0)
                    
                except Exception as e:
                    print(f"오류: {e}")
            
            # 배치 완료 후 저장
            self.save_completed(completed)
            
            # 휴식
            if remaining[self.BATCH_SIZE:]:  # 남은 종목이 있으면
                print(f"\n😴 {self.REST_TIME}초 휴식...")
                time.sleep(self.REST_TIME)
        
        print(f"\n최종 완료: {len(completed)}개 종목")

if __name__ == "__main__":
    downloader = SafeAutoDownloader()
    downloader.run()