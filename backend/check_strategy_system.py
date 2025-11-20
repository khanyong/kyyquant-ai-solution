"""
Supabase 전략 시스템 구조 확인
- strategies 테이블 구조
- 전략-지표 연결 방식
- 전략 빌더와의 통합
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd

load_dotenv()

def check_strategy_system():
    """전략 시스템 전체 구조 확인"""

    # Supabase 연결
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        print("❌ Supabase 연결 정보 없음")
        return

    try:
        client = create_client(url, key)

        print("=" * 60)
        print("[INFO] Supabase Strategy System Analysis")
        print("=" * 60)

        # 1. strategies 테이블 구조 확인
        print("\n1️⃣ strategies 테이블 구조:")
        print("-" * 40)

        # 샘플 전략 가져오기
        strategies = client.table('strategies').select('*').limit(3).execute()

        if strategies.data and len(strategies.data) > 0:
            sample = strategies.data[0]
            print("컬럼 목록:")
            for key in sample.keys():
                value_type = type(sample[key]).__name__
                print(f"  - {key}: {value_type}")
                if key in ['indicators', 'buy_condition', 'sell_condition', 'strategy_config']:
                    if sample[key]:
                        if isinstance(sample[key], str):
                            try:
                                parsed = json.loads(sample[key])
                                print(f"    내용: {json.dumps(parsed, ensure_ascii=False, indent=6)[:200]}...")
                            except:
                                print(f"    내용: {sample[key][:100]}...")
                        else:
                            print(f"    내용: {json.dumps(sample[key], ensure_ascii=False, indent=6)[:200]}...")
        else:
            print("❌ strategies 테이블이 비어있음")

        # 2. 전략-지표 관계 분석
        print("\n2️⃣ 전략-지표 관계:")
        print("-" * 40)

        if strategies.data:
            for strategy in strategies.data[:2]:  # 처음 2개만
                print(f"\n전략: {strategy.get('name', 'Unknown')}")

                # indicators 필드 분석
                indicators_field = strategy.get('indicators')
                if indicators_field:
                    if isinstance(indicators_field, str):
                        try:
                            indicators = json.loads(indicators_field)
                        except:
                            indicators = indicators_field
                    else:
                        indicators = indicators_field

                    if isinstance(indicators, list):
                        print(f"  지표 개수: {len(indicators)}")
                        for ind in indicators[:3]:  # 처음 3개만
                            if isinstance(ind, dict):
                                print(f"    - {ind.get('name', 'unknown')}: {ind.get('params', {})}")
                    else:
                        print(f"  지표 형식: {type(indicators).__name__}")
                else:
                    print("  지표 없음")

                # 매수/매도 조건 분석
                buy_cond = strategy.get('buy_condition')
                sell_cond = strategy.get('sell_condition')

                if buy_cond:
                    print(f"  매수조건: {str(buy_cond)[:100]}...")
                if sell_cond:
                    print(f"  매도조건: {str(sell_cond)[:100]}...")

        # 3. indicators 테이블과의 관계
        print("\n3️⃣ indicators 테이블 활용:")
        print("-" * 40)

        # indicators 테이블 확인
        indicators_table = client.table('indicators').select('name, calculation_type').limit(10).execute()

        if indicators_table.data:
            unique_indicators = {}
            for ind in indicators_table.data:
                name = ind.get('name')
                calc_type = ind.get('calculation_type')
                if name not in unique_indicators:
                    unique_indicators[name] = calc_type

            print("사용 가능한 지표:")
            for name, calc_type in list(unique_indicators.items())[:10]:
                print(f"  - {name}: {calc_type}")

        # 4. 전략 저장 방식
        print("\n4️⃣ 전략 저장 방식:")
        print("-" * 40)

        print("현재 시스템:")
        print("  1. 프론트엔드 전략 빌더에서 지표 선택")
        print("  2. 지표 이름과 파라미터를 indicators 필드에 저장")
        print("  3. 백테스트 시 indicators 테이블에서 정의 조회")
        print("  4. calculator.py가 지표 계산")
        print("  5. engine.py가 매매 신호 생성")

        # 5. 전략 통계
        print("\n5️⃣ 전략 통계:")
        print("-" * 40)

        # 전체 전략 수
        all_strategies = client.table('strategies').select('id, name, created_at, user_id').execute()

        if all_strategies.data:
            total = len(all_strategies.data)
            print(f"총 전략 수: {total}")

            # 사용자별 전략 수
            user_strategies = {}
            for s in all_strategies.data:
                user_id = s.get('user_id')
                if user_id:
                    if user_id not in user_strategies:
                        user_strategies[user_id] = 0
                    user_strategies[user_id] += 1

            print(f"사용자 수: {len(user_strategies)}")

            # 최근 생성된 전략
            recent = sorted(all_strategies.data,
                          key=lambda x: x.get('created_at', ''),
                          reverse=True)[:3]

            print("\n최근 생성 전략:")
            for s in recent:
                name = s.get('name', 'Unknown')
                created = s.get('created_at', 'Unknown')[:10]
                print(f"  - {name}: {created}")

        # 6. 데이터 플로우
        print("\n6️⃣ 데이터 플로우:")
        print("-" * 40)
        print("""
전략 빌더 (Frontend)
    ↓ (전략 설정)
strategies 테이블 (Supabase)
    ↓ (백테스트 요청)
API 서버 (Backend)
    ↓ (지표명 전달)
indicators 테이블 (Supabase)
    ↓ (계산 정의)
calculator.py
    ↓ (계산 결과)
engine.py
    ↓ (매매 신호)
백테스트 결과
        """)

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def check_sample_strategy_detail():
    """샘플 전략 상세 분석"""

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        return

    try:
        client = create_client(url, key)

        # 골든크로스 전략 찾기
        golden_cross = client.table('strategies').select('*').ilike('name', '%golden%').limit(1).execute()

        if golden_cross.data:
            strategy = golden_cross.data[0]

            print("\n" + "=" * 60)
            print("🎯 골든크로스 전략 상세 분석")
            print("=" * 60)

            print(f"\n전략명: {strategy.get('name')}")
            print(f"ID: {strategy.get('id')}")

            # indicators 상세
            indicators = strategy.get('indicators')
            if indicators:
                if isinstance(indicators, str):
                    indicators = json.loads(indicators)

                print("\n📊 사용 지표:")
                for ind in indicators:
                    print(f"  - 지표: {ind.get('name')}")
                    print(f"    파라미터: {json.dumps(ind.get('params', {}), ensure_ascii=False)}")

            # 조건식
            print(f"\n📈 매수 조건: {strategy.get('buy_condition')}")
            print(f"📉 매도 조건: {strategy.get('sell_condition')}")

            # strategy_config
            config = strategy.get('strategy_config')
            if config:
                if isinstance(config, str):
                    config = json.loads(config)

                print("\n⚙️ 전략 설정:")
                print(json.dumps(config, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ 샘플 전략 분석 실패: {e}")

if __name__ == "__main__":
    # 전체 시스템 확인
    success = check_strategy_system()

    if success:
        # 샘플 전략 상세 분석
        check_sample_strategy_detail()

    print("\n" + "=" * 60)
    print("✅ 분석 완료")
    print("=" * 60)