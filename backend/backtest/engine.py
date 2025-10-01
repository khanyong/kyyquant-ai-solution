"""
백테스트 엔진 핵심 모듈
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
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
            df = await self._calculate_indicators(df, strategy_config, stock_code)

            # Preflight 검증 (첫 종목에서만 수행)
            if stock_code == list(price_data.keys())[0]:
                print(f"[Engine] Step 1.5: Validating strategy conditions...")
                validation_result = self._validate_strategy_conditions(
                    strategy_config,
                    list(df.columns)
                )

                if not validation_result['valid']:
                    raise ValueError(
                        f"Strategy validation failed:\n" +
                        "\n".join(validation_result['errors'])
                    )

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
                    # 슬리피지 적용 (매도 시 불리한 가격)
                    sell_price = price * (1 - slippage)
                    sell_amount = sell_quantity * sell_price
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
                        'price': sell_price,
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
                    position_size = strategy_config.get('position_size', 0.3)  # 기본값 30%
                    max_buy_amount = capital * position_size
                    # 슬리피지 적용 (매수 시 불리한 가격)
                    buy_price = price * (1 + slippage)
                    buy_quantity = int(max_buy_amount / buy_price)

                    if buy_quantity > 0:
                        buy_amount = buy_quantity * buy_price
                        commission_fee = buy_amount * commission

                        # 거래 기록
                        trades.append({
                            'trade_id': str(uuid.uuid4()),
                            'date': date,
                            'stock_code': stock_code,
                            'type': 'buy',
                            'quantity': buy_quantity,
                            'price': buy_price,
                            'amount': buy_amount,
                            'commission': commission_fee,
                            'reason': row.get('buy_reason', 'Signal')
                        })

                        # 포지션 추가
                        positions[stock_code] = {
                            'quantity': buy_quantity,
                            'avg_price': buy_price,
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

    def _validate_strategy_conditions(
        self,
        strategy_config: Dict[str, Any],
        available_columns: List[str]
    ) -> Dict[str, Any]:
        """
        백테스트 실행 전 전략 조건 검증 (Preflight Check)

        Args:
            strategy_config: 전략 설정
            available_columns: 사용 가능한 DataFrame 컬럼 목록

        Returns:
            검증 결과 딕셔너리 {'valid': bool, 'errors': List[str], 'warnings': List[str]}
        """
        errors = []
        warnings = []

        # 조건에서 사용하는 모든 지표 이름 추출
        buy_conditions = strategy_config.get('buyConditions', [])
        sell_conditions = strategy_config.get('sellConditions', [])

        all_conditions = buy_conditions + sell_conditions

        # 임시 row 생성 (컬럼명 해석 테스트용)
        temp_row = pd.Series(index=available_columns)

        for idx, condition in enumerate(all_conditions):
            indicator = condition.get('indicator')
            compare_to = condition.get('compareTo')
            value = condition.get('value')

            cond_type = 'buy' if condition in buy_conditions else 'sell'

            # indicator 검증
            if indicator:
                resolved = self._resolve_indicator_name(temp_row, indicator)
                if not resolved:
                    errors.append(
                        f"{cond_type.upper()} condition #{idx+1}: Indicator '{indicator}' not found. "
                        f"Available: {', '.join(available_columns)}"
                    )

            # compareTo 검증
            if compare_to and not isinstance(compare_to, (int, float)):
                # 숫자가 아니면 컬럼명이어야 함
                try:
                    float(compare_to)
                except:
                    resolved = self._resolve_indicator_name(temp_row, compare_to)
                    if not resolved:
                        errors.append(
                            f"{cond_type.upper()} condition #{idx+1}: compareTo '{compare_to}' not found"
                        )

        # 결과
        is_valid = len(errors) == 0

        if not is_valid:
            print("[Engine] [ERROR] Strategy validation FAILED:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("[Engine] [OK] Strategy validation PASSED")

        if warnings:
            print("[Engine] [WARNING] Warnings:")
            for warning in warnings:
                print(f"  - {warning}")

        return {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }

    async def _calculate_indicators(
        self,
        df: pd.DataFrame,
        strategy_config: Dict[str, Any],
        stock_code: Optional[str] = None
    ) -> pd.DataFrame:
        """지표 계산"""
        indicators = strategy_config.get('indicators', [])

        print(f"[Engine] Calculating {len(indicators)} indicators for {stock_code}")
        print(f"[Engine] Initial columns: {list(df.columns)}")

        for idx, indicator in enumerate(indicators):
            try:
                print(f"[Engine] Calculating indicator {idx+1}/{len(indicators)}: {indicator}")

                # calculate 메서드는 IndicatorResult를 반환하므로 이를 처리
                # stock_code를 전달하여 캐시 충돌 방지
                result = self.indicator_calculator.calculate(df, indicator, stock_code=stock_code)

                # IndicatorResult의 columns 속성에서 데이터를 가져와 DataFrame에 추가
                if hasattr(result, 'columns'):
                    for col_name, col_data in result.columns.items():
                        df[col_name] = col_data
                        print(f"[Engine] Added column: {col_name}")

            except Exception as e:
                print(f"[Engine] Error calculating indicator {indicator.get('name', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                # 에러가 발생해도 계속 진행

        # 추가 컬럼은 Supabase 지표 정의를 통해서만 계산
        # 하드코딩 금지 - ENFORCE_DB_INDICATORS 정책 준수

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

    def _resolve_indicator_name(self, row: pd.Series, indicator_name: str) -> Optional[str]:
        """
        지표 이름을 실제 DataFrame 컬럼명으로 해석

        Args:
            row: DataFrame row
            indicator_name: 조건에서 사용하는 지표 이름

        Returns:
            실제 컬럼명 또는 None
        """
        import re

        # 1. 직접 매칭
        if indicator_name in row.index:
            return indicator_name

        # 2. MACD 계열 접미사 제거 (macd_12_26 -> macd)
        macd_pattern = r'^(macd(?:_signal|_hist|_line)?)(?:_\d+){1,3}$'
        match = re.match(macd_pattern, indicator_name)
        if match:
            base_name = match.group(1)
            # macd_line -> macd 매핑
            if base_name == 'macd_line':
                base_name = 'macd'
            if base_name in row.index:
                return base_name

        # 3. RSI 접미사 제거 (rsi_14 -> rsi)
        if indicator_name.startswith('rsi_') and 'rsi' in row.index:
            return 'rsi'

        # 4. BB 접미사 제거 (bb_upper_20_2 -> bb_upper)
        bb_pattern = r'^(bb_(?:upper|middle|lower))(?:_\d+){0,2}$'
        match = re.match(bb_pattern, indicator_name)
        if match:
            base_name = match.group(1)
            if base_name in row.index:
                return base_name

        # 5. SMA/EMA/MA 접미사 처리는 주의 필요 (충돌 가능)
        # sma_5, sma_20이 모두 별도 컬럼으로 존재할 수 있음
        # 따라서 정확한 이름이 없을 때만 base name 시도
        ma_pattern = r'^((?:sma|ema|wma|ma))_(\d+)$'
        match = re.match(ma_pattern, indicator_name)
        if match:
            # 정확한 컬럼명이 있는지 먼저 확인
            if indicator_name in row.index:
                return indicator_name
            # 없으면 숫자 없는 base name 시도
            base_name = match.group(1)
            if base_name in row.index:
                return base_name

        return None

    def _resolve_operand(self, row: pd.Series, operand: Any) -> Tuple[str, Any]:
        """
        피연산자를 해석 (상수 vs 컬럼)

        Returns:
            (type, value) - type은 'const' 또는 'column'
        """
        import re

        # 숫자 타입
        if isinstance(operand, (int, float)):
            return ('const', float(operand))

        # 문자열
        if isinstance(operand, str):
            s = operand.strip()

            # 숫자 문자열 ("0", "30", "1.5")
            if re.fullmatch(r'-?\d+(\.\d+)?', s):
                return ('const', float(s))

            # 컬럼명 해석
            resolved_name = self._resolve_indicator_name(row, s)
            if resolved_name:
                return ('column', resolved_name)

            return ('missing', s)

        return ('unknown', operand)

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

        # 지표 이름 해석
        resolved_indicator = self._resolve_indicator_name(row, indicator)
        if not resolved_indicator:
            print(f"[Engine] Warning: Indicator '{indicator}' not found in row")
            print(f"[Engine] Available columns: {list(row.index)}")
            return False

        indicator_value = row[resolved_indicator]

        # NaN 체크
        if pd.isna(indicator_value):
            return False

        # 비교 대상 값 결정
        if compare_to:
            operand_type, operand_value = self._resolve_operand(row, compare_to)
            if operand_type == 'const':
                compare_value = operand_value
            elif operand_type == 'column':
                compare_value = row[operand_value]
                if pd.isna(compare_value):
                    return False
            else:
                print(f"[Engine] Warning: Cannot resolve compareTo '{compare_to}'")
                return False
        elif value is not None:
            operand_type, operand_value = self._resolve_operand(row, value)
            if operand_type == 'const':
                compare_value = operand_value
            elif operand_type == 'column':
                compare_value = row[operand_value]
                if pd.isna(compare_value):
                    return False
            else:
                print(f"[Engine] Warning: Cannot resolve value '{value}'")
                return False
        else:
            compare_value = 0

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
                prev_indicator_name = 'prev_' + resolved_indicator
                if compare_to:
                    compare_type, compare_col = self._resolve_operand(row, compare_to)
                    if compare_type == 'column':
                        prev_compare_name = 'prev_' + compare_col
                        if prev_indicator_name in row and prev_compare_name in row:
                            prev_indicator = row[prev_indicator_name]
                            prev_compare = row[prev_compare_name]
                            if not pd.isna(prev_indicator) and not pd.isna(prev_compare):
                                result = (prev_indicator <= prev_compare) and (indicator_value > compare_value)
                            else:
                                result = False
                        else:
                            result = False
                    else:
                        # 숫자와 cross는 의미 없음
                        result = False
                else:
                    result = False
            elif operator in ['cross_below', 'crossBelow']:
                # 크로스 다운 체크
                prev_indicator_name = 'prev_' + resolved_indicator
                if compare_to:
                    compare_type, compare_col = self._resolve_operand(row, compare_to)
                    if compare_type == 'column':
                        prev_compare_name = 'prev_' + compare_col
                        if prev_indicator_name in row and prev_compare_name in row:
                            prev_indicator = row[prev_indicator_name]
                            prev_compare = row[prev_compare_name]
                            if not pd.isna(prev_indicator) and not pd.isna(prev_compare):
                                result = (prev_indicator >= prev_compare) and (indicator_value < compare_value)
                            else:
                                result = False
                        else:
                            result = False
                    else:
                        result = False
                else:
                    result = False
            else:
                print(f"[Engine] Unknown operator: {operator}")
                result = False

            # 디버그 로그
            if result:
                print(f"[Engine] Condition matched: {resolved_indicator} {operator} {compare_to or value} (value: {indicator_value:.2f} vs {compare_value:.2f})")

            return result
        except Exception as e:
            print(f"[Engine] Error checking condition: {e}")
            import traceback
            traceback.print_exc()
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