-- 임시 테스트: 일부 종목의 종목명 수동 업데이트

UPDATE kw_price_current
SET stock_name = CASE stock_code
  WHEN '005930' THEN '삼성전자'
  WHEN '000660' THEN 'SK하이닉스'
  WHEN '035720' THEN '카카오'
  WHEN '035420' THEN '네이버'
  WHEN '051910' THEN 'LG화학'
  WHEN '006400' THEN '삼성SDI'
  WHEN '003550' THEN 'LG'
  WHEN '055550' THEN '신한지주'
  WHEN '105560' THEN 'KB금융'
  WHEN '005380' THEN '현대차'
  ELSE stock_code
END
WHERE stock_code IN (
  '005930', '000660', '035720', '035420', '051910',
  '006400', '003550', '055550', '105560', '005380'
);

-- 결과 확인
SELECT stock_code, stock_name, current_price, change_rate
FROM kw_price_current
WHERE stock_code IN ('005930', '000660', '035720')
ORDER BY stock_code;
