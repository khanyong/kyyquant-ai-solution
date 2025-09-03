"""
키움증권 하이브리드 시스템 설정 및 테스트
OpenAPI + REST API 통합 환경 구성
"""

import os
import sys
import json
import subprocess
import platform
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridSystemSetup:
    """하이브리드 시스템 설정 도우미"""
    
    def __init__(self):
        self.env_file = Path(".env")
        load_dotenv()
        self.setup_status = {
            "32bit_python": False,
            "openapi_installed": False,
            "rest_api_keys": False,
            "bridge_server": False,
            "test_passed": False
        }
    
    def check_32bit_python(self):
        """32비트 Python 설치 확인"""
        logger.info("32비트 Python 환경 확인 중...")
        
        # venv32 폴더 확인
        venv32_path = Path("venv32")
        if venv32_path.exists():
            # 가상환경의 Python 확인
            python_exe = venv32_path / "Scripts" / "python.exe"
            if python_exe.exists():
                result = subprocess.run(
                    [str(python_exe), "-c", "import platform; print(platform.architecture()[0])"],
                    capture_output=True,
                    text=True
                )
                if "32bit" in result.stdout:
                    logger.info("✅ 32비트 Python 가상환경 확인됨")
                    self.setup_status["32bit_python"] = True
                    return True
        
        logger.warning("❌ 32비트 Python 환경이 없습니다. setup_32bit_env.bat 실행 필요")
        return False
    
    def check_openapi_installation(self):
        """키움 OpenAPI 설치 확인"""
        logger.info("키움 OpenAPI 설치 확인 중...")
        
        openapi_path = Path("C:/OpenAPI")
        if openapi_path.exists():
            # 주요 파일 확인
            required_files = ["bin", "log", "data"]
            if all((openapi_path / f).exists() for f in required_files):
                logger.info("✅ 키움 OpenAPI 설치 확인됨")
                self.setup_status["openapi_installed"] = True
                return True
        
        logger.warning("❌ 키움 OpenAPI가 설치되지 않았습니다")
        logger.info("https://www3.kiwoom.com/nkw.templateFrameSet.do?m=m1408000000 에서 다운로드")
        return False
    
    def setup_rest_api_keys(self):
        """REST API 키 설정"""
        logger.info("키움 REST API 키 설정 확인 중...")
        
        app_key = os.getenv("KIWOOM_APP_KEY")
        app_secret = os.getenv("KIWOOM_APP_SECRET")
        
        if app_key and app_secret:
            logger.info("✅ REST API 키 설정됨")
            self.setup_status["rest_api_keys"] = True
            return True
        
        logger.warning("❌ REST API 키가 설정되지 않았습니다")
        logger.info("키움증권 개발자센터에서 API 키 발급 필요:")
        logger.info("https://apiportal.koreainvestment.com/")
        
        # 사용자 입력 받기
        print("\nREST API 키를 입력하시겠습니까? (y/n): ", end="")
        if input().lower() == 'y':
            app_key = input("APP_KEY: ").strip()
            app_secret = input("APP_SECRET: ").strip()
            
            if app_key and app_secret:
                set_key(self.env_file, "KIWOOM_APP_KEY", app_key)
                set_key(self.env_file, "KIWOOM_APP_SECRET", app_secret)
                set_key(self.env_file, "KIWOOM_API_URL", "https://openapi.koreainvestment.com:9443")
                logger.info("✅ REST API 키 저장됨")
                self.setup_status["rest_api_keys"] = True
                return True
        
        return False
    
    def test_bridge_server(self):
        """브리지 서버 테스트"""
        logger.info("OpenAPI 브리지 서버 테스트 중...")
        
        try:
            # 브리지 서버 상태 확인
            response = requests.get("http://localhost:8100/", timeout=2)
            if response.status_code == 200:
                logger.info("✅ 브리지 서버 실행 중")
                self.setup_status["bridge_server"] = True
                return True
        except:
            pass
        
        logger.warning("❌ 브리지 서버가 실행되지 않음")
        logger.info("다음 명령으로 브리지 서버 실행:")
        logger.info("cd backend && venv32\\Scripts\\activate && python kiwoom_openapi_bridge.py")
        return False
    
    def run_integration_test(self):
        """통합 테스트"""
        logger.info("하이브리드 시스템 통합 테스트 중...")
        
        test_results = []
        
        # 1. REST API 연결 테스트
        if self.setup_status["rest_api_keys"]:
            try:
                # OAuth 토큰 테스트 (실제로는 인증 필요)
                logger.info("- REST API 연결 테스트: 보류 (실제 인증 필요)")
                test_results.append(("REST API", "PENDING"))
            except Exception as e:
                test_results.append(("REST API", f"FAIL: {e}"))
        
        # 2. OpenAPI 브리지 테스트
        if self.setup_status["bridge_server"]:
            try:
                response = requests.get("http://localhost:8100/")
                if response.json()["status"] == "running":
                    test_results.append(("OpenAPI Bridge", "PASS"))
                else:
                    test_results.append(("OpenAPI Bridge", "FAIL"))
            except Exception as e:
                test_results.append(("OpenAPI Bridge", f"FAIL: {e}"))
        
        # 결과 출력
        logger.info("\n" + "="*50)
        logger.info("통합 테스트 결과:")
        for test_name, result in test_results:
            status = "✅" if "PASS" in result else "⚠️" if "PENDING" in result else "❌"
            logger.info(f"  {status} {test_name}: {result}")
        
        all_passed = all("PASS" in r or "PENDING" in r for _, r in test_results)
        self.setup_status["test_passed"] = all_passed
        return all_passed
    
    def generate_startup_script(self):
        """시작 스크립트 생성"""
        logger.info("시작 스크립트 생성 중...")
        
        script_content = """@echo off
echo ========================================
echo 키움 하이브리드 시스템 시작
echo ========================================
echo.

REM 1. OpenAPI 브리지 서버 시작 (32비트)
echo [1] OpenAPI 브리지 서버 시작 중...
start "OpenAPI Bridge" cmd /k "cd /d %~dp0 && venv32\\Scripts\\activate && python kiwoom_openapi_bridge.py"

timeout /t 3 /nobreak > nul

REM 2. 메인 API 서버 시작 (64비트)
echo [2] 메인 API 서버 시작 중...
start "Main API Server" cmd /k "cd /d %~dp0 && python main_api_server.py"

timeout /t 3 /nobreak > nul

REM 3. 상태 확인
echo [3] 시스템 상태 확인 중...
curl -s http://localhost:8100/ > nul
if %errorlevel% equ 0 (
    echo [+] OpenAPI 브리지 서버: 정상
) else (
    echo [!] OpenAPI 브리지 서버: 오류
)

curl -s http://localhost:8000/ > nul
if %errorlevel% equ 0 (
    echo [+] 메인 API 서버: 정상
) else (
    echo [!] 메인 API 서버: 오류
)

echo.
echo ========================================
echo 하이브리드 시스템 시작 완료!
echo.
echo 접속 URL:
echo - OpenAPI Bridge: http://localhost:8100
echo - Main API: http://localhost:8000
echo - Web UI: http://localhost:3000
echo ========================================
pause
"""
        
        script_path = Path("start_hybrid_system.bat")
        script_path.write_text(script_content)
        logger.info(f"✅ 시작 스크립트 생성됨: {script_path}")
    
    def print_summary(self):
        """설정 요약 출력"""
        print("\n" + "="*60)
        print("🚀 키움 하이브리드 시스템 설정 상태")
        print("="*60)
        
        status_emoji = {
            True: "✅",
            False: "❌"
        }
        
        print(f"\n기본 구성:")
        print(f"  {status_emoji[self.setup_status['32bit_python']]} 32비트 Python 환경")
        print(f"  {status_emoji[self.setup_status['openapi_installed']]} 키움 OpenAPI 설치")
        print(f"  {status_emoji[self.setup_status['rest_api_keys']]} REST API 키 설정")
        print(f"  {status_emoji[self.setup_status['bridge_server']]} OpenAPI 브리지 서버")
        print(f"  {status_emoji[self.setup_status['test_passed']]} 통합 테스트")
        
        all_ready = all(self.setup_status.values())
        
        if all_ready:
            print("\n✅ 모든 구성이 완료되었습니다!")
            print("start_hybrid_system.bat을 실행하여 시스템을 시작하세요.")
        else:
            print("\n⚠️ 추가 설정이 필요합니다:")
            
            if not self.setup_status['32bit_python']:
                print("\n1. 32비트 Python 설정:")
                print("   backend\\setup_32bit_env.bat 실행")
            
            if not self.setup_status['openapi_installed']:
                print("\n2. 키움 OpenAPI 설치:")
                print("   https://www3.kiwoom.com/ 에서 OpenAPI+ 다운로드")
            
            if not self.setup_status['rest_api_keys']:
                print("\n3. REST API 키 발급:")
                print("   https://apiportal.koreainvestment.com/ 에서 신청")
            
            if not self.setup_status['bridge_server']:
                print("\n4. 브리지 서버 실행:")
                print("   cd backend && venv32\\Scripts\\activate")
                print("   python kiwoom_openapi_bridge.py")
        
        print("\n" + "="*60)

def main():
    """메인 실행 함수"""
    print("키움증권 하이브리드 시스템 설정 도우미")
    print("="*60)
    
    setup = HybridSystemSetup()
    
    # 단계별 확인
    setup.check_32bit_python()
    setup.check_openapi_installation()
    setup.setup_rest_api_keys()
    setup.test_bridge_server()
    
    # 통합 테스트
    if setup.setup_status["bridge_server"]:
        setup.run_integration_test()
    
    # 시작 스크립트 생성
    setup.generate_startup_script()
    
    # 요약 출력
    setup.print_summary()

if __name__ == "__main__":
    main()