from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import os
from dotenv import load_dotenv
from supabase import create_client
from api.kiwoom_client import get_kiwoom_client

load_dotenv()

router = APIRouter()

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def perform_account_sync():
    """
    Core function to sync Account Balance and Portfolio from Kiwoom to Supabase.
    Can be called by API or WebSocket event.
    """
    supabase = get_supabase()
    kiwoom = get_kiwoom_client()
    
    # 1. Fetch from Kiwoom
    try:
        data = kiwoom.get_account_balance()
    except Exception as e:
        print(f"[SyncCore] Kiwoom API Error: {str(e)}")
        return {"error": str(e)}

    if isinstance(data, list):
         holdings = data
         summary = {}
    elif isinstance(data, dict):
         holdings = data.get('holdings', [])
         summary = data.get('summary', {})
    else:
         print("[SyncCore] Unknown Kiwoom API response format")
         return {"error": "Unknown format"}

    # 2. Get User ID (Robust method)
    user_id = None
    
    # [FIX] Prioritize the active frontend user identified in logs
    TARGET_USER_ID = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    
    try:
        # Check if target user exists in profiles
        res = supabase.table('profiles').select('id').eq('id', TARGET_USER_ID).execute()
        if res.data:
            user_id = TARGET_USER_ID
    except Exception:
        pass

    if not user_id:
        try:
             res = supabase.table('profiles').select('id').limit(1).execute()
             if res.data:
                 user_id = res.data[0]['id']
                 print(f"[SyncCore] Warning: Using random first user {user_id}")
        except Exception:
             pass
    
    if not user_id:
        print("[SyncCore] No User ID found to sync data to.")
        return {"error": "No User ID"}

    results = {
        "holdings_updated": 0,
        "balance_updated": False
    }

    # 3. Update Portfolio
    # First, get current DB holdings to detect deletions (sells)
    try:
        current_db_holdings = supabase.table('portfolio').select('stock_code').eq('user_id', user_id).execute()
        db_codes = set(item['stock_code'] for item in current_db_holdings.data)
        kiwoom_codes = set()
    except Exception as e:
        print(f"[SyncCore] Failed to fetch current DB holdings: {e}")
        db_codes = set()
        kiwoom_codes = set()

    for h in holdings:
        # [FIX] Strip 'A' prefix from Kiwoom stock codes (e.g. A005930 -> 005930)
        raw_code = h['stock_code']
        stock_code = raw_code[1:] if raw_code.startswith('A') else raw_code
        kiwoom_codes.add(stock_code)
        
        # Ensure stock exists in 'stocks' table
        try:
             stock_name = h.get('stock_name', 'Unknown')
             supabase.table('stocks').upsert({'code': stock_code, 'name': stock_name}).execute()
        except Exception:
             pass

        pf_data = {
            'user_id': user_id,
            'stock_code': stock_code,
            'quantity': h['quantity'],
            'avg_price': h['average_price'],
            'current_price': h['current_price'],
            'profit_loss': h['profit_loss'],
            'profit_loss_rate': h['profit_loss_rate'],
            'updated_at': 'now()'
        }
        try:
           supabase.table('portfolio').upsert(pf_data, on_conflict='user_id, stock_code').execute()
           results["holdings_updated"] += 1
        except Exception as e:
            print(f"[SyncCore] Portfolio Upsert Error: {e}")

    # Remove sold items (in DB but not in Kiwoom)
    sold_codes = db_codes - kiwoom_codes
    if sold_codes:
        print(f"[SyncCore] Detected Sold Items: {sold_codes}")
        try:
            supabase.table('portfolio').delete().eq('user_id', user_id).in_('stock_code', list(sold_codes)).execute()
        except Exception as e:
            print(f"[SyncCore] Portfolio Delete Error: {e}")

    # [IMPROVEMENT] Force Recalculate Summary from Holdings to ensure 'Net' Profit (matching HTS)
    # Kiwoom's Summary (Type 1) often returns Gross profit, while Holdings (Type 2) return Net.
    recalc_triggered = False
    if holdings:
        print("[SyncCore] Recalculating Summary Totals from Holdings (Net Profit focus)...")
        # Use sum of individual Net Profits (evltv_prft) which includes fees/taxes
        calc_total_profit = sum([h['profit_loss'] for h in holdings])
        
        # Standard totals
        calc_total_purch = sum([h['average_price'] * h['quantity'] for h in holdings])
        calc_total_eval = sum([h['current_price'] * h['quantity'] for h in holdings])
        
        if not summary: summary = {}
        
        # Overwrite with aggregated Net values
        summary['total_purchase_amount'] = calc_total_purch
        summary['total_evaluation_amount'] = calc_total_eval
        summary['total_evaluation_profit_loss'] = calc_total_profit
        
        # Update total_assets safely
        raw_assets = summary.get('total_assets', 0)
        chk_deposit = float(summary.get('withdrawable_amount', 0))
        # Reconstruct Assets = Deposit + Stock Eval
        summary['total_assets'] = chk_deposit + calc_total_eval
        
        if calc_total_purch > 0:
             summary['total_earning_rate'] = (calc_total_profit / calc_total_purch) * 100
        else:
             summary['total_earning_rate'] = 0.0
             
        recalc_triggered = True

    if summary:
        bal_data = {
            'user_id': user_id,
            'account_no': summary.get('account_no', '8112-6100'),
            'total_assets': summary.get('total_assets', 0),
            'available_cash': summary.get('withdrawable_amount', 0),
            'total_evaluation': summary.get('total_evaluation_amount', 0),
            'total_profit_loss': summary.get('total_evaluation_profit_loss', 0),
            'total_profit_loss_rate': summary.get('total_earning_rate', 0),
            'invested_amount': summary.get('total_purchase_amount', 0),
            'total_buy_amount': summary.get('total_purchase_amount', 0),
            'updated_at': 'now()'
        }
        try:
            supabase.table('account_balance').upsert(bal_data, on_conflict='user_id').execute()
            results["balance_updated"] = True
        except Exception as e:
            print(f"[SyncCore] Balance Upsert Error: {e}")
            
    # Add Debug Info to Response
    results["debug"] = {
        "recalc_triggered": recalc_triggered,
        "holdings_count": len(holdings),
        "user_id": user_id,
        "final_summary": summary,
        "sold_items": list(sold_codes) if 'sold_codes' in locals() else []
    }
            
    return results

@router.post("/account")
async def sync_account_balance():
    """
    Syncs Account Balance and Portfolio from Kiwoom to Supabase.
    """
    print("[SyncAPI] Starting Account Sync via API...")
    result = perform_account_sync()
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result
