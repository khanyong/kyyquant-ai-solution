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
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO', '').replace('-', '')
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
        """OAuth 2.0 액세스 토큰 발급"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key.strip() if self.app_key else "",
            "secretkey": self.app_secret.strip() if self.app_secret else ""
        }

        try:
            print(f"[KiwoomAPI] Requesting Token from {url}")
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            result = response.json()

            if 'error' in result:
                 raise Exception(f"Token issuance failed: {result}")

            self.access_token = result.get('token') or result.get('access_token')
            if not self.access_token:
                 raise Exception(f"Token not found in response: {result}")

            expires_in = int(result.get('expires_in', 86400))
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            print(f"[KiwoomAPI] Access token issued successfully (expires at {self.token_expires_at})")
            return self.access_token

        except requests.exceptions.RequestException as e:
            print(f"[KiwoomAPI] Token issuance failed: {e}")
            raise Exception(f"Failed to get access token: {str(e)}")

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

    def get_account_balance(self) -> list:
        """계좌 잔고 조회 (kt00018)"""
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
            # Step 1: Fetch Summary (qry_tp=1)
            # This returns accurate Total Assets, Cash, etc.
            data_summary = {
                "qry_tp": "1",          
                "dmst_stex_tp": "KRX",
                "acnt_no": self.account_no if self.account_no else ""
            }
            
            summary = {}
            try:
                res_sum = requests.post(url, headers=headers, data=json.dumps(data_summary), timeout=10)
                res_sum.raise_for_status()
                result_sum = res_sum.json()
                
                if result_sum.get('return_code') == 0 or result_sum.get('return_code') == '0':
                    summary = {
                        'total_purchase_amount': float(result_sum.get('tot_pchs_amt', 0)),
                        'total_evaluation_amount': float(result_sum.get('tot_evlu_amt', 0)),
                        'total_evaluation_profit_loss': float(result_sum.get('evlu_pfls_smtl_amt', 0)), 
                        'total_earning_rate': float(result_sum.get('tot_evlu_pfls_rt', 0)),
                        'total_assets': float(result_sum.get('tot_asst_amt', 0)), 
                        'deposit': float(result_sum.get('dnca_tot_amt', 0)),
                        # [FIX] Use Deposit if Orderable Amount is 0 (Common in Mock API)
                        'withdrawable_amount': float(result_sum.get('pchs_psbl_amt', 0)) or float(result_sum.get('dnca_tot_amt', 0)) 
                    }
                else:
                    print(f"[KiwoomAPI] Balance Summary fetch error: {result_sum.get('return_msg')}")
            except Exception as e:
                print(f"[KiwoomAPI] Balance Summary fetch failed: {e}")

            # Step 2: Fetch Holdings (qry_tp=2)
            # This returns accurate Average Price (pur_pric) and individual details
            data_detail = {
                "qry_tp": "2",          
                "dmst_stex_tp": "KRX",
                "acnt_no": self.account_no if self.account_no else ""
            }
            
            holdings = []
            try:
                res_det = requests.post(url, headers=headers, data=json.dumps(data_detail), timeout=10)
                res_det.raise_for_status()
                result_det = res_det.json()
                
                if result_det.get('return_code') == 0 or result_det.get('return_code') == '0':
                    for item in result_det.get('acnt_evlt_remn_indv_tot', []):
                         # Map 'pur_pric' to 'average_price' for correct investment calculation
                         # 'buy_avg_prc' often 0 in mock.
                         avg_price = float(item.get('pur_pric', 0))
                         if avg_price == 0:
                             avg_price = float(item.get('buy_avg_prc', 0))
                             
                         holdings.append({
                            'stock_code': item.get('stk_cd'),
                            'stock_name': item.get('stk_nm'),
                            'quantity': int(item.get('rmnd_qty', 0)),
                            'current_price': float(item.get('cur_prc', 0)),
                            'average_price': avg_price,
                            'profit_loss': float(item.get('evltv_prft', 0)),
                            'profit_loss_rate': float(item.get('prft_rt', 0)) # Using prft_rt from Step 3231 output
                         })
                else:
                    print(f"[KiwoomAPI] Balance Detail fetch error: {result_det.get('return_msg')}")
            except Exception as e:
                 print(f"[KiwoomAPI] Balance Detail fetch failed: {e}")
            
            # [FIX] Recalculate Summary if API returns 0 (Common in Mock/Demo)
            if holdings:
                calc_total_purch = sum([h['average_price'] * h['quantity'] for h in holdings])
                calc_total_eval = sum([h['current_price'] * h['quantity'] for h in holdings])
                calc_total_profit = calc_total_eval - calc_total_purch
                
                # Update summary if it's zero
                if summary.get('total_purchase_amount', 0) == 0:
                    summary['total_purchase_amount'] = calc_total_purch
                    
                if summary.get('total_evaluation_amount', 0) == 0:
                    summary['total_evaluation_amount'] = calc_total_eval
                    
                if summary.get('total_evaluation_profit_loss', 0) == 0:
                    summary['total_evaluation_profit_loss'] = calc_total_profit
                    
                if summary.get('total_assets', 0) == 0:
                    # Total Assets = Cash (Deposit) + Stock Evaluation
                    summary['total_assets'] = summary.get('deposit', 0) + calc_total_eval
                    
                # Recalculate Profit Rate if needed
                if summary.get('total_purchase_amount', 0) > 0:
                     summary['total_earning_rate'] = (summary['total_evaluation_profit_loss'] / summary['total_purchase_amount']) * 100

            return {'account_no': self.account_no, 'summary': summary, 'holdings': holdings}

        except Exception as e:
            print(f"[KiwoomAPI] Balance fetch failed: {e}")
            return []

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
            
            # 시장가(3) vs 지정가(0)
            trade_type = "3" if price == 0 else "0"
            price_str = "" if price == 0 else str(price)

            data = {
                "dmst_stex_tp": "KRX",
                "stk_cd": stock_code,
                "ord_qty": str(quantity),
                "ord_uv": price_str,
                "trde_tp": trade_type,
                "cond_uv": ""
            }
            
            print(f"[KiwoomAPI] Sending Order ({order_type}): {data}")

            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            result = response.json()
            
            print(f"[KiwoomAPI] Order Response: {result}")

            if result.get('return_code') != '0' and result.get('return_code') != 0:
                print(f"[KiwoomAPI] Order Failed: {result.get('return_msg')}")
                return None
            
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
