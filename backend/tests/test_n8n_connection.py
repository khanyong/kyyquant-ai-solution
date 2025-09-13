"""
n8n 서버 연결 및 자동매매 시스템 테스트
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from n8n_connector import N8NWorkflowManager, N8NConnector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_n8n_connection():
    """n8n 서버 연결 테스트"""
    print_header("n8n 서버 연결 테스트")
    
    # NAS IP 확인
    nas_ip = os.getenv('N8N_HOST', 'not_set')
    n8n_port = os.getenv('N8N_PORT', '5678')
    
    if nas_ip == 'not_set' or nas_ip == 'your-nas-ip-address':
        print("\n⚠️  .env 파일에 NAS IP 주소를 설정해주세요!")
        print("예시: N8N_HOST=192.168.1.100")
        return False
    
    print(f"\n📡 n8n 서버 정보:")
    print(f"  - NAS IP: {nas_ip}")
    print(f"  - Port: {n8n_port}")
    print(f"  - URL: http://{nas_ip}:{n8n_port}")
    
    # 연결 테스트
    connector = N8NConnector()
    
    print("\n🔌 연결 테스트 중...")
    if connector.test_connection():
        print("✅ n8n 서버 연결 성공!")
        return True
    else:
        print("❌ n8n 서버 연결 실패")
        print("\n확인사항:")
        print("1. NAS의 n8n 서버가 실행 중인가?")
        print("2. 방화벽이 포트를 차단하고 있지 않은가?")
        print("3. IP 주소가 올바른가?")
        return False

def import_workflows():
    """워크플로우 임포트"""
    print_header("n8n 워크플로우 임포트")
    
    manager = N8NWorkflowManager()
    
    workflows = [
        ('main-trading-workflow.json', '메인 트레이딩 워크플로우'),
        ('kiwoom-auto-trading.json', '키움 자동매매 워크플로우'),
        ('monitoring-workflow.json', '모니터링 워크플로우')
    ]
    
    print("\n📥 워크플로우 임포트 시작...")
    
    for filename, description in workflows:
        filepath = f"n8n-workflows/{filename}"
        print(f"\n  • {description}")
        print(f"    파일: {filepath}")
        
        if os.path.exists(filepath):
            success = manager.connector.import_workflow(filepath)
            if success:
                print("    ✅ 임포트 성공")
            else:
                print("    ❌ 임포트 실패")
        else:
            print(f"    ⚠️  파일을 찾을 수 없음")
    
    print("\n💡 팁: n8n 웹 UI에서 워크플로우 ID를 확인하고")
    print("    .env 파일에 다음과 같이 추가하세요:")
    print("    MAIN_TRADING_WORKFLOW_ID=xxx")
    print("    KIWOOM_TRADING_WORKFLOW_ID=xxx")
    print("    MONITORING_WORKFLOW_ID=xxx")

def test_workflow_trigger():
    """워크플로우 트리거 테스트"""
    print_header("워크플로우 실행 테스트")
    
    workflow_id = os.getenv('MAIN_TRADING_WORKFLOW_ID', '')
    
    if not workflow_id:
        print("\n⚠️  MAIN_TRADING_WORKFLOW_ID가 설정되지 않았습니다.")
        print("n8n 웹 UI에서 워크플로우 ID를 확인하고 .env에 추가하세요.")
        return
    
    manager = N8NWorkflowManager()
    
    # 테스트 데이터
    test_data = {
        'test': True,
        'timestamp': datetime.now().isoformat(),
        'message': '자동매매 시스템 테스트'
    }
    
    print(f"\n🚀 워크플로우 실행: {workflow_id}")
    print(f"   테스트 데이터: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    result = manager.connector.trigger_workflow(workflow_id, test_data)
    
    if result:
        print("\n✅ 워크플로우 실행 성공!")
        print(f"   결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print("\n❌ 워크플로우 실행 실패")

def check_system_status():
    """전체 시스템 상태 확인"""
    print_header("자동매매 시스템 상태")
    
    manager = N8NWorkflowManager()
    status = manager.get_status()
    
    print("\n📊 시스템 상태:")
    print(f"  • n8n 연결: {'✅ 연결됨' if status['n8n_connected'] else '❌ 연결 안됨'}")
    
    if status['workflows']:
        print("\n📋 워크플로우 상태:")
        for name, info in status['workflows'].items():
            print(f"  • {name}:")
            print(f"    - 마지막 실행: {info.get('last_run', '없음')}")
            print(f"    - 상태: {'완료' if info.get('status') else '실행중/실패'}")
    else:
        print("\n  워크플로우 정보 없음")

def main():
    """메인 실행"""
    while True:
        print("\n" + "=" * 60)
        print(" n8n 자동매매 시스템 테스트")
        print("=" * 60)
        print("\n1. n8n 서버 연결 테스트")
        print("2. 워크플로우 임포트")
        print("3. 워크플로우 실행 테스트")
        print("4. 시스템 상태 확인")
        print("5. 종료")
        print("-" * 60)
        
        choice = input("\n선택 (1-5): ")
        
        if choice == "1":
            test_n8n_connection()
        elif choice == "2":
            if test_n8n_connection():
                import_workflows()
        elif choice == "3":
            if test_n8n_connection():
                test_workflow_trigger()
        elif choice == "4":
            check_system_status()
        elif choice == "5":
            print("\n프로그램을 종료합니다.")
            break
        else:
            print("\n잘못된 선택입니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다...")
        sys.exit(0)