
-- Fix RLS Policies for Auto Trading Dashboard
-- Run this in Supabase Dashboard -> SQL Editor

-- 1. Enable RLS (just in case)
ALTER TABLE public.kw_account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kw_portfolio ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view their own account balance" ON public.kw_account_balance;
DROP POLICY IF EXISTS "Users can insert/update their own account balance" ON public.kw_account_balance;
DROP POLICY IF EXISTS "Users can view their own portfolio" ON public.kw_portfolio;
DROP POLICY IF EXISTS "Users can insert/update their own portfolio" ON public.kw_portfolio;

-- 3. Create Policies for kw_account_balance
CREATE POLICY "Users can view their own account balance"
ON public.kw_account_balance FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert/update their own account balance"
ON public.kw_account_balance FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 4. Create Policies for kw_portfolio
CREATE POLICY "Users can view their own portfolio"
ON public.kw_portfolio FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert/update their own portfolio"
ON public.kw_portfolio FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

RAISE NOTICE 'RLS Policies updated successfully.';
