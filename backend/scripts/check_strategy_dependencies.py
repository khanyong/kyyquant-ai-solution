"""
전략 의존성 확인 및 안전한 삭제
"""

import os
from supabase import create_client
from datetime import datetime

# Supabase 설정
SUPABASE_URL = 'https://kpnioqijldwmidguzwox.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY2NzY2NjgsImV4cCI6MjA0MjI1MjY2OH0.u8mE0Zii_TdN7Rwgehs83kYKVLWAuEz8sFYR2daJ4wA'

def check_empty_strategies():
    """config가 비어있는 전략 확인"""

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\n" + "="*80)
    print("EMPTY CONFIG STRATEGIES CHECK")
    print("="*80)

    # 1. config가 비어있는 전략 조회
    print("\n[1] Finding strategies with empty config...")

    try:
        # 모든 전략 조회
        result = supabase.table('strategies')\
            .select('id, name, user_id, config, created_at')\
            .execute()

        empty_strategies = []

        for strategy in result.data:
            config = strategy.get('config')

            # config가 비어있는 경우 체크
            if config is None or config == {} or config == 'null' or str(config) == '{}':
                empty_strategies.append({
                    'id': strategy['id'],
                    'name': strategy['name'],
                    'user_id': strategy['user_id'],
                    'created_at': strategy['created_at']
                })

        print(f"Found {len(empty_strategies)} strategies with empty config")

        if empty_strategies:
            print("\nEmpty strategies:")
            for s in empty_strategies[:10]:  # 처음 10개만 표시
                print(f"  - {s['name'][:50]:50} (ID: {s['id'][:8]}...)")

        # 2. 의존성 확인
        if empty_strategies:
            print(f"\n[2] Checking dependencies for {len(empty_strategies)} strategies...")

            strategy_ids = [s['id'] for s in empty_strategies]

            # 각 관련 테이블 확인
            tables_to_check = [
                'backtest_results',
                'user_favorites',
                'strategy_performance',
                'trading_signals'
            ]

            total_dependencies = 0

            for table in tables_to_check:
                try:
                    # 각 테이블에서 관련 레코드 수 확인
                    result = supabase.table(table)\
                        .select('strategy_id', count='exact')\
                        .in_('strategy_id', strategy_ids)\
                        .execute()

                    count = result.count if hasattr(result, 'count') else len(result.data)
                    print(f"  - {table}: {count} records")
                    total_dependencies += count

                except Exception as e:
                    print(f"  - {table}: Error checking ({str(e)[:50]})")

            print(f"\nTotal dependencies: {total_dependencies} records")

            # 3. 삭제 옵션 제공
            print("\n[3] Deletion options:")
            print("-"*40)

            if total_dependencies > 0:
                print("[WARNING] Dependencies found!")
                print("You must delete related records first:")
                print("\n-- SQL to delete dependencies:")

                for table in tables_to_check:
                    print(f"DELETE FROM {table}")
                    print(f"WHERE strategy_id IN (")
                    for sid in strategy_ids[:3]:
                        print(f"  '{sid}',")
                    if len(strategy_ids) > 3:
                        print(f"  -- ... and {len(strategy_ids)-3} more")
                    print(");")
                    print()

            print("\n-- SQL to delete strategies:")
            print("DELETE FROM strategies")
            print("WHERE id IN (")
            for sid in strategy_ids[:3]:
                print(f"  '{sid}',")
            if len(strategy_ids) > 3:
                print(f"  -- ... and {len(strategy_ids)-3} more")
            print(");")

            # 4. 안전한 삭제 함수
            print("\n[4] Safe deletion script:")
            print("-"*40)
            print("Run the SQL script: cleanup_empty_strategies.sql")
            print("Or use this Python function to delete safely")

            return empty_strategies

        else:
            print("\n[OK] No strategies with empty config found!")

    except Exception as e:
        print(f"\n[ERROR] {e}")

    print("\n" + "="*80)

def safe_delete_strategies(strategy_ids, confirm=False):
    """전략과 관련 데이터 안전하게 삭제"""

    if not confirm:
        print("[WARNING] Set confirm=True to actually delete")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print(f"\n[DELETING] {len(strategy_ids)} strategies...")

    # 순서대로 삭제 (foreign key 제약 고려)
    tables = [
        'trading_signals',
        'strategy_performance',
        'user_favorites',
        'backtest_results',
        'strategies'  # 마지막에 삭제
    ]

    for table in tables:
        try:
            if table == 'strategies':
                # strategies 테이블 직접 삭제
                result = supabase.table(table)\
                    .delete()\
                    .in_('id', strategy_ids)\
                    .execute()
            else:
                # 관련 테이블에서 strategy_id로 삭제
                result = supabase.table(table)\
                    .delete()\
                    .in_('strategy_id', strategy_ids)\
                    .execute()

            print(f"  - {table}: Deleted successfully")

        except Exception as e:
            print(f"  - {table}: Error - {e}")
            return False

    print(f"\n[DONE] Deleted {len(strategy_ids)} strategies and related data")
    return True

if __name__ == "__main__":
    # 1. 빈 전략 확인
    empty_strategies = check_empty_strategies()

    # 2. 삭제하려면 (주의: 실제 삭제됨!)
    # if empty_strategies:
    #     strategy_ids = [s['id'] for s in empty_strategies]
    #     safe_delete_strategies(strategy_ids, confirm=False)  # True로 변경하면 실제 삭제