import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from api.kiwoom_client import KiwoomAPIClient

def test_parsing():
    print("--- Testing Kiwoom Parsing Logic ---")
    client = KiwoomAPIClient()
    
    # Mock Response Data (Based on debug_output.txt)
    mock_detail_response = {
        "return_code": "0",
        "return_msg": "OK",
        "acnt_evlt_remn_indv_tot": [
            {
                "stk_cd": "A005930",
                "stk_nm": "Samsung Elec",
                "hldg_qty": "10",
                "pur_pric": "",        # Empty string (Mock API behavior)
                "cur_prc": "70000",
                "evlt_amt": "700000",
                "evlt_pfls_amt": "",   # Empty string
                "pft_rt": ""           # Empty string
            }
        ]
    }
    
    # Patch requests
    with patch('requests.post') as mock_post:
        # Mock Token response
        mock_post.return_value.json.return_value = {"access_token": "TEST_TOKEN"}
        
        # Override _get_access_token to avoid real calls
        client._get_access_token = MagicMock(return_value="TEST_TOKEN")
        
        # Setup specific response for Balance call
        mock_response = MagicMock()
        mock_response.json.return_value = mock_detail_response
        mock_response.raise_for_status.return_value = None
        
        # We need to mock the SUMMARY call too, or it might fail
        mock_sum_response = MagicMock()
        mock_sum_response.json.return_value = {"return_code": "0", "tot_asst_amt": "1000000"}
        
        # Configure side_effect for multiple calls
        mock_post.side_effect = [mock_sum_response, mock_response] 
        
        print("Calling get_account_balance()...")
        result = client.get_account_balance()
        
        print(f"Result Type: {type(result)}")
        print(f"Result Content: {result}")
        
        if isinstance(result, list):
             print("❌ Parsing FAILED: Returned empty list (Exception caught inside method).")
             return

        print(f"Result Holdings Count: {len(result.get('holdings', []))}")
        for h in result.get('holdings', []):
            print(f" - {h['stock_name']} Qty:{h['quantity']} Price:{h['current_price']}")
            
        if len(result.get('holdings', [])) == 1:
            print("✅ Parsing SUCCESS: Handled empty strings correctly.")
        else:
            print("❌ Parsing FAILED: Holdings list empty but dict returned?")

if __name__ == "__main__":
    test_parsing()
