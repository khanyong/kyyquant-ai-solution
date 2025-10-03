-- SMA 지표의 default_params 확인
SELECT
  name,
  default_params,
  calculation_type,
  output_columns
FROM indicators
WHERE name = 'sma';
