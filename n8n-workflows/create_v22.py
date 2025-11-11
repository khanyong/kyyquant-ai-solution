import json

# v21 읽기
with open('auto-trading-with-capital-validation-v21.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 이름 변경
workflow['name'] = '자동매매 모니터링 v22 (지수 조회 제거 + RPC 수정)'

# 삭제할 노드 ID 목록
nodes_to_remove = [
    'get-kospi-index',      # KOSPI 지수 조회
    'get-kosdaq-index',     # KOSDAQ 지수 조회
    'parse-index-data',     # 지수 데이터 파싱
    'save-market-index'     # 시장 지수 저장
]

# 노드 삭제
workflow['nodes'] = [node for node in workflow['nodes'] if node['id'] not in nodes_to_remove]

# "종목 코드 추출" 노드 찾아서 코드 수정
for node in workflow['nodes']:
    if node['id'] == 'extract-stocks-1':
        # 새로운 JavaScript 코드 (jsonb 배열 처리 추가)
        node['parameters']['jsCode'] = """const items = $input.all();
const results = [];

const envVars = $('환경변수 설정').first().json;
const tokenData = $('키움 토큰 발급').first().json;

for (const item of items) {
  const strategy = item.json;
  let stockCodes = [];

  // filtered_stocks가 jsonb 타입인 경우 처리
  if (strategy.filtered_stocks) {
    if (Array.isArray(strategy.filtered_stocks)) {
      // 이미 배열인 경우 (JavaScript에서 파싱됨)
      stockCodes = strategy.filtered_stocks.filter(code => code && typeof code === 'string');
    } else if (typeof strategy.filtered_stocks === 'object') {
      // jsonb 객체인 경우 배열로 변환
      stockCodes = Object.values(strategy.filtered_stocks).filter(code => code && typeof code === 'string');
    }
  }

  console.log(`📊 Strategy: ${strategy.strategy_name}, Stock count: ${stockCodes.length}`);

  stockCodes.forEach(stockCode => {
    results.push({
      json: {
        strategy_id: strategy.strategy_id,
        strategy_name: strategy.strategy_name,
        entry_conditions: strategy.entry_conditions,
        exit_conditions: strategy.exit_conditions,
        stock_code: stockCode,
        access_token: tokenData.token,
        KIWOOM_APP_KEY: envVars.KIWOOM_APP_KEY,
        KIWOOM_APP_SECRET: envVars.KIWOOM_APP_SECRET,
        SUPABASE_URL: envVars.SUPABASE_URL,
        SUPABASE_ANON_KEY: envVars.SUPABASE_ANON_KEY,
        BACKEND_URL: envVars.BACKEND_URL
      }
    });
  });
}

console.log(`✅ Total items created: ${results.length}`);
return results;"""

# connections에서 지수 관련 연결 제거
if 'connections' in workflow:
    # "조건 체크 및 신호 생성" 노드의 연결에서 KOSPI/KOSDAQ 제거
    if '조건 체크 및 신호 생성' in workflow['connections']:
        main_connections = workflow['connections']['조건 체크 및 신호 생성']['main'][0]
        # KOSPI/KOSDAQ 지수 조회 노드 제거
        main_connections = [
            conn for conn in main_connections
            if conn['node'] not in ['KOSPI 지수 조회', 'KOSDAQ 지수 조회']
        ]
        workflow['connections']['조건 체크 및 신호 생성']['main'][0] = main_connections

    # 지수 관련 노드의 connections 완전히 제거
    for node_name in ['KOSPI 지수 조회', 'KOSDAQ 지수 조회', '지수 데이터 파싱', '시장 지수 저장']:
        if node_name in workflow['connections']:
            del workflow['connections'][node_name]

# v22로 저장
with open('auto-trading-with-capital-validation-v22.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("OK: v22 workflow created")
print(f"- Total nodes: {len(workflow['nodes'])}")
print("- Removed: KOSPI/KOSDAQ index nodes")
print("- Updated: Stock code extraction node")
