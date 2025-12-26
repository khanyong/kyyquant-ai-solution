-- [FIX ALLOCATION MANUAL]
-- User provided Real HTS Asset: 9,725,340 KRW
-- Target Allocation (50%): 4,862,670 KRW

-- 1. Insert/Update Account Balance Snapshot (for Dashboard)
-- We need a valid user_id. We'll pick one from the strategies table (assuming single user).
WITH user_ref AS (
    SELECT user_id FROM strategies LIMIT 1
)
INSERT INTO kw_account_balance (
    user_id, 
    account_number, 
    total_asset, 
    deposit, 
    available_cash, 
    updated_at
)
SELECT 
    user_id, 
    'MANUAL_SYNC', -- Placeholder until real sync
    9725340,       -- Fixed Total Asset
    9725340,       -- Assuming mostly cash/deposit for mock
    4862670,       -- Cash (Available)
    NOW()
FROM user_ref
ON CONFLICT (user_id, account_number, updated_at) DO NOTHING;
-- Note: The PK for kw_account_balance might be just (user_id, account_number) or include timestamp. 
-- If it's time-series, this insert is fine. If it's single-row, we might need UPDATE.
-- Based on previous scripts, it seems to be a log table (order by desc limit 1).

-- 2. Update Strategy Allocation
UPDATE strategies
SET 
    allocated_capital = 4862670,  -- 50% of 9,725,340
    allocated_percent = 0.5
WHERE name IN ('TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB');
