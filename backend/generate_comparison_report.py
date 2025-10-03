import os
import sys
import io
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# ============================================================
# 1. Supabase Indicators - Formula가 생성하는 컬럼명
# ============================================================
import re

indicators_data = supabase.table('indicators').select('*').eq('is_active', True).order('name').execute()

indicator_output_map = {}

for ind in indicators_data.data:
    name = ind['name']
    formula = ind.get('formula', {})
    output_cols = ind.get('output_columns', [])
    default_params = ind.get('default_params', {})

    if isinstance(formula, dict) and 'code' in formula:
        code = formula['code']

        # 동적 컬럼명 패턴
        if re.search(r"f['\"](\w+)_\{period\}['\"]|f['\"](\w+)_\{(\w+)\}['\"]:", code):
            # period 사용
            period = default_params.get('period', 20)
            indicator_output_map[name] = {
                'type': 'dynamic',
                'pattern': f'{name}_{{period}}',
                'example': f'{name}_{period}',
                'columns': output_cols
            }
        else:
            # 고정 컬럼명
            indicator_output_map[name] = {
                'type': 'static',
                'pattern': ', '.join(output_cols),
                'example': ', '.join(output_cols),
                'columns': output_cols
            }
    else:
        indicator_output_map[name] = {
            'type': 'static',
            'pattern': ', '.join(output_cols),
            'example': ', '.join(output_cols),
            'columns': output_cols
        }

# ============================================================
# 2. 템플릿 전략 - 요구하는 컬럼명
# ============================================================
templates = supabase.table('strategies').select('*').is_('user_id', 'null').order('name').execute()

template_data = {}

for t in templates.data:
    tname = t['name']
    config = t['config']

    # 지표 정보
    indicators_used = []
    for ind_config in config.get('indicators', []):
        ind_name = ind_config.get('name')
        params = ind_config.get('params', {})
        indicators_used.append({
            'name': ind_name,
            'params': params
        })

    # 조건에서 사용하는 컬럼
    buy_cols = set()
    sell_cols = set()

    for cond in config.get('buyConditions', []):
        left = cond.get('left')
        right = cond.get('right')

        if left and isinstance(left, str) and not str(left).replace('.','').replace('-','').isdigit():
            buy_cols.add(left)
        if right and isinstance(right, str) and not str(right).replace('.','').replace('-','').isdigit():
            buy_cols.add(right)

    for cond in config.get('sellConditions', []):
        left = cond.get('left')
        right = cond.get('right')

        if left and isinstance(left, str) and not str(left).replace('.','').replace('-','').isdigit():
            sell_cols.add(left)
        if right and isinstance(right, str) and not str(right).replace('.','').replace('-','').isdigit():
            sell_cols.add(right)

    template_data[tname] = {
        'indicators': indicators_used,
        'buy_columns': sorted(buy_cols),
        'sell_columns': sorted(sell_cols),
        'all_columns': sorted(buy_cols | sell_cols)
    }

# ============================================================
# Markdown 생성
# ============================================================
md = []

md.append('# 전략 및 지표 컬럼명 일관성 검증 리포트')
md.append('')
md.append('생성일: ' + str(supabase.table('indicators').select('updated_at').limit(1).execute().data[0]['updated_at']))
md.append('')

# 섹션 1: Indicators
md.append('## 1. Supabase Indicators - Formula가 생성하는 컬럼명')
md.append('')
md.append('| 지표명 | 타입 | 생성 패턴 | 예시 | output_columns |')
md.append('|--------|------|-----------|------|----------------|')

for ind_name in sorted(indicator_output_map.keys()):
    ind_data = indicator_output_map[ind_name]
    type_icon = '🔄' if ind_data['type'] == 'dynamic' else '📌'
    cols_str = ', '.join([f'`{c}`' for c in ind_data['columns']])
    md.append(f"| `{ind_name}` | {type_icon} {ind_data['type']} | `{ind_data['pattern']}` | `{ind_data['example']}` | {cols_str} |")

md.append('')
md.append('**범례:**')
md.append('- 🔄 dynamic: period 파라미터에 따라 컬럼명 변경 (예: sma_20, sma_60)')
md.append('- 📌 static: 고정된 컬럼명 사용')
md.append('')

# 섹션 2: 템플릿 전략
md.append('## 2. 템플릿 전략 - 사용하는 지표 및 컬럼')
md.append('')

for tname in sorted(template_data.keys()):
    tdata = template_data[tname]

    md.append(f'### {tname}')
    md.append('')

    # 사용 지표
    md.append('**사용 지표:**')
    for ind in tdata['indicators']:
        params_str = ', '.join([f"{k}={v}" for k, v in ind['params'].items()])
        md.append(f"- `{ind['name']}` ({params_str})")
    md.append('')

    # 매수 조건 컬럼
    md.append('**매수 조건에서 사용하는 컬럼:**')
    if tdata['buy_columns']:
        for col in tdata['buy_columns']:
            md.append(f'- `{col}`')
    else:
        md.append('- (없음)')
    md.append('')

    # 매도 조건 컬럼
    md.append('**매도 조건에서 사용하는 컬럼:**')
    if tdata['sell_columns']:
        for col in tdata['sell_columns']:
            md.append(f'- `{col}`')
    else:
        md.append('- (없음)')
    md.append('')

# 섹션 3: 전략빌더
md.append('## 3. 전략빌더(StrategyBuilder.tsx) - 사용 가능한 지표')
md.append('')
md.append('| 지표 ID | 지표명 | 타입 | 기본 파라미터 |')
md.append('|---------|--------|------|---------------|')

strategy_builder_indicators = [
  { 'id': 'ma', 'name': 'MA (이동평균)', 'type': 'trend', 'defaultParams': { 'period': 20 } },
  { 'id': 'sma', 'name': 'SMA (단순이동평균)', 'type': 'trend', 'defaultParams': { 'period': 20 } },
  { 'id': 'ema', 'name': 'EMA (지수이동평균)', 'type': 'trend', 'defaultParams': { 'period': 20 } },
  { 'id': 'bollinger', 'name': '볼린저밴드', 'type': 'volatility', 'defaultParams': { 'period': 20, 'std': 2 } },
  { 'id': 'rsi', 'name': 'RSI', 'type': 'momentum', 'defaultParams': { 'period': 14 } },
  { 'id': 'macd', 'name': 'MACD', 'type': 'momentum', 'defaultParams': { 'fast': 12, 'slow': 26, 'signal': 9 } },
  { 'id': 'stochastic', 'name': '스토캐스틱', 'type': 'momentum', 'defaultParams': { 'k': 14, 'd': 3 } },
  { 'id': 'ichimoku', 'name': '일목균형표', 'type': 'trend', 'defaultParams': { 'tenkan': 9, 'kijun': 26, 'senkou': 52, 'chikou': 26 } },
  { 'id': 'volume', 'name': '거래량', 'type': 'volume', 'defaultParams': { 'period': 20 } },
  { 'id': 'obv', 'name': 'OBV (누적거래량)', 'type': 'volume', 'defaultParams': {} },
  { 'id': 'vwap', 'name': 'VWAP (거래량가중평균)', 'type': 'volume', 'defaultParams': {} },
  { 'id': 'atr', 'name': 'ATR (변동성)', 'type': 'volatility', 'defaultParams': { 'period': 14 } },
  { 'id': 'cci', 'name': 'CCI', 'type': 'momentum', 'defaultParams': { 'period': 20 } },
  { 'id': 'williams', 'name': 'Williams %R', 'type': 'momentum', 'defaultParams': { 'period': 14 } },
  { 'id': 'adx', 'name': 'ADX (추세강도)', 'type': 'trend', 'defaultParams': { 'period': 14 } },
  { 'id': 'dmi', 'name': 'DMI (+DI/-DI)', 'type': 'trend', 'defaultParams': { 'period': 14 } },
  { 'id': 'parabolic', 'name': 'Parabolic SAR', 'type': 'trend', 'defaultParams': { 'acc': 0.02, 'max': 0.2 } }
]

for ind in strategy_builder_indicators:
    params_str = ', '.join([f"{k}={v}" for k, v in ind['defaultParams'].items()]) if ind['defaultParams'] else '(없음)'
    md.append(f"| `{ind['id']}` | {ind['name']} | {ind['type']} | {params_str} |")

md.append('')

# 섹션 4: 비교 분석
md.append('## 4. 비교 분석 및 검증 결과')
md.append('')

md.append('### 4.1 전략빌더 ↔ Supabase Indicators 일치 여부')
md.append('')
md.append('| 전략빌더 지표 | Supabase 존재 | 비고 |')
md.append('|--------------|--------------|------|')

for sb_ind in strategy_builder_indicators:
    ind_id = sb_ind['id']
    exists = '✅' if ind_id in indicator_output_map else '❌'
    note = ''
    if ind_id not in indicator_output_map:
        note = '⚠️ Supabase에 없음'
    md.append(f'| `{ind_id}` | {exists} | {note} |')

md.append('')

md.append('### 4.2 템플릿 전략 검증 결과')
md.append('')
md.append('| 템플릿 전략 | 상태 | 비고 |')
md.append('|------------|------|------|')

for tname in sorted(template_data.keys()):
    tdata = template_data[tname]

    # 각 지표가 생성할 컬럼 계산
    generated_cols = set(['close', 'open', 'high', 'low', 'volume'])

    for ind in tdata['indicators']:
        ind_name = ind['name']
        params = ind['params']

        if ind_name in indicator_output_map:
            ind_info = indicator_output_map[ind_name]
            if ind_info['type'] == 'dynamic':
                period = params.get('period', 20)
                generated_cols.add(f"{ind_name}_{period}")
            else:
                generated_cols.update(ind_info['columns'])

    # 사용하는 컬럼
    used_cols = set(tdata['all_columns'])

    # 불일치 검사
    missing = used_cols - generated_cols

    if missing:
        status = '⚠️'
        note = f"누락 컬럼: {', '.join(sorted(missing))}"
    else:
        status = '✅'
        note = '정상'

    md.append(f'| {tname} | {status} | {note} |')

md.append('')

# 섹션 5: 결론
md.append('## 5. 결론')
md.append('')
md.append('### 동적 컬럼명 생성 지표')
md.append('')

dynamic_inds = [name for name, data in indicator_output_map.items() if data['type'] == 'dynamic']
if dynamic_inds:
    for ind_name in sorted(dynamic_inds):
        md.append(f"- **`{ind_name}`**: `{ind_name}_{{period}}` 형태로 생성")
else:
    md.append('- (없음)')

md.append('')
md.append('### 정적 컬럼명 생성 지표')
md.append('')

static_inds = [name for name, data in indicator_output_map.items() if data['type'] == 'static']
md.append(f'총 {len(static_inds)}개의 지표가 고정된 컬럼명을 사용합니다.')
md.append('')

md.append('### 검증 요약')
md.append('')
md.append(f'- **전체 지표 수**: {len(indicator_output_map)}개')
md.append(f'- **전체 템플릿 수**: {len(template_data)}개')
md.append(f'- **전략빌더 지표 수**: {len(strategy_builder_indicators)}개')
md.append('')

# 파일 저장
md_content = '\n'.join(md)

with open('INDICATOR_COLUMN_COMPARISON.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print('✅ INDICATOR_COLUMN_COMPARISON.md 생성 완료')
print(f'   총 {len(md)} 라인')
print(f'   지표: {len(indicator_output_map)}개')
print(f'   템플릿: {len(template_data)}개')
