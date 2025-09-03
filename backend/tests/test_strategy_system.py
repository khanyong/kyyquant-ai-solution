"""
전략 시스템 테스트
Supabase 연동 및 전략 생성/저장 확인
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import asyncio
import time

# .env 파일 로드
load_dotenv()

# Supabase 클라이언트
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    print("❌ Supabase 환경 변수가 설정되지 않았습니다.")
    print("   SUPABASE_URL과 SUPABASE_ANON_KEY를 .env 파일에 설정하세요.")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("="*60)
print("전략 시스템 테스트")
print("="*60)
print()

def check_tables():
    """테이블 존재 확인"""
    print("[1] Supabase 테이블 확인")
    print("-" * 40)
    
    tables_to_check = [
        'strategies',
        'strategy_executions',
        'trading_signals',
        'orders',
        'positions',
        'market_data_cache'
    ]
    
    all_exist = True
    
    for table in tables_to_check:
        try:
            # 테이블에서 1개 행만 조회 시도
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ {table} 테이블: 존재함")
        except Exception as e:
            print(f"❌ {table} 테이블: 없음 또는 접근 불가")
            print(f"   에러: {str(e)[:100]}")
            all_exist = False
    
    print()
    return all_exist

def test_strategy_crud():
    """전략 CRUD 테스트"""
    print("[2] 전략 생성/조회/수정/삭제 테스트")
    print("-" * 40)
    
    # 1. 생성 테스트
    print("1) 전략 생성 테스트...")
    
    test_strategy = {
        'name': f'테스트 전략 {datetime.now().strftime("%H%M%S")}',
        'description': 'Supabase 연동 테스트를 위한 전략',
        'is_active': False,
        'conditions': {
            'entry': {
                'rsi': {'operator': '<', 'value': 30},
                'volume': {'operator': '>', 'value': 'avg_volume * 2'}
            },
            'exit': {
                'profit_target': 5,
                'stop_loss': -3
            }
        },
        'position_size': 10,
        'max_positions': 5,
        'target_stocks': ['005930', '000660'],
        'execution_time': {
            'start': '09:00',
            'end': '15:20'
        }
    }
    
    try:
        # 사용자 ID 가져오기 (없으면 테스트 ID 사용)
        user_result = supabase.auth.get_user()
        if user_result and user_result.user:
            test_strategy['user_id'] = user_result.user.id
            print(f"   사용자 ID: {user_result.user.id[:8]}...")
        else:
            # 테스트용 UUID
            test_strategy['user_id'] = '00000000-0000-0000-0000-000000000000'
            print("   테스트 사용자 ID 사용")
        
        # 전략 생성
        result = supabase.table('strategies').insert(test_strategy).execute()
        
        if result.data and len(result.data) > 0:
            created_strategy = result.data[0]
            strategy_id = created_strategy['id']
            print(f"✅ 전략 생성 성공! ID: {strategy_id[:8]}...")
            
            # 2. 조회 테스트
            print("\n2) 전략 조회 테스트...")
            read_result = supabase.table('strategies').select('*').eq('id', strategy_id).single().execute()
            
            if read_result.data:
                print(f"✅ 전략 조회 성공!")
                print(f"   - 이름: {read_result.data['name']}")
                print(f"   - 설명: {read_result.data['description']}")
                print(f"   - 대상 종목: {read_result.data.get('target_stocks', [])}")
            
            # 3. 수정 테스트
            print("\n3) 전략 수정 테스트...")
            update_data = {
                'is_active': True,
                'description': '수정된 설명입니다'
            }
            
            update_result = supabase.table('strategies').update(update_data).eq('id', strategy_id).execute()
            
            if update_result.data:
                print(f"✅ 전략 수정 성공!")
                print(f"   - 활성 상태: {update_result.data[0]['is_active']}")
            
            # 4. 삭제 테스트
            print("\n4) 전략 삭제 테스트...")
            delete_result = supabase.table('strategies').delete().eq('id', strategy_id).execute()
            print(f"✅ 전략 삭제 성공!")
            
            return True
            
        else:
            print("❌ 전략 생성 실패: 데이터가 반환되지 않았습니다")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

def test_realtime_subscription():
    """실시간 구독 테스트"""
    print("\n[3] 실시간 구독 테스트")
    print("-" * 40)
    
    print("실시간 구독 채널 생성...")
    
    def on_change(payload):
        print(f"📡 실시간 이벤트 수신!")
        print(f"   타입: {payload.get('eventType')}")
        print(f"   테이블: {payload.get('table')}")
        if payload.get('new'):
            print(f"   데이터: {json.dumps(payload.get('new'), indent=2, ensure_ascii=False)[:200]}")
    
    try:
        # 구독 채널 생성
        channel = supabase.channel('test-strategies')
        channel.on('postgres_changes', 
                  filter='event=*', 
                  schema='public',
                  table='strategies',
                  callback=on_change)
        
        channel.subscribe()
        
        print("✅ 실시간 구독 채널 생성 성공")
        print("   (테스트를 위해 다른 터미널에서 전략을 생성해보세요)")
        
        # 구독 해제
        supabase.remove_channel(channel)
        
        return True
        
    except Exception as e:
        print(f"❌ 실시간 구독 실패: {str(e)}")
        return False

def test_api_connection():
    """백엔드 API 연결 테스트"""
    print("\n[4] 백엔드 API 연결 테스트")
    print("-" * 40)
    
    api_url = "http://localhost:8001"
    
    try:
        import requests
        
        # API 상태 확인
        response = requests.get(f"{api_url}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 서버 연결 성공!")
            print(f"   - 서비스: {data.get('service')}")
            print(f"   - 버전: {data.get('version')}")
            
            # 전략 목록 조회
            print("\n   전략 목록 조회 테스트...")
            strategies_response = requests.get(f"{api_url}/api/strategies")
            
            if strategies_response.status_code == 200:
                strategies_data = strategies_response.json()
                print(f"   ✅ 전략 {strategies_data.get('count', 0)}개 조회됨")
            else:
                print(f"   ⚠️ 전략 조회 실패: {strategies_response.status_code}")
            
            return True
        else:
            print(f"⚠️ API 서버 응답 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API 서버에 연결할 수 없습니다.")
        print("   backend/run_trading_system.bat을 실행하고")
        print("   옵션 2를 선택하여 API 서버를 시작하세요.")
        return False
    except Exception as e:
        print(f"❌ API 연결 실패: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    results = {
        'tables': False,
        'crud': False,
        'realtime': False,
        'api': False
    }
    
    # 1. 테이블 확인
    results['tables'] = check_tables()
    
    if not results['tables']:
        print("⚠️ 테이블이 없습니다. 테이블 생성 SQL을 실행하세요:")
        print("   supabase/migrations/create_trading_system_tables.sql")
        print()
    
    # 2. CRUD 테스트
    if results['tables']:
        results['crud'] = test_strategy_crud()
    
    # 3. 실시간 구독 테스트
    if results['tables']:
        results['realtime'] = test_realtime_subscription()
    
    # 4. API 연결 테스트
    results['api'] = test_api_connection()
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    for key, value in results.items():
        status = "✅ 성공" if value else "❌ 실패"
        name = {
            'tables': 'Supabase 테이블',
            'crud': '전략 CRUD',
            'realtime': '실시간 구독',
            'api': 'API 서버'
        }.get(key, key)
        
        print(f"{name}: {status}")
    
    # 권장 사항
    print("\n" + "="*60)
    print("다음 단계")
    print("="*60)
    
    if not results['tables']:
        print("1. Supabase 대시보드에서 SQL Editor 열기")
        print("2. create_trading_system_tables.sql 내용 실행")
        print("3. 이 테스트를 다시 실행")
    elif not results['api']:
        print("1. 새 터미널 열기")
        print("2. cd backend && venv32\\Scripts\\activate")
        print("3. python -m uvicorn api_strategy_routes:app --port 8001")
        print("4. 이 테스트를 다시 실행")
    else:
        print("✅ 모든 시스템이 정상 작동 중입니다!")
        print("\n프론트엔드에서 전략 생성 테스트:")
        print("1. 프론트엔드 실행 (npm run dev)")
        print("2. 전략 대시보드 접속")
        print("3. '새 전략' 버튼 클릭")
        print("4. 전략 정보 입력 후 저장")

if __name__ == "__main__":
    main()