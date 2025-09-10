"""
서버 상태 및 다운로드 진행 상황 확인
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from core.supabase_client import get_supabase_client

def check_download_status():
    """다운로드된 데이터 확인"""
    supabase = get_supabase_client()
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 최근 저장된 데이터 확인
    print("=" * 60)
    print("최근 저장된 주가 데이터 확인")
    print("=" * 60)
    
    # 종목별 데이터 개수 확인
    response = supabase.table('kw_price_daily').select(
        'stock_code', 
        count='exact'
    ).execute()
    
    if response.data:
        # 종목별로 그룹화
        stock_counts = {}
        for row in response.data:
            code = row['stock_code']
            if code not in stock_counts:
                stock_counts[code] = 0
            stock_counts[code] += 1
        
        print(f"\n총 {len(stock_counts)}개 종목 데이터 보유")
        print("\n최근 추가된 종목 (상위 10개):")
        for code in sorted(stock_counts.keys())[:10]:
            print(f"  {code}: {stock_counts[code]}개 레코드")
    
    # 최근 백테스트 결과 확인
    print("\n" + "=" * 60)
    print("최근 백테스트 실행 내역")
    print("=" * 60)
    
    results = supabase.table('backtest_results').select(
        'created_at, strategy_name, total_return, win_rate'
    ).order('created_at', desc=True).limit(5).execute()
    
    if results.data:
        for result in results.data:
            print(f"\n시간: {result['created_at']}")
            print(f"전략: {result['strategy_name']}")
            print(f"수익률: {result['total_return']:.2f}%")
            print(f"승률: {result['win_rate']:.2f}%")

if __name__ == "__main__":
    check_download_status()