"""
Supabase에 저장된 모든 전략을 올바른 형식으로 마이그레이션
"""

import os
import json
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Supabase 환경변수가 설정되지 않음")
    exit(1)

supabase = create_client(url, key)

def fix_strategy_config(config):
    """전략 config를 올바른 형식으로 수정"""

    fixed_config = config.copy()

    # 1. indicators가 비어있는 경우 처리
    if not fixed_config.get('indicators') or len(fixed_config.get('indicators', [])) == 0:
        print("  ⚠️  indicators가 비어있음. 추출 시작...")

        extracted_indicators = []

        # 1-1. templateId로 판단
        template_id = fixed_config.get('templateId', '')
        if template_id:
            print(f"  템플릿 ID 발견: {template_id}")

            template_indicators = {
                'golden-cross': [
                    {"type": "ma", "params": {"period": 20}},
                    {"type": "ma", "params": {"period": 60}}
                ],
                'rsi-reversal': [
                    {"type": "rsi", "params": {"period": 14}}
                ],
                'bollinger-band': [
                    {"type": "bb", "params": {"period": 20, "std": 2}},
                    {"type": "rsi", "params": {"period": 14}}
                ],
                'macd-signal': [
                    {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
                ]
            }

            if template_id in template_indicators:
                extracted_indicators = template_indicators[template_id]

        # 1-2. Stage 전략에서 추출
        if not extracted_indicators and fixed_config.get('useStageBasedStrategy'):
            print("  Stage 전략에서 지표 추출...")
            indicator_set = set()

            # buyStageStrategy 분석
            buy_stages = fixed_config.get('buyStageStrategy', {}).get('stages', [])
            for stage in buy_stages:
                for ind in stage.get('indicators', []):
                    ind_id = ind.get('indicatorId', '').lower()
                    params = ind.get('params', {})

                    if 'stoch' in ind_id:
                        indicator_set.add(('stochastic', params.get('k', 14), params.get('d', 3)))
                    elif 'macd' in ind_id:
                        indicator_set.add(('macd', params.get('fast', 12), params.get('slow', 26), params.get('signal', 9)))
                    elif 'rsi' in ind_id:
                        indicator_set.add(('rsi', params.get('period', 14)))
                    elif 'ma' in ind_id:
                        indicator_set.add(('ma', params.get('period', 20)))
                    elif 'bb' in ind_id or 'bollinger' in ind_id:
                        indicator_set.add(('bb', params.get('period', 20), params.get('std', 2)))

            # sellStageStrategy 분석
            sell_stages = fixed_config.get('sellStageStrategy', {}).get('stages', [])
            for stage in sell_stages:
                for ind in stage.get('indicators', []):
                    ind_id = ind.get('indicatorId', '').lower()
                    params = ind.get('params', {})

                    if 'stoch' in ind_id:
                        indicator_set.add(('stochastic', params.get('k', 14), params.get('d', 3)))
                    elif 'macd' in ind_id:
                        indicator_set.add(('macd', params.get('fast', 12), params.get('slow', 26), params.get('signal', 9)))

            # Set을 List로 변환
            for ind_tuple in indicator_set:
                if ind_tuple[0] == 'stochastic':
                    extracted_indicators.append({"type": "stochastic", "params": {"k": ind_tuple[1], "d": ind_tuple[2]}})
                elif ind_tuple[0] == 'macd':
                    extracted_indicators.append({"type": "macd", "params": {"fast": ind_tuple[1], "slow": ind_tuple[2], "signal": ind_tuple[3]}})
                elif ind_tuple[0] == 'rsi':
                    extracted_indicators.append({"type": "rsi", "params": {"period": ind_tuple[1]}})
                elif ind_tuple[0] == 'ma':
                    extracted_indicators.append({"type": "ma", "params": {"period": ind_tuple[1]}})
                elif ind_tuple[0] == 'bb':
                    extracted_indicators.append({"type": "bb", "params": {"period": ind_tuple[1], "std": ind_tuple[2]}})

        # 1-3. 조건에서 추출
        if not extracted_indicators:
            print("  조건에서 지표 추출...")
            indicator_set = set()

            # 모든 조건 분석
            all_conditions = fixed_config.get('buyConditions', []) + fixed_config.get('sellConditions', [])
            for cond in all_conditions:
                indicator = cond.get('indicator', '').lower()
                value = str(cond.get('value', '')).lower()

                # indicator와 value 모두에서 지표 찾기
                for check_val in [indicator, value]:
                    if 'stoch' in check_val:
                        indicator_set.add('stochastic')
                    elif 'macd' in check_val:
                        indicator_set.add('macd')
                    elif 'rsi' in check_val:
                        # rsi_14 형태에서 period 추출
                        if '_' in check_val:
                            parts = check_val.split('_')
                            if len(parts) > 1 and parts[1].isdigit():
                                indicator_set.add(f'rsi_{parts[1]}')
                        else:
                            indicator_set.add('rsi')
                    elif 'ma_' in check_val:
                        # ma_20, ma_60 형태
                        parts = check_val.split('_')
                        if len(parts) > 1 and parts[1].isdigit():
                            indicator_set.add(f'ma_{parts[1]}')
                    elif 'sma_' in check_val:
                        parts = check_val.split('_')
                        if len(parts) > 1 and parts[1].isdigit():
                            indicator_set.add(f'ma_{parts[1]}')
                    elif 'bb' in check_val or 'bollinger' in check_val:
                        indicator_set.add('bb')

            # Set을 List로 변환
            for ind_name in indicator_set:
                if ind_name == 'stochastic':
                    extracted_indicators.append({"type": "stochastic", "params": {"k": 14, "d": 3}})
                elif ind_name == 'macd':
                    extracted_indicators.append({"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}})
                elif ind_name == 'rsi':
                    extracted_indicators.append({"type": "rsi", "params": {"period": 14}})
                elif ind_name.startswith('rsi_'):
                    period = int(ind_name.split('_')[1])
                    extracted_indicators.append({"type": "rsi", "params": {"period": period}})
                elif ind_name.startswith('ma_'):
                    period = int(ind_name.split('_')[1])
                    extracted_indicators.append({"type": "ma", "params": {"period": period}})
                elif ind_name == 'bb':
                    extracted_indicators.append({"type": "bb", "params": {"period": 20, "std": 2}})

        if extracted_indicators:
            fixed_config['indicators'] = extracted_indicators
            print(f"  ✅ {len(extracted_indicators)}개 지표 추가됨")

    # 2. 기존 indicators의 params 구조 확인 및 수정
    else:
        fixed_indicators = []
        for ind in fixed_config.get('indicators', []):
            if isinstance(ind, dict):
                # params가 없는 경우
                if 'params' not in ind and 'period' in ind:
                    fixed_ind = {
                        "type": ind.get('type', 'ma').lower(),
                        "params": {"period": ind.get('period', 20)}
                    }
                    fixed_indicators.append(fixed_ind)
                    print(f"  ⚠️  params 구조 수정: {ind} → {fixed_ind}")
                else:
                    # type을 소문자로
                    ind['type'] = ind.get('type', '').lower()
                    fixed_indicators.append(ind)

        if fixed_indicators:
            fixed_config['indicators'] = fixed_indicators

    # 3. 조건의 operator 수정
    # buyConditions
    for cond in fixed_config.get('buyConditions', []):
        # 지표명 소문자로
        if 'indicator' in cond:
            orig_indicator = cond['indicator']
            cond['indicator'] = cond['indicator'].lower().replace('ma_', 'ma_').replace('rsi_', 'rsi_').replace('sma_', 'ma_')
            if orig_indicator != cond['indicator']:
                print(f"  ⚠️  지표명 수정: {orig_indicator} → {cond['indicator']}")

        # value도 지표명이면 소문자로
        if 'value' in cond and isinstance(cond['value'], str) and not cond['value'].replace('.', '').replace('-', '').isdigit():
            orig_value = cond['value']
            cond['value'] = cond['value'].lower().replace('sma_', 'ma_')
            if orig_value != cond['value']:
                print(f"  ⚠️  value 수정: {orig_value} → {cond['value']}")

        # operator 수정
        operator = cond.get('operator', '')
        if operator == '>' and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_above'
            print(f"  ⚠️  operator 수정: > → cross_above")
        elif operator == '<' and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_below'
            print(f"  ⚠️  operator 수정: < → cross_below")
        elif operator.upper() != operator:
            cond['operator'] = operator.lower()
            print(f"  ⚠️  operator 소문자화: {operator} → {operator.lower()}")

    # sellConditions
    for cond in fixed_config.get('sellConditions', []):
        # 지표명 소문자로
        if 'indicator' in cond:
            orig_indicator = cond['indicator']
            cond['indicator'] = cond['indicator'].lower().replace('sma_', 'ma_')
            if orig_indicator != cond['indicator']:
                print(f"  ⚠️  지표명 수정: {orig_indicator} → {cond['indicator']}")

        # value도 지표명이면 소문자로
        if 'value' in cond and isinstance(cond['value'], str) and not cond['value'].replace('.', '').replace('-', '').isdigit():
            orig_value = cond['value']
            cond['value'] = cond['value'].lower().replace('sma_', 'ma_')
            if orig_value != cond['value']:
                print(f"  ⚠️  value 수정: {orig_value} → {cond['value']}")

        # operator 수정
        operator = cond.get('operator', '')
        if operator == '<' and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_below'
            print(f"  ⚠️  operator 수정: < → cross_below")
        elif operator == '>' and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_above'
            print(f"  ⚠️  operator 수정: > → cross_above")
        elif operator.upper() != operator:
            cond['operator'] = operator.lower()
            print(f"  ⚠️  operator 소문자화: {operator} → {operator.lower()}")

    return fixed_config


def migrate_strategies():
    """모든 전략 마이그레이션"""

    print("="*60)
    print("전략 마이그레이션 시작")
    print("="*60)

    # 1. 모든 전략 가져오기
    response = supabase.table('strategies').select("*").execute()

    if not response.data:
        print("❌ 전략이 없거나 가져올 수 없음")
        return

    strategies = response.data
    print(f"\n총 {len(strategies)}개 전략 발견")

    # 2. 각 전략 수정
    success_count = 0
    fail_count = 0

    for strategy in strategies:
        print(f"\n{'='*40}")
        print(f"전략: {strategy.get('name', 'Unknown')}")
        print(f"ID: {strategy.get('id')}")

        try:
            # config 가져오기
            config = strategy.get('config', {})

            if not config:
                print("  ❌ config가 비어있음. 건너뜀.")
                continue

            # 백업 (원본 저장)
            original_config = json.dumps(config, ensure_ascii=False)

            # config 수정
            fixed_config = fix_strategy_config(config)

            # 변경사항이 있는지 확인
            if json.dumps(fixed_config, ensure_ascii=False) == original_config:
                print("  ℹ️  변경사항 없음")
                continue

            # Supabase 업데이트
            update_response = supabase.table('strategies').update({
                'config': fixed_config,
                'updated_at': datetime.now().isoformat()
            }).eq('id', strategy['id']).execute()

            if update_response.data:
                print("  ✅ 성공적으로 업데이트됨")
                success_count += 1
            else:
                print("  ❌ 업데이트 실패")
                fail_count += 1

        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
            fail_count += 1

    # 3. 결과 요약
    print("\n" + "="*60)
    print("마이그레이션 완료")
    print("="*60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"ℹ️  건너뜀: {len(strategies) - success_count - fail_count}개")

    if success_count > 0:
        print("\n✨ 전략이 수정되었습니다. 이제 백테스트를 다시 실행해보세요!")


if __name__ == "__main__":
    # 확인
    response = input("모든 전략을 수정하시겠습니까? (y/n): ")

    if response.lower() == 'y':
        migrate_strategies()
    else:
        print("취소되었습니다.")

        # 대신 첫 번째 전략만 테스트
        print("\n첫 번째 전략만 테스트합니다...")
        response = supabase.table('strategies').select("*").limit(1).execute()

        if response.data:
            strategy = response.data[0]
            print(f"\n전략: {strategy.get('name')}")
            print("\n원본 config:")
            print(json.dumps(strategy.get('config', {}), indent=2, ensure_ascii=False))

            fixed_config = fix_strategy_config(strategy.get('config', {}))
            print("\n수정된 config:")
            print(json.dumps(fixed_config, indent=2, ensure_ascii=False))