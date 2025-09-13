"""
모든 종목명을 stock_code 기준으로 새로 가져와서 업데이트
"""
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# 환경변수 로드
from dotenv import load_dotenv
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase
from supabase import create_client

# PyQt5
from PyQt5.QtWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom

class StockNameUpdater:
    def __init__(self):
        print("\n" + "="*50)
        print("🔄 전체 종목명 업데이트")
        print("="*50)
        
        # Supabase 연결
        print("📡 Supabase 연결...", end="", flush=True)
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        print(" ✅")
        
        # PyQt 앱
        print("🖥️ PyQt 초기화...", end="", flush=True)
        self.app = QApplication.instance() or QApplication(sys.argv)
        print(" ✅")
        
        # 키움 연결
        print("📈 키움 OpenAPI 연결...", end="", flush=True)
        self.kiwoom = Kiwoom()
        if self.kiwoom.GetConnectState() == 0:
            self.kiwoom.CommConnect()
            time.sleep(2)
        print(" ✅")
    
    def fix_encoding(self, text):
        """인코딩 수정 시도"""
        if not text:
            return text
        
        try:
            # Latin-1으로 인코딩된 CP949 복원 시도
            if any(ord(c) > 127 and ord(c) < 256 for c in text):
                fixed = text.encode('latin-1').decode('cp949')
                # 한글이 포함되어 있으면 성공
                if any(ord(c) >= 0xAC00 and ord(c) <= 0xD7AF for c in fixed):
                    return fixed
        except:
            pass
        
        return text
    
    def get_all_stock_codes(self):
        """데이터베이스의 모든 종목 코드 조회"""
        print("\n📊 종목 코드 조회 중...")
        
        result = self.supabase.table('kw_financial_snapshot')\
            .select('stock_code')\
            .execute()
        
        print(f"  - 전체 레코드: {len(result.data)}개")
        
        # 중복 제거
        codes = list(set([r['stock_code'] for r in result.data]))
        print(f"  - 고유 종목: {len(codes)}개")
        
        # 중복 확인
        if len(result.data) > len(codes):
            print(f"  - 중복 레코드: {len(result.data) - len(codes)}개")
            
            # 중복 종목 샘플 확인
            from collections import Counter
            code_counts = Counter([r['stock_code'] for r in result.data])
            duplicates = {k: v for k, v in code_counts.items() if v > 1}
            if duplicates:
                print(f"  - 중복 종목 예시 (상위 5개):")
                for code, count in list(duplicates.items())[:5]:
                    print(f"    {code}: {count}개")
        
        return codes
    
    def update_all_names(self):
        """모든 종목명 업데이트"""
        codes = self.get_all_stock_codes()
        
        print(f"\n{'='*50}")
        print(f"📋 {len(codes)}개 종목명 업데이트 시작")
        print(f"{'='*50}\n")
        
        success_count = 0
        fail_count = 0
        
        # 진행 상황 파일
        progress_file = f"name_update_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        for i, code in enumerate(codes, 1):
            # 진행률 표시
            percent = (i / len(codes)) * 100
            
            try:
                # 키움에서 종목명 가져오기
                raw_name = self.kiwoom.GetMasterCodeName(code)
                
                # 인코딩 수정
                fixed_name = self.fix_encoding(raw_name)
                
                # 정상적인 이름인지 확인 (한글 또는 영문 포함)
                if fixed_name and (
                    any(ord(c) >= 0xAC00 and ord(c) <= 0xD7AF for c in fixed_name) or  # 한글
                    any(c.isalpha() and ord(c) < 128 for c in fixed_name)  # 영문
                ):
                    # Supabase 업데이트
                    self.supabase.table('kw_financial_snapshot')\
                        .update({'stock_name': fixed_name})\
                        .eq('stock_code', code)\
                        .execute()
                    
                    success_count += 1
                    
                    # 주요 진행 상황 출력
                    if success_count <= 10 or success_count % 100 == 0:
                        print(f"[{i}/{len(codes)}] {percent:.1f}% - {code}: {fixed_name}")
                else:
                    fail_count += 1
                    print(f"[{i}/{len(codes)}] {percent:.1f}% - {code}: ❌ 이름 조회 실패")
                
            except Exception as e:
                fail_count += 1
                print(f"[{i}/{len(codes)}] {percent:.1f}% - {code}: ❌ 오류: {str(e)[:30]}")
            
            # 진행 상황 파일 저장
            if i % 50 == 0:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    f.write(f"진행: {i}/{len(codes)} ({percent:.1f}%)\n")
                    f.write(f"성공: {success_count}\n")
                    f.write(f"실패: {fail_count}\n")
                    f.write(f"시간: {datetime.now()}\n")
            
            # API 제한 대기
            time.sleep(0.1)
            
            # 100개마다 잠시 휴식
            if i % 100 == 0:
                print(f"  💾 {i}개 완료. 잠시 대기...")
                time.sleep(2)
        
        # 최종 결과
        print(f"\n{'='*50}")
        print(f"✅ 종목명 업데이트 완료!")
        print(f"  성공: {success_count}개")
        print(f"  실패: {fail_count}개")
        print(f"  진행 파일: {progress_file}")
        print(f"{'='*50}")
    
    def verify_results(self, sample_size=20):
        """업데이트 결과 확인"""
        print(f"\n📋 업데이트 결과 샘플 ({sample_size}개):")
        print("-"*50)
        
        # 샘플 종목 확인
        result = self.supabase.table('kw_financial_snapshot')\
            .select('stock_code, stock_name')\
            .limit(sample_size)\
            .execute()
        
        for r in result.data:
            print(f"{r['stock_code']}: {r['stock_name']}")

if __name__ == "__main__":
    updater = StockNameUpdater()
    
    print("\n모든 종목명을 새로 업데이트합니다.")
    print("예상 시간: 약 10-15분 (3,349개 종목)")
    print("\n시작하시겠습니까? (y/n): ", end="")
    
    if input().lower() == 'y':
        updater.update_all_names()
        updater.verify_results()