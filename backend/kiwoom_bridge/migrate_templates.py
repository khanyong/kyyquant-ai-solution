"""
전략 템플릿 마이그레이션 스크립트
- 대문자 컬럼명을 소문자 표준으로 변환
- 파라미터 없는 지표명에 기본 파라미터 추가
"""

import json
from typing import Dict, Any, List
from core.naming import COLUMN_MAPPING, convert_legacy_column, _lc

def migrate_indicator_name(indicator: str) -> str:
    """
    지표명을 새 표준으로 변환

    Examples:
        'RSI_14' -> 'rsi_14'
        'BB_UPPER' -> 'bb_upper_20_2'
        'MACD' -> 'macd_12_26'
    """
    # 먼저 매핑 테이블 확인
    if indicator.upper() in COLUMN_MAPPING:
        return COLUMN_MAPPING[indicator.upper()]

    # 매핑에 없으면 소문자 변환 + 기본 파라미터 추가
    indicator_lower = indicator.lower()

    # 파라미터가 없는 지표에 기본값 추가
    if indicator_lower == 'rsi':
        return 'rsi_14'
    elif indicator_lower == 'sma':
        return 'sma_20'
    elif indicator_lower == 'ema':
        return 'ema_20'
    elif indicator_lower == 'atr':
        return 'atr_14'
    elif indicator_lower == 'adx':
        return 'adx_14'
    elif indicator_lower == 'cci':
        return 'cci_20'
    elif indicator_lower == 'mfi':
        return 'mfi_14'
    elif indicator_lower in ['willr', 'williams_r']:
        return 'willr_14'
    elif indicator_lower == 'vr':
        return 'vr_20'
    elif indicator_lower == 'macd':
        return 'macd_12_26'
    elif indicator_lower == 'macd_signal':
        return 'macd_signal_12_26_9'
    elif indicator_lower == 'macd_hist':
        return 'macd_hist_12_26_9'

    return indicator_lower

def migrate_condition(condition: Dict[str, Any]) -> Dict[str, Any]:
    """
    단일 조건을 새 표준으로 변환
    """
    migrated = dict(condition)

    # indicator 변환
    if 'indicator' in migrated:
        migrated['indicator'] = migrate_indicator_name(migrated['indicator'])

    # operator 소문자 변환
    if 'operator' in migrated:
        migrated['operator'] = _lc(migrated['operator'])

    # value가 지표명인 경우 변환
    if 'value' in migrated and isinstance(migrated['value'], str):
        # 숫자가 아닌 문자열이면 지표명일 가능성
        try:
            float(migrated['value'])
        except ValueError:
            migrated['value'] = migrate_indicator_name(migrated['value'])

    # combineWith 소문자 변환
    if 'combineWith' in migrated:
        migrated['combineWith'] = _lc(migrated['combineWith'])

    return migrated

def migrate_indicator_config(indicator: Dict[str, Any]) -> Dict[str, Any]:
    """
    지표 설정 변환
    """
    migrated = dict(indicator)

    # type을 대문자로 (설정에서는 대문자 유지)
    if 'type' in migrated:
        migrated['type'] = migrated['type'].upper()

    return migrated

def migrate_target_profit(target_profit: Dict[str, Any]) -> Dict[str, Any]:
    """
    목표 수익률 설정 변환
    """
    migrated = dict(target_profit)

    # simple mode
    if 'simple' in migrated and isinstance(migrated['simple'], dict):
        if 'combineWith' in migrated['simple']:
            migrated['simple']['combineWith'] = _lc(migrated['simple']['combineWith'])

    # staged mode
    if 'staged' in migrated and isinstance(migrated['staged'], dict):
        if 'combineWith' in migrated['staged']:
            migrated['staged']['combineWith'] = _lc(migrated['staged']['combineWith'])

        if 'stages' in migrated['staged']:
            for stage in migrated['staged']['stages']:
                if 'combineWith' in stage:
                    stage['combineWith'] = _lc(stage['combineWith'])

    # 이전 버전 호환성
    if 'combineWith' in migrated and 'simple' not in migrated and 'staged' not in migrated:
        migrated['combineWith'] = _lc(migrated['combineWith'])

    return migrated

def migrate_strategy_template(template: Dict[str, Any]) -> Dict[str, Any]:
    """
    전체 전략 템플릿 변환
    """
    migrated = dict(template)

    # indicators 변환
    if 'indicators' in migrated:
        migrated['indicators'] = [
            migrate_indicator_config(ind) for ind in migrated['indicators']
        ]

    # buyConditions 변환
    if 'buyConditions' in migrated:
        migrated['buyConditions'] = [
            migrate_condition(cond) for cond in migrated['buyConditions']
        ]

    # sellConditions 변환
    if 'sellConditions' in migrated:
        migrated['sellConditions'] = [
            migrate_condition(cond) for cond in migrated['sellConditions']
        ]

    # targetProfit 변환
    if 'targetProfit' in migrated:
        migrated['targetProfit'] = migrate_target_profit(migrated['targetProfit'])

    return migrated

def create_migration_report(original: Dict[str, Any], migrated: Dict[str, Any]) -> Dict[str, Any]:
    """
    마이그레이션 보고서 생성
    """
    changes = []

    # 매수 조건 변경사항
    if 'buyConditions' in original:
        for i, (orig, mig) in enumerate(zip(original.get('buyConditions', []),
                                            migrated.get('buyConditions', []))):
            if orig != mig:
                changes.append({
                    'type': 'buyCondition',
                    'index': i,
                    'original': orig,
                    'migrated': mig
                })

    # 매도 조건 변경사항
    if 'sellConditions' in original:
        for i, (orig, mig) in enumerate(zip(original.get('sellConditions', []),
                                            migrated.get('sellConditions', []))):
            if orig != mig:
                changes.append({
                    'type': 'sellCondition',
                    'index': i,
                    'original': orig,
                    'migrated': mig
                })

    return {
        'total_changes': len(changes),
        'changes': changes,
        'mapping_used': COLUMN_MAPPING
    }

def migrate_file(input_path: str, output_path: str = None, create_report: bool = True):
    """
    JSON 파일 마이그레이션

    Args:
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로 (None이면 _migrated 접미사 추가)
        create_report: 보고서 생성 여부
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        original = json.load(f)

    migrated = migrate_strategy_template(original)

    if output_path is None:
        output_path = input_path.replace('.json', '_migrated.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(migrated, f, indent=2, ensure_ascii=False)

    print(f"마이그레이션 완료: {input_path} -> {output_path}")

    if create_report:
        report = create_migration_report(original, migrated)
        report_path = output_path.replace('.json', '_report.json')

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"보고서 생성: {report_path}")
        print(f"총 {report['total_changes']}개 항목 변경됨")

    return migrated

def migrate_templates_bulk(templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    여러 템플릿 일괄 변환

    Args:
        templates: 템플릿 리스트

    Returns:
        변환된 템플릿 리스트
    """
    return [migrate_strategy_template(template) for template in templates]

if __name__ == "__main__":
    # 테스트 예제
    test_template = {
        "name": "RSI & MACD Strategy",
        "indicators": [
            {"type": "RSI", "params": {"period": 14}},
            {"type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
            {"type": "BB", "params": {"period": 20, "std": 2}}
        ],
        "buyConditions": [
            {"indicator": "RSI_14", "operator": ">", "value": 30},
            {"indicator": "MACD", "operator": "CROSS_ABOVE", "value": "MACD_SIGNAL", "combineWith": "AND"}
        ],
        "sellConditions": [
            {"indicator": "RSI_14", "operator": ">", "value": 70},
            {"indicator": "PRICE", "operator": ">", "value": "BB_UPPER", "combineWith": "OR"}
        ],
        "targetProfit": {
            "enabled": True,
            "value": 5.0,
            "combineWith": "OR"
        }
    }

    print("원본 템플릿:")
    print(json.dumps(test_template, indent=2, ensure_ascii=False))

    migrated = migrate_strategy_template(test_template)

    print("\n변환된 템플릿:")
    print(json.dumps(migrated, indent=2, ensure_ascii=False))

    print("\n주요 변환 매핑:")
    for old, new in COLUMN_MAPPING.items():
        if old in ['RSI_14', 'MACD', 'MACD_SIGNAL', 'BB_UPPER', 'PRICE']:
            print(f"  {old} -> {new}")