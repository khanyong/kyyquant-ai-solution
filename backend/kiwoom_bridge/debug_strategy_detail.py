"""
전략 상세 디버그
"""

import requests
import json

def get_strategy_detail(strategy_id):
    """전략 상세 정보 조회"""

    # Supabase에서 직접 조회
    from supabase import create_client

    SUPABASE_URL = 'https://kpnioqijldwmidguzwox.supabase.co'
    SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY2NzY2NjgsImV4cCI6MjA0MjI1MjY2OH0.u8mE0Zii_TdN7Rwgehs83kYKVLWAuEz8sFYR2daJ4wA'

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    result = supabase.table('strategies')\
        .select('*')\
        .eq('id', strategy_id)\
        .single()\
        .execute()

    return result.data if result else None

# 두 전략 비교
strategies = [
    ("88d01e47-c979-4e80-bef8-746a53f3bbca", "테스트 전략 (작동함)"),
    ("931f0e11-afb3-4620-acfe-a24efd325ba0", "스윙 트레이딩 (0 거래)")
]

print("\n" + "="*80)
print("STRATEGY CONFIGURATION COMPARISON")
print("="*80)

for strategy_id, desc in strategies:
    print(f"\n[{desc}]")
    print(f"ID: {strategy_id}")
    print("-"*40)

    strategy = get_strategy_detail(strategy_id)

    if strategy:
        config = strategy.get('config', {})

        # 지표 확인
        indicators = config.get('indicators', [])
        print(f"\nIndicators ({len(indicators)}):")
        for i, ind in enumerate(indicators, 1):
            print(f"  {i}. {json.dumps(ind, ensure_ascii=False)}")

        # 매수 조건 확인
        buy_conditions = config.get('buyConditions', [])
        print(f"\nBuy Conditions ({len(buy_conditions)}):")
        for i, cond in enumerate(buy_conditions, 1):
            print(f"  {i}. {json.dumps(cond, ensure_ascii=False)}")

        # 매도 조건 확인
        sell_conditions = config.get('sellConditions', [])
        print(f"\nSell Conditions ({len(sell_conditions)}):")
        for i, cond in enumerate(sell_conditions, 1):
            print(f"  {i}. {json.dumps(cond, ensure_ascii=False)}")

        # 기타 설정
        print(f"\nOther Settings:")
        print(f"  - stopLoss: {config.get('stopLoss')}")
        print(f"  - takeProfit: {config.get('takeProfit')}")
        print(f"  - targetProfit: {config.get('targetProfit')}")
        print(f"  - useStageBasedStrategy: {config.get('useStageBasedStrategy')}")

        # 형식 문제 체크
        print(f"\nPotential Issues:")
        issues = []

        # 지표에 period가 params 밖에 있는지 체크
        for ind in indicators:
            if 'period' in ind and 'params' not in ind:
                issues.append(f"  ⚠️ Indicator has 'period' outside 'params': {ind}")
            if 'params' in ind and not isinstance(ind['params'], dict):
                issues.append(f"  ⚠️ Invalid params format: {ind}")

        # 조건의 operator 체크
        for cond in buy_conditions + sell_conditions:
            operator = cond.get('operator', '')
            if operator in ['cross_above', 'cross_below']:
                issues.append(f"  ⚠️ Complex operator '{operator}' may not be supported")

        if not issues:
            print("  ✅ No obvious issues found")
        else:
            for issue in issues:
                print(issue)

    else:
        print("  ERROR: Strategy not found")

    print("="*80)