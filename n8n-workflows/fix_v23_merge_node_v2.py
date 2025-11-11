import json

# v23 읽기
with open('auto-trading-with-capital-validation-v23.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# "데이터 병합" 노드 찾아서 코드 수정
for node in workflow['nodes']:
    if node['id'] == 'merge-data-1':
        # 새로운 JavaScript 코드 - all items 방식 사용
        node['parameters']['jsCode'] = """// 모든 입력 아이템 가져오기
const allItems = $input.all();

// 첫 번째 아이템: 종목 코드 추출 노드의 데이터
// 두 번째 아이템: 키움 호가 조회 응답
const originalData = allItems[0].json;
const kiwoomData = allItems[1].json;

console.log('🔄 데이터 병합 시작');
console.log('📋 Original stock_code:', originalData.stock_code);
console.log('📋 Original strategy_id:', originalData.strategy_id);
console.log('📋 Original strategy_name:', originalData.strategy_name);

// 원본 데이터 보존
const mergedData = {
  _original_stock_code: originalData.stock_code,
  _original_strategy_id: originalData.strategy_id,
  _original_strategy_name: originalData.strategy_name,
  _original_entry_conditions: originalData.entry_conditions,
  _original_exit_conditions: originalData.exit_conditions,
  _original_SUPABASE_URL: originalData.SUPABASE_URL,
  _original_SUPABASE_ANON_KEY: originalData.SUPABASE_ANON_KEY,
  _original_BACKEND_URL: originalData.BACKEND_URL,

  // 키움 API 응답 데이터 병합
  ...kiwoomData
};

console.log('✅ Merged data keys count:', Object.keys(mergedData).length);
console.log('✅ _original_stock_code:', mergedData._original_stock_code);
console.log('✅ _original_strategy_id:', mergedData._original_strategy_id);

return mergedData;"""

# v23-fixed-v2로 저장
with open('auto-trading-with-capital-validation-v23-fixed-v2.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("OK: v23-fixed-v2 created")
print("- Fixed: Data merge using $input.all() method")
