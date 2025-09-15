"""
기존 저장된 전략의 지표명을 소문자로 변환하는 마이그레이션 스크립트
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 환경 변수 로드
load_dotenv()

# Supabase 클라이언트 설정
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    print("Error: Supabase credentials not found")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def convert_indicator_to_lowercase(indicator_name):
    """지표명을 소문자로 변환"""
    if not indicator_name:
        return indicator_name

    # 문자열인 경우 소문자로 변환
    if isinstance(indicator_name, str):
        return indicator_name.lower()

    return indicator_name

def convert_condition(condition):
    """조건 객체의 지표명과 값을 소문자로 변환"""
    if not condition:
        return condition

    # indicator 필드 변환
    if 'indicator' in condition:
        condition['indicator'] = convert_indicator_to_lowercase(condition['indicator'])

    # value가 문자열이고 지표를 참조하는 경우 변환
    if 'value' in condition and isinstance(condition['value'], str):
        # 숫자가 아닌 문자열인 경우 (지표 참조)
        if not condition['value'].replace('.', '').replace('-', '').isdigit():
            condition['value'] = convert_indicator_to_lowercase(condition['value'])

    return condition

def migrate_strategy_config(config):
    """전략 설정의 모든 지표명을 소문자로 변환"""
    if not config:
        return config

    modified = False

    # buyConditions 변환
    if 'buyConditions' in config and isinstance(config['buyConditions'], list):
        for condition in config['buyConditions']:
            old_indicator = condition.get('indicator', '')
            old_value = condition.get('value', '')
            convert_condition(condition)
            if old_indicator != condition.get('indicator', '') or old_value != condition.get('value', ''):
                modified = True

    # sellConditions 변환
    if 'sellConditions' in config and isinstance(config['sellConditions'], list):
        for condition in config['sellConditions']:
            old_indicator = condition.get('indicator', '')
            old_value = condition.get('value', '')
            convert_condition(condition)
            if old_indicator != condition.get('indicator', '') or old_value != condition.get('value', ''):
                modified = True

    # buyStageStrategy 변환 (3단계 전략)
    if 'buyStageStrategy' in config and 'stages' in config['buyStageStrategy']:
        for stage in config['buyStageStrategy']['stages']:
            if 'indicators' in stage:
                for indicator in stage['indicators']:
                    if 'indicatorId' in indicator:
                        old_value = indicator['indicatorId']
                        indicator['indicatorId'] = convert_indicator_to_lowercase(indicator['indicatorId'])
                        if old_value != indicator['indicatorId']:
                            modified = True
                    if 'value' in indicator and isinstance(indicator['value'], str):
                        if not indicator['value'].replace('.', '').replace('-', '').isdigit():
                            old_value = indicator['value']
                            indicator['value'] = convert_indicator_to_lowercase(indicator['value'])
                            if old_value != indicator['value']:
                                modified = True

    # sellStageStrategy 변환 (3단계 전략)
    if 'sellStageStrategy' in config and 'stages' in config['sellStageStrategy']:
        for stage in config['sellStageStrategy']['stages']:
            if 'indicators' in stage:
                for indicator in stage['indicators']:
                    if 'indicatorId' in indicator:
                        old_value = indicator['indicatorId']
                        indicator['indicatorId'] = convert_indicator_to_lowercase(indicator['indicatorId'])
                        if old_value != indicator['indicatorId']:
                            modified = True
                    if 'value' in indicator and isinstance(indicator['value'], str):
                        if not indicator['value'].replace('.', '').replace('-', '').isdigit():
                            old_value = indicator['value']
                            indicator['value'] = convert_indicator_to_lowercase(indicator['value'])
                            if old_value != indicator['value']:
                                modified = True

    return config, modified

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("전략 지표명 마이그레이션 시작")
    print("=" * 60)

    try:
        # 모든 전략 가져오기
        response = supabase.table('strategies').select("*").execute()
        strategies = response.data

        if not strategies:
            print("저장된 전략이 없습니다.")
            return

        print(f"총 {len(strategies)}개의 전략을 찾았습니다.\n")

        updated_count = 0

        for strategy in strategies:
            strategy_id = strategy['id']
            strategy_name = strategy.get('name', 'Unknown')
            config = strategy.get('config', {})

            if not config:
                print(f"⏭️  전략 '{strategy_name}' (ID: {strategy_id[:8]}...): config가 비어있음")
                continue

            # config 변환
            updated_config, was_modified = migrate_strategy_config(config)

            if was_modified:
                # DB 업데이트
                update_response = supabase.table('strategies').update({
                    'config': updated_config,
                    'updated_at': datetime.now().isoformat()
                }).eq('id', strategy_id).execute()

                if update_response.data:
                    print(f"✅ 전략 '{strategy_name}' (ID: {strategy_id[:8]}...): 지표명 소문자로 변환 완료")
                    updated_count += 1

                    # 변경 내용 상세 출력
                    if 'buyConditions' in config:
                        print(f"   - 매수 조건: {len(config.get('buyConditions', []))}개")
                    if 'sellConditions' in config:
                        print(f"   - 매도 조건: {len(config.get('sellConditions', []))}개")
                else:
                    print(f"❌ 전략 '{strategy_name}' (ID: {strategy_id[:8]}...): 업데이트 실패")
            else:
                print(f"⏭️  전략 '{strategy_name}' (ID: {strategy_id[:8]}...): 변경 사항 없음 (이미 소문자)")

        print("\n" + "=" * 60)
        print(f"마이그레이션 완료: {updated_count}/{len(strategies)}개 전략 업데이트")
        print("=" * 60)

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()