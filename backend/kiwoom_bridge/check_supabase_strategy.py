"""
Supabase에 저장된 전략 형식 확인
"""

import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Supabase 환경변수가 설정되지 않음")
    exit(1)

supabase = create_client(url, key)

# 전략 목록 가져오기
response = supabase.table('strategies').select("*").limit(5).execute()

if response.data:
    print("="*60)
    print("Supabase에 저장된 전략")
    print("="*60)

    for strategy in response.data:
        print(f"\n전략: {strategy.get('name', 'Unknown')}")
        print(f"ID: {strategy.get('id')}")

        # config 필드 확인
        config = strategy.get('config', {})
        if config:
            print("\nconfig 내용:")
            print(json.dumps(config, indent=2, ensure_ascii=False))

            # 문제점 체크
            indicators = config.get('indicators', [])
            if indicators and len(indicators) > 0:
                first_ind = indicators[0]
                if 'params' not in first_ind:
                    print("⚠️  문제: indicators에 params 구조 없음")
                if isinstance(first_ind.get('type', ''), str) and first_ind['type'].isupper():
                    print("⚠️  문제: 지표 type이 대문자")

            buy_conditions = config.get('buyConditions', [])
            if buy_conditions and len(buy_conditions) > 0:
                first_cond = buy_conditions[0]
                indicator = first_cond.get('indicator', '')
                operator = first_cond.get('operator', '')

                if '_' in indicator and indicator.split('_')[0].isupper():
                    print(f"⚠️  문제: 지표명이 대문자 포함: {indicator}")
                if operator.isupper():
                    print(f"⚠️  문제: operator가 대문자: {operator}")
        else:
            print("❌ config 필드가 비어있음")

        print("-"*40)
else:
    print("❌ 전략이 없거나 가져올 수 없음")

print("\n" + "="*60)
print("해결 방법:")
print("1. 프론트엔드에서 새 전략을 저장할 때 올바른 형식으로 저장")
print("2. 기존 전략을 수정하여 다시 저장")
print("3. 또는 Supabase에서 직접 수정")
print("="*60)