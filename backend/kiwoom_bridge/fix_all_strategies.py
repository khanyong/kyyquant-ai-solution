#!/usr/bin/env python
"""
Supabase에 저장된 모든 전략을 올바른 형식으로 수정하는 통합 스크립트
- indicators 배열이 비어있는 문제 해결
- 대문자를 소문자로 변환
- params 구조 추가
- operator 형식 수정
"""

import os
import json
import sys
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Supabase 환경변수가 설정되지 않음")
    print("   .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정하세요.")
    exit(1)

supabase = create_client(url, key)

# 템플릿별 기본 지표 매핑
TEMPLATE_INDICATORS = {
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
    ],
    'volume-spike': [
        {"type": "volume", "params": {}},
        {"type": "ma", "params": {"period": 20}}
    ],
    'stochastic-oversold': [
        {"type": "stochastic", "params": {"k": 14, "d": 3}}
    ]
}

def extract_indicators_from_conditions(conditions):
    """조건에서 사용된 지표 추출"""
    indicators = {}

    for cond in conditions:
        indicator = str(cond.get('indicator', '')).lower()
        value = str(cond.get('value', '')).lower()

        # indicator와 value 모두에서 지표 찾기
        for check_val in [indicator, value]:
            # MA 지표
            if 'ma_' in check_val or 'sma_' in check_val:
                parts = check_val.replace('sma_', 'ma_').split('_')
                if len(parts) > 1 and parts[1].isdigit():
                    period = int(parts[1])
                    key = f"ma_{period}"
                    if key not in indicators:
                        indicators[key] = {"type": "ma", "params": {"period": period}}

            # RSI 지표
            elif 'rsi' in check_val:
                if '_' in check_val:
                    parts = check_val.split('_')
                    if len(parts) > 1 and parts[1].isdigit():
                        period = int(parts[1])
                        key = f"rsi_{period}"
                        if key not in indicators:
                            indicators[key] = {"type": "rsi", "params": {"period": period}}
                else:
                    if "rsi_14" not in indicators:
                        indicators["rsi_14"] = {"type": "rsi", "params": {"period": 14}}

            # MACD 지표
            elif 'macd' in check_val:
                if "macd" not in indicators:
                    indicators["macd"] = {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}

            # Bollinger Band
            elif 'bb' in check_val or 'bollinger' in check_val:
                if "bb" not in indicators:
                    indicators["bb"] = {"type": "bb", "params": {"period": 20, "std": 2}}

            # Stochastic
            elif 'stoch' in check_val:
                if "stochastic" not in indicators:
                    indicators["stochastic"] = {"type": "stochastic", "params": {"k": 14, "d": 3}}

            # Volume
            elif 'volume' in check_val and check_val != 'volume':
                if "volume" not in indicators:
                    indicators["volume"] = {"type": "volume", "params": {}}

    return list(indicators.values())

def extract_indicators_from_stage_strategy(stage_strategy):
    """Stage 전략에서 지표 추출"""
    indicators = {}

    stages = stage_strategy.get('stages', [])
    for stage in stages:
        for ind in stage.get('indicators', []):
            ind_id = ind.get('indicatorId', '').lower()
            params = ind.get('params', {})

            if 'stoch' in ind_id:
                key = "stochastic"
                if key not in indicators:
                    indicators[key] = {"type": "stochastic", "params": {"k": params.get('k', 14), "d": params.get('d', 3)}}
            elif 'macd' in ind_id:
                key = "macd"
                if key not in indicators:
                    indicators[key] = {"type": "macd", "params": {"fast": params.get('fast', 12), "slow": params.get('slow', 26), "signal": params.get('signal', 9)}}
            elif 'rsi' in ind_id:
                period = params.get('period', 14)
                key = f"rsi_{period}"
                if key not in indicators:
                    indicators[key] = {"type": "rsi", "params": {"period": period}}
            elif 'ma' in ind_id:
                period = params.get('period', 20)
                key = f"ma_{period}"
                if key not in indicators:
                    indicators[key] = {"type": "ma", "params": {"period": period}}
            elif 'bb' in ind_id or 'bollinger' in ind_id:
                key = "bb"
                if key not in indicators:
                    indicators[key] = {"type": "bb", "params": {"period": params.get('period', 20), "std": params.get('std', 2)}}

    return list(indicators.values())

def fix_strategy_config(config, strategy_name="Unknown"):
    """전략 config를 올바른 형식으로 수정"""

    fixed_config = config.copy()
    changes = []

    # 1. indicators가 비어있는 경우 처리
    if not fixed_config.get('indicators') or len(fixed_config.get('indicators', [])) == 0:
        extracted_indicators = []

        # 1-1. templateId로 판단
        template_id = fixed_config.get('templateId', '')
        if template_id and template_id in TEMPLATE_INDICATORS:
            extracted_indicators = TEMPLATE_INDICATORS[template_id]
            changes.append(f"템플릿 '{template_id}'에서 {len(extracted_indicators)}개 지표 추가")

        # 1-2. Stage 전략에서 추출
        if not extracted_indicators and fixed_config.get('useStageBasedStrategy'):
            # buyStageStrategy에서 추출
            if fixed_config.get('buyStageStrategy'):
                buy_indicators = extract_indicators_from_stage_strategy(fixed_config['buyStageStrategy'])
                extracted_indicators.extend(buy_indicators)

            # sellStageStrategy에서 추출
            if fixed_config.get('sellStageStrategy'):
                sell_indicators = extract_indicators_from_stage_strategy(fixed_config['sellStageStrategy'])
                for ind in sell_indicators:
                    if ind not in extracted_indicators:
                        extracted_indicators.append(ind)

            if extracted_indicators:
                changes.append(f"Stage 전략에서 {len(extracted_indicators)}개 지표 추출")

        # 1-3. 조건에서 추출
        if not extracted_indicators:
            all_conditions = fixed_config.get('buyConditions', []) + fixed_config.get('sellConditions', [])
            if all_conditions:
                extracted_indicators = extract_indicators_from_conditions(all_conditions)
                if extracted_indicators:
                    changes.append(f"조건에서 {len(extracted_indicators)}개 지표 추출")

        if extracted_indicators:
            fixed_config['indicators'] = extracted_indicators

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
                    changes.append(f"params 구조 추가: {ind.get('type')}")
                else:
                    # type을 소문자로
                    if ind.get('type', '').isupper():
                        changes.append(f"지표 타입 소문자화: {ind.get('type')}")
                    ind['type'] = ind.get('type', '').lower()
                    fixed_indicators.append(ind)

        if fixed_indicators:
            fixed_config['indicators'] = fixed_indicators

    # 3. 조건의 지표명과 operator 수정
    # buyConditions
    for cond in fixed_config.get('buyConditions', []):
        # 지표명 소문자로
        if 'indicator' in cond:
            orig = cond['indicator']
            cond['indicator'] = cond['indicator'].lower().replace('sma_', 'ma_')
            if orig != cond['indicator']:
                changes.append(f"매수 지표명: {orig} → {cond['indicator']}")

        # value도 지표명이면 소문자로
        if 'value' in cond and isinstance(cond['value'], str):
            if not cond['value'].replace('.', '').replace('-', '').isdigit():
                orig = cond['value']
                cond['value'] = cond['value'].lower().replace('sma_', 'ma_')
                if orig != cond['value']:
                    changes.append(f"매수 value: {orig} → {cond['value']}")

        # operator 수정
        operator = cond.get('operator', '')
        if operator in ['>', 'CROSS_ABOVE'] and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_above'
            changes.append(f"매수 operator: {operator} → cross_above")
        elif operator in ['<', 'CROSS_BELOW'] and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_below'
            changes.append(f"매수 operator: {operator} → cross_below")
        elif operator != operator.lower():
            orig = operator
            cond['operator'] = operator.lower()
            changes.append(f"매수 operator: {orig} → {cond['operator']}")

    # sellConditions
    for cond in fixed_config.get('sellConditions', []):
        # 지표명 소문자로
        if 'indicator' in cond:
            orig = cond['indicator']
            cond['indicator'] = cond['indicator'].lower().replace('sma_', 'ma_')
            if orig != cond['indicator']:
                changes.append(f"매도 지표명: {orig} → {cond['indicator']}")

        # value도 지표명이면 소문자로
        if 'value' in cond and isinstance(cond['value'], str):
            if not cond['value'].replace('.', '').replace('-', '').isdigit():
                orig = cond['value']
                cond['value'] = cond['value'].lower().replace('sma_', 'ma_')
                if orig != cond['value']:
                    changes.append(f"매도 value: {orig} → {cond['value']}")

        # operator 수정
        operator = cond.get('operator', '')
        if operator in ['<', 'CROSS_BELOW'] and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_below'
            changes.append(f"매도 operator: {operator} → cross_below")
        elif operator in ['>', 'CROSS_ABOVE'] and 'ma' in cond.get('indicator', '').lower():
            cond['operator'] = 'cross_above'
            changes.append(f"매도 operator: {operator} → cross_above")
        elif operator != operator.lower():
            orig = operator
            cond['operator'] = operator.lower()
            changes.append(f"매도 operator: {orig} → {cond['operator']}")

    return fixed_config, changes

def main():
    """메인 실행 함수"""

    print("="*60)
    print("Supabase 전략 수정 스크립트")
    print("="*60)

    # 1. 모든 전략 가져오기
    print("\n📊 전략 로드 중...")
    response = supabase.table('strategies').select("*").execute()

    if not response.data:
        print("❌ 전략이 없거나 가져올 수 없음")
        return

    strategies = response.data
    print(f"✅ 총 {len(strategies)}개 전략 발견")

    # 2. 수정이 필요한 전략 확인
    print("\n🔍 수정이 필요한 전략 확인 중...")
    strategies_to_fix = []

    for strategy in strategies:
        config = strategy.get('config', {})
        if not config:
            continue

        # indicators가 비어있거나 대문자가 포함된 경우
        needs_fix = False

        # indicators 체크
        if not config.get('indicators') or len(config.get('indicators', [])) == 0:
            needs_fix = True

        # 대문자 체크
        for cond in config.get('buyConditions', []) + config.get('sellConditions', []):
            if cond.get('indicator', '').upper() == cond.get('indicator', ''):
                needs_fix = True
                break
            if cond.get('operator', '').upper() == cond.get('operator', ''):
                needs_fix = True
                break

        if needs_fix:
            strategies_to_fix.append(strategy)

    print(f"⚠️  {len(strategies_to_fix)}개 전략이 수정 필요")

    if not strategies_to_fix:
        print("✨ 모든 전략이 이미 올바른 형식입니다!")
        return

    # 3. 수정 시작
    print("\n수정할 전략 목록:")
    for i, strategy in enumerate(strategies_to_fix, 1):
        print(f"  {i}. {strategy.get('name', 'Unknown')} (ID: {strategy.get('id')})")

    # 확인
    print("\n" + "="*60)
    response = input("위 전략들을 수정하시겠습니까? (y/n): ")

    if response.lower() != 'y':
        print("취소되었습니다.")
        return

    # 4. 각 전략 수정
    print("\n🔧 전략 수정 시작...")
    success_count = 0
    fail_count = 0

    for strategy in strategies_to_fix:
        print(f"\n{'='*40}")
        print(f"전략: {strategy.get('name', 'Unknown')}")
        print(f"ID: {strategy.get('id')}")

        try:
            # config 가져오기
            config = strategy.get('config', {})

            # config 수정
            fixed_config, changes = fix_strategy_config(config, strategy.get('name', 'Unknown'))

            if changes:
                print("\n변경사항:")
                for change in changes:
                    print(f"  • {change}")

            # Supabase 업데이트
            update_response = supabase.table('strategies').update({
                'config': fixed_config,
                'updated_at': datetime.now().isoformat()
            }).eq('id', strategy['id']).execute()

            if update_response.data:
                print("✅ 성공적으로 업데이트됨")
                success_count += 1
            else:
                print("❌ 업데이트 실패")
                fail_count += 1

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            fail_count += 1

    # 5. 결과 요약
    print("\n" + "="*60)
    print("수정 완료")
    print("="*60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")

    if success_count > 0:
        print("\n✨ 전략이 수정되었습니다!")
        print("📈 이제 백테스트를 다시 실행해보세요.")
        print("\n수정된 내용:")
        print("  • indicators 배열이 비어있던 전략에 지표 추가")
        print("  • 대문자를 소문자로 변환 (MA_20 → ma_20)")
        print("  • operator 형식 수정 (> → cross_above)")
        print("  • params 구조 추가")

if __name__ == "__main__":
    main()