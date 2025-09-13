"""
키움증권 API 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.kiwoom_data_api import KiwoomDataAPI
from datetime import datetime, timedelta
import pandas as pd

def test_kiwoom_api():
    """키움증권 API 테스트"""
    
    print("=" * 50)
    print("키움증권 API 테스트 시작")
    print("=" * 50)
    
    # API 초기화
    api = KiwoomDataAPI()
    
    # 테스트용 인증 정보 (실제 키로 교체 필요)
    app_key = "iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk"
    app_secret = "9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA"
    
    # 1. 인증 테스트
    print("\n1. 키움 API 인증 테스트...")
    auth_result = api.authenticate(app_key, app_secret)
    if auth_result:
        print("   [OK] 인증 성공")
    else:
        print("   [FAIL] 인증 실패 - API 키를 확인하세요")
        return
    
    # 2. 주가 데이터 조회 테스트
    print("\n2. 주가 데이터 조회 테스트...")
    stock_code = "005930"  # 삼성전자
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"   종목: {stock_code} (삼성전자)")
    print(f"   기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    
    # 캐시 없이 직접 조회
    data = api.get_historical_data(
        stock_code,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        use_cache=False  # 캐시 사용 안함
    )
    
    if not data.empty:
        print(f"   [OK] 데이터 조회 성공: {len(data)}개 레코드")
        print("\n   최근 5일 데이터:")
        print(data.tail().to_string())
        
        # 데이터 통계
        print("\n   데이터 통계:")
        print(f"   - 평균 종가: {data['close'].mean():,.0f}원")
        print(f"   - 최고가: {data['high'].max():,.0f}원")
        print(f"   - 최저가: {data['low'].min():,.0f}원")
        print(f"   - 평균 거래량: {data['volume'].mean():,.0f}주")
    else:
        print("   [FAIL] 데이터 조회 실패")
    
    # 3. Supabase 캐시 테스트
    print("\n3. Supabase 캐시 테스트...")
    
    # 캐시 저장
    if not data.empty:
        saved_count = api.save_to_supabase(data, stock_code)
        print(f"   [OK] {saved_count}개 레코드를 Supabase에 저장")
    
    # 캐시에서 조회
    cached_data = api.get_from_supabase(
        stock_code,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if not cached_data.empty:
        print(f"   [OK] 캐시에서 {len(cached_data)}개 레코드 조회 성공")
    else:
        print("   [FAIL] 캐시 조회 실패")
    
    # 4. 여러 종목 테스트
    print("\n4. 여러 종목 조회 테스트...")
    test_stocks = {
        "000660": "SK하이닉스",
        "035720": "카카오",
        "005380": "현대차",
        "051910": "LG화학"
    }
    
    for code, name in test_stocks.items():
        print(f"   {code} ({name}): ", end="")
        data = api.get_historical_data(
            code,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            use_cache=True  # 캐시 사용
        )
        if not data.empty:
            print(f"[OK] {len(data)}개 레코드")
        else:
            print("[FAIL]")
    
    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)

if __name__ == "__main__":
    test_kiwoom_api()