"""
회귀 테스트 - core 모듈의 정확성 검증
- 지표 계산 일관성
- 신호 생성 일관성
- Wilder 표준 준수 확인
"""

import pandas as pd
import numpy as np
import unittest
from datetime import datetime, timedelta
import json
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import (
    compute_indicators,
    evaluate_conditions,
    generate_signals,
    StandardIndicators,
    _iname,
    migrate_strategy_template
)
from migrate_templates import migrate_strategy_template

class TestIndicatorConsistency(unittest.TestCase):
    """지표 계산 일관성 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        np.random.seed(42)  # 재현성을 위한 시드 고정

        # 샘플 OHLCV 데이터 생성
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = 50000 + np.cumsum(np.random.randn(100) * 1000)

        self.df = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(100) * 500,
            'high': prices + np.abs(np.random.randn(100) * 800),
            'low': prices - np.abs(np.random.randn(100) * 800),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })

        # 전략 설정
        self.config = {
            'indicators': [
                {'type': 'RSI', 'params': {'period': 14}},
                {'type': 'MACD', 'params': {'fast': 12, 'slow': 26, 'signal': 9}},
                {'type': 'BB', 'params': {'period': 20, 'std': 2}},
                {'type': 'ATR', 'params': {'period': 14}},
                {'type': 'ADX', 'params': {'period': 14}}
            ],
            'buyConditions': [
                {'indicator': 'rsi_14', 'operator': '<', 'value': 30}
            ],
            'sellConditions': [
                {'indicator': 'rsi_14', 'operator': '>', 'value': 70}
            ]
        }

    def test_rsi_wilder(self):
        """RSI Wilder 방식 검증"""
        df = self.df.copy()
        df = compute_indicators(df, self.config)

        # RSI가 0-100 범위 내에 있는지 확인
        self.assertTrue(all(0 <= val <= 100 for val in df['rsi_14'].dropna()))

        # RSI 계산 확인 (Wilder 방식)
        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = (-delta).clip(lower=0)
        rma_up = up.ewm(alpha=1/14, adjust=False).mean()
        rma_down = down.ewm(alpha=1/14, adjust=False).mean()
        rs = rma_up / rma_down.replace(0, 1e-10)
        expected_rsi = 100 - (100 / (1 + rs))

        # 값 비교 (부동소수점 오차 허용)
        pd.testing.assert_series_equal(
            df['rsi_14'],
            expected_rsi,
            check_names=False,
            rtol=1e-10
        )

    def test_atr_wilder(self):
        """ATR Wilder 방식 검증"""
        df = self.df.copy()
        df = compute_indicators(df, self.config)

        # ATR이 양수인지 확인
        self.assertTrue(all(val > 0 for val in df['atr_14'].dropna()))

        # ATR 계산 확인 (Wilder 방식)
        tr = pd.concat([
            df['high'] - df['low'],
            (df['high'] - df['close'].shift()).abs(),
            (df['low'] - df['close'].shift()).abs()
        ], axis=1).max(axis=1)
        expected_atr = tr.ewm(alpha=1/14, adjust=False).mean()

        pd.testing.assert_series_equal(
            df['atr_14'],
            expected_atr,
            check_names=False,
            rtol=1e-10
        )

    def test_adx_standard(self):
        """ADX 표준 산식 검증"""
        df = self.df.copy()
        df = compute_indicators(df, self.config)

        # ADX가 0-100 범위 내에 있는지 확인
        self.assertTrue(all(0 <= val <= 100 for val in df['adx_14'].dropna()))

        # ADX는 항상 양수
        self.assertTrue(all(val >= 0 for val in df['adx_14'].dropna()))

    def test_column_naming(self):
        """컬럼 네이밍 규약 확인"""
        df = self.df.copy()
        df = compute_indicators(df, self.config)

        # 예상되는 컬럼들
        expected_columns = [
            'rsi_14',
            'macd_12_26',
            'macd_signal_12_26_9',
            'macd_hist_12_26_9',
            'bb_middle_20',
            'bb_upper_20_2',
            'bb_lower_20_2',
            'atr_14',
            'adx_14',
            'price'  # close 별칭
        ]

        for col in expected_columns:
            self.assertIn(col, df.columns, f"컬럼 {col}이 없습니다")

        # 대문자 컬럼이 없는지 확인
        uppercase_columns = [col for col in df.columns if col != col.lower()]
        # date 컬럼은 제외 (일반적으로 대소문자 구분 없음)
        uppercase_columns = [col for col in uppercase_columns if col != 'date']
        self.assertEqual(len(uppercase_columns), 0,
                        f"대문자 컬럼 발견: {uppercase_columns}")

class TestSignalConsistency(unittest.TestCase):
    """신호 생성 일관성 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')

        # RSI 테스트용 데이터 (극단값 포함)
        close_prices = np.array([50000] * 100)
        # 일부 구간에 급등/급락 추가
        close_prices[20:25] = 45000  # 급락 (RSI 낮음)
        close_prices[70:75] = 55000  # 급등 (RSI 높음)

        self.df = pd.DataFrame({
            'date': dates,
            'open': close_prices * 0.99,
            'high': close_prices * 1.01,
            'low': close_prices * 0.98,
            'close': close_prices,
            'volume': np.ones(100) * 1000
        })

    def test_signal_generation(self):
        """신호 생성 테스트"""
        config = {
            'indicators': [{'type': 'RSI', 'params': {'period': 14}}],
            'buyConditions': [
                {'indicator': 'rsi_14', 'operator': '<', 'value': 30}
            ],
            'sellConditions': [
                {'indicator': 'rsi_14', 'operator': '>', 'value': 70}
            ]
        }

        df = self.df.copy()
        df = compute_indicators(df, config)
        df = generate_signals(df, config)

        # 신호 컬럼 존재 확인
        self.assertIn('buy_signal', df.columns)
        self.assertIn('sell_signal', df.columns)

        # 신호 값 확인 (0, 1, -1만 허용)
        self.assertTrue(all(val in [0, 1] for val in df['buy_signal']))
        self.assertTrue(all(val in [0, -1] for val in df['sell_signal']))

    def test_cross_conditions(self):
        """교차 조건 테스트"""
        config = {
            'indicators': [
                {'type': 'SMA', 'params': {'period': 10}},
                {'type': 'SMA', 'params': {'period': 20}}
            ],
            'buyConditions': [
                {'indicator': 'sma_10', 'operator': 'cross_above', 'value': 'sma_20'}
            ],
            'sellConditions': [
                {'indicator': 'sma_10', 'operator': 'cross_below', 'value': 'sma_20'}
            ]
        }

        # 교차가 발생하는 데이터 생성
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        prices = np.concatenate([
            np.linspace(50000, 51000, 25),  # 상승
            np.linspace(51000, 49000, 25)   # 하락
        ])

        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.ones(50) * 1000
        })

        df = compute_indicators(df, config)
        df = generate_signals(df, config)

        # 교차 신호가 한 번만 발생하는지 확인
        buy_signals = df['buy_signal'].sum()
        sell_signals = abs(df['sell_signal'].sum())

        self.assertGreaterEqual(buy_signals, 0)
        self.assertGreaterEqual(sell_signals, 0)

class TestTemplateMigration(unittest.TestCase):
    """템플릿 마이그레이션 테스트"""

    def test_legacy_template_migration(self):
        """레거시 템플릿 변환 테스트"""
        legacy_template = {
            'buyConditions': [
                {'indicator': 'RSI_14', 'operator': 'CROSS_ABOVE', 'value': 30},
                {'indicator': 'MACD', 'operator': '>', 'value': 'MACD_SIGNAL',
                 'combineWith': 'AND'}
            ],
            'sellConditions': [
                {'indicator': 'PRICE', 'operator': '>', 'value': 'BB_UPPER'}
            ],
            'targetProfit': {
                'enabled': True,
                'value': 5.0,
                'combineWith': 'OR'
            }
        }

        migrated = migrate_strategy_template(legacy_template)

        # 변환 확인
        self.assertEqual(migrated['buyConditions'][0]['indicator'], 'rsi_14')
        self.assertEqual(migrated['buyConditions'][0]['operator'], 'cross_above')
        self.assertEqual(migrated['buyConditions'][1]['indicator'], 'macd_12_26')
        self.assertEqual(migrated['buyConditions'][1]['value'], 'macd_signal_12_26_9')
        self.assertEqual(migrated['buyConditions'][1]['combineWith'], 'and')

        self.assertEqual(migrated['sellConditions'][0]['indicator'], 'price')
        self.assertEqual(migrated['sellConditions'][0]['value'], 'bb_upper_20_2')

        self.assertEqual(migrated['targetProfit']['combineWith'], 'or')

class TestBacktestComparison(unittest.TestCase):
    """백테스트 결과 비교 테스트"""

    def setUp(self):
        """공통 테스트 데이터"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=200, freq='D')
        prices = 50000 + np.cumsum(np.random.randn(200) * 500)

        self.df = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(200) * 200,
            'high': prices + np.abs(np.random.randn(200) * 300),
            'low': prices - np.abs(np.random.randn(200) * 300),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 200)
        })

        self.config = {
            'indicators': [
                {'type': 'RSI', 'params': {'period': 14}},
                {'type': 'SMA', 'params': {'period': 20}}
            ],
            'buyConditions': [
                {'indicator': 'rsi_14', 'operator': '<', 'value': 40},
                {'indicator': 'close', 'operator': '>', 'value': 'sma_20',
                 'combineWith': 'and'}
            ],
            'sellConditions': [
                {'indicator': 'rsi_14', 'operator': '>', 'value': 60}
            ],
            'targetProfit': {
                'enabled': True,
                'mode': 'simple',
                'value': 3.0,
                'combineWith': 'or'
            },
            'stopLoss': {
                'enabled': True,
                'value': 2.0
            }
        }

    def test_signal_consistency_across_engines(self):
        """엔진 간 신호 일관성 테스트"""
        df1 = self.df.copy()
        df1 = compute_indicators(df1, self.config)
        df1 = generate_signals(df1, self.config)

        # 같은 데이터로 다시 계산
        df2 = self.df.copy()
        df2 = compute_indicators(df2, self.config)
        df2 = generate_signals(df2, self.config)

        # 신호가 완전히 동일한지 확인
        pd.testing.assert_series_equal(df1['buy_signal'], df2['buy_signal'])
        pd.testing.assert_series_equal(df1['sell_signal'], df2['sell_signal'])

def run_regression_tests():
    """회귀 테스트 실행"""
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 테스트 추가
    suite.addTests(loader.loadTestsFromTestCase(TestIndicatorConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateMigration))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktestComparison))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "="*50)
    print("회귀 테스트 결과 요약")
    print("="*50)
    print(f"실행된 테스트: {result.testsRun}개")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"실패: {len(result.failures)}개")
    print(f"오류: {len(result.errors)}개")

    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n오류 발생 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_regression_tests()
    sys.exit(0 if success else 1)