"""
전략 적용 분석 도구
전략이 제대로 적용되는지 상세하게 분석
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys

# 백테스트 엔진 import
from backtest_engine_advanced import AdvancedBacktestEngine, SignalGenerator
from indicators_complete import CompleteIndicators

class StrategyAnalyzer:
    """전략 분석 클래스"""

    def __init__(self):
        self.analysis_results = {}
        self.debug_log = []

    def analyze_strategy(self,
                         data: pd.DataFrame,
                         strategy_config: Dict,
                         save_to_file: bool = True) -> Dict[str, Any]:
        """전략 상세 분석"""

        print("\n" + "="*80)
        print("전략 분석 시작")
        print("="*80)

        # 1. 전략 설정 분석
        print("\n[1] 전략 설정 분석")
        print("-"*40)
        strategy_summary = self._analyze_strategy_config(strategy_config)

        # 2. 지표 계산 및 검증
        print("\n[2] 지표 계산 검증")
        print("-"*40)
        data_with_indicators = CompleteIndicators.calculate_all(data.copy(), strategy_config)
        indicator_analysis = self._analyze_indicators(data_with_indicators, strategy_config)

        # 3. 신호 생성 분석
        print("\n[3] 매매 신호 생성 분석")
        print("-"*40)
        signal_analysis = self._analyze_signals(data_with_indicators, strategy_config)

        # 4. 백테스트 실행 및 분석
        print("\n[4] 백테스트 실행")
        print("-"*40)
        backtest_analysis = self._run_backtest(data_with_indicators, strategy_config)

        # 5. 조건 충족 상세 분석
        print("\n[5] 조건 충족 상세 분석")
        print("-"*40)
        condition_analysis = self._analyze_condition_details(data_with_indicators, strategy_config)

        # 종합 결과 (numpy 타입을 Python 기본 타입으로 변환)
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'strategy_summary': self._convert_numpy_types(strategy_summary),
            'indicator_analysis': self._convert_numpy_types(indicator_analysis),
            'signal_analysis': self._convert_numpy_types(signal_analysis),
            'backtest_analysis': self._convert_numpy_types(backtest_analysis),
            'condition_analysis': self._convert_numpy_types(condition_analysis),
            'debug_log': self.debug_log
        }

        # 파일로 저장
        if save_to_file:
            filename = f"strategy_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n[SAVED] 분석 결과 저장: {filename}")

        # CSV로도 저장 (신호 데이터)
        if save_to_file and 'signals' in signal_analysis:
            csv_filename = f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            signal_df = pd.DataFrame(signal_analysis['signals'])
            signal_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"[SAVED] 신호 데이터 CSV: {csv_filename}")

        return analysis_results

    def _analyze_strategy_config(self, config: Dict) -> Dict:
        """전략 설정 분석"""

        indicators = config.get('indicators', [])
        buy_conditions = config.get('buyConditions', [])
        sell_conditions = config.get('sellConditions', [])

        summary = {
            'indicators_count': len(indicators),
            'indicators': [
                {
                    'type': ind.get('type'),
                    'params': ind.get('params', {})
                } for ind in indicators
            ],
            'buy_conditions_count': len(buy_conditions),
            'buy_conditions': buy_conditions,
            'sell_conditions_count': len(sell_conditions),
            'sell_conditions': sell_conditions,
            'position_sizing': config.get('positionSizing', {}),
            'split_buy': config.get('splitBuy', {'enabled': False}),
            'split_sell': config.get('splitSell', {'enabled': False})
        }

        print(f"  지표: {summary['indicators_count']}개")
        for ind in summary['indicators']:
            print(f"    - {ind['type']}: {ind['params']}")

        print(f"  매수 조건: {summary['buy_conditions_count']}개")
        for i, cond in enumerate(buy_conditions, 1):
            print(f"    {i}. {cond.get('indicator')} {cond.get('operator')} {cond.get('value')}")

        print(f"  매도 조건: {summary['sell_conditions_count']}개")
        for i, cond in enumerate(sell_conditions, 1):
            print(f"    {i}. {cond.get('indicator')} {cond.get('operator')} {cond.get('value')}")

        return summary

    def _analyze_indicators(self, data: pd.DataFrame, config: Dict) -> Dict:
        """지표 계산 결과 분석"""

        indicators = config.get('indicators', [])
        analysis = {
            'calculated_columns': [],
            'statistics': {},
            'nulls': {}
        }

        # 계산된 지표 컬럼 찾기
        original_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        indicator_cols = [col for col in data.columns if col not in original_cols]

        print(f"  계산된 지표 컬럼: {len(indicator_cols)}개")

        for col in indicator_cols:
            non_null = data[col].notna().sum()
            null_count = data[col].isna().sum()

            if non_null > 0:
                stats = {
                    'mean': float(data[col].mean()) if pd.api.types.is_numeric_dtype(data[col]) else None,
                    'std': float(data[col].std()) if pd.api.types.is_numeric_dtype(data[col]) else None,
                    'min': float(data[col].min()) if pd.api.types.is_numeric_dtype(data[col]) else None,
                    'max': float(data[col].max()) if pd.api.types.is_numeric_dtype(data[col]) else None,
                    'non_null_count': int(non_null),
                    'null_count': int(null_count)
                }

                analysis['calculated_columns'].append(col)
                analysis['statistics'][col] = stats

                if null_count > 0:
                    analysis['nulls'][col] = null_count

                mean_str = f"{stats['mean']:.2f}" if stats['mean'] is not None else "N/A"
                print(f"    - {col}: {non_null}/{len(data)} 값, 평균={mean_str}")

        return analysis

    def _analyze_signals(self, data: pd.DataFrame, config: Dict) -> Dict:
        """신호 생성 분석"""

        # 신호 생성
        buy_conditions = config.get('buyConditions', [])
        sell_conditions = config.get('sellConditions', [])

        data['buy_signal'] = SignalGenerator.evaluate_conditions(data, buy_conditions, 'buy')
        data['sell_signal'] = SignalGenerator.evaluate_conditions(data, sell_conditions, 'sell')

        # 신호 통계
        buy_signals = data[data['buy_signal'] == 1]
        sell_signals = data[data['sell_signal'] == -1]

        analysis = {
            'buy_signal_count': len(buy_signals),
            'sell_signal_count': len(sell_signals),
            'buy_signal_dates': buy_signals['date'].tolist() if 'date' in buy_signals.columns else [],
            'sell_signal_dates': sell_signals['date'].tolist() if 'date' in sell_signals.columns else [],
            'signals': []
        }

        print(f"  매수 신호: {analysis['buy_signal_count']}개")
        print(f"  매도 신호: {analysis['sell_signal_count']}개")

        # 신호 발생 시점의 상세 정보
        for idx, row in buy_signals.iterrows():
            signal_info = {
                'date': str(row['date']),
                'type': 'BUY',
                'price': float(row['close']),
                'conditions_met': self._check_conditions_at_point(row, buy_conditions)
            }
            analysis['signals'].append(signal_info)

        for idx, row in sell_signals.iterrows():
            signal_info = {
                'date': str(row['date']),
                'type': 'SELL',
                'price': float(row['close']),
                'conditions_met': self._check_conditions_at_point(row, sell_conditions)
            }
            analysis['signals'].append(signal_info)

        # 신호 간격 분석
        if len(analysis['buy_signal_dates']) > 1:
            buy_dates = pd.to_datetime(analysis['buy_signal_dates'])
            intervals = []
            for i in range(1, len(buy_dates)):
                interval = (buy_dates[i] - buy_dates[i-1]).days
                intervals.append(interval)
            if intervals:
                analysis['buy_signal_interval_avg'] = float(np.mean(intervals))
                print(f"  매수 신호 평균 간격: {analysis['buy_signal_interval_avg']:.1f}일")

        return analysis

    def _check_conditions_at_point(self, row: pd.Series, conditions: List[Dict]) -> List[Dict]:
        """특정 시점에서 조건 충족 여부 확인"""

        results = []
        for cond in conditions:
            indicator = cond.get('indicator', '')
            operator = cond.get('operator', '')
            value = cond.get('value', 0)

            # 지표값 가져오기
            if indicator in row.index:
                ind_value = row[indicator]
            else:
                ind_value = None

            # 비교값 가져오기
            if isinstance(value, str) and value in row.index:
                compare_value = row[value]
            else:
                compare_value = value

            # 조건 평가
            met = False
            if ind_value is not None and not pd.isna(ind_value):
                if operator == '>':
                    met = ind_value > compare_value
                elif operator == '<':
                    met = ind_value < compare_value
                elif operator == '>=':
                    met = ind_value >= compare_value
                elif operator == '<=':
                    met = ind_value <= compare_value
                elif operator == '==':
                    met = ind_value == compare_value

            results.append({
                'indicator': indicator,
                'operator': operator,
                'value': str(value),
                'indicator_value': float(ind_value) if ind_value is not None and not pd.isna(ind_value) else None,
                'compare_value': float(compare_value) if isinstance(compare_value, (int, float)) else str(compare_value),
                'met': met
            })

        return results

    def _run_backtest(self, data: pd.DataFrame, config: Dict) -> Dict:
        """백테스트 실행 및 분석"""

        engine = AdvancedBacktestEngine(
            initial_capital=10000000,
            commission=0.00015,
            slippage=0.001
        )

        results = engine.run(data, config)

        print(f"  총 수익률: {results['total_return']:.2f}%")
        print(f"  승률: {results['win_rate']:.2f}%")
        print(f"  최대 낙폭: {results['max_drawdown']:.2f}%")
        print(f"  총 거래: {results['total_trades']}회")

        return results

    def _analyze_condition_details(self, data: pd.DataFrame, config: Dict) -> Dict:
        """조건 충족 상세 분석"""

        buy_conditions = config.get('buyConditions', [])
        sell_conditions = config.get('sellConditions', [])

        analysis = {
            'buy_conditions_detail': [],
            'sell_conditions_detail': []
        }

        print("\n  [매수 조건 상세]")
        for i, cond in enumerate(buy_conditions, 1):
            detail = self._analyze_single_condition(data, cond)
            analysis['buy_conditions_detail'].append(detail)
            print(f"    조건 {i}: {cond.get('indicator')} {cond.get('operator')} {cond.get('value')}")
            print(f"      - 충족 횟수: {detail['met_count']}회 ({detail['met_percentage']:.1f}%)")

        print("\n  [매도 조건 상세]")
        for i, cond in enumerate(sell_conditions, 1):
            detail = self._analyze_single_condition(data, cond)
            analysis['sell_conditions_detail'].append(detail)
            print(f"    조건 {i}: {cond.get('indicator')} {cond.get('operator')} {cond.get('value')}")
            print(f"      - 충족 횟수: {detail['met_count']}회 ({detail['met_percentage']:.1f}%)")

        return analysis

    def _analyze_single_condition(self, data: pd.DataFrame, condition: Dict) -> Dict:
        """단일 조건 분석"""

        indicator = condition.get('indicator', '')
        operator = condition.get('operator', '')
        value = condition.get('value', 0)

        if indicator not in data.columns:
            return {
                'condition': condition,
                'met_count': 0,
                'met_percentage': 0.0,
                'error': f"Indicator {indicator} not found"
            }

        # 값 가져오기
        ind_values = data[indicator]

        # 비교값
        if isinstance(value, str) and value in data.columns:
            compare_values = data[value]
        else:
            compare_values = value

        # 조건 평가
        if operator == '>':
            met = ind_values > compare_values
        elif operator == '<':
            met = ind_values < compare_values
        elif operator == '>=':
            met = ind_values >= compare_values
        elif operator == '<=':
            met = ind_values <= compare_values
        elif operator == '==':
            met = ind_values == compare_values
        elif operator == 'cross_above':
            if isinstance(compare_values, pd.Series):
                met = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values.shift(1))
            else:
                met = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values)
        elif operator == 'cross_below':
            if isinstance(compare_values, pd.Series):
                met = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values.shift(1))
            else:
                met = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values)
        else:
            met = pd.Series([False] * len(data))

        met_count = met.sum()
        met_percentage = (met_count / len(data)) * 100

        return {
            'condition': condition,
            'met_count': int(met_count),
            'met_percentage': float(met_percentage),
            'first_met': str(data[met]['date'].iloc[0]) if met.any() and 'date' in data.columns else None,
            'last_met': str(data[met]['date'].iloc[-1]) if met.any() and 'date' in data.columns else None
        }

    def _convert_numpy_types(self, obj):
        """NumPy 타입을 Python 기본 타입으로 변환"""
        import numpy as np

        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif hasattr(obj, 'isoformat'):  # datetime 객체
            return obj.isoformat()
        else:
            return obj


def create_sample_strategy():
    """샘플 전략 생성"""
    return {
        'name': 'RSI + MACD + 볼린저밴드 복합 전략',
        'indicators': [
            {'type': 'RSI', 'params': {'period': 14}},
            {'type': 'MACD', 'params': {'fast': 12, 'slow': 26, 'signal': 9}},
            {'type': 'BB', 'params': {'period': 20, 'stdDev': 2}},
            {'type': 'SMA', 'params': {'period': 50}},
            {'type': 'Volume', 'params': {'period': 20}}
        ],
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 30, 'combineWith': None},
            {'indicator': 'close', 'operator': '<', 'value': 'BB_lower', 'combineWith': 'OR'},
            {'indicator': 'MACD', 'operator': 'cross_above', 'value': 'MACD_signal', 'combineWith': 'OR'}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 70, 'combineWith': None},
            {'indicator': 'close', 'operator': '>', 'value': 'BB_upper', 'combineWith': 'OR'},
            {'indicator': 'MACD', 'operator': 'cross_below', 'value': 'MACD_signal', 'combineWith': 'OR'}
        ]
    }


def main():
    """메인 실행 함수"""

    print("\n" + "="*80)
    print("전략 적용 분석 시스템")
    print("="*80)

    # 테스트 데이터 생성
    dates = pd.date_range(start='2024-01-01', end='2024-06-01', freq='D')
    n = len(dates)

    # 실제와 유사한 주가 패턴 생성
    base_price = 50000
    trend = np.sin(np.linspace(0, 4*np.pi, n)) * 5000  # 사인파 패턴
    noise = np.random.randn(n) * 1000
    prices = base_price + trend + noise

    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': prices * (1 + np.random.uniform(0, 0.02, n)),
        'low': prices * (1 - np.random.uniform(0, 0.02, n)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n)
    })

    # 샘플 전략
    strategy = create_sample_strategy()

    # 분석 실행
    analyzer = StrategyAnalyzer()
    results = analyzer.analyze_strategy(data, strategy, save_to_file=True)

    print("\n" + "="*80)
    print("분석 완료")
    print("="*80)

    # 주요 결과 요약
    print("\n[요약]")
    print(f"  - 매수 신호: {results['signal_analysis']['buy_signal_count']}회")
    print(f"  - 매도 신호: {results['signal_analysis']['sell_signal_count']}회")
    print(f"  - 백테스트 수익률: {results['backtest_analysis']['total_return']:.2f}%")
    print(f"  - 승률: {results['backtest_analysis']['win_rate']:.2f}%")

    return results


if __name__ == "__main__":
    results = main()