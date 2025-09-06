"""
직접 매핑으로 종목명 수정
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# 깨진 이름 → 올바른 이름 직접 매핑
name_mapping = {
    '259960': '크래프톤',
    '267250': 'HD현대',
    '285130': 'SK케미칼',
    '367760': 'RISE 5G테크',
    '438900': 'HANARO Fn K-푸드',
    '449450': 'PLUS K방산',
    '469790': 'KIWOOM K-테크TOP10',
    '490480': 'SOL K방산',
    '032750': '삼진',
    '032850': '비트컴퓨터',
    '032860': '더라미',
    '033540': '파라텍',
    '033560': '블루콤',
    '033790': '피노',
    '036560': 'KZ정밀',
    '037440': '희림',
    '038290': '마크로젠',
    '041960': '코미팜',
    '042000': '카페24',
    '042500': '링네트',
    '043090': '더테크놀로지',
    '043150': '바텍',
    '043200': '파루',
    '046070': '코다코',
    '046210': 'HLB파나진',
    '049430': '코메론',
    '049950': '미래컴퍼니',
    '050120': 'ES큐브',
    '052330': '코텍',
    '052600': '한네트',
    '053290': 'NE능률',
    '053610': '프로텍',
    '054670': '대한뉴팜',
    '057030': 'YBM넷',
    '059090': '미코',
    '060260': '뉴보텍',
    '060720': 'KH바텍',
    '064260': '다날',
    '064480': '브리지텍',
    '078150': 'HB테크놀러지',
    '080530': '코디',
    '086960': 'MDS테크',
    '087010': '펩트론',
    '091340': 'S&K폴리텍',
    '091700': '파트론',
    '091970': '나노캠텍',
    '092460': '한라IMS',
}

print("="*50)
print("🔧 직접 매핑으로 종목명 수정")
print("="*50)

success = 0
for code, correct_name in name_mapping.items():
    try:
        supabase.table('kw_financial_snapshot')\
            .update({'stock_name': correct_name})\
            .eq('stock_code', code)\
            .execute()
        
        print(f"✅ {code}: {correct_name}")
        success += 1
        
    except Exception as e:
        print(f"❌ {code}: {e}")

print(f"\n✅ {success}개 수정 완료")

# 추가로 깨진 종목 확인
result = supabase.table('kw_financial_snapshot')\
    .select('stock_code, stock_name')\
    .execute()

remaining_broken = []
for r in result.data:
    if r['stock_name'] and any(c in r['stock_name'] for c in ['¶', '¸', '±', '°', '¿', 'À', 'Ã', '¼', '½', '¾']):
        remaining_broken.append((r['stock_code'], r['stock_name']))

if remaining_broken:
    print(f"\n아직 {len(remaining_broken)}개 깨진 종목이 남았습니다:")
    for code, name in remaining_broken[:20]:
        print(f"  {code}: {name[:20]}")
else:
    print("\n✅ 모든 종목명이 정상입니다!")

print("="*50)