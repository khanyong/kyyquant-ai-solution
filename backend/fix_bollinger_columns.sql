-- 볼린저 밴드의 output_columns를 formula 출력과 일치시키기
-- formula는 'bollinger_upper', 'bollinger_middle', 'bollinger_lower'를 출력

UPDATE indicators
SET
  output_columns = ARRAY['bollinger_upper', 'bollinger_middle', 'bollinger_lower'],
  updated_at = NOW()
WHERE name = 'bb';

-- indicator_columns 테이블도 업데이트
DELETE FROM indicator_columns WHERE indicator_name = 'bb';

INSERT INTO indicator_columns (indicator_name, column_name, column_description, is_primary, output_order) VALUES
('bb', 'bollinger_upper', 'Upper band (SMA + std_dev * multiplier)', false, 1),
('bb', 'bollinger_middle', 'Middle band (SMA)', true, 2),
('bb', 'bollinger_lower', 'Lower band (SMA - std_dev * multiplier)', false, 3)
ON CONFLICT (indicator_name, column_name) DO UPDATE SET
  column_description = EXCLUDED.column_description,
  is_primary = EXCLUDED.is_primary,
  output_order = EXCLUDED.output_order;

-- 결과 확인
SELECT
  name,
  display_name,
  output_columns
FROM indicators
WHERE name = 'bb';

SELECT
  indicator_name,
  column_name,
  is_primary,
  output_order
FROM indicator_columns
WHERE indicator_name = 'bb'
ORDER BY output_order;
