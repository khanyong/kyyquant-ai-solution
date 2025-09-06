"""
과거 주가 데이터 일괄 다운로드 스크립트
10년치 데이터를 미리 다운로드하여 Supabase에 저장
"""
import sys
import os
from datetime import datetime, timedelta
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.kiwoom_openapi import KiwoomOpenAPI
from core.supabase_client import get_supabase_client

def download_historical_data(years=10):
    """
    주요 종목의 과거 데이터 다운로드
    
    Args:
        years: 다운로드할 연수 (기본 10년)
    """
    print("=" * 60)
    print(f"과거 {years}년 주가 데이터 다운로드")
    print("=" * 60)
    
    # 키움 API 초기화
    kiwoom = KiwoomOpenAPI()
    
    # 키움 접속
    print("\n1. 키움증권 OpenAPI+ 접속 중...")
    if not kiwoom.connect():
        print("   [실패] 키움증권 접속 실패")
        print("   - KOA Studio가 실행 중인지 확인하세요")
        print("   - 키움증권 로그인이 되어있는지 확인하세요")
        return
    print("   [성공] 접속 완료")
    
    # 다운로드할 종목 리스트
    stock_list = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035720", "카카오"),
        ("005380", "현대차"),
        ("051910", "LG화학"),
        ("006400", "삼성SDI"),
        ("035420", "네이버"),
        ("003550", "LG"),
        ("105560", "KB금융"),
        ("055550", "신한지주"),
        ("000270", "기아"),
        ("068270", "셀트리온"),
        ("028260", "삼성물산"),
        ("012330", "현대모비스"),
        ("066570", "LG전자"),
        ("096770", "SK이노베이션"),
        ("003670", "포스코홀딩스"),
        ("034730", "SK"),
        ("015760", "한국전력"),
        ("032830", "삼성생명")
    ]
    
    # 날짜 범위 설정
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    print(f"\n2. 다운로드 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print(f"3. 다운로드할 종목 수: {len(stock_list)}개")
    
    # Supabase 클라이언트
    supabase = get_supabase_client()
    
    total_records = 0
    success_count = 0
    fail_count = 0
    
    print("\n4. 데이터 다운로드 시작...")
    print("-" * 40)
    
    for i, (code, name) in enumerate(stock_list, 1):
        print(f"\n[{i}/{len(stock_list)}] {name} ({code})")
        
        try:
            # 기존 데이터 확인
            existing = supabase.table('price_data').select('count', count='exact')\
                .eq('stock_code', code)\
                .gte('date', start_date.strftime('%Y-%m-%d'))\
                .execute()
            
            existing_count = existing.count if existing else 0
            
            if existing_count > 0:
                print(f"   이미 {existing_count}개 레코드 존재 - 스킵")
                continue
            
            # 키움 API로 데이터 조회
            print(f"   데이터 다운로드 중...")
            df = kiwoom.get_ohlcv(
                code,
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            if df is not None and not df.empty:
                # Supabase에 저장
                saved = kiwoom.save_to_supabase(df, code)
                total_records += saved
                success_count += 1
                print(f"   ✓ {len(df)}개 레코드 저장 완료")
            else:
                fail_count += 1
                print(f"   ✗ 데이터 조회 실패")
            
            # API 호출 제한 방지 (0.5초 대기)
            time.sleep(0.5)
            
        except Exception as e:
            fail_count += 1
            print(f"   ✗ 오류 발생: {e}")
            continue
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("다운로드 완료!")
    print("=" * 60)
    print(f"성공: {success_count}개 종목")
    print(f"실패: {fail_count}개 종목")
    print(f"총 저장된 레코드: {total_records:,}개")
    
    # 저장된 데이터 통계
    print("\n5. 저장된 데이터 통계...")
    try:
        stats = supabase.table('price_data').select('stock_code', count='exact')\
            .execute()
        
        print(f"총 데이터 레코드 수: {stats.count:,}개")
    except:
        pass


def verify_data():
    """저장된 데이터 검증"""
    print("\n데이터 검증 중...")
    supabase = get_supabase_client()
    
    # 종목별 데이터 개수 확인
    result = supabase.rpc('get_stock_data_stats').execute()
    
    if result.data:
        print("\n종목별 저장된 데이터:")
        print("-" * 40)
        for row in result.data:
            print(f"{row['stock_code']}: {row['count']:,}개 레코드")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='과거 주가 데이터 다운로드')
    parser.add_argument('--years', type=int, default=10, help='다운로드할 연수 (기본: 10년)')
    parser.add_argument('--verify', action='store_true', help='데이터 검증만 수행')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_data()
    else:
        download_historical_data(args.years)