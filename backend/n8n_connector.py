"""
n8n 서버 연결 및 워크플로우 실행 관리
"""

import requests
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime

from n8n_config import N8NConfig

logger = logging.getLogger(__name__)

class N8NConnector:
    """n8n 서버 연결 관리"""
    
    def __init__(self):
        self.base_url = N8NConfig.get_n8n_url()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Basic Auth 설정
        if N8NConfig.N8N_BASIC_AUTH_USER:
            import base64
            credentials = f"{N8NConfig.N8N_BASIC_AUTH_USER}:{N8NConfig.N8N_BASIC_AUTH_PASSWORD}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self.headers['Authorization'] = f'Basic {encoded}'
        
        # API Key 설정
        if N8NConfig.N8N_API_KEY:
            self.headers['X-N8N-API-KEY'] = N8NConfig.N8N_API_KEY
    
    def test_connection(self) -> bool:
        """n8n 서버 연결 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/healthz",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ n8n 서버 연결 성공: {self.base_url}")
                return True
            else:
                logger.error(f"❌ n8n 서버 연결 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ n8n 서버 연결 실패: {e}")
            return False
    
    def trigger_workflow(self, workflow_id: str, data: Dict = None) -> Optional[Dict]:
        """워크플로우 실행 트리거"""
        try:
            webhook_url = N8NConfig.get_webhook_url(workflow_id)
            
            logger.info(f"워크플로우 실행: {workflow_id}")
            
            response = requests.post(
                webhook_url,
                json=data or {},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ 워크플로우 실행 성공")
                return response.json()
            else:
                logger.error(f"❌ 워크플로우 실행 실패: {response.status_code}")
                logger.error(response.text)
                return None
                
        except Exception as e:
            logger.error(f"❌ 워크플로우 실행 에러: {e}")
            return None
    
    def get_workflow_executions(self, workflow_id: str, limit: int = 10) -> Optional[List]:
        """워크플로우 실행 기록 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                params={
                    'workflowId': workflow_id,
                    'limit': limit
                },
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"실행 기록 조회 실패: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"실행 기록 조회 에러: {e}")
            return None
    
    def import_workflow(self, workflow_json_path: str) -> bool:
        """워크플로우 JSON 파일 임포트"""
        try:
            with open(workflow_json_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                json=workflow_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ 워크플로우 임포트 성공: {workflow_data.get('name')}")
                return True
            else:
                logger.error(f"❌ 워크플로우 임포트 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 워크플로우 임포트 에러: {e}")
            return False

class N8NWorkflowManager:
    """n8n 워크플로우 관리"""
    
    def __init__(self):
        self.connector = N8NConnector()
        
    def setup_workflows(self):
        """모든 워크플로우 설정"""
        workflows = [
            'n8n-workflows/main-trading-workflow.json',
            'n8n-workflows/kiwoom-auto-trading.json',
            'n8n-workflows/monitoring-workflow.json'
        ]
        
        for workflow_path in workflows:
            logger.info(f"워크플로우 임포트: {workflow_path}")
            self.connector.import_workflow(workflow_path)
    
    def start_auto_trading(self, strategy_id: str):
        """자동매매 시작"""
        data = {
            'action': 'start',
            'strategy_id': strategy_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.connector.trigger_workflow(
            N8NConfig.MAIN_TRADING_WORKFLOW_ID,
            data
        )
    
    def stop_auto_trading(self, strategy_id: str):
        """자동매매 중지"""
        data = {
            'action': 'stop',
            'strategy_id': strategy_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.connector.trigger_workflow(
            N8NConfig.MAIN_TRADING_WORKFLOW_ID,
            data
        )
    
    def execute_trade(self, signal_data: Dict):
        """매매 실행"""
        return self.connector.trigger_workflow(
            N8NConfig.KIWOOM_TRADING_WORKFLOW_ID,
            signal_data
        )
    
    def get_status(self):
        """시스템 상태 조회"""
        status = {
            'n8n_connected': self.connector.test_connection(),
            'workflows': {}
        }
        
        # 각 워크플로우 실행 기록 확인
        workflow_ids = [
            ('main_trading', N8NConfig.MAIN_TRADING_WORKFLOW_ID),
            ('kiwoom_trading', N8NConfig.KIWOOM_TRADING_WORKFLOW_ID),
            ('monitoring', N8NConfig.MONITORING_WORKFLOW_ID)
        ]
        
        for name, workflow_id in workflow_ids:
            if workflow_id:
                executions = self.connector.get_workflow_executions(workflow_id, 1)
                if executions:
                    last_execution = executions[0]
                    status['workflows'][name] = {
                        'last_run': last_execution.get('startedAt'),
                        'status': last_execution.get('finished', False)
                    }
        
        return status

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 50)
    print("n8n 서버 연결 테스트")
    print("=" * 50)
    
    # .env 파일에 NAS IP 설정 필요
    print("\n⚠️  .env 파일에 다음 설정이 필요합니다:")
    print("N8N_HOST=your-nas-ip-address")
    print("N8N_PORT=5678")
    print()
    
    manager = N8NWorkflowManager()
    
    # 연결 테스트
    if manager.connector.test_connection():
        print("\n✅ n8n 서버 연결 성공!")
        
        # 상태 확인
        status = manager.get_status()
        print("\n시스템 상태:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print("\n❌ n8n 서버 연결 실패")
        print("NAS의 n8n 서버가 실행 중인지 확인하세요.")