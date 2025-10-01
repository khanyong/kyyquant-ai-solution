"""
Supabase indicators 테이블 간단 다운로드
빠르게 JSON으로만 저장
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not url or not key:
    print("❌ .env 파일에 SUPABASE_URL과 SUPABASE_KEY 설정 필요")
else:
    try:
        client = create_client(url, key)

        # 데이터 다운로드
        print("📥 다운로드 중...")
        response = client.table('indicators').select('*').order('name').execute()

        if response.data:
            # 파일명
            filename = f"indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # JSON 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(response.data, f, ensure_ascii=False, indent=2)

            print(f"✅ {len(response.data)}개 지표 저장 완료: {filename}")

            # 간단 요약
            print("\n📊 지표 요약:")
            indicators = {}
            for item in response.data:
                name = item.get('name', 'unknown')
                if name not in indicators:
                    indicators[name] = 0
                indicators[name] += 1

            for name, count in sorted(indicators.items()):
                print(f"  - {name}: {count}개")

        else:
            print("⚠️  테이블이 비어있음")

    except Exception as e:
        print(f"❌ 실패: {e}")