-- Add max_investment_per_stock column to strategies table
ALTER TABLE strategies 
ADD COLUMN IF NOT EXISTS max_investment_per_stock numeric;

-- Optional: Add comment
COMMENT ON COLUMN strategies.max_investment_per_stock IS 'Maximum investment amount allowed per single stock';
