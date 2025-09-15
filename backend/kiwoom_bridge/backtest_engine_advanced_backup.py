"""
ê³ ê¸‰ ë°±í…Œ?¤íŠ¸ ?”ì§„
- ë¶„í• ë§¤ìˆ˜/ë§¤ë„ ì§€??
- ?•í™•??ê¸°ìˆ ??ì§€??ê³„ì‚°
- ?¤ì œ ì£¼ê? ?°ì´???œìš©
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os

# Core ëª¨ë“ˆ ê²½ë¡œ ì¶”ê?
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core ëª¨ë“ˆ ?°ì„  ?„í¬??
try:
    from core import (
        compute_indicators,
        evaluate_conditions,
        _normalize_conditions,
        convert_legacy_column,
        _iname
    )
    USE_CORE = True
    print("[INFO] AdvancedBacktestEngine: Core ëª¨ë“ˆ ë¡œë“œ ?±ê³µ")
except ImportError as e:
    USE_CORE = False
    print(f"[WARNING] AdvancedBacktestEngine: Core ëª¨ë“ˆ ë¡œë“œ ?¤íŒ¨: {e}")

# ?´ë°±: ê¸°ì¡´ ëª¨ë“ˆ??
try:
    from indicators_complete import CompleteIndicators
    USE_COMPLETE_INDICATORS = True
except ImportError:
    USE_COMPLETE_INDICATORS = False

try:
    from strategy_engine import StrategyEngine
    USE_STRATEGY_ENGINE = True
    if not USE_CORE:
        print("[INFO] AdvancedBacktestEngine: strategy_engine.pyë¥??¬ìš©?©ë‹ˆ??")
except ImportError:
    USE_STRATEGY_ENGINE = False
    if not USE_CORE:
        print("[WARNING] AdvancedBacktestEngine: strategy_engine.pyë¥?ì°¾ì„ ???†ìŠµ?ˆë‹¤.")

@dataclass
class Position:
    """?¬ì????•ë³´"""
    stock_code: str
    quantity: int
    avg_price: float
    entry_date: datetime
    entry_reason: str
    partial_entries: List[Dict] = field(default_factory=list)  # ë¶„í• ë§¤ìˆ˜ ê¸°ë¡

    def add_partial(self, quantity: int, price: float, date: datetime):
        """ë¶„í• ë§¤ìˆ˜ ì¶”ê?"""
        # ?‰ê· ?¨ê? ?¬ê³„??
        total_value = self.quantity * self.avg_price + quantity * price
        self.quantity += quantity
        self.avg_price = total_value / self.quantity if self.quantity > 0 else 0

        self.partial_entries.append({
            'date': date,
            'quantity': quantity,
            'price': price
        })

    def remove_partial(self, quantity: int, price: float, date: datetime) -> float:
        """ë¶„í• ë§¤ë„ ?¤í–‰"""
        if quantity > self.quantity:
            quantity = self.quantity

        profit = (price - self.avg_price) * quantity
        self.quantity -= quantity

        return profit

@dataclass
class Trade:
    """ê±°ë˜ ê¸°ë¡"""
    date: datetime
    stock_code: str
    action: str  # 'buy', 'sell', 'buy_partial', 'sell_partial'
    quantity: int
    price: float
    commission: float
    slippage: float
    profit: Optional[float] = None
    profit_pct: Optional[float] = None
    position_size: Optional[int] = None  # ê±°ë˜ ???¬ì????¬ê¸°

# ? í‹¸ë¦¬í‹° ?¨ìˆ˜??
def _iname(base: str, *params) -> str:
    """ì§€?œëª… ?ì„± - ëª¨ë“  ?Œë¼ë¯¸í„°ë¥??Œë¬¸?ë¡œ ë³€?˜í•˜???°ê²°"""
    parts = [str(base).lower()] + [str(p).lower() for p in params if p is not None]
    return "_".join(parts)

def _lc(s):
    """ë¬¸ì?´ì„ ?Œë¬¸?ë¡œ ë³€??""
    return s.lower() if isinstance(s, str) else s

def _normalize_conditions(conditions):
    """ì¡°ê±´ ?•ê·œ??- ì§€?œëª…, ?°ì‚°?? ê°’ì„ ?Œë¬¸?í™”"""
    norm = []
    for c in conditions or []:
        c = dict(c)
        c['indicator'] = _lc(c.get('indicator', ''))
        c['operator'] = _lc(c.get('operator', ''))
        v = c.get('value', 0)
        c['value'] = _lc(v) if isinstance(v, str) else v
        c['combineWith'] = _lc(c.get('combineWith')) if c.get('combineWith') else None
        norm.append(c)
    return norm

class TechnicalIndicators:
    """ê¸°ìˆ ??ì§€??ê³„ì‚° ?´ë˜??- Core ëª¨ë“ˆ ?¬ìš© ??ê±´ë„ˆ?€"""

    @staticmethod
    def compute_all(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Core ëª¨ë“ˆ ?¬ìš© ???„ì„"""
        if USE_CORE:
            return compute_indicators(df, config)
        # ê¸°ì¡´ ë¡œì§ ? ì?
        return TechnicalIndicators._legacy_compute(df, config)

    @staticmethod
    def _legacy_compute(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """?ˆê±°??ì§€??ê³„ì‚°""
    """?•í™•??ê¸°ìˆ ??ì§€??ê³„ì‚°"""

    @staticmethod
    def calculate_all(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """ëª¨ë“  ì§€??ê³„ì‚°"""
        # ?°ì´??ê²€ì¦?
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"?„ìˆ˜ ì»¬ëŸ¼ ?„ë½: {col}")

        # Use StrategyEngine if available for comprehensive indicator calculation
        if USE_STRATEGY_ENGINE:
            try:
                print(f"[DEBUG] StrategyEngine ?¬ìš© ?œì‘. DataFrame shape: {df.shape}")
                engine = StrategyEngine()
                df = engine.calculate_all_indicators(df)

                # price ë³„ì¹­ ì¶”ê?
                df['price'] = df['close']

                print(f"[INFO] StrategyEngine?ì„œ ëª¨ë“  ì§€??ê³„ì‚° ?„ë£Œ")
                print(f"[DEBUG] ?¬ìš© ê°€?¥í•œ ì»¬ëŸ¼: {list(df.columns)}")

                # Check if rsi_14 exists
                if 'rsi_14' in df.columns:
                    print(f"[DEBUG] rsi_14 ë°œê²¬! ?˜í”Œ ê°? {df['rsi_14'].iloc[-5:].values}")
                else:
                    print(f"[WARNING] rsi_14ê°€ ?¬ì „???†ìŠµ?ˆë‹¤. RSI ê´€??ì»¬ëŸ¼: {[col for col in df.columns if 'rsi' in col.lower()]}")

                return df
            except Exception as e:
                print(f"[WARNING] StrategyEngine ?¬ìš© ?¤íŒ¨: {e}. ê¸°ë³¸ ë°©ë²•?¼ë¡œ ?„í™˜.")
                import traceback
                traceback.print_exc()

        # ì§€???¤ì •
        indicators = config.get('indicators', [])

        for indicator in indicators:
            ind_type = indicator.get('type')
            params = indicator.get('params', {})

            if ind_type == 'SMA' or ind_type == 'MA':
                period = params.get('period', 20)
                df[_iname('sma', period)] = df['close'].rolling(window=period).mean()
                df[_iname('ma', period)] = df[_iname('sma', period)]  # ?™ì¼ ê°??œê³µ

            elif ind_type == 'EMA':
                period = params.get('period', 20)
                df[_iname('ema', period)] = df['close'].ewm(span=period, adjust=False).mean()

            elif ind_type == 'RSI':
                # Wilder RSI ?œì? ?°ì‹
                period = params.get('period', 14)
                delta = df['close'].diff()
                up = delta.clip(lower=0)
                down = (-delta).clip(lower=0)
                rma_up = up.ewm(alpha=1/period, adjust=False).mean()
                rma_down = down.ewm(alpha=1/period, adjust=False).mean()
                rs = rma_up / rma_down.replace(0, 1e-10)
                df[_iname('rsi', period)] = 100 - (100 / (1 + rs))

            elif ind_type == 'MACD':
                f = params.get('fast', 12)
                s = params.get('slow', 26)
                sig = params.get('signal', 9)

                macd = df['close'].ewm(span=f, adjust=False).mean() - df['close'].ewm(span=s, adjust=False).mean()
                df[_iname('macd', f, s)] = macd
                df[_iname('macd_signal', f, s, sig)] = macd.ewm(span=sig, adjust=False).mean()
                df[_iname('macd_hist', f, s, sig)] = df[_iname('macd', f, s)] - df[_iname('macd_signal', f, s, sig)]

            elif ind_type == 'BB':
                p = params.get('period', 20)
                k = params.get('std', 2)
                ma = df['close'].rolling(window=p).mean()
                sd = df['close'].rolling(window=p).std()
                df[_iname('bb_middle', p)] = ma
                df[_iname('bb_upper', p, k)] = ma + k * sd
                df[_iname('bb_lower', p, k)] = ma - k * sd

            elif ind_type == 'Stochastic':
                k_period = params.get('k_period', 14)
                d_period = params.get('d_period', 3)
                low_min = df['low'].rolling(window=k_period).min()
                high_max = df['high'].rolling(window=k_period).max()
                k_fast = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
                df[_iname('stoch_k', k_period, d_period)] = k_fast
                df[_iname('stoch_d', k_period, d_period)] = k_fast.rolling(window=d_period).mean()

            elif ind_type == 'ATR':
                # Wilder ATR ?œì? ?°ì‹
                p = params.get('period', 14)
                tr = pd.concat([
                    df['high'] - df['low'],
                    (df['high'] - df['close'].shift()).abs(),
                    (df['low'] - df['close'].shift()).abs()
                ], axis=1).max(axis=1)
                df[_iname('atr', p)] = tr.ewm(alpha=1/p, adjust=False).mean()

            elif ind_type == 'OBV':
                df[_iname('obv')] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

            elif ind_type == 'ADX':
                # ?œì? ADX ?°ì‹ (Wilder ë°©ì‹)
                p = params.get('period', 14)
                upMove = df['high'].diff()
                downMove = df['low'].shift(1) - df['low']
                plus_dm = np.where((upMove > downMove) & (upMove > 0), upMove, 0.0)
                minus_dm = np.where((downMove > upMove) & (downMove > 0), downMove, 0.0)

                tr = pd.concat([
                    df['high'] - df['low'],
                    (df['high'] - df['close'].shift()).abs(),
                    (df['low'] - df['close'].shift()).abs()
                ], axis=1).max(axis=1)

                atr = tr.ewm(alpha=1/p, adjust=False).mean()
                plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/p, adjust=False).mean() / atr.replace(0,1e-10))
                minus_di = 100 * (pd.Series(minus_dm, index=df.index).ewm(alpha=1/p, adjust=False).mean() / atr.replace(0,1e-10))
                dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0,1e-10)
                df[_iname('adx', p)] = dx.ewm(alpha=1/p, adjust=False).mean()

            elif ind_type == 'CCI':
                p = params.get('period', 20)
                tp = (df['high'] + df['low'] + df['close']) / 3
                sma_tp = tp.rolling(window=p).mean()
                mad = tp.rolling(window=p).apply(lambda x: np.abs(x - x.mean()).mean())
                df[_iname('cci', p)] = (tp - sma_tp) / (0.015 * mad + 1e-10)

            elif ind_type == 'MFI':
                p = params.get('period', 14)
                tp = (df['high'] + df['low'] + df['close']) / 3
                mf = tp * df['volume']
                pos_mf = pd.Series(np.where(tp > tp.shift(), mf, 0), index=df.index)
                neg_mf = pd.Series(np.where(tp < tp.shift(), mf, 0), index=df.index)
                mfr = pos_mf.rolling(window=p).sum() / (neg_mf.rolling(window=p).sum() + 1e-10)
                df[_iname('mfi', p)] = 100 - (100 / (1 + mfr))

            elif ind_type == 'WILLIAMS_R':
                p = params.get('period', 14)
                hh = df['high'].rolling(window=p).max()
                ll = df['low'].rolling(window=p).min()
                df[_iname('willr', p)] = -100 * (hh - df['close']) / (hh - ll + 1e-10)

        # price ë³„ì¹­ ì¶”ê? (close?€ ?™ì¼)
        df['price'] = df['close']

        return df

class SignalGenerator:
    """ë§¤ë§¤ ? í˜¸ ?ì„±"""

    @staticmethod
    def evaluate_conditions(df: pd.DataFrame, conditions: List[Dict], signal_type: str) -> pd.Series:
        """ì¡°ê±´ ?‰ê? ë°?? í˜¸ ?ì„±"""
        if not conditions:
            return pd.Series(0, index=df.index)

        # ì¡°ê±´ ?•ê·œ??
        conditions = _normalize_conditions(conditions)

        # ê°?ì¡°ê±´???‰ê?
        condition_results = []

        for i, condition in enumerate(conditions):
            indicator = condition.get('indicator', '')
            operator = condition.get('operator', '')
            value = condition.get('value', 0)
            combine = condition.get('combineWith', 'and' if i > 0 else None)

            # ì§€??ì»¬ëŸ¼ ?•ì¸
            if indicator not in df.columns:
                # ?´ì˜ ?˜ê²½?ì„œ??ê²½ê³ ë§?ì¶œë ¥
                if signal_type == 'buy':
                    print(f"ê²½ê³ : ë§¤ìˆ˜ ì¡°ê±´??ì§€??'{indicator}'ë¥?ì°¾ì„ ???†ìŠµ?ˆë‹¤")
                else:
                    print(f"ê²½ê³ : ë§¤ë„ ì¡°ê±´??ì§€??'{indicator}'ë¥?ì°¾ì„ ???†ìŠµ?ˆë‹¤")
                continue

            ind_values = df[indicator]

            # ë¹„êµ ê°’ì´ ?¤ë¥¸ ì§€?œì¸ ê²½ìš°
            if isinstance(value, str):
                # ë¬¸ì?´ì¸ ê²½ìš°, ë¨¼ì? ì»¬ëŸ¼ëª…ì¸ì§€ ?•ì¸
                if value in df.columns:
                    compare_values = df[value]
                else:
                    # ì»¬ëŸ¼ëª…ì´ ?„ë‹ˆë©??«ìë¡?ë³€???œë„
                    try:
                        compare_values = float(value)
                    except ValueError:
                        print(f"ê²½ê³ : ê°?'{value}'ë¥?ì²˜ë¦¬?????†ìŠµ?ˆë‹¤ (ì§€?œë„ ?„ë‹ˆê³??«ì???„ë‹˜)")
                        continue
            else:
                compare_values = float(value)

            # ì¡°ê±´ ?‰ê?
            if operator == '>':
                result = ind_values > compare_values
            elif operator == '<':
                result = ind_values < compare_values
            elif operator == '>=':
                result = ind_values >= compare_values
            elif operator == '<=':
                result = ind_values <= compare_values
            elif operator == '==':
                result = ind_values == compare_values
            elif operator == 'cross_above':
                if isinstance(compare_values, pd.Series):
                    result = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values.shift(1))
                else:
                    result = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values)
            elif operator == 'cross_below':
                if isinstance(compare_values, pd.Series):
                    result = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values.shift(1))
                else:
                    result = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values)
            else:
                continue

            condition_results.append((result, combine))

        # ì¡°ê±´ ê²°í•©
        if condition_results:
            final_result = condition_results[0][0]

            for i in range(1, len(condition_results)):
                if condition_results[i][1] == 'and':
                    final_result = final_result & condition_results[i][0]
                else:  # or
                    final_result = final_result | condition_results[i][0]

            # ? í˜¸ ?ì„± (ì§„ì… ?œì ë§?
            signal = pd.Series(0, index=df.index)
            signal[final_result & ~final_result.shift(1).fillna(False)] = 1 if signal_type == 'buy' else -1

            return signal

        return pd.Series(0, index=df.index)

    @staticmethod
    def evaluate_conditions_with_profit(df: pd.DataFrame, strategy_config: Dict,
                                       signal_type: str, positions: Dict = None,
                                       stock_code: str = 'TEST') -> pd.Series:
        """ëª©í‘œ ?˜ìµë¥ ì„ ?¬í•¨??ì¡°ê±´ ?‰ê? (?¨ê³„ë³?ëª©í‘œ ì§€??"""

        # 1. ê¸°ë³¸ ì§€??ì¡°ê±´ ?‰ê?
        if signal_type == 'sell':
            conditions = strategy_config.get('sellConditions', [])
        else:
            conditions = strategy_config.get('buyConditions', [])

        base_signal = SignalGenerator.evaluate_conditions(df, conditions, signal_type)

        # 2. ë§¤ë„ ??ëª©í‘œ ?˜ìµë¥?ì¡°ê±´ ì¶”ê? ?‰ê?
        if signal_type == 'sell' and positions and stock_code in positions:
            target_profit = strategy_config.get('targetProfit', {})
            stop_loss = strategy_config.get('stopLoss', {})
            position = positions[stock_code]

            # ëª©í‘œ ?˜ìµë¥?? í˜¸ ?ì„±
            if target_profit:
                mode = target_profit.get('mode', 'simple')

                if mode == 'simple' and target_profit.get('enabled'):
                    # ?¨ì¼ ëª©í‘œ ëª¨ë“œ (?´ì „ ë²„ì „ ?¸í™˜??
                    profit_signal = pd.Series(0, index=df.index)

                    # simple ëª¨ë“œ: enabledê°€ ì§ì ‘ ?ˆê±°??simple.enabledê°€ ?ˆëŠ” ê²½ìš° ì²˜ë¦¬
                    if target_profit.get('simple'):
                        target_value = target_profit['simple'].get('value', 5.0)
                        combine_method = _lc(target_profit['simple'].get('combineWith', 'or'))
                    else:
                        # ?´ì „ ë²„ì „ ?¸í™˜??
                        target_value = target_profit.get('value', 5.0)
                        combine_method = _lc(target_profit.get('combineWith', 'or'))

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        if profit_pct >= target_value:
                            profit_signal[idx] = -1  # ?„ëŸ‰ ë§¤ë„ ? í˜¸

                    # ê¸°ì¡´ ì¡°ê±´ê³?ê²°í•©
                    if combine_method == 'and':
                        base_signal = base_signal & profit_signal
                    else:  # or
                        base_signal = base_signal | profit_signal

                elif mode == 'staged' and target_profit.get('staged', {}).get('enabled'):
                    # ?¨ê³„ë³?ëª©í‘œ ëª¨ë“œ
                    profit_signal = pd.Series(0, index=df.index)
                    staged_config = target_profit['staged']
                    stages = staged_config.get('stages', [])

                    # ?´ë? ?¤í–‰???¨ê³„ ì¶”ì 
                    if not hasattr(position, 'executed_stages'):
                        position.executed_stages = []

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        # ê°??¨ê³„ë³?ëª©í‘œ ?•ì¸
                        for stage in stages:
                            stage_num = stage.get('stage', 1)
                            stage_target = stage.get('targetProfit', 5.0)
                            exit_ratio = stage.get('exitRatio', 100) / 100.0
                            stage_combine = _lc(stage.get('combineWith', staged_config.get('combineWith', 'or')))

                            # ?´ë? ?¤í–‰???¨ê³„???¤í‚µ
                            if stage_num in position.executed_stages:
                                continue

                            if profit_pct >= stage_target:
                                # ê°??¨ê³„ë³?ê²°í•© ë°©ì‹ ?€??
                                if not hasattr(profit_signal, 'stage_combines'):
                                    profit_signal.stage_combines = {}
                                profit_signal.stage_combines[idx] = stage_combine

                                # ë¶€ë¶?ë§¤ë„ ? í˜¸ (ë¹„ìœ¨ ?€??
                                if not hasattr(profit_signal, 'exit_ratios'):
                                    profit_signal.exit_ratios = {}
                                profit_signal.exit_ratios[idx] = exit_ratio
                                profit_signal[idx] = -exit_ratio  # ?Œìˆ˜ë¡?ë§¤ë„ ë¹„ìœ¨ ?œì‹œ
                                position.executed_stages.append(stage_num)

                                # ?™ì  ?ì ˆ ì¡°ì •
                                if stage.get('dynamicStopLoss', False):
                                    # ?ì ˆ? ì„ ?„ì¬ ?¨ê³„??ëª©í‘œ ?˜ìµë¥ ë¡œ ?í–¥
                                    if hasattr(position, 'dynamic_stop_loss'):
                                        position.dynamic_stop_loss = max(
                                            position.dynamic_stop_loss,
                                            position.avg_price * (1 + stage_target / 100)
                                        )
                                    else:
                                        position.dynamic_stop_loss = position.avg_price * (1 + stage_target / 100)
                                break  # ??ë²ˆì— ?˜ë‚˜???¨ê³„ë§??¤í–‰

                    # ?¨ê³„ë³?ê²°í•© ë°©ì‹ ?ìš©
                    # profit_signal??ê°??¸ë±?¤ë³„ ê²°í•© ë°©ì‹???€?¥ë˜???ˆìŒ
                    combined_signal = pd.Series(0, index=df.index)

                    for idx in df.index:
                        if profit_signal[idx] != 0:
                            # ?´ë‹¹ ?¸ë±?¤ì˜ ê²°í•© ë°©ì‹ ?•ì¸
                            stage_combine = _lc(getattr(profit_signal, 'stage_combines', {}).get(idx, 'or'))

                            if stage_combine == 'and':
                                # AND: ì§€??ì¡°ê±´ê³?ëª©í‘œ ?˜ìµ ëª¨ë‘ ì¶©ì¡±
                                if base_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                            else:  # or
                                # OR: ??ì¤??˜ë‚˜ë§?ì¶©ì¡±
                                if profit_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                                elif base_signal[idx] != 0:
                                    combined_signal[idx] = base_signal[idx]
                        elif base_signal[idx] != 0:
                            # ëª©í‘œ ?˜ìµ ë¯¸ë‹¬????ì§€??ì¡°ê±´ë§??•ì¸
                            combined_signal[idx] = base_signal[idx]

                    base_signal = combined_signal

            # ?ì ˆ ì¡°ê±´ (??ƒ ORë¡?ê²°í•©)
            if stop_loss.get('enabled'):
                loss_signal = pd.Series(0, index=df.index)
                loss_value = stop_loss.get('value', 3.0)

                # ?¸ë ˆ?¼ë§ ?¤í†± ?•ì¸
                trailing_stop = stop_loss.get('trailingStop', {})

                for idx in df.index:
                    current_price = df.loc[idx, 'close']
                    profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                    # ?™ì  ?ì ˆ ?•ì¸ (Break Even Stop)
                    if hasattr(position, 'dynamic_stop_loss'):
                        dynamic_loss_pct = ((current_price - position.dynamic_stop_loss) / position.dynamic_stop_loss) * 100
                        if dynamic_loss_pct <= 0:
                            loss_signal[idx] = -1  # ?™ì  ?ì ˆ ë§¤ë„
                            continue

                    # ?¸ë ˆ?¼ë§ ?¤í†± ?•ì¸
                    if trailing_stop.get('enabled'):
                        activation = trailing_stop.get('activation', 5.0)
                        distance = trailing_stop.get('distance', 2.0)

                        # ìµœê³ ê°€ ì¶”ì 
                        if not hasattr(position, 'peak_price'):
                            position.peak_price = position.avg_price

                        if profit_pct >= activation:
                            # ?¸ë ˆ?¼ë§ ?¤í†± ?œì„±??
                            position.peak_price = max(position.peak_price, current_price)
                            peak_drop_pct = ((current_price - position.peak_price) / position.peak_price) * 100

                            if peak_drop_pct <= -abs(distance):
                                loss_signal[idx] = -1  # ?¸ë ˆ?¼ë§ ?¤í†± ë§¤ë„
                                continue

                    # ?¼ë°˜ ?ì ˆ
                    if profit_pct <= -abs(loss_value):
                        loss_signal[idx] = -1  # ?ì ˆ ë§¤ë„

                # ?ì ˆ?€ ??ƒ OR (ì¦‰ì‹œ ?¤í–‰)
                base_signal = base_signal | loss_signal

        return base_signal

class AdvancedBacktestEngine:
    """ê³ ê¸‰ ë°±í…Œ?¤íŠ¸ ?”ì§„"""

    def __init__(self, initial_capital: float = 10000000, commission: float = 0.00015, slippage: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []

    def calculate_position_size(self, capital: float, price: float, config: Dict) -> int:
        """?¬ì????¬ê¸° ê³„ì‚°"""
        position_sizing = config.get('positionSizing', {})
        method = position_sizing.get('method', 'fixed')

        if method == 'fixed':
            # ê³ ì • ê¸ˆì•¡
            amount = position_sizing.get('amount', capital * 0.1)
            shares = int(amount / price)
        elif method == 'percent':
            # ?ë³¸???¼ì • ë¹„ìœ¨
            percent = position_sizing.get('percent', 10) / 100
            amount = capital * percent
            shares = int(amount / price)
        elif method == 'kelly':
            # ì¼ˆë¦¬ ê³µì‹ (win_rateê³?avg_win/avg_loss ?„ìš”)
            win_rate = position_sizing.get('win_rate', 0.5)
            win_loss_ratio = position_sizing.get('win_loss_ratio', 1.5)
            kelly_percent = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            kelly_percent = max(0, min(kelly_percent, 0.25))  # ìµœë? 25% ?œí•œ
            amount = capital * kelly_percent
            shares = int(amount / price)
        else:
            # ê¸°ë³¸ê°? ?ë³¸??10%
            shares = int((capital * 0.1) / price)

        return max(0, shares)

    def execute_buy(self, stock_code: str, date: datetime, price: float, config: Dict) -> Optional[Trade]:
        """ë§¤ìˆ˜ ?¤í–‰"""
        # ë¶„í• ë§¤ìˆ˜ ?¤ì •
        split_buy = config.get('splitBuy', {})
        enable_split = split_buy.get('enabled', False)
        split_count = split_buy.get('count', 1)
        split_interval = split_buy.get('interval', 'price')  # 'price' or 'time'

        # ?¬ë¦¬?¼ì? ?ìš©
        actual_price = price * (1 + self.slippage)

        # ?¬ì????¬ê¸° ê³„ì‚°
        position_size = self.calculate_position_size(self.capital, actual_price, config)

        if enable_split and split_count > 1:
            # ë¶„í• ë§¤ìˆ˜
            split_size = position_size // split_count
            if split_size <= 0:
                return None

            # ì²?ë²ˆì§¸ ë¶„í• ë§¤ìˆ˜ë§??¤í–‰ (?˜ë¨¸ì§€??ì¡°ê±´ ì¶©ì¡± ??
            position_size = split_size

        # ?˜ìˆ˜ë£?ê³„ì‚°
        cost = position_size * actual_price * (1 + self.commission)

        if cost > self.capital:
            return None

        # ?¬ì????ì„± ?ëŠ” ì¶”ê?
        if stock_code in self.positions:
            # ê¸°ì¡´ ?¬ì??˜ì— ì¶”ê? (?¼ë¼ë¯¸ë”©)
            position = self.positions[stock_code]
            position.add_partial(position_size, actual_price, date)
            action = 'buy_partial'
        else:
            # ???¬ì????ì„±
            self.positions[stock_code] = Position(
                stock_code=stock_code,
                quantity=position_size,
                avg_price=actual_price,
                entry_date=date,
                entry_reason='signal'
            )
            action = 'buy'

        # ?ë³¸ ì°¨ê°
        self.capital -= cost

        # ê±°ë˜ ê¸°ë¡
        trade = Trade(
            date=date,
            stock_code=stock_code,
            action=action,
            quantity=position_size,
            price=actual_price,
            commission=self.commission,
            slippage=self.slippage,
            position_size=self.positions[stock_code].quantity
        )
        self.trades.append(trade)

        return trade

    def execute_sell(self, stock_code: str, date: datetime, price: float, config: Dict) -> Optional[Trade]:
        """ë§¤ë„ ?¤í–‰"""
        if stock_code not in self.positions:
            return None

        position = self.positions[stock_code]
        if position.quantity <= 0:
            return None

        # ë¶„í• ë§¤ë„ ?¤ì •
        split_sell = config.get('splitSell', {})
        enable_split = split_sell.get('enabled', False)
        split_count = split_sell.get('count', 1)

        # ?¬ë¦¬?¼ì? ?ìš©
        actual_price = price * (1 - self.slippage)

        # ë§¤ë„ ?˜ëŸ‰ ê²°ì •
        if enable_split and split_count > 1:
            sell_quantity = position.quantity // split_count
            if sell_quantity <= 0:
                sell_quantity = position.quantity
        else:
            sell_quantity = position.quantity

        # ?˜ìµ ê³„ì‚°
        profit = position.remove_partial(sell_quantity, actual_price, date)
        proceeds = sell_quantity * actual_price * (1 - self.commission)

        # ?ë³¸ ì¦ê?
        self.capital += proceeds

        # ?¬ì????•ë¦¬
        if position.quantity <= 0:
            del self.positions[stock_code]
            action = 'sell'
        else:
            action = 'sell_partial'

        # ê±°ë˜ ê¸°ë¡
        trade = Trade(
            date=date,
            stock_code=stock_code,
            action=action,
            quantity=sell_quantity,
            price=actual_price,
            commission=self.commission,
            slippage=self.slippage,
            profit=profit,
            profit_pct=(profit / (position.avg_price * sell_quantity)) * 100 if position.avg_price > 0 else 0,
            position_size=position.quantity if stock_code in self.positions else 0
        )
        self.trades.append(trade)

        return trade

    def run(self, data: pd.DataFrame, strategy_config: Dict) -> Dict[str, Any]:
        """ë°±í…Œ?¤íŠ¸ ?¤í–‰ - Core ëª¨ë“ˆ ?°ì„  ?¬ìš©"""
        print(f"[DEBUG] AdvancedBacktestEngine.run ?œì‘")
        print(f"[DEBUG] ?…ë ¥ ?°ì´??shape: {data.shape}")
        print(f"[DEBUG] Core ëª¨ë“ˆ ?¬ìš©: {USE_CORE}")

        # Core ëª¨ë“ˆ ?¬ìš© ??
        if USE_CORE:
            print("[DEBUG] Core ëª¨ë“ˆë¡?ì²˜ë¦¬")

            # params êµ¬ì¡° ?ë™ ?˜ì •
            indicators = strategy_config.get('indicators', [])
            fixed_indicators = []
            for ind in indicators:
                if 'params' not in ind and 'period' in ind:
                    fixed_ind = {
                        'type': ind.get('type', 'MA').upper(),
                        'params': {'period': ind.get('period', 20)}
                    }
                    print(f"[FIX] ì§€??êµ¬ì¡°: {ind} ??{fixed_ind}")
                    fixed_indicators.append(fixed_ind)
                else:
                    fixed_indicators.append(ind)

            # ì¡°ê±´ ?•ê·œ??
            buy_conditions = _normalize_conditions(strategy_config.get('buyConditions', []))
            sell_conditions = _normalize_conditions(strategy_config.get('sellConditions', []))

            # Core ?¤ì •
            config = {
                **strategy_config,
                'indicators': fixed_indicators,
                'buyConditions': buy_conditions,
                'sellConditions': sell_conditions
            }

            # ì§€??ê³„ì‚°
            data = compute_indicators(data, config)

            # ? í˜¸ ?ì„±
            data['buy_signal'] = evaluate_conditions(data, buy_conditions, 'buy')
            data['sell_signal'] = evaluate_conditions(data, sell_conditions, 'sell')

            buy_count = (data['buy_signal'] == 1).sum()
            sell_count = (data['sell_signal'] == -1).sum()
            print(f"[Core] ? í˜¸: ë§¤ìˆ˜ {buy_count}, ë§¤ë„ {sell_count}")

        # ?´ë°±: ê¸°ì¡´ ë°©ì‹
        elif USE_COMPLETE_INDICATORS:
            print(f"[DEBUG] CompleteIndicators ?¬ìš©")
            data = CompleteIndicators.calculate_all(data, strategy_config)
        else:
            print(f"[DEBUG] TechnicalIndicators ?¬ìš©")
            data = TechnicalIndicators.calculate_all(data, strategy_config)

        print(f"[DEBUG] ì§€??ê³„ì‚° ???°ì´??shape: {data.shape}")
        print(f"[DEBUG] ì§€??ê³„ì‚° ??ì»¬ëŸ¼: {list(data.columns)[:30]}...")

        # Core ëª¨ë“ˆ???¬ìš©?˜ì? ?ŠëŠ” ê²½ìš°?ë§Œ ê¸°ì¡´ ? í˜¸ ?ì„±
        if not USE_CORE:
            # ? í˜¸ ?ì„±
            buy_conditions = strategy_config.get('buyConditions', [])
            sell_conditions = strategy_config.get('sellConditions', [])

            print(f"[DEBUG] ë§¤ìˆ˜ ì¡°ê±´: {buy_conditions}")
            print(f"[DEBUG] ë§¤ë„ ì¡°ê±´: {sell_conditions}")

            # ëª©í‘œ ?˜ìµë¥??•ë³´ ì¶œë ¥
            target_profit = strategy_config.get('targetProfit', {})
            if target_profit.get('enabled'):
                print(f"[DEBUG] ëª©í‘œ ?˜ìµë¥? {target_profit.get('value')}%, ê²°í•©: {target_profit.get('combineWith', 'OR')}")

            data['buy_signal'] = SignalGenerator.evaluate_conditions(data, buy_conditions, 'buy')

        # ë§¤ë„ ? í˜¸???¬ì??˜ì´ ?ˆì„ ?Œë§Œ ëª©í‘œ ?˜ìµë¥?ê³ ë ¤
        if self.positions:
            data['sell_signal'] = SignalGenerator.evaluate_conditions_with_profit(
                data, strategy_config, 'sell', self.positions, 'TEST'
            )
        else:
            data['sell_signal'] = SignalGenerator.evaluate_conditions(data, sell_conditions, 'sell')

        # ë°±í…Œ?¤íŠ¸ ?¤í–‰
        for i in range(len(data)):
            row = data.iloc[i]
            date = row['date']
            close = row['close']

            # ?„ì¬ ?¬íŠ¸?´ë¦¬??ê°€ì¹?ê³„ì‚°
            portfolio_value = self.capital
            for stock_code, position in self.positions.items():
                portfolio_value += position.quantity * close
            self.equity_curve.append(portfolio_value)

            # ?¬ì??˜ì´ ?ˆì„ ??ë§¤ë„ ? í˜¸ ?¬ê³„??(ëª©í‘œ ?˜ìµë¥??¤ì‹œê°?ì²´í¬)
            if self.positions:
                current_sell_signal = SignalGenerator.evaluate_conditions_with_profit(
                    data.iloc[[i]], strategy_config, 'sell', self.positions, 'TEST'
                )
                if not current_sell_signal.empty and current_sell_signal.iloc[0] == -1:
                    for stock_code in list(self.positions.keys()):
                        position = self.positions[stock_code]
                        profit_pct = ((close - position.avg_price) / position.avg_price) * 100

                        # ëª©í‘œ ?˜ìµë¥??ëŠ” ?ì ˆ ?„ë‹¬ ??ë¡œê·¸
                        target_profit = strategy_config.get('targetProfit', {})
                        stop_loss = strategy_config.get('stopLoss', {})

                        if target_profit.get('enabled') and profit_pct >= target_profit.get('value', 5.0):
                            print(f"[ëª©í‘œ ?˜ìµë¥??„ë‹¬] {stock_code}: {profit_pct:.2f}% >= {target_profit.get('value')}%")
                        elif stop_loss.get('enabled') and profit_pct <= -abs(stop_loss.get('value', 3.0)):
                            print(f"[?ì ˆ ?¤í–‰] {stock_code}: {profit_pct:.2f}% <= -{stop_loss.get('value')}%")

                        self.execute_sell(stock_code, date, close, strategy_config)
            elif row['sell_signal'] == -1:
                # ?¬ì??˜ì´ ?†ìœ¼ë©?ê¸°ë³¸ ë§¤ë„ ? í˜¸ ?¬ìš©
                for stock_code in list(self.positions.keys()):
                    self.execute_sell(stock_code, date, close, strategy_config)

            # ë§¤ìˆ˜ ? í˜¸ ì²˜ë¦¬
            if row['buy_signal'] == 1:
                # ìµœë? ?¬ì?????ì²´í¬
                max_positions = strategy_config.get('maxPositions', 1)
                if len(self.positions) < max_positions:
                    self.execute_buy('TEST', date, close, strategy_config)

        # ìµœì¢… ?¬ì????•ë¦¬
        if len(data) > 0:
            final_date = data.iloc[-1]['date']
            final_price = data.iloc[-1]['close']

            for stock_code in list(self.positions.keys()):
                position = self.positions[stock_code]
                if position.quantity > 0:
                    self.execute_sell(stock_code, final_date, final_price, strategy_config)

        # ?±ê³¼ ë¶„ì„
        return self.analyze_performance()

    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance"""
        if not self.trades:
            return {
                'total_return': 0,
                'win_rate': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'trades': []
            }

        # ê¸°ë³¸ ?µê³„
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100

        # ?„ë£Œ??ê±°ë˜ë§?ë¶„ì„
        completed_trades = [t for t in self.trades if t.profit is not None]
        winning_trades = [t for t in completed_trades if t.profit > 0]
        losing_trades = [t for t in completed_trades if t.profit <= 0]

        win_rate = (len(winning_trades) / len(completed_trades) * 100) if completed_trades else 0

        # ?‰ê·  ?ìµ
        avg_win = np.mean([t.profit for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.profit for t in losing_trades])) if losing_trades else 0

        # Profit Factor
        total_wins = sum([t.profit for t in winning_trades]) if winning_trades else 0
        total_losses = abs(sum([t.profit for t in losing_trades])) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # ìµœë? ?™í­
        if self.equity_curve:
            equity_array = np.array(self.equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (peak - equity_array) / peak * 100
            max_drawdown = np.max(drawdown)
        else:
            max_drawdown = 0

        # Sharpe Ratio (?¼ê°„ ?˜ìµë¥?ê¸°ì?)
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # ê±°ë˜ ?ì„¸ ?•ë³´
        trade_details = []
        for trade in self.trades:
            trade_details.append({
                'date': trade.date.isoformat() if isinstance(trade.date, datetime) else str(trade.date),
                'stock_code': trade.stock_code,
                'action': trade.action,
                'quantity': trade.quantity,
                'price': trade.price,
                'profit': trade.profit,
                'profit_pct': trade.profit_pct,
                'position_size': trade.position_size
            })

        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'buy_count': len([t for t in self.trades if 'buy' in t.action]),
            'sell_count': len([t for t in self.trades if 'sell' in t.action]),
            'trades': trade_details,
            'equity_curve': self.equity_curve
        }
