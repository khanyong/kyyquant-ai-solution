"""
Supabase 데이터베이스 설정 및 초기화 스크립트
모든 필요한 테이블을 생성하고 데이터 수집 준비
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase_client import get_supabase_client

def setup_database():
    """
    데이터베이스 설정 안내
    """
    print("=" * 70)
    print("Supabase 데이터베이스 설정 가이드")
    print("=" * 70)
    
    print("\n1. Supabase 대시보드 접속")
    print("   https://app.supabase.com")
    
    print("\n2. SQL Editor 열기")
    print("   좌측 메뉴 > SQL Editor")
    
    print("\n3. 테이블 생성 SQL 실행")
    print("   supabase/create_all_kiwoom_tables.sql 파일의 내용을")
    print("   SQL Editor에 붙여넣고 실행")
    
    print("\n4. 생성된 테이블 확인")
    print("   다음 테이블들이 생성되었는지 확인:")
    
    tables = [
        "stock_master - 종목 마스터 정보",
        "price_data - 일봉 데이터",
        "price_data_weekly - 주봉 데이터",
        "price_data_monthly - 월봉 데이터",
        "price_data_minute - 분봉 데이터",
        "realtime_price - 실시간 현재가",
        "financial_statements - 재무제표",
        "financial_ratios - 재무비율",
        "investor_trading - 투자자별 매매",
        "disclosures - 공시정보",
        "news - 뉴스",
        "analyst_reports - 애널리스트 리포트",
        "sector_data - 업종 정보",
        "technical_indicators - 기술적 지표"
    ]
    
    for table in tables:
        print(f"   ✓ {table}")
    
    print("\n5. 데이터 수집 준비 완료!")
    print("   이제 다음 명령으로 데이터를 수집할 수 있습니다:")
    print("   python collect_all_data.py")

def verify_connection():
    """
    Supabase 연결 확인
    """
    print("\n" + "=" * 70)
    print("Supabase 연결 테스트")
    print("=" * 70)
    
    try:
        supabase = get_supabase_client()
        
        # 간단한 쿼리로 연결 테스트
        result = supabase.table('stock_master').select('count', count='exact').execute()
        
        print("✅ Supabase 연결 성공!")
        
        # 기존 데이터 확인
        tables_to_check = [
            'stock_master',
            'price_data',
            'financial_statements',
            'investor_trading'
        ]
        
        print("\n현재 데이터 현황:")
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('count', count='exact').execute()
                count = result.count if result else 0
                print(f"  {table}: {count:,}개 레코드")
            except:
                print(f"  {table}: 테이블 없음")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        print("\n.env 파일에 다음 설정이 있는지 확인하세요:")
        print("VITE_SUPABASE_URL=your_supabase_url")
        print("VITE_SUPABASE_ANON_KEY=your_anon_key")
        return False

if __name__ == "__main__":
    print("\n키움 OpenAPI+ 전체 데이터 수집 시스템")
    print("-" * 70)
    
    # 데이터베이스 설정 안내
    setup_database()
    
    # 연결 테스트
    if verify_connection():
        print("\n✅ 모든 준비가 완료되었습니다!")
        print("\n다음 단계:")
        print("1. 전체 데이터 수집: python collect_all_data.py")
        print("2. 특정 종목 테스트: python collect_all_data.py --stock 005930")
    else:
        print("\n⚠️  먼저 Supabase 설정을 완료해주세요.")