"""
일봉 데이터로 모든 기술적 지표 계산
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """일봉 데이터로 모든 기술적 지표 계산"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        모든 지표 한번에 계산
        
        Args:
            df: OHLCV 데이터 (columns: open, high, low, close, volume)
        
        Returns:
            지표가 추가된 DataFrame
        """
        df = df.copy()
        
        # 1. 이동평균선
        df['SMA_5'] = df['close'].rolling(window=5).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_60'] = df['close'].rolling(window=60).mean()
        df['SMA_120'] = df['close'].rolling(window=120).mean()
        
        # EMA (지수이동평균)
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # 2. 볼린저밴드
        bb_period = 20
        bb_std = 2
        df['BB_middle'] = df['close'].rolling(window=bb_period).mean()
        bb_std_val = df['close'].rolling(window=bb_period).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * bb_std_val)
        df['BB_lower'] = df['BB_middle'] - (bb_std * bb_std_val)
        df['BB_width'] = df['BB_upper'] - df['BB_lower']
        df['BB_position'] = (df['close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # 3. RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['close'], 14)
        
        # 4. MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # 5. 스토캐스틱
        k_period = 14
        d_period = 3
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        df['Stochastic_K'] = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        df['Stochastic_D'] = df['Stochastic_K'].rolling(window=d_period).mean()
        
        # 6. ATR (Average True Range)
        df['ATR'] = TechnicalIndicators.calculate_atr(df, 14)
        
        # 7. OBV (On Balance Volume)
        df['OBV'] = TechnicalIndicators.calculate_obv(df)
        
        # 8. VWAP (Volume Weighted Average Price)
        df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        
        # 9. CCI (Commodity Channel Index)
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(window=20).mean()
        md = (tp - ma).abs().rolling(window=20).mean()
        df['CCI'] = (tp - ma) / (0.015 * md)
        
        # 10. Williams %R
        period = 14
        highest = df['high'].rolling(window=period).max()
        lowest = df['low'].rolling(window=period).min()
        df['Williams_R'] = -100 * ((highest - df['close']) / (highest - lowest))
        
        # 11. ADX (Average Directional Index)
        df['ADX'], df['DI_plus'], df['DI_minus'] = TechnicalIndicators.calculate_adx(df, 14)
        
        # 12. 일목균형표
        # 전환선 (9일)
        period_9_high = df['high'].rolling(window=9).max()
        period_9_low = df['low'].rolling(window=9).min()
        df['Ichimoku_tenkan'] = (period_9_high + period_9_low) / 2
        
        # 기준선 (26일)
        period_26_high = df['high'].rolling(window=26).max()
        period_26_low = df['low'].rolling(window=26).min()
        df['Ichimoku_kijun'] = (period_26_high + period_26_low) / 2
        
        # 선행스팬A
        df['Ichimoku_senkou_a'] = ((df['Ichimoku_tenkan'] + df['Ichimoku_kijun']) / 2).shift(26)
        
        # 선행스팬B  
        period_52_high = df['high'].rolling(window=52).max()
        period_52_low = df['low'].rolling(window=52).min()
        df['Ichimoku_senkou_b'] = ((period_52_high + period_52_low) / 2).shift(26)
        
        # 후행스팬
        df['Ichimoku_chikou'] = df['close'].shift(-26)
        
        # 13. Parabolic SAR
        df['PSAR'] = TechnicalIndicators.calculate_psar(df)
        
        # 14. 추가 지표들
        # MFI (Money Flow Index)
        df['MFI'] = TechnicalIndicators.calculate_mfi(df, 14)
        
        # ROC (Rate of Change)
        df['ROC'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100
        
        # 켈트너 채널
        kc_ema = df['close'].ewm(span=20, adjust=False).mean()
        kc_atr = df['ATR']
        df['KC_upper'] = kc_ema + (2 * kc_atr)
        df['KC_lower'] = kc_ema - (2 * kc_atr)
        
        return df
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR 계산"""
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """OBV 계산"""
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> tuple:
        """ADX와 DI 계산"""
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = TechnicalIndicators.calculate_atr(df, 1)
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        
        dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def calculate_psar(df: pd.DataFrame, acc: float = 0.02, max_acc: float = 0.2) -> pd.Series:
        """Parabolic SAR 계산"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        psar = close[0:1].copy()
        bull = True
        af = acc
        ep = high[0] if bull else low[0]
        
        for i in range(1, len(df)):
            if bull:
                psar.loc[i] = psar.iloc[i-1] + af * (ep - psar.iloc[i-1])
            else:
                psar.loc[i] = psar.iloc[i-1] - af * (psar.iloc[i-1] - ep)
            
            # 추세 전환 체크
            if bull and low[i] < psar.iloc[i]:
                bull = False
                psar.loc[i] = ep
                ep = low[i]
                af = acc
            elif not bull and high[i] > psar.iloc[i]:
                bull = True
                psar.loc[i] = ep
                ep = high[i]
                af = acc
            else:
                # EP 업데이트
                if bull and high[i] > ep:
                    ep = high[i]
                    af = min(af + acc, max_acc)
                elif not bull and low[i] < ep:
                    ep = low[i]
                    af = min(af + acc, max_acc)
        
        return psar
    
    @staticmethod
    def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """MFI (Money Flow Index) 계산"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        positive_flow_sum = positive_flow.rolling(window=period).sum()
        negative_flow_sum = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_flow_sum / negative_flow_sum))
        return mfi


# 사용 예시
if __name__ == "__main__":
    # 데이터 로드
    import sys
    sys.path.append('..')
    from core.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    
    # 삼성전자 데이터 가져오기
    result = supabase.table('price_data')\
        .select('*')\
        .eq('stock_code', '005930')\
        .order('date', desc=False)\
        .limit(500)\
        .execute()
    
    if result.data:
        df = pd.DataFrame(result.data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # 모든 지표 계산
        df_with_indicators = TechnicalIndicators.calculate_all(df)
        
        # 결과 확인
        print("계산된 지표 컬럼:")
        indicator_columns = [col for col in df_with_indicators.columns 
                           if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        for col in indicator_columns:
            print(f"  - {col}")
        
        print(f"\n총 {len(indicator_columns)}개 지표 계산 완료!")
        
        # 최근 데이터 샘플
        print("\n최근 5일 주요 지표:")
        print(df_with_indicators[['close', 'SMA_20', 'RSI', 'MACD', 'BB_position']].tail())