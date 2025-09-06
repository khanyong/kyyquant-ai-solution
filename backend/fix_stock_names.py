"""
종목명 인코딩 수정 전용 스크립트
CP949 인코딩 문제 해결
"""
# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# 환경변수 로드
from dotenv import load_dotenv
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase
from supabase import create_client

# PyQt5
from PyQt5.QtWidgets import QApplication

# pykiwoom
from pykiwoom.kiwoom import Kiwoom

class StockNameFixer:
    def __init__(self):
        print("\n" + "="*50)
        print("종목명 인코딩 수정")
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
            self.kiwoom.CommConnect()
            time.sleep(2)
    
    def get_all_stocks(self):
        """모든 종목 조회"""
        result = self.supabase.table('kw_financial_snapshot')\
            .select('stock_code, stock_name')\
            .execute()
        
        # 중복 제거
        stocks = {}
        for r in result.data:
            stocks[r['stock_code']] = r['stock_name']
        
        return stocks
    
    def fix_encoding(self, text):
        """인코딩 수정 시도"""
        if not text:
            return text
            
        try:
            # CP949로 인코딩된 것을 UTF-8로 변환
            if isinstance(text, str):
                # 잘못된 인코딩 패턴 확인
                if any(c in text for c in ['¿', '°', '±', 'Â', '½', '¾', 'À', 'Ã']):
                    # CP949로 다시 인코딩 후 UTF-8로 디코딩
                    return text.encode('cp949', errors='ignore').decode('utf-8', errors='ignore')
            return text
        except:
            return text
    
    def fix_all_names(self):
        """전체 종목명 수정"""
        stocks = self.get_all_stocks()
        print(f"\n총 {len(stocks)}개 종목 확인")
        
        broken_count = 0
        fixed_count = 0
        
        for code, current_name in stocks.items():
            # 깨진 이름 확인
            if current_name and any(c in current_name for c in ['¿', '°', '±', 'Â', '½', '¾', 'À', 'Ã', '¢ç']):
                broken_count += 1
                print(f"\n[{broken_count}] {code}: {current_name[:20]}...", end=" ")
                
                try:
                    # 키움에서 올바른 이름 가져오기
                    correct_name = self.kiwoom.GetMasterCodeName(code)
                    
                    # 이름이 있고 정상적인 경우만 업데이트
                    if correct_name and not any(c in correct_name for c in ['¿', '°', '±']):
                        # Supabase 업데이트
                        self.supabase.table('kw_financial_snapshot')\
                            .update({'stock_name': correct_name})\
                            .eq('stock_code', code)\
                            .execute()
                        
                        print(f"→ {correct_name} ✅")
                        fixed_count += 1
                    else:
                        print(f"→ 여전히 깨짐")
                        
                except Exception as e:
                    print(f"❌ 오류: {e}")
                
                # API 제한
                time.sleep(0.1)
                
                # 100개마다 잠시 대기
                if broken_count % 100 == 0:
                    print(f"\n  {broken_count}개 처리... 잠시 대기")
                    time.sleep(2)
        
        print("\n" + "="*50)
        print(f"결과:")
        print(f"  깨진 종목: {broken_count}개")
        print(f"  수정 완료: {fixed_count}개")
        print(f"  수정 실패: {broken_count - fixed_count}개")
        print("="*50)

if __name__ == "__main__":
    fixer = StockNameFixer()
    fixer.fix_all_names()