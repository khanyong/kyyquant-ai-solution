"""
데이터 확인 및 수정
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

print("="*50)
print("📊 데이터 확인 및 수정")
print("="*50)

# 주요 종목 데이터 확인
test_stocks = [
    ('005930', '삼성전자'),
    ('000660', 'SK하이닉스'),
    ('035720', '카카오'),
    ('051910', 'LG화학'),
    ('207940', '삼성바이오로직스'),
    ('005380', '현대차'),
    ('035420', 'NAVER'),
    ('000270', '기아'),
    ('068270', '셀트리온'),
    ('105560', 'KB금융')
]

print("\n현재 저장된 데이터:")
print("-"*40)

for code, name in test_stocks:
    result = supabase.table('kw_financial_snapshot')\
        .select('*')\
        .eq('stock_code', code)\
        .execute()
    
    if result.data:
        data = result.data[0]
        print(f"\n{code} - {name}")
        print(f"  DB 이름: {data.get('stock_name', 'N/A')}")
        print(f"  시가총액: {data.get('market_cap', 0):,}원")
        
        # 시가총액이 너무 작으면 수정 필요
        market_cap = data.get('market_cap', 0)
        if market_cap > 0 and market_cap < 1000000000:  # 10억원 미만이면 이상함
            print(f"    → 시가총액 이상! 억원 단위로 보임")
            correct_market_cap = market_cap * 100000000
            print(f"    → 수정값: {correct_market_cap:,}원")
        
        print(f"  현재가: {data.get('current_price', 0):,}원")
        print(f"  PER: {data.get('per', 'N/A')}")
        print(f"  PBR: {data.get('pbr', 'N/A')}")
        print(f"  ROE: {data.get('roe', 'N/A')}%")
        print(f"  ROA: {data.get('roa', 'N/A')}%")
        print(f"  부채비율: {data.get('debt_ratio', 'N/A')}%")
        print(f"  유동비율: {data.get('current_ratio', 'N/A')}%")
        print(f"  영업이익률: {data.get('operating_margin', 'N/A')}%")
        print(f"  순이익률: {data.get('net_margin', 'N/A')}%")
        print(f"  배당수익률: {data.get('dividend_yield', 'N/A')}%")
        print(f"  업종: {data.get('sector_name', 'N/A')}")

# 시가총액 수정이 필요한 종목 확인
print("\n" + "="*50)
print("시가총액 수정이 필요한 종목 확인 중...")

# 전체 종목에서 시가총액이 이상한 것 찾기
result = supabase.table('kw_financial_snapshot')\
    .select('stock_code, stock_name, market_cap')\
    .gt('market_cap', 0)\
    .lt('market_cap', 1000000000)\
    .execute()

if result.data:
    print(f"\n시가총액이 10억원 미만인 종목: {len(result.data)}개")
    print("수정이 필요합니다. (억원 → 원 변환)")
    
    print("\n수정하시겠습니까? (y/n): ", end="")
    response = input()
    
    if response.lower() == 'y':
        success = 0
        for item in result.data:
            try:
                correct_market_cap = item['market_cap'] * 100000000
                supabase.table('kw_financial_snapshot')\
                    .update({'market_cap': correct_market_cap})\
                    .eq('stock_code', item['stock_code'])\
                    .execute()
                success += 1
            except Exception as e:
                print(f"오류 {item['stock_code']}: {e}")
        
        print(f"✅ {success}개 종목 시가총액 수정 완료")

# NULL 데이터 확인
print("\n" + "="*50)
print("누락된 데이터 통계:")

# 각 컬럼별 NULL 개수 확인
columns = ['market_cap', 'current_price', 'per', 'pbr', 'roe', 'roa', 
           'debt_ratio', 'current_ratio', 'operating_margin', 'net_margin', 
           'dividend_yield', 'sector_name']

for col in columns:
    # NULL인 것 세기 (Supabase는 is.null 필터 지원)
    result = supabase.table('kw_financial_snapshot')\
        .select('stock_code', count='exact')\
        .is_(col, 'null')\
        .execute()
    
    null_count = result.count if hasattr(result, 'count') else 0
    print(f"  {col}: {null_count}개 누락")

print("\n" + "="*50)