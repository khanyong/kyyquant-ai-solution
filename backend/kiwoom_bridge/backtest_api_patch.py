"""
backtest_api.py 패치 - core 모듈 사용으로 통일
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

# Core 모듈 임포트 (표준화된 단일 소스)
from core import (
    compute_indicators,
    evaluate_conditions,
    evaluate_with_position_management,
    _normalize_conditions,
    convert_legacy_column,
    _iname
)

class Strategy:
    """전략 실행 클래스 - 얇은 오케스트레이터로 축소"""

    @staticmethod
    async def execute_strategy(data: pd.DataFrame, strategy_config: Dict[str, Any]) -> pd.DataFrame:
        """
        전략 실행 - 모든 지표/신호 처리를 core 모듈에 위임
        """
        # 0) 데이터 복사 및 별칭 추가
        data = data.copy()
        data['price'] = data['close']  # 가격 별칭 항상 추가

        # 1) 조건 정규화 (레거시 → 표준)
        print("[DEBUG] 조건 정규화 시작")

        # 원본 조건 백업 (디버깅용)
        original_buy = strategy_config.get('buyConditions', [])
        original_sell = strategy_config.get('sellConditions', [])

        # 정규화 실행
        buy_conditions = _normalize_conditions(original_buy)
        sell_conditions = _normalize_conditions(original_sell)

        # 정규화 결과 출력
        if original_buy != buy_conditions:
            print(f"[INFO] 매수 조건 정규화: {original_buy} → {buy_conditions}")
        if original_sell != sell_conditions:
            print(f"[INFO] 매도 조건 정규화: {original_sell} → {sell_conditions}")

        # 2) indicators 구조 수정 (params 누락 문제 해결)
        indicators = strategy_config.get('indicators', [])
        fixed_indicators = []

        for ind in indicators:
            if 'params' not in ind and 'period' in ind:
                # params 구조 수정
                fixed_ind = {
                    'type': ind.get('type', 'MA').upper(),
                    'params': {'period': ind.get('period', 20)}
                }
                print(f"[FIX] 지표 구조 수정: {ind} → {fixed_ind}")
                fixed_indicators.append(fixed_ind)
            else:
                fixed_indicators.append(ind)

        # 3) 수정된 설정으로 지표 계산
        config = {
            **strategy_config,
            'indicators': fixed_indicators,
            'buyConditions': buy_conditions,
            'sellConditions': sell_conditions
        }

        print(f"[DEBUG] 지표 계산 시작. 컬럼 수: {len(data.columns)}")
        data = compute_indicators(data, config)
        print(f"[DEBUG] 지표 계산 완료. 컬럼 수: {len(data.columns)}")

        # 계산된 지표 컬럼 확인
        indicator_cols = [col for col in data.columns if any(
            x in col for x in ['ma_', 'sma_', 'ema_', 'rsi_', 'macd', 'bb_', 'stoch_', 'atr_', 'adx_']
        )]
        if indicator_cols:
            print(f"[INFO] 계산된 지표: {indicator_cols}")

        # 4) 신호 생성 (core 모듈 사용)
        print("[DEBUG] 신호 생성 시작")

        # 기본 신호 생성
        data['buy_signal'] = evaluate_conditions(data, buy_conditions, 'buy')
        data['sell_signal'] = evaluate_conditions(data, sell_conditions, 'sell')

        # 신호 통계
        buy_count = (data['buy_signal'] == 1).sum()
        sell_count = (data['sell_signal'] == -1).sum()

        print(f"[INFO] 신호 생성 완료: 매수 {buy_count}개, 매도 {sell_count}개")

        # 5) 통합 신호 컬럼 생성
        data['signal'] = 0
        data.loc[data['buy_signal'] == 1, 'signal'] = 1
        data.loc[data['sell_signal'] == -1, 'signal'] = -1

        # 6) 디버깅: 신호가 없는 경우 원인 분석
        if buy_count == 0 and sell_count == 0:
            print("[WARNING] 신호가 전혀 생성되지 않음!")

            # 조건에서 요구하는 컬럼 확인
            required_cols = set()
            for cond in buy_conditions + sell_conditions:
                required_cols.add(cond.get('indicator', ''))
                val = cond.get('value', '')
                if isinstance(val, str) and not val.replace('.', '').replace('-', '').isdigit():
                    required_cols.add(val)

            # 누락된 컬럼 확인
            missing_cols = required_cols - set(data.columns)
            if missing_cols:
                print(f"[ERROR] 누락된 컬럼: {missing_cols}")
                print(f"[HINT] 사용 가능한 컬럼: {indicator_cols}")

            # 조건 만족 여부 확인
            for cond in buy_conditions[:1]:  # 첫 번째 조건만 확인
                ind = cond.get('indicator', '')
                op = cond.get('operator', '')
                val = cond.get('value', '')

                if ind in data.columns:
                    if op in ['>', '<', '>=', '<=']:
                        if isinstance(val, str) and val in data.columns:
                            satisfied = eval(f"(data['{ind}'] {op} data['{val}'])")
                        else:
                            satisfied = eval(f"(data['{ind}'] {op} {float(val)})")

                        count = satisfied.sum()
                        print(f"[DEBUG] 조건 '{ind} {op} {val}' 만족: {count}개 행")

        return data


class BacktestEngine:
    """백테스트 엔진 - core 모듈 활용"""

    def __init__(self, initial_capital: float = 10000000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []

    async def run(self, data: pd.DataFrame, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """백테스트 실행"""

        # 전략 실행
        data = await Strategy.execute_strategy(data, strategy_config)

        # 거래 시뮬레이션
        position = None
        for i in range(len(data)):
            row = data.iloc[i]

            if row['signal'] == 1 and position is None:
                # 매수
                position = {
                    'entry_price': row['close'],
                    'entry_date': row['date'],
                    'quantity': int(self.capital * 0.1 / row['close'])
                }
                self.trades.append({
                    'date': row['date'],
                    'action': 'buy',
                    'price': row['close'],
                    'quantity': position['quantity']
                })

            elif row['signal'] == -1 and position is not None:
                # 매도
                profit = (row['close'] - position['entry_price']) * position['quantity']
                profit_pct = ((row['close'] - position['entry_price']) / position['entry_price']) * 100

                self.trades.append({
                    'date': row['date'],
                    'action': 'sell',
                    'price': row['close'],
                    'quantity': position['quantity'],
                    'profit': profit,
                    'profit_pct': profit_pct
                })

                self.capital += profit
                position = None

        # 결과 반환
        return {
            'total_trades': len(self.trades),
            'buy_count': len([t for t in self.trades if t['action'] == 'buy']),
            'sell_count': len([t for t in self.trades if t['action'] == 'sell']),
            'final_capital': self.capital,
            'total_return': ((self.capital - self.initial_capital) / self.initial_capital) * 100,
            'trades': self.trades
        }


# 헬스체크 메트릭 수집
class HealthMetrics:
    """운영 헬스체크 메트릭"""

    def __init__(self):
        self.metrics = {
            'missing_indicators': [],
            'parse_failures': [],
            'operator_errors': [],
            'zero_signals': [],
            'timestamp': []
        }

    def log_missing_indicator(self, indicator: str, strategy_id: str):
        """누락된 지표 기록"""
        self.metrics['missing_indicators'].append({
            'indicator': indicator,
            'strategy_id': strategy_id,
            'timestamp': datetime.now()
        })

    def log_parse_failure(self, value: str, strategy_id: str):
        """파싱 실패 기록"""
        self.metrics['parse_failures'].append({
            'value': value,
            'strategy_id': strategy_id,
            'timestamp': datetime.now()
        })

    def log_zero_signals(self, strategy_id: str, data_length: int):
        """신호 없음 기록"""
        self.metrics['zero_signals'].append({
            'strategy_id': strategy_id,
            'data_length': data_length,
            'timestamp': datetime.now()
        })

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """대시보드용 통계"""
        now = datetime.now()
        last_hour = [x for x in self.metrics['missing_indicators']
                    if (now - x['timestamp']).seconds < 3600]

        return {
            'last_hour': {
                'missing_indicators': len(last_hour),
                'parse_failures': len([x for x in self.metrics['parse_failures']
                                     if (now - x['timestamp']).seconds < 3600]),
                'zero_signals': len([x for x in self.metrics['zero_signals']
                                   if (now - x['timestamp']).seconds < 3600])
            },
            'top_missing_indicators': self._get_top_issues('missing_indicators'),
            'top_parse_failures': self._get_top_issues('parse_failures'),
            'alert_level': self._calculate_alert_level()
        }

    def _get_top_issues(self, metric_type: str, limit: int = 5):
        """가장 빈번한 문제 추출"""
        from collections import Counter

        if metric_type == 'missing_indicators':
            items = [x['indicator'] for x in self.metrics[metric_type]]
        elif metric_type == 'parse_failures':
            items = [x['value'] for x in self.metrics[metric_type]]
        else:
            return []

        return Counter(items).most_common(limit)

    def _calculate_alert_level(self) -> str:
        """경고 수준 계산"""
        recent_errors = sum([
            len([x for x in self.metrics['missing_indicators']
                if (datetime.now() - x['timestamp']).seconds < 300]),
            len([x for x in self.metrics['parse_failures']
                if (datetime.now() - x['timestamp']).seconds < 300]),
            len([x for x in self.metrics['zero_signals']
                if (datetime.now() - x['timestamp']).seconds < 300])
        ])

        if recent_errors > 10:
            return "CRITICAL"
        elif recent_errors > 5:
            return "WARNING"
        else:
            return "OK"


# 전역 메트릭 인스턴스
health_metrics = HealthMetrics()


if __name__ == "__main__":
    # 테스트
    import asyncio

    async def test():
        # 테스트 데이터
        dates = pd.date_range('2024-01-01', periods=100)
        prices = 50000 + np.cumsum(np.random.randn(100) * 500)

        data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': [1000000] * 100
        })

        # 테스트 전략
        strategy = {
            'indicators': [
                {'type': 'ma', 'period': 20},  # params 누락 (자동 수정됨)
                {'type': 'MA', 'params': {'period': 60}}
            ],
            'buyConditions': [
                {'indicator': 'MA_20', 'operator': 'CROSS_ABOVE', 'value': 'MA_60'}  # 대문자 (자동 정규화)
            ],
            'sellConditions': [
                {'indicator': 'ma_20', 'operator': 'cross_below', 'value': 'ma_60'}
            ]
        }

        # 실행
        result = await Strategy.execute_strategy(data, strategy)
        print(f"\n최종 결과: 매수 {(result['buy_signal'] == 1).sum()}개, 매도 {(result['sell_signal'] == -1).sum()}개")

        # 헬스체크
        stats = health_metrics.get_dashboard_stats()
        print(f"\n헬스체크: {stats}")

    asyncio.run(test())