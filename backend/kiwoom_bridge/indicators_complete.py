"""
완전한 기술적 지표 계산 모듈
전략빌더의 모든 지표 구현
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class CompleteIndicators:
    """전략빌더의 모든 기술적 지표 계산"""

    @staticmethod
    def calculate_all(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """모든 지표 계산"""
        # 데이터 검증
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"필수 컬럼 누락: {col}")

        # 지표 설정
        indicators = config.get('indicators', [])

        for indicator in indicators:
            ind_type = indicator.get('type').lower()
            params = indicator.get('params', {})

            # 1. 이동평균선 계열
            if ind_type in ['sma', 'ma']:
                period = params.get('period', 20)
                df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()

            elif ind_type == 'ema':
                period = params.get('period', 20)
                df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

            elif ind_type == 'wma':
                period = params.get('period', 20)
                weights = np.arange(1, period + 1)
                df[f'WMA_{period}'] = df['close'].rolling(window=period).apply(
                    lambda x: np.dot(x, weights) / weights.sum(), raw=True
                )

            # 2. 모멘텀 지표
            elif ind_type == 'rsi':
                period = params.get('period', 14)
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss.replace(0, 1e-10)
                df[f'RSI_{period}'] = 100 - (100 / (1 + rs))

            elif ind_type == 'macd':
                fast = params.get('fast', 12)
                slow = params.get('slow', 26)
                signal = params.get('signal', 9)

                exp1 = df['close'].ewm(span=fast, adjust=False).mean()
                exp2 = df['close'].ewm(span=slow, adjust=False).mean()
                df['MACD'] = exp1 - exp2
                df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
                df['MACD_hist'] = df['MACD'] - df['MACD_signal']

            elif ind_type == 'stochastic':
                k_period = params.get('k', 14)
                d_period = params.get('d', 3)

                low_min = df['low'].rolling(window=k_period).min()
                high_max = df['high'].rolling(window=k_period).max()
                df['Stoch_K'] = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
                df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()

            elif ind_type == 'cci':
                period = params.get('period', 20)
                tp = (df['high'] + df['low'] + df['close']) / 3
                ma = tp.rolling(window=period).mean()
                mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
                df[f'CCI_{period}'] = (tp - ma) / (0.015 * mad + 1e-10)

            elif ind_type == 'williams':
                period = params.get('period', 14)
                high_max = df['high'].rolling(window=period).max()
                low_min = df['low'].rolling(window=period).min()
                df[f'WILLR_{period}'] = -100 * (high_max - df['close']) / (high_max - low_min + 1e-10)

            elif ind_type == 'roc':
                period = params.get('period', 12)
                df[f'ROC_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100

            elif ind_type == 'momentum':
                period = params.get('period', 10)
                df[f'MOM_{period}'] = df['close'] - df['close'].shift(period)

            # 3. 변동성 지표
            elif ind_type == 'bb':
                period = params.get('period', 20)
                std = params.get('stdDev', 2)
                ma = df['close'].rolling(window=period).mean()
                std_dev = df['close'].rolling(window=period).std()
                df['BB_upper'] = ma + (std_dev * std)
                df['BB_lower'] = ma - (std_dev * std)
                df['BB_middle'] = ma
                df['BB_width'] = df['BB_upper'] - df['BB_lower']
                df['BB_percent'] = (df['close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'] + 1e-10)

            elif ind_type == 'atr':
                period = params.get('period', 14)
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = ranges.max(axis=1)
                df[f'ATR_{period}'] = true_range.rolling(window=period).mean()

            elif ind_type == 'keltner':
                period = params.get('period', 20)
                mult = params.get('mult', 2)
                ma = df['close'].ewm(span=period, adjust=False).mean()
                atr = CompleteIndicators._calculate_atr(df, period)
                df['KC_upper'] = ma + (mult * atr)
                df['KC_lower'] = ma - (mult * atr)
                df['KC_middle'] = ma

            # 4. 거래량 지표
            elif ind_type == 'volume':
                period = params.get('period', 20)
                df[f'Volume_MA_{period}'] = df['volume'].rolling(window=period).mean()
                df['Volume_ratio'] = df['volume'] / df[f'Volume_MA_{period}']

            elif ind_type == 'obv':
                df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

            elif ind_type == 'vwap':
                # VWAP은 일중 데이터용이므로 일별 데이터에서는 근사값 사용
                tp = (df['high'] + df['low'] + df['close']) / 3
                df['VWAP'] = (tp * df['volume']).cumsum() / df['volume'].cumsum()
                # 일별 리셋이 필요한 경우 날짜별로 그룹화
                if 'date' in df.columns:
                    df['VWAP'] = df.groupby(pd.Grouper(key='date', freq='D')).apply(
                        lambda x: (x['close'] * x['volume']).cumsum() / x['volume'].cumsum()
                    ).reset_index(0, drop=True)

            elif ind_type == 'mfi':
                period = params.get('period', 14)
                tp = (df['high'] + df['low'] + df['close']) / 3
                mf = tp * df['volume']

                pos_mf = pd.Series(np.where(tp > tp.shift(), mf, 0), index=df.index)
                neg_mf = pd.Series(np.where(tp < tp.shift(), mf, 0), index=df.index)

                pos_mf_sum = pos_mf.rolling(window=period).sum()
                neg_mf_sum = neg_mf.rolling(window=period).sum()

                df[f'MFI_{period}'] = 100 - (100 / (1 + pos_mf_sum / (neg_mf_sum + 1e-10)))

            elif ind_type == 'cmf':
                period = params.get('period', 20)
                mf_mult = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
                mf_vol = mf_mult * df['volume']
                df[f'CMF_{period}'] = mf_vol.rolling(window=period).sum() / df['volume'].rolling(window=period).sum()

            elif ind_type == 'ad':
                # Accumulation/Distribution Line
                mf_mult = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
                df['AD'] = (mf_mult * df['volume']).cumsum()

            # 5. 추세 지표
            elif ind_type == 'adx':
                period = params.get('period', 14)
                plus_dm = df['high'].diff()
                minus_dm = -df['low'].diff()
                plus_dm[plus_dm < 0] = 0
                minus_dm[minus_dm < 0] = 0

                tr = pd.concat([
                    df['high'] - df['low'],
                    np.abs(df['high'] - df['close'].shift()),
                    np.abs(df['low'] - df['close'].shift())
                ], axis=1).max(axis=1)

                atr = tr.rolling(window=period).mean()
                plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
                minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
                dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
                df[f'ADX_{period}'] = dx.rolling(window=period).mean()
                df[f'PDI_{period}'] = plus_di
                df[f'MDI_{period}'] = minus_di

            elif ind_type == 'dmi':
                period = params.get('period', 14)
                # DMI는 ADX와 함께 +DI, -DI를 포함
                plus_dm = df['high'].diff()
                minus_dm = -df['low'].diff()

                plus_dm[plus_dm < 0] = 0
                minus_dm[minus_dm < 0] = 0

                # 조건부 처리
                mask = (plus_dm > minus_dm)
                plus_dm[~mask] = 0
                minus_dm[mask] = 0

                tr = pd.concat([
                    df['high'] - df['low'],
                    np.abs(df['high'] - df['close'].shift()),
                    np.abs(df['low'] - df['close'].shift())
                ], axis=1).max(axis=1)

                atr = tr.ewm(span=period, adjust=False).mean()
                plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
                minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)

                df[f'DMI_plus_{period}'] = plus_di
                df[f'DMI_minus_{period}'] = minus_di
                df[f'DMI_diff_{period}'] = plus_di - minus_di

            elif ind_type == 'parabolic':
                acc = params.get('acc', 0.02)
                max_acc = params.get('max', 0.2)

                # Parabolic SAR 계산
                df['PSAR'] = CompleteIndicators._calculate_psar(df, acc, max_acc)

            elif ind_type == 'supertrend':
                period = params.get('period', 10)
                mult = params.get('mult', 3)

                hl_avg = (df['high'] + df['low']) / 2
                atr = CompleteIndicators._calculate_atr(df, period)

                upper = hl_avg + (mult * atr)
                lower = hl_avg - (mult * atr)

                df['ST_upper'] = upper
                df['ST_lower'] = lower

                # Supertrend 방향 결정
                supertrend = pd.Series(index=df.index, dtype=float)
                direction = pd.Series(index=df.index, dtype=int)

                for i in range(len(df)):
                    if i == 0:
                        supertrend.iloc[i] = upper.iloc[i]
                        direction.iloc[i] = -1
                    else:
                        if df['close'].iloc[i] > upper.iloc[i-1]:
                            direction.iloc[i] = 1
                        elif df['close'].iloc[i] < lower.iloc[i-1]:
                            direction.iloc[i] = -1
                        else:
                            direction.iloc[i] = direction.iloc[i-1]

                        if direction.iloc[i] == 1:
                            supertrend.iloc[i] = lower.iloc[i]
                        else:
                            supertrend.iloc[i] = upper.iloc[i]

                df['SuperTrend'] = supertrend
                df['ST_direction'] = direction

            # 6. 일목균형표 (Ichimoku Cloud)
            elif ind_type == 'ichimoku':
                tenkan_period = params.get('tenkan', 9)
                kijun_period = params.get('kijun', 26)
                senkou_period = params.get('senkou', 52)
                chikou_period = params.get('chikou', 26)

                # 전환선 (Tenkan-sen)
                high_9 = df['high'].rolling(window=tenkan_period).max()
                low_9 = df['low'].rolling(window=tenkan_period).min()
                df['Ichimoku_tenkan'] = (high_9 + low_9) / 2

                # 기준선 (Kijun-sen)
                high_26 = df['high'].rolling(window=kijun_period).max()
                low_26 = df['low'].rolling(window=kijun_period).min()
                df['Ichimoku_kijun'] = (high_26 + low_26) / 2

                # 선행스팬 A (Senkou Span A)
                df['Ichimoku_senkou_a'] = ((df['Ichimoku_tenkan'] + df['Ichimoku_kijun']) / 2).shift(kijun_period)

                # 선행스팬 B (Senkou Span B)
                high_52 = df['high'].rolling(window=senkou_period).max()
                low_52 = df['low'].rolling(window=senkou_period).min()
                df['Ichimoku_senkou_b'] = ((high_52 + low_52) / 2).shift(kijun_period)

                # 후행스팬 (Chikou Span)
                df['Ichimoku_chikou'] = df['close'].shift(-chikou_period)

                # 구름대 (Cloud)
                df['Ichimoku_cloud_top'] = df[['Ichimoku_senkou_a', 'Ichimoku_senkou_b']].max(axis=1)
                df['Ichimoku_cloud_bottom'] = df[['Ichimoku_senkou_a', 'Ichimoku_senkou_b']].min(axis=1)
                df['Ichimoku_cloud_thickness'] = df['Ichimoku_cloud_top'] - df['Ichimoku_cloud_bottom']

                # 추가 신호
                df['Ichimoku_above_cloud'] = df['close'] > df['Ichimoku_cloud_top']
                df['Ichimoku_below_cloud'] = df['close'] < df['Ichimoku_cloud_bottom']
                df['Ichimoku_in_cloud'] = (df['close'] <= df['Ichimoku_cloud_top']) & (df['close'] >= df['Ichimoku_cloud_bottom'])

            # 7. 피봇 포인트
            elif ind_type == 'pivot':
                # 전일 데이터 기준 피봇 계산
                df['Pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
                df['Pivot_R1'] = 2 * df['Pivot'] - df['low'].shift(1)
                df['Pivot_S1'] = 2 * df['Pivot'] - df['high'].shift(1)
                df['Pivot_R2'] = df['Pivot'] + (df['high'].shift(1) - df['low'].shift(1))
                df['Pivot_S2'] = df['Pivot'] - (df['high'].shift(1) - df['low'].shift(1))
                df['Pivot_R3'] = df['high'].shift(1) + 2 * (df['Pivot'] - df['low'].shift(1))
                df['Pivot_S3'] = df['low'].shift(1) - 2 * (df['high'].shift(1) - df['Pivot'])

            # 8. 기타 지표
            elif ind_type == 'trix':
                period = params.get('period', 14)
                ema1 = df['close'].ewm(span=period, adjust=False).mean()
                ema2 = ema1.ewm(span=period, adjust=False).mean()
                ema3 = ema2.ewm(span=period, adjust=False).mean()
                df[f'TRIX_{period}'] = (ema3.pct_change() * 10000)

            elif ind_type == 'vortex':
                period = params.get('period', 14)
                vm_plus = np.abs(df['high'] - df['low'].shift(1))
                vm_minus = np.abs(df['low'] - df['high'].shift(1))

                tr = pd.concat([
                    df['high'] - df['low'],
                    np.abs(df['high'] - df['close'].shift()),
                    np.abs(df['low'] - df['close'].shift())
                ], axis=1).max(axis=1)

                vi_plus = vm_plus.rolling(window=period).sum() / tr.rolling(window=period).sum()
                vi_minus = vm_minus.rolling(window=period).sum() / tr.rolling(window=period).sum()

                df[f'VI_plus_{period}'] = vi_plus
                df[f'VI_minus_{period}'] = vi_minus

            elif ind_type == 'aroon':
                period = params.get('period', 25)

                aroon_up = df['high'].rolling(window=period + 1).apply(
                    lambda x: (period - x.argmax()) / period * 100
                )
                aroon_down = df['low'].rolling(window=period + 1).apply(
                    lambda x: (period - x.argmin()) / period * 100
                )

                df[f'Aroon_up_{period}'] = aroon_up
                df[f'Aroon_down_{period}'] = aroon_down
                df[f'Aroon_osc_{period}'] = aroon_up - aroon_down

        return df

    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
        """ATR 계산 헬퍼 함수"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()

    @staticmethod
    def _calculate_psar(df: pd.DataFrame, initial_acc: float, max_acc: float) -> pd.Series:
        """Parabolic SAR 계산"""
        psar = pd.Series(index=df.index, dtype=float)
        bull = True
        acc = initial_acc
        extreme = df['high'].iloc[0]
        psar.iloc[0] = df['low'].iloc[0]

        for i in range(1, len(df)):
            if bull:
                psar.iloc[i] = psar.iloc[i-1] + acc * (extreme - psar.iloc[i-1])

                if df['low'].iloc[i] < psar.iloc[i]:
                    bull = False
                    psar.iloc[i] = extreme
                    extreme = df['low'].iloc[i]
                    acc = initial_acc
                else:
                    if df['high'].iloc[i] > extreme:
                        extreme = df['high'].iloc[i]
                        acc = min(acc + initial_acc, max_acc)

                    # SAR이 당일/전일 저가보다 높으면 조정
                    if psar.iloc[i] > df['low'].iloc[i]:
                        psar.iloc[i] = df['low'].iloc[i]
                    if psar.iloc[i] > df['low'].iloc[i-1]:
                        psar.iloc[i] = df['low'].iloc[i-1]
            else:
                psar.iloc[i] = psar.iloc[i-1] - acc * (psar.iloc[i-1] - extreme)

                if df['high'].iloc[i] > psar.iloc[i]:
                    bull = True
                    psar.iloc[i] = extreme
                    extreme = df['high'].iloc[i]
                    acc = initial_acc
                else:
                    if df['low'].iloc[i] < extreme:
                        extreme = df['low'].iloc[i]
                        acc = min(acc + initial_acc, max_acc)

                    # SAR이 당일/전일 고가보다 낮으면 조정
                    if psar.iloc[i] < df['high'].iloc[i]:
                        psar.iloc[i] = df['high'].iloc[i]
                    if psar.iloc[i] < df['high'].iloc[i-1]:
                        psar.iloc[i] = df['high'].iloc[i-1]

        return psar