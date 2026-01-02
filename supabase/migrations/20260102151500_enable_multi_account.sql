-- Drop the constraint that limits 1 account per user
ALTER TABLE account_balance DROP CONSTRAINT IF EXISTS account_balance_user_id_key;

-- Ensure account_no is the unique identifier (if it isn't already handled by PK)
-- We assume account_balance_pkey is on (id) or (account_no). 
-- This migration just removes the 1-to-1 restriction.
