"""
백테스트 API에 상세 디버깅 로그 추가
"""

import os

# backtest_api.py에 추가할 로그
debug_code = '''
            # === 디버깅 로그 추가 ===
            print(f"[DEBUG API] strategy_config indicators: {strategy_config.get('indicators', [])[:2]}...")
            print(f"[DEBUG API] strategy_config templateId: {strategy_config.get('templateId')}")
            print(f"[DEBUG API] buyConditions: {strategy_config.get('buyConditions', [])}")
            print(f"[DEBUG API] sellConditions: {strategy_config.get('sellConditions', [])}")
'''

# backtest_engine_advanced.py의 run 메서드에 추가할 로그
engine_debug = '''
        # === 디버깅 로그 추가 ===
        print(f"[DEBUG ENGINE] 백테스트 시작: {stock_code}")
        print(f"[DEBUG ENGINE] 데이터 shape: {data.shape}")
        print(f"[DEBUG ENGINE] 데이터 날짜 범위: {data['date'].min()} ~ {data['date'].max()}")
        print(f"[DEBUG ENGINE] 전략 templateId: {strategy_config.get('templateId')}")
'''

print("="*60)
print("디버깅 로그 추가 위치")
print("="*60)

print("\n1. backtest_api.py의 execute_strategy 메서드:")
print("   - strategy_config 내용 출력")
print("   - indicators 배열 확인")
print("   - 조건 확인")

print("\n2. backtest_engine_advanced.py의 run 메서드:")
print("   - 데이터 정보 출력")
print("   - 전략 정보 출력")

print("\n3. core/signals.py의 evaluate_conditions:")
print("   - 조건 평가 과정 출력")
print("   - 교차 감지 출력")

print("\n" + "="*60)
print("수동으로 다음 위치에 로그 추가:")
print("="*60)

print("\nbacktest_api.py - execute_strategy 메서드 시작 부분:")
print(debug_code)

print("\nbacktest_engine_advanced.py - run 메서드 시작 부분:")
print(engine_debug)

print("\ncore/signals.py - evaluate_conditions 함수:")
print('''
    # cross_above/cross_below 처리 부분에 추가
    if operator == 'cross_above':
        print(f"[DEBUG SIGNAL] cross_above 평가: {indicator} > {value}")
        print(f"[DEBUG SIGNAL] 현재 {indicator} > {value}: {(ind_series > val_series).sum()}개")
        print(f"[DEBUG SIGNAL] 교차: {result.sum()}개")
''')

print("\n이 로그들을 추가한 후 Docker에 복사하고 백테스트를 실행하면")
print("정확한 문제점을 찾을 수 있습니다.")