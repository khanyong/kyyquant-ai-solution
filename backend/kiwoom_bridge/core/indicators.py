"""
표준 기술적 지표 계산 모듈
- 모든 지표는 소문자 + 파라미터 포함 컬럼명 사용
- Wilder 표준 산식 적용 (RSI, ATR, ADX)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from .naming import _iname, DEFAULT_PARAMS, extract_indicator_params

class StandardIndicators:
    """표준 기술적 지표 계산 클래스"""

    @staticmethod
    def sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """단순 이동평균"""
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """지수 이동평균"""
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSI - Wilder 방식"""
        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = (-delta).clip(lower=0)
        rma_up = up.ewm(alpha=1/period, adjust=False).mean()
        rma_down = down.ewm(alpha=1/period, adjust=False).mean()
        rs = rma_up / rma_down.replace(0, 1e-10)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD"""
        macd_line = df['close'].ewm(span=fast, adjust=False).mean() - df['close'].ewm(span=slow, adjust=False).mean()
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        hist = macd_line - signal_line
        return {
            'macd': macd_line,
            'signal': signal_line,
            'hist': hist
        }

    @staticmethod
    def bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2) -> Dict[str, pd.Series]:
        """볼린저 밴드"""
        ma = df['close'].rolling(window=period).mean()
        sd = df['close'].rolling(window=period).std()
        return {
            'middle': ma,
            'upper': ma + std * sd,
            'lower': ma - std * sd
        }

    @staticmethod
    def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """스토캐스틱 (Fast)"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        k_fast = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
        d_fast = k_fast.rolling(window=d_period).mean()
        return {
            'k': k_fast,
            'd': d_fast
        }

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR - Wilder 방식"""
        tr = pd.concat([
            df['high'] - df['low'],
            (df['high'] - df['close'].shift()).abs(),
            (df['low'] - df['close'].shift()).abs()
        ], axis=1).max(axis=1)
        return tr.ewm(alpha=1/period, adjust=False).mean()

    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """ADX - 표준 산식 (Wilder)"""
        upMove = df['high'].diff()
        downMove = df['low'].shift(1) - df['low']
        plus_dm = np.where((upMove > downMove) & (upMove > 0), upMove, 0.0)
        minus_dm = np.where((downMove > upMove) & (downMove > 0), downMove, 0.0)

        tr = pd.concat([
            df['high'] - df['low'],
            (df['high'] - df['close'].shift()).abs(),
            (df['low'] - df['close'].shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean() / atr.replace(0, 1e-10))
        minus_di = 100 * (pd.Series(minus_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean() / atr.replace(0, 1e-10))
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-10)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()

        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        }

    @staticmethod
    def cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """CCI"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        return (tp - sma_tp) / (0.015 * mad + 1e-10)

    @staticmethod
    def mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """MFI"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        mf = tp * df['volume']
        pos_mf = pd.Series(np.where(tp > tp.shift(), mf, 0), index=df.index)
        neg_mf = pd.Series(np.where(tp < tp.shift(), mf, 0), index=df.index)
        mfr = pos_mf.rolling(window=period).sum() / (neg_mf.rolling(window=period).sum() + 1e-10)
        return 100 - (100 / (1 + mfr))

    @staticmethod
    def williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Williams %R"""
        hh = df['high'].rolling(window=period).max()
        ll = df['low'].rolling(window=period).min()
        return -100 * (hh - df['close']) / (hh - ll + 1e-10)

    @staticmethod
    def obv(df: pd.DataFrame) -> pd.Series:
        """OBV"""
        return (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

    @staticmethod
    def volume_ratio(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """거래량 비율"""
        avg_volume = df['volume'].rolling(window=period).mean()
        return df['volume'] / avg_volume.replace(0, 1e-10)


def compute_indicators(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    설정에 따라 필요한 지표 계산

    Args:
        df: OHLCV 데이터프레임
        config: 전략 설정 (indicators, buyConditions, sellConditions 포함)

    Returns:
        지표가 추가된 데이터프레임
    """
    # 필수 컬럼 검증
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 누락: {col}")

    # price 별칭 추가
    df['price'] = df['close']

    # 1. indicators 설정에서 지표 추출
    # config가 리스트인 경우 직접 사용, 딕셔너리인 경우 indicators 추출
    if isinstance(config, list):
        indicators = config
    else:
        indicators = config.get('indicators', [])
    for indicator in indicators:
        ind_type = indicator.get('type', '').upper()
        params = indicator.get('params', {})

        if ind_type in ['SMA', 'MA']:
            # params가 있으면 params에서, 없으면 indicator에서 직접 period 가져오기
            period = params.get('period') or indicator.get('period') or DEFAULT_PARAMS['sma']['period']
            # MA로 통일 (sma도 ma로 저장)
            df[_iname('ma', period)] = StandardIndicators.sma(df, period)

        elif ind_type == 'EMA':
            period = params.get('period') or indicator.get('period') or DEFAULT_PARAMS['ema']['period']
            df[_iname('ema', period)] = StandardIndicators.ema(df, period)

        elif ind_type == 'RSI':
            period = params.get('period') or indicator.get('period') or DEFAULT_PARAMS['rsi']['period']
            df[_iname('rsi', period)] = StandardIndicators.rsi(df, period)

        elif ind_type == 'MACD':
            fast = params.get('fast') or indicator.get('fast') or DEFAULT_PARAMS['macd']['fast']
            slow = params.get('slow') or indicator.get('slow') or DEFAULT_PARAMS['macd']['slow']
            signal = params.get('signal') or indicator.get('signal') or DEFAULT_PARAMS['macd']['signal']
            macd_result = StandardIndicators.macd(df, fast, slow, signal)
            df[_iname('macd', fast, slow)] = macd_result['macd']
            df[_iname('macd_signal', fast, slow, signal)] = macd_result['signal']
            df[_iname('macd_hist', fast, slow, signal)] = macd_result['hist']

        elif ind_type == 'BB':
            period = params.get('period', DEFAULT_PARAMS['bb']['period'])
            std = params.get('std', DEFAULT_PARAMS['bb']['std'])
            bb_result = StandardIndicators.bollinger_bands(df, period, std)
            df[_iname('bb_middle', period)] = bb_result['middle']
            df[_iname('bb_upper', period, std)] = bb_result['upper']
            df[_iname('bb_lower', period, std)] = bb_result['lower']

        elif ind_type in ['STOCHASTIC', 'STOCH']:
            k_period = params.get('k_period', DEFAULT_PARAMS['stoch']['k_period'])
            d_period = params.get('d_period', DEFAULT_PARAMS['stoch']['d_period'])
            stoch_result = StandardIndicators.stochastic(df, k_period, d_period)
            df[_iname('stoch_k', k_period, d_period)] = stoch_result['k']
            df[_iname('stoch_d', k_period, d_period)] = stoch_result['d']

        elif ind_type == 'ATR':
            period = params.get('period', DEFAULT_PARAMS['atr']['period'])
            df[_iname('atr', period)] = StandardIndicators.atr(df, period)

        elif ind_type == 'ADX':
            period = params.get('period', DEFAULT_PARAMS['adx']['period'])
            adx_result = StandardIndicators.adx(df, period)
            df[_iname('adx', period)] = adx_result['adx']
            # 필요시 DI 지표도 추가
            # df[_iname('plus_di', period)] = adx_result['plus_di']
            # df[_iname('minus_di', period)] = adx_result['minus_di']

        elif ind_type == 'CCI':
            period = params.get('period', DEFAULT_PARAMS['cci']['period'])
            df[_iname('cci', period)] = StandardIndicators.cci(df, period)

        elif ind_type == 'MFI':
            period = params.get('period', DEFAULT_PARAMS['mfi']['period'])
            df[_iname('mfi', period)] = StandardIndicators.mfi(df, period)

        elif ind_type in ['WILLIAMS_R', 'WILLR']:
            period = params.get('period', DEFAULT_PARAMS['willr']['period'])
            df[_iname('willr', period)] = StandardIndicators.williams_r(df, period)

        elif ind_type == 'OBV':
            df[_iname('obv')] = StandardIndicators.obv(df)

        elif ind_type in ['VR', 'VOLUME_RATIO']:
            period = params.get('period', DEFAULT_PARAMS['vr']['period'])
            df[_iname('vr', period)] = StandardIndicators.volume_ratio(df, period)

    # 2. 조건에서 사용되는 지표 자동 감지 및 계산
    # config가 리스트인 경우 조건 처리 스킵
    if isinstance(config, list):
        all_conditions = []
    else:
        all_conditions = config.get('buyConditions', []) + config.get('sellConditions', [])
    for condition in all_conditions:
        indicator_name = condition.get('indicator', '').lower()
        if indicator_name and indicator_name not in df.columns:
            # 컬럼이 없으면 파라미터 추출하여 계산
            indicator_info = extract_indicator_params(indicator_name)
            ind_type = indicator_info.get('type', '')

            if ind_type == 'rsi' and _iname('rsi', indicator_info.get('period', 14)) not in df.columns:
                period = indicator_info.get('period', 14)
                df[_iname('rsi', period)] = StandardIndicators.rsi(df, period)

            elif ind_type in ['sma', 'ma'] and indicator_name not in df.columns:
                period = indicator_info.get('period', 20)
                # MA로 통일
                df[_iname('ma', period)] = StandardIndicators.sma(df, period)

            elif ind_type == 'ema' and indicator_name not in df.columns:
                period = indicator_info.get('period', 20)
                df[_iname('ema', period)] = StandardIndicators.ema(df, period)

            # 필요한 다른 지표들도 동일하게 처리...

        # 비교 값이 지표인 경우도 체크
        value = condition.get('value', '')
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower and value_lower not in df.columns:
                value_info = extract_indicator_params(value_lower)
                value_type = value_info.get('type', '')

                if value_type in ['sma', 'ma'] and value_lower not in df.columns:
                    period = value_info.get('period', 20)
                    # MA로 통일
                    df[_iname('ma', period)] = StandardIndicators.sma(df, period)

                elif value_type == 'ema' and value_lower not in df.columns:
                    period = value_info.get('period', 20)
                    df[_iname('ema', period)] = StandardIndicators.ema(df, period)

    return df