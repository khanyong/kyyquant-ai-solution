-- Fix stochastic indicator column names in indicator_columns table
-- Change stoch_k -> stochastic_k and stoch_d -> stochastic_d

-- 1. Delete old entries
DELETE FROM indicator_columns
WHERE indicator_name = 'stochastic'
  AND column_name IN ('stoch_k', 'stoch_d');

-- 2. Insert corrected entries
INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('stochastic', 'stochastic_k', '%K line (fast stochastic)', true, 1),
('stochastic', 'stochastic_d', '%D line (slow stochastic, SMA of %K)', false, 2)
ON CONFLICT (indicator_name, column_name) DO UPDATE SET
  column_description = EXCLUDED.column_description,
  is_primary = EXCLUDED.is_primary,
  output_order = EXCLUDED.output_order;

-- 3. Verify the fix
SELECT * FROM indicator_columns
WHERE indicator_name = 'stochastic'
ORDER BY output_order;
