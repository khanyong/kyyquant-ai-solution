"""
백테스트 엔진 강제청산 패치
마지막 봉에서 미청산 포지션 정리
"""

class BacktestEngineWithForceClose:
    """강제청산 기능이 추가된 백테스트 엔진"""

    async def run(self, data: pd.DataFrame, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """백테스트 실행 - 마지막에 강제청산 추가"""

        # ... 기존 백테스트 로직 ...

        position = None
        trades = []

        for i in range(len(data)):
            row = data.iloc[i]

            # 기존 매수/매도 로직
            if row['signal'] == 1 and position is None:
                # 매수
                position = {
                    'entry_price': row['close'],
                    'entry_date': row['date'],
                    'quantity': int(self.capital * 0.1 / row['close'])
                }
                trades.append({
                    'date': row['date'],
                    'action': 'buy',
                    'price': row['close'],
                    'quantity': position['quantity']
                })

            elif row['signal'] == -1 and position is not None:
                # 매도
                profit = (row['close'] - position['entry_price']) * position['quantity']
                profit_pct = ((row['close'] - position['entry_price']) / position['entry_price']) * 100

                trades.append({
                    'date': row['date'],
                    'action': 'sell',
                    'price': row['close'],
                    'quantity': position['quantity'],
                    'profit': profit,
                    'profit_pct': profit_pct
                })

                position = None

        # ===== 강제청산 추가 =====
        if position is not None and len(data) > 0:
            # 마지막 봉에서 미청산 포지션 정리
            last_row = data.iloc[-1]
            profit = (last_row['close'] - position['entry_price']) * position['quantity']
            profit_pct = ((last_row['close'] - position['entry_price']) / position['entry_price']) * 100

            trades.append({
                'date': last_row['date'],
                'action': 'sell',
                'price': last_row['close'],
                'quantity': position['quantity'],
                'profit': profit,
                'profit_pct': profit_pct,
                'note': 'FORCE_CLOSE'  # 강제청산 표시
            })

            print(f"[강제청산] {last_row['date']}: {last_row['close']:.0f}원 (수익률: {profit_pct:.2f}%)")
            position = None

        # 결과 반환
        return {
            'total_trades': len(trades),
            'buy_count': len([t for t in trades if t['action'] == 'buy']),
            'sell_count': len([t for t in trades if t['action'] == 'sell']),
            'trades': trades
        }


# backtest_engine_advanced.py의 run 메서드 끝부분에 추가할 코드:
"""
# 백테스트 종료 시 미청산 포지션 강제청산
if self.position is not None and not df.empty:
    last_price = df.iloc[-1]['close']
    last_date = df.iloc[-1]['date'] if 'date' in df.columns else df.index[-1]

    # 수익률 계산
    profit_pct = ((last_price - self.position['entry_price']) / self.position['entry_price']) * 100

    # 거래 기록
    self.trades.append({
        'date': last_date,
        'type': 'sell',
        'price': last_price,
        'shares': self.position['shares'],
        'amount': last_price * self.position['shares'],
        'profit': (last_price - self.position['entry_price']) * self.position['shares'],
        'profit_pct': profit_pct,
        'commission': last_price * self.position['shares'] * self.commission_rate,
        'reason': 'FORCE_CLOSE_END_OF_BACKTEST'
    })

    print(f"[강제청산] 백테스트 종료 - 포지션 정리: {profit_pct:.2f}%")
    self.position = None
"""