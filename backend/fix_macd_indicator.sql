[
  {
    "name": "macd",
    "output_columns": [
      "macd",
      "macd_signal",
      "macd_hist"
    ],
    "code_preview": "exp1 = df[\"close\"].ewm(span=params.get(\"fast\", 12), adjust=False).mean()\r\nexp2 = df[\"close\"].ewm(span=params.get(\"slow\", 26), adjust=False).mean()\r\nmacd = exp1 - exp2\r\nmacd_signal = macd.ewm(span=params.get(\"signal\", 9), adjust=False).mean()\r\nmacd_hist = macd - macd_signal\r\nresult = {\"macd\": macd, \"macd_signal\": macd_signal, \"macd_hist\": macd_hist}"
  }
]