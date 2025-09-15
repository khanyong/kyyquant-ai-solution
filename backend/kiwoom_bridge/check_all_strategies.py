"""
모든 전략 테스트 및 분석
"""

import os
import sys
from datetime import datetime
from supabase import create_client, Client
import json

# 환경 변수
SUPABASE_URL = 'https://kpnioqijldwmidguzwox.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY2NzY2NjgsImV4cCI6MjA0MjI1MjY2OH0.u8mE0Zii_TdN7Rwgehs83kYKVLWAuEz8sFYR2daJ4wA'

def check_strategies():
    """전략 설정 확인"""

    print("\n" + "="*80)
    print("STRATEGY CONFIGURATION CHECK")
    print("="*80)

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # 모든 전략 조회
        result = supabase.table('strategies')\
            .select('id, name, config')\
            .execute()

        if result.data:
            print(f"\nTotal strategies: {len(result.data)}")
            print("-"*80)

            for strategy in result.data[:10]:  # 처음 10개만
                print(f"\n[{strategy['name']}]")
                print(f"ID: {strategy['id']}")

                config = strategy.get('config', {})

                # 주요 설정 확인
                indicators = config.get('indicators', [])
                buy_conditions = config.get('buyConditions', [])
                sell_conditions = config.get('sellConditions', [])

                print(f"Indicators: {len(indicators)}")
                if indicators:
                    for i, ind in enumerate(indicators[:3]):
                        print(f"  {i+1}. {ind}")

                print(f"Buy Conditions: {len(buy_conditions)}")
                if buy_conditions:
                    for i, cond in enumerate(buy_conditions[:3]):
                        print(f"  {i+1}. {cond}")

                print(f"Sell Conditions: {len(sell_conditions)}")
                if sell_conditions:
                    for i, cond in enumerate(sell_conditions[:3]):
                        print(f"  {i+1}. {cond}")

                # 형식 문제 체크
                issues = []

                # 1. indicators 체크
                for ind in indicators:
                    if not isinstance(ind, dict):
                        issues.append(f"Invalid indicator format: {ind}")
                    elif 'type' not in ind:
                        issues.append(f"Missing 'type' in indicator: {ind}")
                    elif 'params' not in ind and 'period' in ind:
                        issues.append(f"'period' should be in 'params': {ind}")

                # 2. conditions 체크
                for cond in buy_conditions + sell_conditions:
                    if not isinstance(cond, dict):
                        issues.append(f"Invalid condition format: {cond}")
                    elif 'indicator' not in cond:
                        issues.append(f"Missing 'indicator' in condition: {cond}")
                    elif 'operator' not in cond:
                        issues.append(f"Missing 'operator' in condition: {cond}")

                    # operator 유효성 체크
                    operator = cond.get('operator', '')
                    if operator not in ['>', '<', '>=', '<=', '==', '!=', 'cross_above', 'cross_below']:
                        issues.append(f"Invalid operator '{operator}' in condition: {cond}")

                if issues:
                    print("\n⚠️ ISSUES FOUND:")
                    for issue in issues:
                        print(f"  - {issue}")
                else:
                    print("✅ No issues found")

                print("-"*80)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_strategies()