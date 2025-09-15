"""
템플릿 전략 자동 수정
indicators가 비어있지만 templateId가 있는 경우 자동으로 채움
"""

def fix_template_strategy(strategy_config):
    """템플릿 전략의 누락된 indicators를 자동으로 채움"""

    # indicators가 비어있고 templateId가 있는 경우
    if (not strategy_config.get('indicators') or len(strategy_config.get('indicators', [])) == 0) \
       and strategy_config.get('templateId'):

        template_id = strategy_config['templateId']
        print(f"[FIX] 템플릿 {template_id}의 indicators 자동 추가")

        # 템플릿별 기본 지표 설정
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
            strategy_config['indicators'] = template_indicators[template_id]
            print(f"[FIX] {len(strategy_config['indicators'])}개 지표 추가됨")

        # operator 수정 (> → cross_above)
        buy_conditions = strategy_config.get('buyConditions', [])
        for cond in buy_conditions:
            if cond.get('operator') == '>' and 'ma' in cond.get('indicator', '').lower():
                cond['operator'] = 'cross_above'
                print(f"[FIX] 매수 조건 operator 수정: > → cross_above")

        sell_conditions = strategy_config.get('sellConditions', [])
        for cond in sell_conditions:
            if cond.get('operator') == '<' and 'ma' in cond.get('indicator', '').lower():
                cond['operator'] = 'cross_below'
                print(f"[FIX] 매도 조건 operator 수정: < → cross_below")

    return strategy_config


# backtest_api.py의 Strategy 클래스에 추가할 코드:
"""
# execute_strategy 메서드 시작 부분에 추가
if USE_CORE:
    # 템플릿 전략 자동 수정
    if not strategy_config.get('indicators') and strategy_config.get('templateId'):
        from fix_template_strategy import fix_template_strategy
        strategy_config = fix_template_strategy(strategy_config)
"""