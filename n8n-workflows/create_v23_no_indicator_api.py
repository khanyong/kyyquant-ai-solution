import json

# v22 읽기
with open('auto-trading-with-capital-validation-v22.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 이름 변경
workflow['name'] = '자동매매 모니터링 v23 (지표 계산 API 제거)'

# "지표 계산 API 호출" 노드 제거
workflow['nodes'] = [node for node in workflow['nodes'] if node['id'] != 'calc-indicators-1']

# connections 수정: "데이터 병합" -> "조건 체크 및 신호 생성" 직접 연결
if '데이터 병합' in workflow['connections']:
    workflow['connections']['데이터 병합']['main'][0] = [
        {
            "node": "조건 체크 및 신호 생성",
            "type": "main",
            "index": 0
        }
    ]

# "지표 계산 API 호출" connections 제거
if '지표 계산 API 호출' in workflow['connections']:
    del workflow['connections']['지표 계산 API 호출']

# "조건 체크 및 신호 생성" 노드의 코드 수정 - backendIndicators 제거
for node in workflow['nodes']:
    if node['id'] == 'check-conditions-1':
        # 간단한 버전으로 수정: Backend API 호출 없이 호가 데이터만 사용
        node['parameters']['jsCode'] = """// 병합된 데이터에서 정보 추출
const item = $input.item.json;
const kiwoomData = item;

// 환경변수를 직접 참조
const envVars = $('환경변수 설정').first().json;

// 이전 노드(데이터 병합)에서 추가한 원본 데이터 사용
const strategy_id = kiwoomData._original_strategy_id || '';
const strategy_name = kiwoomData._original_strategy_name || '';
const entry_conditions = kiwoomData._original_entry_conditions;
const exit_conditions = kiwoomData._original_exit_conditions;
const stockCode = kiwoomData._original_stock_code || '';
const SUPABASE_URL = kiwoomData._original_SUPABASE_URL || envVars.SUPABASE_URL;
const SUPABASE_ANON_KEY = kiwoomData._original_SUPABASE_ANON_KEY || envVars.SUPABASE_ANON_KEY;
const BACKEND_URL = kiwoomData._original_BACKEND_URL || envVars.BACKEND_URL;

console.log('🎯 조건 체크 시작');
console.log('📋 Stock code:', stockCode);
console.log('📋 Strategy:', strategy_name);

// 호가 데이터 파싱 (부호 제거 및 숫자 변환)
const parsePrice = (price) => {
  if (!price) return 0;
  return parseFloat(String(price).replace(/[+\\-]/g, ''));
};

const selPrice = parsePrice(kiwoomData.sel_fpr_bid);
const buyPrice = parsePrice(kiwoomData.buy_fpr_bid);
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
}

// 거래량 계산 (문자열을 숫자로 변환)
const selVolume = parseInt(String(kiwoomData.sel_fpr_req || 0).replace(/[+\\-]/g, '')) || 0;
const buyVolume = parseInt(String(kiwoomData.buy_fpr_req || 0).replace(/[+\\-]/g, '')) || 0;

// ⭐⭐⭐ 지표 객체: 호가 데이터만 사용 (Backend API 제거)
const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume
};

console.log('📈 Indicators:', indicators);

// 매수/매도 신호는 조건이 없으므로 항상 false
const buySignal = false;
const sellSignal = false;

return {
  strategy_id: strategy_id,
  strategy_name: strategy_name,
  stock_code: stockCode,
  stock_name: stockName,
  current_price: estimatedPrice,
  indicators: indicators,
  buy_signal: buySignal,
  sell_signal: sellSignal,
  signal_type: 'NONE',
  signal_strength: 0,
  timestamp: new Date().toISOString(),
  SUPABASE_URL: SUPABASE_URL,
  SUPABASE_ANON_KEY: SUPABASE_ANON_KEY,
  BACKEND_URL: BACKEND_URL,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: indicators.volume
};"""

# v23로 저장
with open('auto-trading-with-capital-validation-v23.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("OK: v23 workflow created")
print(f"- Total nodes: {len(workflow['nodes'])}")
print("- Removed: Indicator calculation API node")
print("- Simplified: Condition check without backend API")
