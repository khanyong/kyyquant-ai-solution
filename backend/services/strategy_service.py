
from typing import List, Dict, Any, Optional
import os
import asyncio
import math
import pandas as pd
from datetime import datetime
from supabase import create_client
from backtest.engine import BacktestEngine
from services.notification_service import NotificationService

class StrategyService:
    def __init__(self):
        self.supabase = self._init_supabase()
        self.notification_service = NotificationService()
        self.engine = BacktestEngine()
        
    def _init_supabase(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
        if not url or not key:
            print("[StrategyService] Supabase credentials missing!")
            return None
        return create_client(url, key)

    async def verify_all_active_strategies(self) -> List[Dict]:
        """
        Verify all active strategies and send notifications if signals differ from previous state.
        """
        if not self.supabase:
            return []

        results = []
        try:
            print("[StrategyService] Starting verification cycle...")
            
            # 1. Fetch active strategies with universe
            rpc_response = self.supabase.rpc('get_active_strategies_with_universe', {}).execute()
            strategies_data = rpc_response.data
            
            if not strategies_data:
                print("[StrategyService] No active strategies found.")
                return []

            # 2. Prepare tasks
            tasks = []
            sem = asyncio.Semaphore(20) # Limit concurrency

            for item in strategies_data:
                strategy_name = item.get('strategy_name', 'Unknown')
                
                # Fetch full config
                try:
                    full_strategy_resp = self.supabase.table('strategies').select('*').eq('id', item['strategy_id']).single().execute()
                    full_strategy = full_strategy_resp.data
                    strategy_config = full_strategy.get('config') or full_strategy
                except Exception as e:
                    print(f"[StrategyService] Failed to fetch config for {strategy_name}: {e}")
                    continue

                # Collect target stocks
                target_stocks = []
                # Top-level
                f_stocks_top = item.get('filtered_stocks')
                if f_stocks_top:
                    for s in f_stocks_top:
                        if isinstance(s, dict) and 'stock_code' in s: target_stocks.append(s['stock_code'])
                        elif isinstance(s, str): target_stocks.append(s)
                
                # Universe-level
                if item.get('universes'):
                    for u in item['universes']:
                        f_stocks = u.get('filtered_stocks')
                        if f_stocks:
                            for s in f_stocks:
                                if isinstance(s, dict) and 'stock_code' in s: target_stocks.append(s['stock_code'])
                                elif isinstance(s, str): target_stocks.append(s)

                target_stocks = list(set(target_stocks))
                
                for stock_code in target_stocks:
                    tasks.append(self._process_single_stock(sem, stock_code, strategy_name, strategy_config, item['strategy_id']))

            print(f"[StrategyService] Processing {len(tasks)} verification tasks...")
            if tasks:
                results_raw = await asyncio.gather(*tasks)
                results = [r for r in results_raw if r is not None]

            print(f"[StrategyService] Cycle completed. {len(results)} results.")
            return results

        except Exception as e:
            print(f"[StrategyService] Verification cycle failed: {e}")
            return []

    async def _process_single_stock(self, sem, stock_code, strategy_name, strategy_config, strategy_id) -> Optional[Dict]:
        async with sem:
            try:
                # Data Fetching (Threaded)
                def fetch_data():
                    p = self.supabase.table('kw_price_daily').select('trade_date,open,high,low,close,volume').eq('stock_code', stock_code).order('trade_date', desc=False).limit(200).execute()
                    c = self.supabase.table('kw_price_current').select('*').eq('stock_code', stock_code).limit(1).execute()
                    return p, c
                
                price_response, curr_resp = await asyncio.to_thread(fetch_data)

                if not price_response.data or len(price_response.data) < 20:
                    return None

                # DataFrame Prep
                df = pd.DataFrame(price_response.data)
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df.set_index('trade_date', inplace=True)
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # Merge Current Price
                current_price = 0.0
                stock_name = stock_code
                if curr_resp.data:
                    row = curr_resp.data[0]
                    current_price = float(row.get('current_price') or 0)
                    stock_name = row.get('stock_name', stock_code)
                    
                    if current_price > 0:
                        now = datetime.now()
                        last_date = df.index[-1]
                        if last_date.date() < now.date():
                            new_row = pd.DataFrame([{'open': current_price, 'high': current_price, 'low': current_price, 'close': current_price, 'volume': 0}], index=[pd.Timestamp(now)])
                            df = pd.concat([df, new_row])
                        elif last_date.date() == now.date():
                            df.iloc[-1, df.columns.get_loc('close')] = current_price

                if current_price <= 0:
                    if not df.empty:
                        current_price = df.iloc[-1]['close']
                    else:
                        return None

                # Evaluation
                eval_result = await self.engine.evaluate_snapshot(stock_code, df, strategy_config)
                signal = eval_result.get('signal', 'hold').upper()
                if signal == 'CONFLICT': signal = 'HOLD'
                score = eval_result.get('score', 0)
                reasons = eval_result.get('reasons', [])
                indicators = eval_result.get('indicators', {})

                # NOTIFICATION LOGIC
                if signal in ['BUY', 'SELL']:
                    await self._handle_signal_notification(
                        strategy_name, stock_code, stock_name, signal, current_price, score, strategy_id, reasons, indicators
                    )

                return {
                    'strategy_name': strategy_name,
                    'stock_code': stock_code,
                    'signal': signal,
                    'score': score
                }

            except Exception as e:
                # print(f"[StrategyService] Error {stock_code}: {e}")
                return None

    async def _handle_signal_notification(self, strategy_name, stock_code, stock_name, signal, price, score, strategy_id, reasons, indicators):
        """
        Send notification and save to DB
        """
        # 1. Save to DB (trading_signals) - Avoid Duplicate (Optional)
        should_notify = True
        try:
            # Check last signal for this stock/strategy today
            today_start = datetime.now().strftime('%Y-%m-%dT00:00:00')
            last_sig_resp = self.supabase.table('trading_signals') \
                .select('created_at, signal_type') \
                .eq('strategy_id', strategy_id) \
                .eq('stock_code', stock_code) \
                .gte('created_at', today_start) \
                .order('created_at', desc=True) \
                .limit(1) \
                .execute()
                
            if last_sig_resp.data:
                last_sig = last_sig_resp.data[0]
                if last_sig['signal_type'] == signal.lower():
                    should_notify = False

            if should_notify:
                signal_record = {
                    'strategy_id': strategy_id,
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'signal_type': signal.lower(),
                    'signal_strength': score,
                    'current_price': price,
                    'strategy_name': strategy_name,
                    'conditions_met': {'reasons': reasons, 'indicators': indicators}, 
                    'status': 'new',
                    'created_at': datetime.now().isoformat()
                }
                self.supabase.table('trading_signals').insert(signal_record).execute()
                
                # 2. Send Telegram (Rich Format)
                emoji = "🔴" if signal == "BUY" else "🔵"
                
                # Format Indicators (Take top 5 or specific ones)
                # Filter out internal/temp columns if possible, but for now show relevant ones
                indicator_str = ""
                if indicators:
                    # Sort to make it deterministic
                    sorted_inds = sorted(indicators.items())
                    # Format: key=value
                    # Only show first 5 to avoid spam, or filtered list
                    count = 0
                    for k, v in sorted_inds:
                        if isinstance(v, float):
                            val_str = f"{v:.2f}"
                        else:
                            val_str = str(v)
                        indicator_str += f"- {k}: {val_str}\n"
                        count += 1
                        if count >= 8: # Limit lines
                            indicator_str += "... (more)\n"
                            break

                reason_str = ", ".join(reasons) if reasons else "Condition Met"

                msg = (
                    f"{emoji} <b>{signal} SIGNAL</b>\n"
                    f"<b>Strategy</b>: {strategy_name}\n"
                    f"<b>Stock</b>: {stock_name} ({stock_code})\n"
                    f"<b>Price</b>: {price:,} KRW\n"
                    f"<b>Score</b>: {score:.0f}\n"
                    f"<b>Reason</b>: {reason_str}\n\n"
                    f"<b>Key Indicators</b>:\n"
                    f"<pre>{indicator_str}</pre>"
                )
                await self.notification_service.send_telegram_message(msg, level="info")
                print(f"[StrategyService] Notification Sent: {stock_code} {signal}")

        except Exception as e:
            print(f"[StrategyService] Notification/DB Error: {e}")
