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

@router.post("/account")
async def sync_account_balance():
    """
    Syncs Account Balance and Portfolio from Kiwoom to Supabase.
    """
    supabase = get_supabase()
    kiwoom = get_kiwoom_client()
    print("[SyncAPI] Starting Account Sync...")
    
    # 1. Fetch from Kiwoom
    try:
        data = kiwoom.get_account_balance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kiwoom API Error: {str(e)}")

    if isinstance(data, list):
         holdings = data
         summary = {}
    elif isinstance(data, dict):
         holdings = data.get('holdings', [])
         summary = data.get('summary', {})
    else:
         raise HTTPException(status_code=500, detail="Unknown Kiwoom API response format")

    # 2. Get User ID (Robust method)
    user_id = None
    
    # [FIX] Prioritize the active frontend user identified in logs
    TARGET_USER_ID = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    
    try:
        # Check if target user exists in profiles
        res = supabase.table('profiles').select('id').eq('id', TARGET_USER_ID).execute()
        if res.data:
            user_id = TARGET_USER_ID
            print(f"[SyncAPI] Using Target User ID: {user_id}")
    except Exception:
        pass

    if not user_id:
        try:
             res = supabase.table('profiles').select('id').limit(1).execute()
             if res.data:
                 user_id = res.data[0]['id']
                 print(f"[SyncAPI] Warning: Using random first user {user_id}")
        except Exception:
             pass
    
    if not user_id:
        raise HTTPException(status_code=404, detail="No User ID found to sync data to.")

    results = {
        "holdings_updated": 0,
        "balance_updated": False
    }

    # 3. Update Portfolio
    for h in holdings:
        # [FIX] Strip 'A' prefix from Kiwoom stock codes (e.g. A005930 -> 005930)
        raw_code = h['stock_code']
        stock_code = raw_code[1:] if raw_code.startswith('A') else raw_code
        
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
            print(f"[SyncAPI] Portfolio Upsert Error: {e}")

    # 4. Update Balance
    recalc_triggered = False
    if summary or holdings:
        # [ROBUST] Recalculate if 'total_purchase_amount' is 0
        pass

    if summary:
        bal_data = {
            'user_id': user_id,
            'account_no': summary.get('account_no', '8112-6100'), # Default to screenshot acc no if missing
            'total_assets': summary.get('total_assets', 0),
            'available_cash': summary.get('withdrawable_amount', 0),
            'total_evaluation': summary.get('total_evaluation_amount', 0),
            recalc_triggered = True
            print("[SyncAPI] Recalculating Summary from Holdings...")
            calc_total_purch = sum([h['average_price'] * h['quantity'] for h in holdings])
            calc_total_eval = sum([h['current_price'] * h['quantity'] for h in holdings])
            calc_total_profit = calc_total_eval - calc_total_purch
            
            if not summary: summary = {}
            summary['total_purchase_amount'] = calc_total_purch
            summary['total_evaluation_amount'] = calc_total_eval
            summary['total_evaluation_profit_loss'] = calc_total_profit
            
            # Update total_assets if it looks invalid (0)
            raw_assets = summary.get('total_assets', 0)
            try:
                if float(raw_assets) == 0:
                     summary['total_assets'] = float(summary.get('withdrawable_amount', 0)) + calc_total_eval
            except:
                 pass
            
            if calc_total_purch > 0:
                 summary['total_earning_rate'] = (calc_total_profit / calc_total_purch) * 100

    if summary:
        bal_data = {
            'user_id': user_id,
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
            print(f"[SyncAPI] Balance Upsert Error: {e}")
            
    # Add Debug Info to Response
    results["debug"] = {
        "recalc_triggered": recalc_triggered,
        "holdings_count": len(holdings),
        "user_id": user_id,
        "final_summary": summary
    }
            
    return results
