#!/usr/bin/env python3
"""
전략에 포함된 종목들만 일봉 데이터 다운로드
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import time

sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()

def main():
    # Supabase 초기화
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)

    # Kiwoom API 초기화
    kiwoom = get_kiwoom_client()

    print("=" * 80)
    print("전략 종목 일봉 데이터 업데이트")
    print("=" * 80)

    # 활성화된 전략의 모든 종목 가져오기
    print("\n1. 활성 전략의 종목 조회 중...")
    result = supabase.rpc('get_active_strategies_with_universe').execute()

    if not result.data:
        print("활성화된 전략이 없습니다.")
        return

    # 모든 종목 코드 수집 (중복 제거)
    all_stocks = set()
    for strategy in result.data:
        filtered_stocks = strategy.get('filtered_stocks', [])
        for stock in filtered_stocks:
            if isinstance(stock, dict) and 'stock_code' in stock:
                all_stocks.add(stock['stock_code'])
            elif isinstance(stock, str):
                all_stocks.add(stock)

    stock_list = sorted(list(all_stocks))
    print(f"   총 {len(stock_list)}개 종목 발견")

    # 각 종목의 일봉 데이터 다운로드
    print("\n2. 일봉 데이터 다운로드 중 (대상 기간: 약 3년)...")
    success_count = 0
    fail_count = 0

    total_stocks = len(stock_list)
    
    for i, stock_code in enumerate(stock_list, 1):
        try:
            print(f"\n[{i}/{total_stocks}] {stock_code} 처리 중...")
            
            # Rate limiting
            time.sleep(0.5)
            
            # Pagination Logic
            # 목표: 약 3년치 (약 1200거래일)
            # 1회 최대 600일이므로 3번 반복 (600 + 600 + X)
            
            current_base_date = None # 오늘부터 시작
            total_fetched = 0
            
            # 3회 반복 (약 4.5년 커버 가능, 충분함)
            for page in range(1, 4): 
                print(f"  - Page {page}: Fetching 600 days from {current_base_date if current_base_date else 'Today'}")
                
                # 데이터 조회 (get_historical_price 사용)
                daily_data = kiwoom.get_historical_price(stock_code, period=600, base_date=current_base_date)

                if daily_data and len(daily_data) > 0:
                    # Supabase에 저장 (upsert)
                    # 데이터 변환 (Kiwoom API format -> DB format)
                    # get_historical_price returns: 
                    # [{'stck_bsop_date': '20250927', 'stck_clpr': '77000', ...}]
                    
                    db_data = []
                    dates = []
                    
                    for row in daily_data:
                        # Key Mapping for Kiwoom Mock API (chart endpoint)
                        # dt -> trade_date
                        # cur_prc -> close
                        # open_pric -> open
                        # high_pric -> high
                        # low_pric -> low
                        # trde_qty -> volume
                        
                        trade_date = row['dt']
                        formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}"
                        dates.append(trade_date)
                        
                        db_data.append({
                            'stock_code': stock_code,
                            'trade_date': formatted_date,
                            'close': float(row['cur_prc']),
                            'open': float(row['open_pric']),
                            'high': float(row['high_pric']),
                            'low': float(row['low_pric']),
                            'volume': int(row['trde_qty'])
                        })
                    
                    # Upsert to Supabase
                    supabase.table('kw_price_daily').upsert(
                        db_data,
                        on_conflict='stock_code,trade_date'
                    ).execute()

                    fetched_count = len(db_data)
                    total_fetched += fetched_count
                    print(f"    -> Saved {fetched_count} records.")
                    
                    # 다음 페이지를 위해 가장 과거 날짜 계산
                    # data is sorted by date desc (latest first)
                    oldest_date_str = min(dates) # 'YYYYMMDD'
                    
                    # oldest_date - 1 day
                    oldest_date = datetime.strptime(oldest_date_str, '%Y%m%d')
                    next_base_date = (oldest_date - timedelta(days=1)).strftime('%Y%m%d')
                    current_base_date = next_base_date
                    
                    # 만약 가져온 데이터가 요청한 600개보다 적으면 더 이상 데이터가 없다는 의미
                    if fetched_count < 550:
                        print("    -> End of history reached.")
                        break
                        
                else:
                    print("    -> No data received or end of history.")
                    break
                    
                time.sleep(0.5) # API 부하 조절

            if total_fetched > 0:
                print(f"  => Summary: Total {total_fetched} records saved for {stock_code}")
                success_count += 1
            else:
                print(f"  => FAIL: No data saved for {stock_code}")
                fail_count += 1

        except Exception as e:
            print(f"ERROR processing {stock_code}: {e}")
            fail_count += 1

            # 429 에러면 잠시 대기
            if "429" in str(e):
                print("   ⏸️  Rate limit - 대기 중 (30초)...")
                time.sleep(30)
                
        # 종목 간 딜레이
        time.sleep(1)

    # 결과 요약
    print("\n" + "=" * 80)
    print("완료!")
    print(f"  성공: {success_count}개 종목")
    print(f"  실패: {fail_count}개 종목")
    print("=" * 80)

if __name__ == '__main__':
    main()
