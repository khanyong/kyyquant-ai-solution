"""
n8n 없이 로컬에서 자동매매 시스템 실행
키움 API 직접 연동 및 스케줄링
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auto_trading_scheduler import AutoTradingScheduler
from scripts.kiwoom.kiwoom_bridge_server import KiwoomBridgeServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class LocalTradingSystem:
    """로컬 자동매매 시스템"""
    
    def __init__(self):
        self.scheduler = None
        self.bridge_server = None
        self.is_running = False
        
    def start(self):
        """시스템 시작"""
        try:
            logger.info("=" * 50)
            logger.info("로컬 자동매매 시스템 시작")
            logger.info("=" * 50)
            
            # 1. 키움 브리지 서버 시작 (별도 프로세스로 실행 필요)
            logger.info("1. 키움 브리지 서버 초기화...")
            # 주의: 키움 API는 32비트 Python 필요
            # self.bridge_server = KiwoomBridgeServer()
            # self.bridge_server.start()
            
            # 2. 자동매매 스케줄러 시작
            logger.info("2. 자동매매 스케줄러 초기화...")
            self.scheduler = AutoTradingScheduler()
            
            if not self.scheduler.initialize():
                logger.error("스케줄러 초기화 실패")
                return False
            
            self.is_running = True
            logger.info("시스템 시작 완료!")
            logger.info("-" * 50)
            logger.info("주요 기능:")
            logger.info("- 전략 실행: 1분마다")
            logger.info("- 포지션 업데이트: 5분마다")
            logger.info("- 장 시간: 09:00 ~ 15:30")
            logger.info("-" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"시스템 시작 실패: {e}")
            return False
    
    def run_simulation_mode(self):
        """시뮬레이션 모드로 실행 (실제 주문 없이)"""
        logger.info("=" * 50)
        logger.info("시뮬레이션 모드로 실행")
        logger.info("실제 주문은 실행되지 않습니다")
        logger.info("=" * 50)
        
        from tests.test_kiwoom_data_flow import KiwoomDataFlowTest
        
        # 테스트 데이터로 시뮬레이션
        test = KiwoomDataFlowTest()
        test.run_all_tests()
        
        logger.info("시뮬레이션 완료!")
    
    def check_status(self):
        """시스템 상태 확인"""
        status = {
            "scheduler": "running" if self.is_running else "stopped",
            "market": "open" if self.scheduler and self.scheduler.is_market_open() else "closed",
            "active_strategies": len(self.scheduler.active_strategies) if self.scheduler else 0,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info("-" * 50)
        logger.info("시스템 상태:")
        for key, value in status.items():
            logger.info(f"  {key}: {value}")
        logger.info("-" * 50)
        
        return status
    
    def stop(self):
        """시스템 종료"""
        logger.info("시스템을 종료합니다...")
        
        if self.scheduler:
            self.scheduler.stop()
            
        if self.bridge_server:
            self.bridge_server.stop()
            
        self.is_running = False
        logger.info("시스템 종료 완료")

def print_menu():
    """메뉴 출력"""
    print("\n" + "=" * 50)
    print("로컬 자동매매 시스템")
    print("=" * 50)
    print("1. 실제 모드 시작 (키움 API 필요)")
    print("2. 시뮬레이션 모드 (테스트 데이터)")
    print("3. 시스템 상태 확인")
    print("4. 종료")
    print("-" * 50)

def main():
    """메인 실행"""
    system = LocalTradingSystem()
    
    while True:
        print_menu()
        choice = input("선택하세요 (1-4): ")
        
        if choice == "1":
            print("\n⚠️  주의: 키움 OpenAPI가 설치되어 있어야 합니다.")
            print("⚠️  32비트 Python 환경이 필요할 수 있습니다.")
            confirm = input("계속하시겠습니까? (y/n): ")
            
            if confirm.lower() == 'y':
                if system.start():
                    print("✅ 시스템이 시작되었습니다.")
                    print("백그라운드에서 실행 중입니다...")
                else:
                    print("❌ 시스템 시작 실패")
                    
        elif choice == "2":
            print("\n시뮬레이션 모드를 실행합니다...")
            system.run_simulation_mode()
            
        elif choice == "3":
            system.check_status()
            
        elif choice == "4":
            if system.is_running:
                system.stop()
            print("프로그램을 종료합니다.")
            break
            
        else:
            print("잘못된 선택입니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다...")
        sys.exit(0)