"""
Supabase 테이블 컬럼 구조 상세 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import requests

load_dotenv()

class TableInspector:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
    def inspect_table(self, table_name):
        """테이블의 실제 컬럼 구조 확인"""
        print(f"\n=== {table_name} 테이블 구조 ===\n")
        
        # REST API를 직접 호출하여 테이블 정보 가져오기
        headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}'
        }
        
        # 빈 쿼리로 테이블 구조 확인
        url = f"{self.supabase_url}/rest/v1/{table_name}?limit=0"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # OPTIONS 요청으로 스키마 정보 가져오기
                options_response = requests.options(url, headers=headers)
                print(f"테이블이 존재합니다: {table_name}")
                
                # 실제 데이터로 컬럼 확인 (1개 행만)
                data_url = f"{self.supabase_url}/rest/v1/{table_name}?limit=1"
                data_response = requests.get(data_url, headers=headers)
                
                if data_response.status_code == 200 and data_response.json():
                    columns = list(data_response.json()[0].keys())
                    print(f"컬럼 목록 ({len(columns)}개):")
                    for col in columns:
                        print(f"  - {col}")
                else:
                    print("데이터가 없어 컬럼을 확인할 수 없습니다")
                    
            elif response.status_code == 404:
                print(f"테이블을 찾을 수 없습니다: {table_name}")
            else:
                print(f"에러: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"테이블 조회 실패: {e}")
            
    def test_insert_signal(self):
        """trading_signals 테이블에 최소 데이터로 삽입 테스트"""
        print("\n=== trading_signals 삽입 테스트 ===\n")
        
        # 먼저 전략 ID 가져오기
        strategies = self.supabase.table('strategies').select('id').limit(1).execute()
        if not strategies.data:
            print("전략이 없습니다")
            return
            
        strategy_id = strategies.data[0]['id']
        
        # 최소한의 필드로 시도
        minimal_signal = {
            'strategy_id': strategy_id,
            'stock_code': '005930',
            'signal_type': 'BUY'
        }
        
        try:
            result = self.supabase.table('trading_signals').insert(minimal_signal).execute()
            if result.data:
                print("삽입 성공!")
                print("저장된 데이터:")
                for key, value in result.data[0].items():
                    print(f"  - {key}: {value}")
                return result.data[0]['id']
        except Exception as e:
            print(f"삽입 실패: {e}")
            
        return None
        
    def test_insert_order(self):
        """orders 테이블에 최소 데이터로 삽입 테스트"""
        print("\n=== orders 삽입 테스트 ===\n")
        
        # 먼저 전략 ID 가져오기
        strategies = self.supabase.table('strategies').select('id').limit(1).execute()
        if not strategies.data:
            print("전략이 없습니다")
            return
            
        strategy_id = strategies.data[0]['id']
        
        # 최소한의 필드로 시도
        minimal_order = {
            'strategy_id': strategy_id,
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'order_type': 'BUY',
            'status': 'PENDING'
        }
        
        try:
            result = self.supabase.table('orders').insert(minimal_order).execute()
            if result.data:
                print("삽입 성공!")
                print("저장된 데이터:")
                for key, value in result.data[0].items():
                    print(f"  - {key}: {value}")
        except Exception as e:
            print(f"삽입 실패: {e}")
            
            # 에러 메시지에서 필수 필드 확인
            error_msg = str(e)
            if 'null value in column' in error_msg:
                print("\n필수 필드가 누락되었습니다.")
            elif 'Could not find the' in error_msg:
                print("\n존재하지 않는 컬럼입니다.")
                
    def run_inspection(self):
        """전체 검사 실행"""
        print("\n" + "="*50)
        print("테이블 구조 검사")
        print("="*50)
        
        # 각 테이블 구조 확인
        tables = ['strategies', 'trading_signals', 'orders', 'positions']
        for table in tables:
            self.inspect_table(table)
            
        # 삽입 테스트
        signal_id = self.test_insert_signal()
        self.test_insert_order()
        
        print("\n" + "="*50)
        print("검사 완료")
        print("="*50)

if __name__ == "__main__":
    inspector = TableInspector()
    inspector.run_inspection()