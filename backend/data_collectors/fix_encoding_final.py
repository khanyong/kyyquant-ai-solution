"""
종목명 인코딩 최종 수정
Latin-1으로 잘못 디코딩된 CP949 복원
"""
import sys
import os
from pathlib import Path
import time

# 환경변수 로드
from dotenv import load_dotenv
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase
from supabase import create_client

# PyQt5
from PyQt5.QtWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom

class EncodingFixer:
    def __init__(self):
        print("\n" + "="*50)
        print("종목명 인코딩 최종 수정")
        print("="*50)
        
        # Supabase 연결
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        # PyQt 앱
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # 키움 연결
        self.kiwoom = Kiwoom()
        if self.kiwoom.GetConnectState() == 0:
            print("키움 연결 중...")
            self.kiwoom.CommConnect()
            time.sleep(2)
    
    def fix_korean_encoding(self, broken_text):
        """
        Latin-1으로 잘못 디코딩된 CP949 텍스트 복원
        예: '»ï¼ºÀüÀÚ' -> '삼성전자'
        """
        try:
            # Latin-1로 인코딩하여 원본 바이트 복원
            # 그 다음 CP949로 올바르게 디코딩
            fixed = broken_text.encode('latin-1').decode('cp949')
            return fixed
        except:
            return broken_text
    
    def test_fix(self):
        """인코딩 수정 테스트"""
        test_codes = ['005930', '000660', '035720']
        
        print("\n테스트 결과:")
        print("-"*40)
        
        for code in test_codes:
            broken_name = self.kiwoom.GetMasterCodeName(code)
            fixed_name = self.fix_korean_encoding(broken_name)
            
            print(f"종목코드: {code}")
            print(f"  깨진 이름: {broken_name}")
            print(f"  수정된 이름: {fixed_name}")
            print()
    
    def fix_all_database(self):
        """데이터베이스의 모든 종목명 수정"""
        # 모든 종목 조회
        result = self.supabase.table('kw_financial_snapshot')\
            .select('stock_code, stock_name')\
            .execute()
        
        # 중복 제거
        stocks = {}
        for r in result.data:
            if r['stock_code'] not in stocks:
                stocks[r['stock_code']] = r['stock_name']
        
        print(f"\n총 {len(stocks)}개 종목 수정 시작")
        print("-"*50)
        
        fixed_count = 0
        failed_count = 0
        
        for i, (code, broken_name) in enumerate(stocks.items(), 1):
            # 진행 상황 표시
            if i % 100 == 0:
                print(f"\n[{i}/{len(stocks)}] 진행 중...")
            
            try:
                # 깨진 이름인지 확인 (한글이 아닌 이상한 문자 포함)
                if broken_name and any(ord(c) > 127 and ord(c) < 256 for c in broken_name):
                    # 인코딩 수정
                    fixed_name = self.fix_korean_encoding(broken_name)
                    
                    # 제대로 수정되었는지 확인
                    if fixed_name != broken_name and any(ord(c) >= 0xAC00 and ord(c) <= 0xD7AF for c in fixed_name):
                        # Supabase 업데이트
                        self.supabase.table('kw_financial_snapshot')\
                            .update({'stock_name': fixed_name})\
                            .eq('stock_code', code)\
                            .execute()
                        
                        fixed_count += 1
                        
                        # 주요 종목은 출력
                        if fixed_count <= 10 or fixed_count % 50 == 0:
                            print(f"  {code}: {broken_name[:10]}... → {fixed_name}")
                    
            except Exception as e:
                failed_count += 1
                if failed_count <= 5:
                    print(f"  ❌ {code} 실패: {e}")
        
        print("\n" + "="*50)
        print("✅ 수정 완료!")
        print(f"  수정된 종목: {fixed_count}개")
        print(f"  실패: {failed_count}개")
        print("="*50)
    
    def verify_results(self, limit=10):
        """수정 결과 확인"""
        print("\n수정 결과 샘플:")
        print("-"*50)
        
        # 주요 종목 확인
        major_codes = ['005930', '000660', '035720', '035420', '005380', 
                      '051910', '006400', '003550', '105560', '055550']
        
        for code in major_codes[:limit]:
            result = self.supabase.table('kw_financial_snapshot')\
                .select('stock_name')\
                .eq('stock_code', code)\
                .limit(1)\
                .execute()
            
            if result.data:
                print(f"{code}: {result.data[0]['stock_name']}")

if __name__ == "__main__":
    fixer = EncodingFixer()
    
    # 1. 테스트
    print("\n1단계: 인코딩 수정 테스트")
    fixer.test_fix()
    
    print("\n수정을 진행하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        # 2. 전체 수정
        print("\n2단계: 데이터베이스 전체 수정")
        fixer.fix_all_database()
        
        # 3. 결과 확인
        print("\n3단계: 결과 확인")
        fixer.verify_results()