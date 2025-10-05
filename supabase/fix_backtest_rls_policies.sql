-- Step 1: Check current RLS policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'backtest_results';

-- Step 2: Drop existing policies
DROP POLICY IF EXISTS "Users can view own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can insert own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can update own backtest results" ON backtest_results;
DROP POLICY IF EXISTS "Users can delete own backtest results" ON backtest_results;

-- Step 3: Create new policies with correct syntax
-- SELECT policy
CREATE POLICY "Users can view own backtest results" ON backtest_results
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

-- INSERT policy
CREATE POLICY "Users can insert own backtest results" ON backtest_results
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- UPDATE policy
CREATE POLICY "Users can update own backtest results" ON backtest_results
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- DELETE policy
CREATE POLICY "Users can delete own backtest results" ON backtest_results
    FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- Step 4: Verify RLS is enabled
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;

-- Step 5: Verify policies were created
SELECT
    policyname,
    cmd,
    roles,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'backtest_results';
