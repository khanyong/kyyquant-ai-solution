"""
Supabase indicators 테이블 다운로드 스크립트
여러 형식으로 저장 가능: JSON, CSV, Excel
"""

import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
load_dotenv()

def download_indicators():
    """indicators 테이블 전체 데이터 다운로드"""

    # Supabase 연결
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        print("❌ Supabase 연결 정보가 없습니다.")
        print("   .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정하세요.")
        return None

    try:
        client = create_client(url, key)

        # 모든 indicators 데이터 가져오기
        print("📥 indicators 테이블 다운로드 중...")
        response = client.table('indicators').select('*').execute()

        if response.data:
            print(f"✅ {len(response.data)}개 지표 다운로드 완료")
            return response.data
        else:
            print("⚠️  indicators 테이블이 비어있습니다.")
            return []

    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return None

def save_as_json(data, filename=None):
    """JSON 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indicators_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 JSON 저장 완료: {filename}")
    return filename

def save_as_csv(data, filename=None):
    """CSV 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indicators_{timestamp}.csv"

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"💾 CSV 저장 완료: {filename}")
    return filename

def save_as_excel(data, filename=None):
    """Excel 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indicators_{timestamp}.xlsx"

    df = pd.DataFrame(data)

    # Excel Writer 설정
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='indicators', index=False)

        # 컬럼 너비 자동 조정
        worksheet = writer.sheets['indicators']
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_width + 2, 50)

    print(f"💾 Excel 저장 완료: {filename}")
    return filename

def save_as_sql(data, filename=None):
    """SQL INSERT 문으로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indicators_{timestamp}.sql"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Supabase indicators 테이블 데이터\n")
        f.write("-- Generated at: " + datetime.now().isoformat() + "\n\n")

        for item in data:
            # NULL 값 처리
            values = []
            for key, value in item.items():
                if value is None:
                    values.append("NULL")
                elif isinstance(value, str):
                    # 작은따옴표 이스케이프
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                elif isinstance(value, (dict, list)):
                    json_str = json.dumps(value, ensure_ascii=False).replace("'", "''")
                    values.append(f"'{json_str}'")
                else:
                    values.append(str(value))

            columns = ', '.join(item.keys())
            values_str = ', '.join(values)
            f.write(f"INSERT INTO indicators ({columns}) VALUES ({values_str});\n")

    print(f"💾 SQL 저장 완료: {filename}")
    return filename

def analyze_indicators(data):
    """다운로드한 지표 분석"""
    if not data:
        return

    print("\n" + "=" * 60)
    print("📊 지표 분석 결과")
    print("=" * 60)

    # 지표별 분류
    by_name = {}
    for item in data:
        name = item.get('name', 'unknown')
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(item)

    print(f"\n총 {len(data)}개 지표 정의")
    print(f"고유 지표명: {len(by_name)}개")

    print("\n지표별 상세:")
    for name, items in sorted(by_name.items()):
        print(f"\n📌 {name}: {len(items)}개 정의")
        for item in items:
            calc_type = item.get('calculation_type', 'unknown')
            description = item.get('description', '')[:50]
            print(f"   - ID: {item.get('id')}, Type: {calc_type}")
            if description:
                print(f"     {description}...")

            # formula 분석
            formula = item.get('formula')
            if formula:
                try:
                    formula_dict = json.loads(formula) if isinstance(formula, str) else formula
                    if 'method' in formula_dict:
                        print(f"     Method: {formula_dict['method']}")
                    if 'code' in formula_dict:
                        code_preview = formula_dict['code'][:100].replace('\n', ' ')
                        print(f"     Code: {code_preview}...")
                except:
                    pass

def create_backup_script(data):
    """백업/복원 스크립트 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Python 복원 스크립트
    script_filename = f"restore_indicators_{timestamp}.py"

    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write('''"""
Supabase indicators 테이블 복원 스크립트
사용법: python restore_indicators_TIMESTAMP.py
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# 백업 데이터
backup_data = ''')
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
        f.write('''

def restore():
    """indicators 테이블에 데이터 복원"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        print("❌ Supabase 연결 정보가 없습니다.")
        return

    client = create_client(url, key)

    print(f"복원할 지표: {len(backup_data)}개")
    response = input("계속하시겠습니까? (y/n): ")

    if response.lower() != 'y':
        print("복원 취소됨")
        return

    success = 0
    failed = 0

    for item in backup_data:
        try:
            # id 제거 (자동 생성되도록)
            item_copy = item.copy()
            if 'id' in item_copy:
                del item_copy['id']

            result = client.table('indicators').insert(item_copy).execute()
            success += 1
            print(f"✅ {item['name']} 복원 완료")
        except Exception as e:
            failed += 1
            print(f"❌ {item['name']} 복원 실패: {e}")

    print(f"\\n복원 완료: 성공 {success}, 실패 {failed}")

if __name__ == "__main__":
    restore()
''')

    print(f"💾 복원 스크립트 저장: {script_filename}")
    return script_filename

def main():
    """메인 함수"""
    print("=" * 60)
    print("Supabase Indicators 테이블 다운로드")
    print("=" * 60)

    # 데이터 다운로드
    data = download_indicators()

    if not data:
        print("\n다운로드할 데이터가 없습니다.")
        return

    # 저장 디렉토리 생성
    output_dir = "indicators_backup"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 모든 형식으로 저장
    print(f"\n📁 저장 디렉토리: {output_dir}")
    os.chdir(output_dir)

    files = []
    files.append(save_as_json(data))
    files.append(save_as_csv(data))
    files.append(save_as_excel(data))
    files.append(save_as_sql(data))
    files.append(create_backup_script(data))

    # 분석 결과 출력
    analyze_indicators(data)

    # 결과 요약
    print("\n" + "=" * 60)
    print("✅ 다운로드 완료")
    print("=" * 60)
    print(f"총 {len(data)}개 지표 저장됨")
    print(f"저장 위치: {os.getcwd()}")
    print("\n생성된 파일:")
    for file in files:
        print(f"  - {file}")

    # 사용 예시
    print("\n" + "=" * 60)
    print("📌 사용 방법")
    print("=" * 60)
    print("1. Excel에서 보기: indicators_*.xlsx 파일 열기")
    print("2. 다른 DB로 이전: indicators_*.sql 실행")
    print("3. 프로그래밍: indicators_*.json 또는 *.csv 로드")
    print("4. 복원하기: python restore_indicators_*.py")

if __name__ == "__main__":
    main()