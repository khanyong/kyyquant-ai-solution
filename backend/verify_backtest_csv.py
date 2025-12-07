import pandas as pd
import numpy as np
import sys
import os

def verify_backtest_csv(file_path):
    print(f"Loading backtest results from: {file_path}")
    
    try:
        # Load CSV (handle potential encoding issues)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
            
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print(f"Loaded {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    
    # Column Mapping (Korean -> Internal)
    col_map = {
        '구분': 'type',
        '단가': 'price', 
        '수량': 'quantity',
        '금액': 'amount',
        '손익': 'profit',
        '수익률': 'profit_rate',
        '수수료': 'commission'
    }
    
    # Rename columns for consistency
    df.rename(columns=col_map, inplace=True)
    
    # Required columns
    required = ['type', 'price', 'quantity', 'amount']
    missing = [c for c in required if c not in df.columns]
    
    if missing:
        print(f"CRITICAL: Missing columns: {missing}")
        return

    print("\n[VERIFICATION START]")
    
    error_count = 0
    checked_count = 0
    
    for idx, row in df.iterrows():
        # Clean type value (remove whitespace, lower case)
        trade_type = str(row['type']).strip().lower()
        
        # Parse numbers (remove commas if string)
        try:
            price = float(str(row['price']).replace(',', ''))
            quantity = float(str(row['quantity']).replace(',', ''))
            amount = float(str(row['amount']).replace(',', ''))
            
            commission = 0
            if 'commission' in row and not pd.isna(row['commission']):
                commission = float(str(row['commission']).replace(',', ''))
                
            profit = 0
            if 'profit' in row and not pd.isna(row['profit']):
                 profit = float(str(row['profit']).replace(',', ''))
                 
            profit_rate = 0
            if 'profit_rate' in row and not pd.isna(row['profit_rate']):
                profit_rate = float(str(row['profit_rate']).replace(',', ''))
                
        except ValueError:
            continue # Skip invalid rows

        # 1. Verify Amount (Price * Quantity)
        expected_amount = price * quantity
        # Allow small float diff or rounding differences (int vs float)
        # Often amount is floored or rounded.
        if abs(expected_amount - amount) > (price * 0.1): # Allow some margin if logic differs (e.g. slippage applied?)
             # Check if amount includes slippage? Usually Amount = Price * Qty.
             # Let's assume strict checks first, verify output.
             if abs(expected_amount - amount) > 100: # 100 won diff
                 print(f"Row {idx}: Amount mismatch! Expected {expected_amount:.2f}, Got {amount:.2f} (Diff: {expected_amount-amount:.2f})")
                 error_count += 1
        
        checked_count += 1
        
        # 2. Verify Profit Rate (for Sells)
        if trade_type in ['sell', '매도'] and 'profit' in df.columns and 'profit_rate' in df.columns:
            # Profit = Net Sell Amount - Cost
            # Cost = Net Sell Amount - Profit
            # Profit Rate = (Profit / Cost) * 100
            
            # Net Sell Amount (Amount - Commission)
            net_sell_amount = amount - commission
            cost = net_sell_amount - profit
            
            if cost > 0:
                calc_profit_rate = (profit / cost) * 100
                
                # Tolerance: 0.1% absolute
                if abs(calc_profit_rate - profit_rate) > 0.1:
                    print(f"Row {idx} ({row.get('stock_code', 'Unknown')}): Profit Rate mismatch! Expected {calc_profit_rate:.4f}%, Got {profit_rate:.4f}%")
                    error_count += 1

    print(f"\nChecked {checked_count} rows.")

    if error_count == 0:
        print("\n[SUCCESS] All checks passed! Calculations appear consistent.")
    else:
        print(f"\n[FAILURE] Found {error_count} inconsistencies.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_backtest_cvs.py <path_to_csv>")
    else:
        verify_backtest_csv(sys.argv[1])
