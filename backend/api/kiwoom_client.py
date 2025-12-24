"""
키움증권 REST API 클라이언트
실시간 시세 조회 및 주문 기능
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class KiwoomAPIClient:
    """키움증권 REST API 클라이언트"""

    def __init__(self):
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO', '')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

        # 환경 변수 확인
        if not self.app_key or not self.app_secret:
            print(f"[KiwoomAPI] WARNING: Missing credentials - APP_KEY: {bool(self.app_key)}, APP_SECRET: {bool(self.app_secret)}")
        else:
            print(f"[KiwoomAPI] Credentials loaded - APP_KEY: {self.app_key[:10]}..., MODE: {'DEMO' if self.is_demo else 'REAL'}")

        # API URL 설정 (모의투자/실전투자 구분)
        if self.is_demo:
            self.base_url = "https://mockapi.kiwoom.com"
        else:
            self.base_url = "https://api.kiwoom.com"
            
        print(f"[KiwoomAPI] Base URL set to: {self.base_url}")

        self.access_token = None
        self.token_expires_at = None

    def _get_access_token(self) -> str:
        """OAuth 2.0 액세스 토큰 발급 (TokenManager 사용)"""
        from .token_manager import get_token_manager
        return get_token_manager(self.is_demo).get_token()

    def get_current_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """실시간 현재가 조회 (ka10001)"""
        try:
            token = self._get_access_token()
            url = f"{self.base_url}/api/dostk/stkinfo"
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "api-id": "ka10001",
                "cont-yn": "N",
                "next-key": ""
            }
            data = {"stk_cd": stock_code}

            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
            response.raise_for_status()
            result = response.json()

            if result.get('return_code') != '0' and result.get('return_code') != 0:
                 return None

            return {
                'stock_code': stock_code,
                'current_price': float(result.get('cur_prc', 0)),
                'stock_name': result.get('stk_nm'),
                'open': float(result.get('opn_prc', 0)),
                'high': float(result.get('hg_prc', 0)),
                'low': float(result.get('lw_prc', 0)),
                'change_rate': float(result.get('fluc_rt', 0)) # 등락률
            }

        except Exception as e:
            print(f"[KiwoomAPI] Price fetch failed: {e}")
            return None

    def _safe_float(self, value):
        if not value: return 0.0
        try: return float(value)
        except: return 0.0

    def _safe_int(self, value):
        if not value: return 0
        try: return int(value)
        except: return 0

    def get_account_balance(self) -> list:
        """계좌 잔고 조회 (kt00018)"""
        from .token_manager import get_token_manager
        
        # Retry loop for Token Expiry (8005 error)
        for attempt in range(2):
            try:
                token = self._get_access_token()
                url = f"{self.base_url}/api/dostk/acnt"
                headers = {
                    "Content-Type": "application/json;charset=UTF-8",
                    "authorization": f"Bearer {token}",
                    "api-id": "kt00018",
                    "cont-yn": "N",
                    "next-key": ""
                }
                
                # Step 1: Fetch Summary
                data_summary = {
                    "qry_tp": "1",          
                    "dmst_stex_tp": "KRX",
                    "acnt_no": self.account_no if self.account_no else ""
                }
                
                summary = {}
                res_sum = requests.post(url, headers=headers, data=json.dumps(data_summary), timeout=10)
                # Note: Kiwoom might return 200 even with error, so checks below are key
                if res_sum.status_code == 401 or res_sum.status_code == 400:
                     if attempt == 0:
                         print(f"[KiwoomAPI] HTTP {res_sum.status_code}. Invalidating token...")
                         get_token_manager(self.is_demo).invalidate_token()
                         continue

                result_sum = res_sum.json()
                
                # Check for Token Error (8005)
                if '8005' in str(result_sum.get('return_msg', '')):
                     if attempt == 0:
                         print(f"[KiwoomAPI] Token Error 8005 detected. Refreshing token...")
                         get_token_manager(self.is_demo).invalidate_token()
                         continue

                if result_sum.get('return_code') == 0 or result_sum.get('return_code') == '0':
                    summary = {
                        'total_purchase_amount': float(result_sum.get('tot_pchs_amt', 0)),
                        'total_evaluation_amount': float(result_sum.get('tot_evlu_amt', 0)),
                        'total_evaluation_profit_loss': float(result_sum.get('evlu_pfls_smtl_amt', 0)), 
                        'total_earning_rate': float(result_sum.get('tot_evlu_pfls_rt', 0)),
                        'total_assets': float(result_sum.get('tot_asst_amt', 0)), 
                        'deposit': float(result_sum.get('dnca_tot_amt', 0)),
                        'withdrawable_amount': float(result_sum.get('pchs_psbl_amt', 0)) or float(result_sum.get('dnca_tot_amt', 0)) 
                    }
                else:
                    print(f"[KiwoomAPI] Balance Summary fetch error: {result_sum.get('return_msg')}")

                # Step 2: Fetch Holdings (qry_tp=2)
                data_detail = {
                    "qry_tp": "2",          
                    "dmst_stex_tp": "KRX",
                    "acnt_no": self.account_no if self.account_no else ""
                }
                
                holdings = []
                res_det = requests.post(url, headers=headers, data=json.dumps(data_detail), timeout=10)
                if res_det.status_code == 401 or res_det.status_code == 400:
                     if attempt == 0:
                         print(f"[KiwoomAPI] HTTP {res_det.status_code}. Invalidating token...")
                         get_token_manager(self.is_demo).invalidate_token()
                         continue
                         
                result_det = res_det.json()
                
                if '8005' in str(result_det.get('return_msg', '')):
                     if attempt == 0:
                         print(f"[KiwoomAPI] Token Error 8005 detected in Detail. Refreshing token...")
                         get_token_manager(self.is_demo).invalidate_token()
                         continue

                if result_det.get('return_code') == 0 or result_det.get('return_code') == '0':
                    for item in result_det.get('acnt_evlt_remn_indv_tot', []):
                         avg_price = self._safe_float(item.get('pur_pric'))
                         if avg_price == 0:
                             avg_price = self._safe_float(item.get('buy_avg_prc'))
                             
                         raw_code = item.get('stk_cd', '')
                         stock_code = raw_code[1:] if raw_code.startswith('A') else raw_code
                             
                         holdings.append({
                            'stock_code': stock_code,
                            'stock_name': item.get('stk_nm'),
                            'quantity': self._safe_int(item.get('hldg_qty')),
                            'purchase_price': self._safe_float(item.get('pur_pric')),
                            'average_price': avg_price,
                            'current_price': self._safe_float(item.get('cur_prc')),
                            'evaluation_amount': self._safe_float(item.get('evlt_amt')),
                            'profit_loss_amount': self._safe_float(item.get('evlt_pfls_amt')),
                            'earning_rate': self._safe_float(item.get('pft_rt'))
                         })
                else:
                    print(f"[KiwoomAPI] Balance Detail fetch error: {result_det.get('return_msg')}")
            
                # [FIX] Recalculate Summary if API returns 0
                if holdings:
                    calc_total_purch = sum([h['average_price'] * h['quantity'] for h in holdings])
                    calc_total_eval = sum([h['current_price'] * h['quantity'] for h in holdings])
                    calc_total_profit = calc_total_eval - calc_total_purch
                    
                    if summary.get('total_purchase_amount', 0) == 0: summary['total_purchase_amount'] = calc_total_purch
                    if summary.get('total_evaluation_amount', 0) == 0: summary['total_evaluation_amount'] = calc_total_eval
                    if summary.get('total_evaluation_profit_loss', 0) == 0: summary['total_evaluation_profit_loss'] = calc_total_profit
                    if summary.get('total_assets', 0) == 0: summary['total_assets'] = summary.get('deposit', 0) + calc_total_eval
                    if summary.get('total_purchase_amount', 0) > 0:
                         summary['total_earning_rate'] = (summary['total_evaluation_profit_loss'] / summary['total_purchase_amount']) * 100

                return {'account_no': self.account_no, 'summary': summary, 'holdings': holdings}

            except Exception as e:
                if attempt == 0:
                    print(f"[KiwoomAPI] Exception {e}. Retrying with fresh token...")
                    get_token_manager(self.is_demo).invalidate_token()
                    continue
                import sys
                print(f"[KiwoomAPI] Balance fetch failed: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                return []
        
        return []

    def _fetch_account_password(self) -> str:
        """Fetch account password from Env or Supabase"""
        # 1. Try Environment Variable
        pw = os.getenv('KIWOOM_ACCOUNT_PW')
        if pw:
            return pw

        # 2. Try Supabase
        sb_url = os.getenv('SUPABASE_URL') or os.getenv('VITE_SUPABASE_URL')
        sb_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('VITE_SUPABASE_ANON_KEY')
        
        if sb_url and sb_key:
            try:
                headers = {
                    "apikey": sb_key,
                    "Authorization": f"Bearer {sb_key}"
                }
                # Query user_api_keys table
                resp = requests.get(
                    f"{sb_url}/rest/v1/user_api_keys",
                    headers=headers,
                    params={
                        "select": "encrypted_value",
                        "key_type": "eq.account_password",
                        "limit": "1"
                    },
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data and len(data) > 0:
                        print("[KiwoomAPI] Password retrieved from Supabase")
                        return data[0]['encrypted_value']
            except Exception as e:
                print(f"[KiwoomAPI] Password fetch from DB failed: {e}")
        
        return ""

    def order_stock(self, stock_code: str, quantity: int, price: int, order_type: str = "buy") -> Optional[Dict[str, Any]]:
        """주식 주문 (kt10000:매수, kt10001:매도)"""
        try:
            token = self._get_access_token()
            url = f"{self.base_url}/api/dostk/ordr"
            
            # 매수: kt10000, 매도: kt10001
            api_id = "kt10000" if order_type.lower() == "buy" else "kt10001"
            
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "api-id": api_id,
                "cont-yn": "N",
                "next-key": ""
            }
            
            # [FIX] Kiwoom API requires code without 'A' prefix
            if stock_code.startswith('A'):
                stock_code = stock_code[1:]

            # 시장가(3) vs 지정가(0)
            trade_type = "3" if price == 0 else "0"
            price_str = "" if price == 0 else str(price)
            
            # [Added] Fetch Password
            if not getattr(self, 'account_pw', None):
                 self.account_pw = self._fetch_account_password()

            data = {
                "dmst_stex_tp": "KRX",
                "stk_cd": stock_code,
                "ord_qty": str(quantity),
                "ord_uv": price_str,
                "trde_tp": trade_type,
                "cond_uv": "",
                "user_pw": self.account_pw or ""  # [CRITICAL] Add Password
            }
            
            print(f"[KiwoomAPI] Sending Order ({order_type}): {data}")

            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            result = response.json()
            
            print(f"[KiwoomAPI] Order Response: {result}")

            if result.get('return_code') != '0' and result.get('return_code') != 0:
                error_msg = result.get('return_msg', 'Unknown Error')
                print(f"[KiwoomAPI] Order Failed: {error_msg}")
                return {
                    'status': 'error',
                    'message': error_msg
                }
            
            return {
                'status': 'success',
                'order_no': result.get('ord_no') or 'Simulated',
                'message': 'Order placed successfully'
            }

        except Exception as e:
            print(f"[KiwoomAPI] Order failed: {e}")
            return None

    def cancel_order(self, stock_code: str, order_no: str, quantity: int = 0) -> Optional[Dict[str, Any]]:
        """주문 취소 (kt10002)"""
        try:
            token = self._get_access_token()
            # Note: Assuming 'ordr' endpoint handles cancel with kt10002 based on patterns, 
            # Or it might be a different endpoint. Search indicated kt10002 is API ID.
            # Using same endpoint url as order for now (safest bet for REST APIs often), 
            # but user didn't provide cancel example. 
            # I will use '/api/dostk/ordr' with api-id 'kt10002'.
            url = f"{self.base_url}/api/dostk/ordr" 
            
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": f"Bearer {token}",
                "api-id": "kt10002",
                "cont-yn": "N",
                "next-key": ""
            }
            
            data = {
                "dmst_stex_tp": "KRX",
                "stk_cd": stock_code,
                "orgn_ord_no": order_no, # 원주문번호 param name might differ!
                "ord_qty": str(quantity) if quantity > 0 else "0", 
                 # 'orgn_ord_no' is a guess. KIS uses 'ORGN_ODNO'. 
                 # Without doc, this is risky. I will log a warning.
            }
             # Wait, usually cancel needs Org Order No.
            
            # For now, implementing as Best Guess to allow file write.
            # If fails, I will ask user for kt10002 example.
            
            return { 'status': 'error', 'message': 'Cancel not fully verifiable without kt10002 example' }

        except Exception as e:
            return None

_kiwoom_client = None

def get_kiwoom_client() -> KiwoomAPIClient:
    """키움 API 클라이언트 싱글톤 인스턴스 반환"""
    global _kiwoom_client
    if _kiwoom_client is None:
        _kiwoom_client = KiwoomAPIClient()
    return _kiwoom_client
