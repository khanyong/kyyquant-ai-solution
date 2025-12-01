
-- Enable RLS
ALTER TABLE strategy_monitoring ENABLE ROW LEVEL SECURITY;

-- Policy for SELECT
-- Users can see monitoring data for strategies they own
CREATE POLICY "Users can view their own strategy monitoring"
ON strategy_monitoring FOR SELECT
USING (
  auth.uid() IN (
    SELECT user_id 
    FROM strategies 
    WHERE id = strategy_monitoring.strategy_id
  )
);

-- Policy for INSERT/UPDATE (Service Role usually handles this via n8n, but just in case)
-- We'll leave it to Service Role for now.
