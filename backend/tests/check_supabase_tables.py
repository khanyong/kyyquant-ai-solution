"""
Supabase 테이블 구조 확인 스크립트
현재 존재하는 모든 테이블과 컬럼 정보를 조회
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class SupabaseTableChecker:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
    def check_all_tables(self):
        """모든 테이블 목록 확인"""
        print("\n=== Supabase 테이블 확인 ===\n")
        
        # 각 테이블 확인 및 샘플 데이터 조회
        tables_to_check = [
            'strategies',
            'trading_signals', 
            'orders',
            'positions',
            'market_data_cache',
            'stocks',
            'market_index',
            'users',
            'profiles',
            'api_keys',
            'backtest_results',
            'portfolio_history',
            'alerts',
            'watchlists'
        ]
        
        existing_tables = []
        
        for table in tables_to_check:
            try:
                # 테이블에서 1개 행만 조회하여 존재 여부 확인
                result = self.supabase.table(table).select('*').limit(1).execute()
                
                # 테이블이 존재하면 컬럼 정보 출력
                if result.data or result.data == []:  # 빈 테이블도 존재하는 것으로 간주
                    existing_tables.append(table)
                    print(f"[O] {table}")
                    
                    # 데이터가 있으면 컬럼 보여주기
                    if result.data:
                        columns = list(result.data[0].keys())
                        print(f"    컬럼: {', '.join(columns[:5])}" + ("..." if len(columns) > 5 else ""))
                    
                    # 행 개수 확인
                    count_result = self.supabase.table(table).select('*', count='exact').limit(1).execute()
                    if hasattr(count_result, 'count'):
                        print(f"    데이터: {count_result.count}개 행")
                    
            except Exception as e:
                if 'PGRST' in str(e):
                    print(f"[X] {table} - 테이블 없음")
                else:
                    print(f"[?] {table} - 확인 실패: {str(e)[:50]}")
        
        print(f"\n총 {len(existing_tables)}개 테이블 발견:")
        for table in existing_tables:
            print(f"  - {table}")
            
        return existing_tables
    
    def check_strategies_table(self):
        """strategies 테이블 상세 확인"""
        print("\n=== strategies 테이블 상세 정보 ===\n")
        
        try:
            result = self.supabase.table('strategies').select('*').limit(5).execute()
            
            if result.data:
                print(f"총 {len(result.data)}개 전략 (최대 5개 표시)")
                
                # 첫 번째 데이터의 컬럼 구조 확인
                if result.data[0]:
                    print("\n컬럼 구조:")
                    for key in result.data[0].keys():
                        value_type = type(result.data[0][key]).__name__
                        print(f"  - {key}: {value_type}")
                        
                    print("\n샘플 데이터:")
                    for i, strategy in enumerate(result.data[:2], 1):
                        print(f"\n전략 {i}:")
                        for key, value in strategy.items():
                            if key in ['name', 'is_active', 'created_at']:
                                print(f"  {key}: {value}")
            else:
                print("strategies 테이블이 비어있습니다")
                
        except Exception as e:
            print(f"strategies 테이블 조회 실패: {e}")
            
    def check_trading_signals_table(self):
        """trading_signals 테이블 상세 확인"""
        print("\n=== trading_signals 테이블 상세 정보 ===\n")
        
        try:
            result = self.supabase.table('trading_signals').select('*').order('timestamp', desc=True).limit(5).execute()
            
            if result.data:
                print(f"최근 신호 {len(result.data)}개")
                
                # 컬럼 구조
                if result.data[0]:
                    print("\n컬럼 구조:")
                    for key in result.data[0].keys():
                        print(f"  - {key}")
                        
            else:
                print("trading_signals 테이블이 비어있습니다")
                
        except Exception as e:
            # timestamp 컬럼이 없을 수도 있으므로 다시 시도
            try:
                result = self.supabase.table('trading_signals').select('*').limit(5).execute()
                if result.data:
                    print(f"신호 {len(result.data)}개 발견")
                    if result.data[0]:
                        print("\n컬럼 구조:")
                        for key in result.data[0].keys():
                            print(f"  - {key}")
                else:
                    print("trading_signals 테이블이 비어있습니다")
            except Exception as e2:
                print(f"trading_signals 테이블 조회 실패: {e2}")

if __name__ == "__main__":
    checker = SupabaseTableChecker()
    
    # 모든 테이블 확인
    existing_tables = checker.check_all_tables()
    
    # 주요 테이블 상세 확인
    if 'strategies' in existing_tables:
        checker.check_strategies_table()
    
    if 'trading_signals' in existing_tables:
        checker.check_trading_signals_table()