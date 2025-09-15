"""
백테스트 전략 수정 및 테스트
"""

import json
import os

def fix_strategy_format():
    """전략 형식 수정"""

    # 잘못된 형식의 전략 (현재 DB에 저장된 형태)
    wrong_format = {
        "indicators": [
            {"type": "ma", "period": 20},  # ❌ params 없음, 소문자
            {"type": "ma", "period": 60}
        ],
        "buyConditions": [
            {
                "indicator": "MA_20",  # ❌ 대문자
                "operator": "CROSS_ABOVE",  # ❌ 대문자
                "value": "MA_60"
            }
        ]
    }

    # 올바른 형식의 전략
    correct_format = {
        "templateId": "golden-cross",
        "indicators": [
            {"type": "MA", "params": {"period": 20}},  # ✅ params 있음, 대문자
            {"type": "MA", "params": {"period": 60}}
        ],
        "buyConditions": [
            {
                "indicator": "ma_20",  # ✅ 소문자
                "operator": ">",  # ✅ 단순 비교 연산자
                "value": "ma_60",
                "combineWith": "AND"
            }
        ],
        "sellConditions": [
            {
                "indicator": "ma_20",
                "operator": "<",
                "value": "ma_60",
                "combineWith": "AND"
            }
        ],
        "position_size": 100,
        "stop_loss": 5,
        "take_profit": 10,
        "initial_capital": 10000000
    }

    print("="*60)
    print("전략 형식 수정")
    print("="*60)

    print("\n[WRONG FORMAT]:")
    print(json.dumps(wrong_format, indent=2, ensure_ascii=False))

    print("\n[CORRECT FORMAT]:")
    print(json.dumps(correct_format, indent=2, ensure_ascii=False))

    # JSON 파일로 저장
    with open('fixed_golden_cross_strategy.json', 'w', encoding='utf-8') as f:
        json.dump(correct_format, f, indent=2, ensure_ascii=False)

    print("\n[SUCCESS] fixed_golden_cross_strategy.json file created")

    return correct_format

def create_simple_strategies():
    """간단한 테스트용 전략들 생성"""

    strategies = {
        "simple_ma_cross": {
            "name": "간단한 이동평균 교차",
            "templateId": "simple-ma-cross",
            "indicators": [
                {"type": "MA", "params": {"period": 5}},
                {"type": "MA", "params": {"period": 20}}
            ],
            "buyConditions": [
                {
                    "indicator": "ma_5",
                    "operator": ">",
                    "value": "ma_20"
                }
            ],
            "sellConditions": [
                {
                    "indicator": "ma_5",
                    "operator": "<",
                    "value": "ma_20"
                }
            ],
            "position_size": 100,
            "initial_capital": 10000000
        },

        "price_threshold": {
            "name": "가격 임계값",
            "templateId": "price-threshold",
            "indicators": [
                {"type": "MA", "params": {"period": 20}}
            ],
            "buyConditions": [
                {
                    "indicator": "close",
                    "operator": ">",
                    "value": "ma_20",
                    "multiplier": 1.02  # MA20 * 1.02 이상일 때
                }
            ],
            "sellConditions": [
                {
                    "indicator": "close",
                    "operator": "<",
                    "value": "ma_20",
                    "multiplier": 0.98  # MA20 * 0.98 이하일 때
                }
            ],
            "position_size": 100,
            "initial_capital": 10000000
        },

        "rsi_oversold": {
            "name": "RSI 과매도",
            "templateId": "rsi-oversold",
            "indicators": [
                {"type": "RSI", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "indicator": "rsi_14",
                    "operator": "<",
                    "value": 30  # RSI < 30 (과매도)
                }
            ],
            "sellConditions": [
                {
                    "indicator": "rsi_14",
                    "operator": ">",
                    "value": 70  # RSI > 70 (과매수)
                }
            ],
            "position_size": 100,
            "initial_capital": 10000000
        }
    }

    print("\n="*60)
    print("테스트용 전략 생성")
    print("="*60)

    for key, strategy in strategies.items():
        filename = f"test_strategy_{key}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCCESS] {filename} created")
        print(f"   Strategy name: {strategy['name']}")

    # 모든 전략을 하나의 파일로도 저장
    with open('all_test_strategies.json', 'w', encoding='utf-8') as f:
        json.dump(strategies, f, indent=2, ensure_ascii=False)

    print("\n[SUCCESS] all_test_strategies.json file created")

    return strategies

def main():
    """메인 실행"""

    # 1. 전략 형식 수정
    fixed_strategy = fix_strategy_format()

    # 2. 테스트용 전략들 생성
    test_strategies = create_simple_strategies()

    print("\n="*60)
    print("전략 수정 완료")
    print("="*60)
    print("\n다음 단계:")
    print("1. fixed_golden_cross_strategy.json을 백테스트에 사용")
    print("2. test_strategy_*.json 파일들로 다양한 전략 테스트")
    print("3. DB의 전략 데이터를 올바른 형식으로 업데이트")

if __name__ == "__main__":
    main()