// 병합된 데이터에서 정보 추출
const item = $input.item.json;
const kiwoomResponse = item;

// 환경변수를 직접 참조
const envVars = $('환경변수 설정').first().json;

// 이전 노드(데이터 병합)에서 추가한 원본 데이터 사용
const strategy_id = item._original_strategy_id || '';
const strategy_name = item._original_strategy_name || '';
const entry_conditions = item._original_entry_conditions;
const exit_conditions = item._original_exit_conditions;
const stockCode = item._original_stock_code || '';
const SUPABASE_URL = item._original_SUPABASE_URL || envVars.SUPABASE_URL;
const SUPABASE_ANON_KEY = item._original_SUPABASE_ANON_KEY || envVars.SUPABASE_ANON_KEY;
const BACKEND_URL = item._original_BACKEND_URL || envVars.BACKEND_URL;

// 호가 데이터 파싱 (부호 제거 및 숫자 변환)
const parsePrice = (price) => {
  if (!price) return 0;
  return parseFloat(String(price).replace(/[+\-]/g, ''));
};

const selPrice = parsePrice(kiwoomResponse.sel_fpr_bid);
const buyPrice = parsePrice(kiwoomResponse.buy_fpr_bid);
const estimatedPrice = (selPrice + buyPrice) / 2;

// ⭐ 종목명 조회: stock_metadata 테이블에서 가져오기
let stockName = stockCode; // 기본값: 종목코드

try {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/stock_metadata?stock_code=eq.${stockCode}&select=stock_name`,
    {
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
      }
    }
  );

  const data = await response.json();
  if (data && data.length > 0 && data[0].stock_name) {
    stockName = data[0].stock_name;
  }
} catch (error) {
  console.error('Failed to fetch stock name:', error);
  // 에러 시 종목코드 사용 (이미 stockName = stockCode로 설정됨)
}

// 거래량 계산 (문자열을 숫자로 변환)
const selVolume = parseInt(String(kiwoomResponse.sel_fpr_req || 0).replace(/[+\-]/g, '')) || 0;
const buyVolume = parseInt(String(kiwoomResponse.buy_fpr_req || 0).replace(/[+\-]/g, '')) || 0;

const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume
};

let buySignal = false;
if (entry_conditions && entry_conditions.buy) {
  buySignal = entry_conditions.buy.some(condition => {
    const left = indicators[condition.left] || 0;
    const right = typeof condition.right === 'string' ? indicators[condition.right] : condition.right;

    switch(condition.operator) {
      case '<': return left < right;
      case '>': return left > right;
      case '<=': return left <= right;
      case '>=': return left >= right;
      case '==': return left == right;
      default: return false;
    }
  });
}

let sellSignal = false;
if (exit_conditions && exit_conditions.sell) {
  sellSignal = exit_conditions.sell.some(condition => {
    const left = indicators[condition.left] || 0;
    const right = typeof condition.right === 'string' ? indicators[condition.right] : condition.right;

    switch(condition.operator) {
      case '<': return left < right;
      case '>': return left > right;
      case '<=': return left <= right;
      case '>=': return left >= right;
      case '==': return left == right;
      default: return false;
    }
  });
}

return {
  strategy_id: strategy_id,
  strategy_name: strategy_name,
  stock_code: stockCode,
  stock_name: stockName, // ⭐ stock_metadata에서 조회한 실제 종목명
  current_price: estimatedPrice,
  indicators: indicators,
  buy_signal: buySignal,
  sell_signal: sellSignal,
  signal_type: buySignal ? 'BUY' : (sellSignal ? 'SELL' : 'NONE'),
  signal_strength: buySignal ? 0.7 : (sellSignal ? 0.7 : 0),
  timestamp: new Date().toISOString(),
  SUPABASE_URL: SUPABASE_URL,
  SUPABASE_ANON_KEY: SUPABASE_ANON_KEY,
  BACKEND_URL: BACKEND_URL,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: indicators.volume
};
