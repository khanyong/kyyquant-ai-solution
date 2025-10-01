"""
백테스트 엔진 핵심 모듈
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, field

from strategies.manager import StrategyManager
from indicators.calculator import IndicatorCalculator
from data.provider import DataProvider
from .models import BacktestResult, Position, Trade

class BacktestEngine:
    """백테스트 엔진"""

    def __init__(self):
        self.strategy_manager = StrategyManager()
        self.indicator_calculator = IndicatorCalculator()
        self.data_provider = DataProvider()

    async def run(
        self,
        strategy_id: str,
        stock_codes: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 10000000,
        commission: float = 0.00015,
        slippage: float = 0.001,
        **kwargs
    ) -> Dict[str, Any]:
        """
        백테스트 실행

        Args:
            strategy_id: 전략 ID
            stock_codes: 종목 코드 리스트
            start_date: 시작일
            end_date: 종료일
            initial_capital: 초기 자본금
            commission: 수수료율
            slippage: 슬리피지

        Returns:
            백테스트 결과
        """
        print(f"Starting backtest for strategy: {strategy_id}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Stocks: {stock_codes}")

        # 전략 로드
        strategy = await self.strategy_manager.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy not found: {strategy_id}")

        # 데이터 로드
        price_data = await self._load_price_data(stock_codes, start_date, end_date)
        if not price_data:
            raise ValueError("No price data available")

        # 백테스트 실행
        results = await self._run_backtest(
            strategy=strategy,
            price_data=price_data,
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )

        # 결과 정리
        return self._prepare_results(results, strategy_id, start_date, end_date)

    async def run_with_config(
        self,
        strategy_config: Dict[str, Any],
        stock_codes: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        설정으로 직접 백테스트 실행 (전략 저장 없이)
        """
        # 임시 전략 생성
        temp_strategy = {
            'id': f'temp_{uuid.uuid4().hex[:8]}',
            'name': 'Temporary Strategy',
            'config': strategy_config
        }

        return await self._run_with_strategy(temp_strategy, stock_codes, **kwargs)

    async def _load_price_data(
        self,
        stock_codes: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, pd.DataFrame]:
        """주가 데이터 로드"""
        price_data = {}

        for code in stock_codes:
            df = await self.data_provider.get_historical_data(
                stock_code=code,
                start_date=start_date,
                end_date=end_date
            )
            if df is not None and not df.empty:
                price_data[code] = df

        return price_data

    async def _run_backtest(
        self,
        strategy: Dict[str, Any],
        price_data: Dict[str, pd.DataFrame],
        initial_capital: float,
        commission: float,
        slippage: float
    ) -> Dict[str, Any]:
        """백테스트 핵심 로직"""

        capital = initial_capital
        positions = {}  # 현재 보유 포지션
        trades = []  # 거래 기록
        daily_values = []  # 일별 자산 가치

        strategy_config = strategy.get('config', {})
        use_stage_based = strategy_config.get('useStageBasedStrategy', False)

        # 전략 조건 파싱
        if use_stage_based:
            buy_stages = strategy_config.get('buyStageStrategy', {}).get('stages', [])
            sell_stages = strategy_config.get('sellStageStrategy', {}).get('stages', [])
            print(f"Using stage-based strategy with {len(buy_stages)} buy stages and {len(sell_stages)} sell stages")
        else:
            buy_conditions = strategy_config.get('buyConditions', [])
            sell_conditions = strategy_config.get('sellConditions', [])

            if not buy_conditions or not sell_conditions:
                raise ValueError("Strategy must have both buy and sell conditions")

        # 각 종목별 백테스트
        for stock_code, df in price_data.items():
            print(f"[Engine] Processing {stock_code} with {len(df)} rows")

            # 지표 계산
            print(f"[Engine] Step 1: Calculating indicators...")
            df = await self._calculate_indicators(df, strategy_config)

            # 신호 생성
            print(f"[Engine] Step 2: Evaluating signals...")
            if use_stage_based:
                df = await self._evaluate_staged_signals(df, buy_stages, sell_stages, positions, stock_code)
            else:
                df = await self._evaluate_signals(df, buy_conditions, sell_conditions, positions, stock_code)

            # 거래 실행
            print(f"[Engine] Step 3: Executing trades...")
            trade_count = 0
            for idx, row in df.iterrows():
                trade_count += 1
                if trade_count % 50 == 0:  # 50일마다 진행상황 출력
                    print(f"[Engine] Processed {trade_count}/{len(df)} days")
                date = idx
                price = row['close']

                # 매도 체크
                if stock_code in positions and row.get('sell_signal'):
                    position = positions[stock_code]
                    sell_quantity = position['quantity']
                    sell_amount = sell_quantity * price
                    commission_fee = sell_amount * commission

                    # 수익 계산
                    profit = sell_amount - position['total_cost'] - commission_fee
                    profit_rate = profit / position['total_cost'] * 100

                    # 거래 기록
                    trades.append({
                        'trade_id': str(uuid.uuid4()),
                        'date': date,
                        'stock_code': stock_code,
                        'type': 'sell',
                        'quantity': sell_quantity,
                        'price': price,
                        'amount': sell_amount,
                        'commission': commission_fee,
                        'profit': profit,
                        'profit_rate': profit_rate,
                        'reason': row.get('sell_reason', 'Signal')
                    })

                    # 자본금 업데이트
                    capital += sell_amount - commission_fee

                    # 포지션 제거
                    del positions[stock_code]

                # 매수 체크
                if stock_code not in positions and row.get('buy_signal'):
                    # 매수 가능 금액 계산
                    max_buy_amount = capital * 0.3  # 종목당 최대 30%
                    buy_quantity = int(max_buy_amount / price)

                    if buy_quantity > 0:
                        buy_amount = buy_quantity * price
                        commission_fee = buy_amount * commission

                        # 거래 기록
                        trades.append({
                            'trade_id': str(uuid.uuid4()),
                            'date': date,
                            'stock_code': stock_code,
                            'type': 'buy',
                            'quantity': buy_quantity,
                            'price': price,
                            'amount': buy_amount,
                            'commission': commission_fee,
                            'reason': row.get('buy_reason', 'Signal')
                        })

                        # 포지션 추가
                        positions[stock_code] = {
                            'quantity': buy_quantity,
                            'avg_price': price,
                            'total_cost': buy_amount + commission_fee,
                            'entry_date': date
                        }

                        # 자본금 업데이트
                        capital -= buy_amount + commission_fee

                # 일별 자산 가치 계산
                total_value = capital
                for code, pos in positions.items():
                    if code in price_data:
                        current_price = price_data[code].loc[date, 'close'] if date in price_data[code].index else pos['avg_price']
                        total_value += pos['quantity'] * current_price

                daily_values.append({
                    'date': date,
                    'capital': capital,
                    'total_value': total_value,
                    'positions': len(positions)
                })

        # 최종 결과 계산
        print(f"[Engine] Step 4: Calculating final results...")
        final_value = capital
        for code, pos in positions.items():
            # 미청산 포지션 현재가로 평가
            last_price = price_data[code]['close'].iloc[-1] if code in price_data else pos['avg_price']
            final_value += pos['quantity'] * last_price

        results = {
            'initial_capital': initial_capital,
            'final_capital': final_value,
            'total_return': final_value - initial_capital,
            'total_return_rate': ((final_value - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0,
            'trades': trades,
            'positions': positions,
            'daily_values': daily_values
        }

        print(f"[Engine] Backtest completed successfully")
        print(f"[Engine] Results: Total trades: {len(trades)}, Final capital: {final_value:,.0f}, Return: {results['total_return_rate']:.2f}%")

        return results

    async def _calculate_indicators(
        self,
        df: pd.DataFrame,
        strategy_config: Dict[str, Any]
    ) -> pd.DataFrame:
        """지표 계산"""
        indicators = strategy_config.get('indicators', [])

        print(f"[Engine] Calculating {len(indicators)} indicators")
        print(f"[Engine] Initial columns: {list(df.columns)}")

        for idx, indicator in enumerate(indicators):
            try:
                print(f"[Engine] Calculating indicator {idx+1}/{len(indicators)}: {indicator}")
                df = await self.indicator_calculator.calculate(df, indicator)
            except Exception as e:
                print(f"[Engine] Error calculating indicator {indicator.get('name', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                # 에러가 발생해도 계속 진행

        # 추가 필수 컬럼 계산
        # 거래량 이동평균
        if 'volume' in df.columns:
            df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
            print(f"[Engine] Added volume_ma_20 column")

        print(f"[Engine] Indicator calculation complete")
        print(f"[Engine] Final columns: {list(df.columns)}")
        print(f"[Engine] Sample data (first row):")
        if len(df) > 0:
            for col in df.columns:
                if col not in ['open', 'high', 'low', 'close', 'volume']:
                    print(f"  {col}: {df.iloc[0][col] if not pd.isna(df.iloc[0][col]) else 'NaN'}")

        return df

    async def _evaluate_signals(
        self,
        df: pd.DataFrame,
        buy_conditions: List[Dict],
        sell_conditions: List[Dict],
        positions: Dict = None,
        stock_code: str = None
    ) -> pd.DataFrame:
        """신호 평가"""
        df['buy_signal'] = False
        df['sell_signal'] = False
        df['buy_reason'] = ''
        df['sell_reason'] = ''

        print(f"[Engine] Evaluating signals for {len(df)} rows")
        print(f"[Engine] Buy conditions: {buy_conditions}")
        print(f"[Engine] Sell conditions: {sell_conditions}")

        # 이전 값 컬럼 추가 (cross 연산을 위해)
        for col in df.columns:
            if col not in ['buy_signal', 'sell_signal', 'buy_reason', 'sell_reason']:
                df['prev_' + col] = df[col].shift(1)

        # 현재 포지션의 수익률 추가 (매도 조건 평가를 위해)
        if positions and stock_code and stock_code in positions:
            position = positions[stock_code]
            avg_price = position['avg_price']
            df['profit_rate'] = ((df['close'] - avg_price) / avg_price * 100)
        else:
            df['profit_rate'] = 0

        # 매수/매도 조건 평가
        buy_signal_count = 0
        sell_signal_count = 0

        for i in range(len(df)):
            # 매수 조건 체크 - AND 조건으로 평가
            all_buy_conditions_met = True
            buy_reasons = []

            if buy_conditions:
                for condition in buy_conditions:
                    if not self._check_condition(df.iloc[i], condition):
                        all_buy_conditions_met = False
                        break
                    else:
                        buy_reasons.append(self._format_condition_reason(condition))

                if all_buy_conditions_met:
                    df.loc[df.index[i], 'buy_signal'] = True
                    df.loc[df.index[i], 'buy_reason'] = ' & '.join(buy_reasons)
                    buy_signal_count += 1

            # 매도 조건 체크 - OR 조건으로 평가 (하나라도 만족하면 매도)
            for condition in sell_conditions:
                if self._check_condition(df.iloc[i], condition):
                    df.loc[df.index[i], 'sell_signal'] = True
                    df.loc[df.index[i], 'sell_reason'] = self._format_condition_reason(condition)
                    sell_signal_count += 1
                    break

        # 이전 값 컬럼 제거
        prev_cols = [col for col in df.columns if col.startswith('prev_')]
        df.drop(columns=prev_cols, inplace=True)

        print(f"[Engine] Signal evaluation complete: {buy_signal_count} buy signals, {sell_signal_count} sell signals")
        return df

    async def _evaluate_staged_signals(
        self,
        df: pd.DataFrame,
        buy_stages: List[Dict],
        sell_stages: List[Dict],
        positions: Dict = None,
        stock_code: str = None
    ) -> pd.DataFrame:
        """단계별 신호 평가"""
        # TODO: 단계별 거래 로직 구현
        return df

    def _check_condition(self, row: pd.Series, condition: Dict) -> bool:
        """조건 체크"""
        indicator = condition.get('indicator')
        operator = condition.get('operator')
        value = condition.get('value')
        compare_to = condition.get('compareTo')

        # 디버그: 사용 가능한 컬럼 확인
        if not indicator:
            print(f"[Engine] Warning: No indicator specified in condition")
            return False

        if indicator not in row:
            print(f"[Engine] Warning: Indicator '{indicator}' not found in row")
            print(f"[Engine] Available columns: {list(row.index)}")
            return False

        indicator_value = row[indicator]

        # NaN 체크
        if pd.isna(indicator_value):
            return False

        # 비교 대상 값 결정
        if compare_to and compare_to in row:
            compare_value = row[compare_to]
        else:
            compare_value = float(value) if value else 0

        # 연산자별 비교
        try:
            if operator == '>':
                result = indicator_value > compare_value
            elif operator == '<':
                result = indicator_value < compare_value
            elif operator == '>=':
                result = indicator_value >= compare_value
            elif operator == '<=':
                result = indicator_value <= compare_value
            elif operator == '==':
                result = indicator_value == compare_value
            elif operator in ['cross_above', 'crossAbove']:
                # 크로스 업 체크 - 이전 값과 현재 값 비교
                if 'prev_' + indicator in row and compare_to and 'prev_' + compare_to in row:
                    prev_indicator = row['prev_' + indicator]
                    prev_compare = row['prev_' + compare_to]
                    if not pd.isna(prev_indicator) and not pd.isna(prev_compare):
                        result = (prev_indicator <= prev_compare) and (indicator_value > compare_value)
                    else:
                        result = False
                else:
                    result = False
            elif operator in ['cross_below', 'crossBelow']:
                # 크로스 다운 체크
                if 'prev_' + indicator in row and compare_to and 'prev_' + compare_to in row:
                    prev_indicator = row['prev_' + indicator]
                    prev_compare = row['prev_' + compare_to]
                    if not pd.isna(prev_indicator) and not pd.isna(prev_compare):
                        result = (prev_indicator >= prev_compare) and (indicator_value < compare_value)
                    else:
                        result = False
                else:
                    result = False
            else:
                print(f"[Engine] Unknown operator: {operator}")
                result = False

            # 디버그 로그
            if result:
                print(f"[Engine] Condition matched: {indicator} {operator} {compare_to or value} (value: {indicator_value:.2f} vs {compare_value:.2f})")

            return result
        except Exception as e:
            print(f"[Engine] Error checking condition: {e}")
            return False

        return False

    def _format_condition_reason(self, condition: Dict) -> str:
        """조건을 읽기 쉬운 문자열로 변환"""
        indicator = condition.get('indicator', '')
        operator = condition.get('operator', '')
        value = condition.get('value', '')
        compare_to = condition.get('compareTo', '')

        if compare_to:
            return f"{indicator} {operator} {compare_to}"
        else:
            return f"{indicator} {operator} {value}"

    def _prepare_results(
        self,
        results: Dict[str, Any],
        strategy_id: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """결과 정리"""
        print(f"[Engine] Preparing final results for API response...")

        trades = results.get('trades', [])

        # 승률 계산
        winning_trades = [t for t in trades if t.get('type') == 'sell' and t.get('profit', 0) > 0]
        losing_trades = [t for t in trades if t.get('type') == 'sell' and t.get('profit', 0) <= 0]

        # 매도 거래가 있는 경우에만 승률 계산
        sell_trades = [t for t in trades if t.get('type') == 'sell']
        win_rate = (len(winning_trades) / len(sell_trades) * 100) if sell_trades else 0

        # 최대 손실 계산
        max_drawdown = 0
        daily_values = results.get('daily_values', [])
        if daily_values:
            peak = daily_values[0].get('total_value', results['initial_capital'])
            for dv in daily_values:
                value = dv.get('total_value', 0)
                peak = max(peak, value)
                if peak > 0:
                    drawdown = (peak - value) / peak * 100
                    max_drawdown = max(max_drawdown, drawdown)

        final_results = {
            'backtest_id': str(uuid.uuid4()),
            'strategy_id': strategy_id,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': results['initial_capital'],
            'final_capital': results['final_capital'],
            'total_return': results['total_return'],
            'total_return_rate': results['total_return_rate'],
            'win_rate': win_rate,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'max_drawdown': max_drawdown,
            'trades': trades,
            'daily_values': daily_values,
            'status': 'completed'  # 완료 상태 추가
        }

        print(f"[Engine] API Response prepared: {final_results['total_trades']} trades, {final_results['total_return_rate']:.2f}% return")

        return final_results