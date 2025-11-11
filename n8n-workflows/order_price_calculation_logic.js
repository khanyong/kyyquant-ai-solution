// n8n 워크플로우 B - 주문 가격 계산 로직

/**
 * 주문 가격 계산 함수
 * @param {object} priceData - kw_price_current 테이블 데이터
 * @param {object} strategy - 전략 정보 (order_price_strategy 포함)
 * @param {string} signalType - 'buy' or 'sell'
 * @returns {number} 주문 가격
 */
function calculateOrderPrice(priceData, strategy, signalType) {
  const orderStrategy = strategy.order_price_strategy?.[signalType] || {
    type: 'best_ask',
    offset: 0
  };

  // 호가 정보 (현재 DB 컬럼명 주의!)
  const sellPrice = priceData.high_52w;  // 매도 1호가 (팔려는 가격)
  const buyPrice = priceData.low_52w;    // 매수 1호가 (사려는 가격)
  const currentPrice = priceData.current_price;  // 중간가

  let basePrice = 0;

  // 기본 가격 선택
  switch (orderStrategy.type) {
    case 'best_ask':
      // 매도 1호가 (즉시 매수 가능한 가격)
      basePrice = sellPrice;
      break;

    case 'best_bid':
      // 매수 1호가 (즉시 매도 가능한 가격)
      basePrice = buyPrice;
      break;

    case 'mid_price':
      // 중간가
      basePrice = currentPrice;
      break;

    case 'market':
      // 시장가 (실제로는 null 반환, Kiwoom API에서 시장가 주문)
      return null;

    default:
      // 기본값: 매수는 매도1호가, 매도는 매수1호가
      basePrice = signalType === 'buy' ? sellPrice : buyPrice;
  }

  // offset 적용
  const offset = orderStrategy.offset || 0;
  const finalPrice = basePrice + offset;

  console.log(`[${signalType}] 주문가 계산: 기준가=${basePrice}, offset=${offset}, 최종가=${finalPrice}`);

  return Math.round(finalPrice);  // 정수로 반올림
}

// n8n에서 사용 예시
const items = $input.all();
const results = [];

for (const item of items) {
  const signal = item.json;

  // 주문 가격 계산
  const orderPrice = calculateOrderPrice(
    signal.priceData,      // kw_price_current 데이터
    signal.strategy,       // 전략 정보
    signal.signal_type     // 'buy' or 'sell'
  );

  results.push({
    json: {
      ...signal,
      order_price: orderPrice,
      order_method: orderPrice === null ? 'MARKET' : 'LIMIT'
    }
  });
}

return results;
