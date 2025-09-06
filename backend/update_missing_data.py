"""
누락된 재무 지표 업데이트
- 섹터 정보
- ROA, 부채비율, 유동비율
- 영업이익률, 순이익률
- 배당수익률
"""
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
try:
    from PyQt5.QtWidgets import QApplication
except:
    from PyQt5.QWidgets import QApplication

# pykiwoom
from pykiwoom.kiwoom import Kiwoom

class MissingDataUpdater:
    def __init__(self):
        print("\n" + "="*50)
        print("🔄 누락 데이터 업데이트")
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
    
    def add_missing_columns(self):
        """테이블에 누락된 컬럼 추가"""
        print("\n📋 테이블 스키마 업데이트...")
        
        sql = """
        -- 섹터 정보
        ALTER TABLE kw_financial_snapshot 
        ADD COLUMN IF NOT EXISTS sector_name VARCHAR(100),
        ADD COLUMN IF NOT EXISTS sector_code VARCHAR(20);
        
        -- 안정성 지표
        ALTER TABLE kw_financial_snapshot
        ADD COLUMN IF NOT EXISTS debt_ratio DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS current_ratio DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS quick_ratio DECIMAL(10,2);
        
        -- 수익성 지표
        ALTER TABLE kw_financial_snapshot
        ADD COLUMN IF NOT EXISTS roa DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS operating_margin DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS net_margin DECIMAL(10,2);
        
        -- 배당 정보
        ALTER TABLE kw_financial_snapshot
        ADD COLUMN IF NOT EXISTS dividend_yield DECIMAL(5,2);
        
        -- 추가 가치평가
        ALTER TABLE kw_financial_snapshot
        ADD COLUMN IF NOT EXISTS pcr DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS psr DECIMAL(10,2);
        """
        
        print("\n⚠️ Supabase SQL Editor에서 실행:")
        print("-"*50)
        print(sql)
        print("-"*50)
        
        return sql
    
    def get_stocks_to_update(self, fix_names_only=False):
        """업데이트할 종목 조회"""
        if fix_names_only:
            # 잘못된 종목명 패턴 (깨진 한글)
            result = self.supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name')\
                .execute()
            
            # 이상한 문자가 포함된 종목만 필터링
            codes = []
            for r in result.data:
                name = r.get('stock_name', '')
                # 깨진 한글 패턴 확인
                if any(c in name for c in ['¿', '°', '±', 'Â', '½', '¾', 'À', 'Ã']):
                    codes.append(r['stock_code'])
                    print(f"  깨진 종목명 발견: {r['stock_code']} - {name[:20]}")
            
            return list(set(codes))
        else:
            # sector_name이 NULL인 종목들 조회
            result = self.supabase.table('kw_financial_snapshot')\
                .select('stock_code')\
                .is_('sector_name', 'null')\
                .execute()
            
            return list(set([r['stock_code'] for r in result.data]))
    
    def update_stock_data(self, code):
        """개별 종목의 누락 데이터 업데이트"""
        try:
            # 1. 종목명 다시 가져오기 (인코딩 문제 해결)
            stock_name = self.kiwoom.GetMasterCodeName(code)
            
            # 2. 섹터 정보
            sector_name = self.kiwoom.GetMasterStockInfo(code)
            
            # 2. opt10080 - 주식분봉차트 (재무제표 상세)
            df = self.kiwoom.block_request("opt10080",
                종목코드=code,
                조회구분=0,  # 연간
                output="주식분석",
                next=0
            )
            
            update_data = {
                'stock_name': stock_name,  # 종목명 업데이트 (인코딩 수정)
                'sector_name': sector_name
            }
            
            if df is not None and not df.empty:
                data = df.iloc[0]
                
                # 안정성 지표
                update_data['debt_ratio'] = float(data.get('부채비율', 0))
                update_data['current_ratio'] = float(data.get('유동비율', 0))
                update_data['quick_ratio'] = float(data.get('당좌비율', 0))
                
                # 수익성 지표
                update_data['roa'] = float(data.get('ROA', 0))
                update_data['operating_margin'] = float(data.get('영업이익률', 0))
                update_data['net_margin'] = float(data.get('순이익률', 0))
                
                # 배당
                update_data['dividend_yield'] = float(data.get('시가배당률', 0))
            
            # Supabase 업데이트
            self.supabase.table('kw_financial_snapshot')\
                .update(update_data)\
                .eq('stock_code', code)\
                .execute()
            
            return True
            
        except Exception as e:
            print(f"  ❌ {code} 오류: {str(e)[:30]}")
            return False
    
    def update_all_missing(self, limit=None):
        """전체 누락 데이터 업데이트"""
        stocks = self.get_stocks_to_update()
        
        if limit:
            stocks = stocks[:limit]
        
        print(f"\n📊 {len(stocks)}개 종목 업데이트 시작")
        print("-"*50)
        
        success = 0
        for i, code in enumerate(stocks, 1):
            print(f"[{i}/{len(stocks)}] {code}", end=" ")
            
            if self.update_stock_data(code):
                success += 1
                print("✅")
            else:
                print("❌")
            
            time.sleep(0.2)  # API 제한
            
            if i % 100 == 0:
                print(f"  💾 {i}개 완료. 잠시 대기...")
                time.sleep(3)
        
        print("\n" + "="*50)
        print(f"✅ 완료: {success}/{len(stocks)}")
        print("="*50)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='누락 데이터 업데이트')
    parser.add_argument('--fix-names', action='store_true', help='깨진 종목명만 수정')
    parser.add_argument('--add-columns', action='store_true', help='누락 컬럼 추가 SQL 출력')
    parser.add_argument('--limit', type=int, help='처리할 종목 수 제한')
    
    args = parser.parse_args()
    
    updater = MissingDataUpdater()
    
    if args.add_columns:
        # 컬럼 추가 SQL 출력
        sql = updater.add_missing_columns()
    
    elif args.fix_names:
        # 깨진 종목명만 수정
        print("\n🔧 깨진 종목명 수정 모드")
        print("-"*50)
        
        stocks = updater.get_stocks_to_update(fix_names_only=True)
        print(f"\n총 {len(stocks)}개 종목의 이름이 깨져있습니다.")
        
        if stocks:
            print("\n수정을 시작하시겠습니까? (y/n): ", end="")
            if input().lower() == 'y':
                success = 0
                for i, code in enumerate(stocks[:args.limit] if args.limit else stocks, 1):
                    print(f"[{i}/{len(stocks)}] {code}", end=" ")
                    
                    try:
                        # 종목명만 업데이트
                        name = updater.kiwoom.GetMasterCodeName(code)
                        updater.supabase.table('kw_financial_snapshot')\
                            .update({'stock_name': name})\
                            .eq('stock_code', code)\
                            .execute()
                        
                        print(f"→ {name} ✅")
                        success += 1
                    except Exception as e:
                        print(f"❌ {e}")
                    
                    time.sleep(0.1)
                
                print(f"\n✅ 완료: {success}/{len(stocks)} 종목명 수정")
    
    else:
        # 전체 누락 데이터 업데이트
        print("\n📊 누락 데이터 업데이트")
        print("-"*50)
        print("옵션:")
        print("  --fix-names : 깨진 종목명만 수정")
        print("  --add-columns : 누락 컬럼 추가 SQL 출력")
        print("  --limit N : N개만 처리")
        print("\n기본: 모든 누락 데이터 업데이트")
        
        print("\n시작하시겠습니까? (y/n): ", end="")
        if input().lower() == 'y':
            updater.update_all_missing(limit=args.limit)