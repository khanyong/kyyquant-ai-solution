import json

# v23 읽기
with open('auto-trading-with-capital-validation-v23.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# "데이터 병합" 노드 찾아서 코드 수정
for node in workflow['nodes']:
    if node['id'] == 'merge-data-1':
        # 새로운 JavaScript 코드
        node['parameters']['jsCode'] = """// 키움 호가 조회 결과를 그대로 사용
const kiwoomData = $input.item.json;

// 종목 코드 추출 노드의 데이터는 pairedItem으로 접근
const originalItem = $input.item;
const originalData = $('종목 코드 추출').item(originalItem.pairedItem).json;

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

console.log('✅ Merged data keys:', Object.keys(mergedData));
console.log('✅ _original_stock_code:', mergedData._original_stock_code);
console.log('✅ _original_strategy_id:', mergedData._original_strategy_id);

return mergedData;"""

# v23-fixed로 저장
with open('auto-trading-with-capital-validation-v23-fixed.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("OK: v23-fixed created")
print("- Fixed: Data merge node to use pairedItem")
