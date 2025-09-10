# 백테스트 지표 매핑 테이블

## 1. RSI (Relative Strength Index)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| rsi_14 | rsi | < 30 | 과매도 |
| RSI_14 | rsi | > 70 | 과매수 |
| rsi | rsi | < 40 | 매수 신호 |
| RSI | rsi | > 60 | 매도 신호 |

## 2. MACD (Moving Average Convergence Divergence)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| MACD | macd | > 0 | 상승 추세 |
| macd | macd | < 0 | 하락 추세 |
| MACD | macd | cross_above MACD_SIGNAL | 골든크로스 |
| macd | macd | cross_below MACD_SIGNAL | 데드크로스 |

## 3. Bollinger Bands
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| price | bb | < BB_LOWER | 하단 밴드 이탈 |
| price | bb | > BB_UPPER | 상단 밴드 이탈 |
| BB | bb | price_below_lower | 매수 신호 |
| bb | bb | price_above_upper | 매도 신호 |

## 4. SMA (Simple Moving Average)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| sma_20 | sma | price_above | 가격이 이평선 위 |
| SMA_50 | sma | price_below | 가격이 이평선 아래 |
| sma | sma | cross_above | 골든크로스 |
| SMA | sma | cross_below | 데드크로스 |

## 5. EMA (Exponential Moving Average)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| ema_20 | ema | price_above | 가격이 이평선 위 |
| EMA_50 | ema | price_below | 가격이 이평선 아래 |

## 6. Ichimoku Cloud
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| ichimoku | ichimoku | cloud_breakout_up | 구름대 상향 돌파 |
| ICHIMOKU | ichimoku | cloud_breakout_down | 구름대 하향 돌파 |
| ichimoku | ichimoku | price_above_cloud | 가격이 구름대 위 |
| ichimoku | ichimoku | tenkan_above_kijun | 전환선 > 기준선 |

## 7. Stochastic
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| stochastic | stochastic | oversold | K < 20 & D < 20 |
| STOCHASTIC | stochastic | overbought | K > 80 & D > 80 |
| stoch | stochastic | k_above_d | K선이 D선 위 |

## 8. ADX (Average Directional Index)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| adx | adx | strong_trend | ADX > 25 |
| ADX | adx | weak_trend | ADX < 25 |

## 9. CCI (Commodity Channel Index)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| cci | cci | oversold | CCI < -100 |
| CCI | cci | overbought | CCI > 100 |

## 10. Williams %R
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| williams_r | williams_r | oversold | %R < -80 |
| WILLIAMS_R | williams_r | overbought | %R > -20 |

## 11. OBV (On Balance Volume)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| obv | obv | increasing | OBV 상승 |
| OBV | obv | decreasing | OBV 하락 |

## 12. VWAP (Volume Weighted Average Price)
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| vwap | vwap | price_above | 가격 > VWAP |
| VWAP | vwap | price_below | 가격 < VWAP |

## 13. Volume
| Frontend ID | Backend ID | 조건 | 설명 |
|------------|------------|------|------|
| volume | volume | high_volume | 거래량 급증 |
| VOLUME | volume | low_volume | 거래량 감소 |