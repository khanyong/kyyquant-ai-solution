-- 볼린저 밴드 지표의 현재 상태 확인 및 수정

-- 1. 현재 상태 확인
SELECT
  name,
  display_name,
  output_columns,
  formula->>'code' as formula_code_preview
FROM indicators
WHERE name = 'bollinger';

-- 2. output_columns가 formula와 일치하지 않으면 수정
UPDATE indicators
SET
  output_columns = ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower'],
  updated_at = NOW()
WHERE name = 'bollinger'
  AND output_columns != ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower'];

-- 3. indicator_columns 테이블도 확인 및 수정
SELECT
  indicator_name,
  column_name,
  is_primary,
  output_order,
  is_active
FROM indicator_columns
WHERE indicator_name = 'bollinger'
ORDER BY output_order;

-- 4. indicator_columns 테이블 수정 (필요시)
DELETE FROM indicator_columns WHERE indicator_name = 'bollinger';

INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order, is_active) VALUES
('bollinger', 'bollinger_upper', 'Upper band (SMA + std * multiplier)', false, 1, true),
('bollinger', 'bollinger_middle', 'Middle band (SMA)', true, 2, true),
('bollinger', 'bollinger_lower', 'Lower band (SMA - std * multiplier)', false, 3, true)
ON CONFLICT (indicator_name, column_name) DO UPDATE SET
  column_description = EXCLUDED.column_description,
  is_primary = EXCLUDED.is_primary,
  output_order = EXCLUDED.output_order,
  is_active = EXCLUDED.is_active;

-- 5. 최종 확인
SELECT
  i.name,
  i.display_name,
  i.output_columns,
  array_agg(ic.column_name ORDER BY ic.output_order) as indicator_columns_table
FROM indicators i
LEFT JOIN indicator_columns ic ON i.name = ic.indicator_name AND ic.is_active = true
WHERE i.name = 'bollinger'
GROUP BY i.name, i.display_name, i.output_columns;
