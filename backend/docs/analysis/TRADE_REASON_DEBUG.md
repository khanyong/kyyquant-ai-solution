# Trade Reason Debug Verification

## Changes Applied

### 1. Backend Engine (engine.py)
- **Staged Buy Trades** (lines 355-370): Added Korean formatted reasons
  ```python
  buy_reason = f"매수 {stage_num}단계 ({buy_reason_detail})"
  ```

- **Regular Buy Trades** (lines 417-430): Already uses `buy_reason` from signal
  ```python
  buy_reason = row.get('buy_reason', 'Signal')
  ```

- **All Sell Trades** (lines 276-292): Uses `exit_reason` from profit/loss logic
  ```python
  reason = exit_reason  # "Target profit 4%", "Stop loss -6%", etc
  ```

### 2. API Endpoint (backtest.py)
- Added debug logging (lines 145-150):
  ```python
  print(f"[API DEBUG] Sample trade keys: {list(sample_trade.keys())}")
  print(f"[API DEBUG] Sample trade reason: {sample_trade.get('reason', 'MISSING')}")
  ```

### 3. Frontend (BacktestResultViewer.tsx)
- Updated to check both `reason` and `signal_reason` fields (line 446)

## Next Steps

1. **Restart NAS Backend**
   ```bash
   docker restart auto_stock_backend
   ```

2. **Run New Backtest**
   - Use MACD+RSI staged strategy (NOT Golden Cross template)
   - Weekly data (210 stocks should work)
   - Date range: 2024-01-01 to 2024-12-31

3. **Verify Logs**
   - Check Docker logs: `docker logs auto_stock_backend`
   - Look for: `[Engine] Recording buy trade:` and `[Engine] Recording sell trade:`
   - Verify: `[API DEBUG] Sample trade reason:` shows actual reason text

4. **Frontend Verification**
   - Check if "거래 사유" column shows reasons
   - If still blank, investigate API response transformation

## Expected Reason Formats

- **Staged Buy**: "매수 1단계 (MACD상승/RSI과매도)"
- **Regular Buy**: "Golden Cross" or "MACD상승/RSI과매도"
- **Profit Target**: "Target profit 4%" or "Target profit 7%"
- **Stop Loss**: "Stop loss -6%"
- **Signal Sell**: Condition-based reason from sell conditions

## Verification Status

✅ Code paths verified - all trades generate `reason` field
✅ Debug logging added
⏳ Waiting for backend restart
⏳ Waiting for new backtest execution
