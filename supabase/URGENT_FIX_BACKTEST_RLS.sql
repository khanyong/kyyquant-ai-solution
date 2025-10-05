-- ⚠️ URGENT: Run this in Supabase SQL Editor to fix backtest_results RLS
-- This will allow all authenticated users to save their backtest results

-- Step 1: Drop all existing policies on backtest_results
DROP POLICY IF EXISTS "Users can view own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can insert own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can update own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can delete own backtest results" ON backtest_results;

-- Step 2: Ensure RLS is enabled
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;

-- Step 3: Create new policies with TO authenticated clause
-- This ensures all authenticated users (not just admin) can use these policies

-- SELECT: Users can view their own backtest results
CREATE POLICY "Users can view own backtest results"
ON backtest_results
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- INSERT: Users can insert their own backtest results
CREATE POLICY "Users can insert own backtest results"
ON backtest_results
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- UPDATE: Users can update their own backtest results
CREATE POLICY "Users can update own backtest results"
ON backtest_results
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- DELETE: Users can delete their own backtest results
CREATE POLICY "Users can delete own backtest results"
ON backtest_results
FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- Step 4: Verify the policies
SELECT
    policyname,
    cmd,
    CASE
        WHEN roles = '{authenticated}' THEN '✅ Applies to authenticated users'
        ELSE '❌ Check role configuration'
    END as role_status,
    qual as using_expression,
    with_check as with_check_expression
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'backtest_results'
ORDER BY cmd;

-- Step 5: Check if table has RLS enabled
SELECT
    tablename,
    CASE
        WHEN rowsecurity THEN '✅ RLS is enabled'
        ELSE '❌ RLS is NOT enabled'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'backtest_results';
