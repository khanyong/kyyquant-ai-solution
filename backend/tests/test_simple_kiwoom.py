"""
키움증권 OpenAPI 간단 테스트
32비트 Python 환경에서 실행
"""

import sys
import os

print("="*60)
print("키움 OpenAPI 간단 연결 테스트")
print("="*60)
print()

# 1. Python 버전 확인
print("[1] Python 환경 확인")
print(f"Python 버전: {sys.version}")

import platform
print(f"아키텍처: {platform.architecture()[0]}")

if "64" in platform.architecture()[0]:
    print("\n[WARNING] 64비트 Python입니다!")
    print("32비트 환경에서 실행해주세요:")
    print("venv32\\Scripts\\activate")
    sys.exit(1)
else:
    print("[OK] 32비트 Python 확인됨")

print()

# 2. 필수 모듈 확인
print("[2] 필수 모듈 확인")
try:
    from PyQt5 import QtCore
    print(f"[OK] PyQt5 버전: {QtCore.QT_VERSION_STR}")
except ImportError:
    print("[ERROR] PyQt5가 설치되지 않았습니다")
    print("pip install PyQt5==5.15.10")
    sys.exit(1)

try:
    import win32com.client
    print("[OK] pywin32 설치됨")
except ImportError:
    print("[ERROR] pywin32가 설치되지 않았습니다")
    print("pip install pywin32")
    sys.exit(1)

print()

# 3. QAxContainer 테스트
print("[3] QAxContainer 테스트")
try:
    from PyQt5.QAxContainer import QAxWidget
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    print("[OK] QApplication 생성 성공")
    
    # OCX 생성 시도
    try:
        ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        print("[OK] 키움 OpenAPI OCX 로드 성공!")
        print("\n✅ 키움 OpenAPI를 사용할 준비가 되었습니다!")
        
        # 간단한 정보 출력
        print("\n[4] API 정보")
        print("연결 상태:", ocx.dynamicCall("GetConnectState()"))
        print("(0: 미연결, 1: 연결됨)")
        
    except Exception as e:
        print(f"[ERROR] OCX 로드 실패: {e}")
        print("\n가능한 원인:")
        print("1. 키움 OpenAPI가 설치되지 않았습니다")
        print("2. 관리자 권한이 필요할 수 있습니다")
        print("3. OCX 등록이 필요할 수 있습니다")
        print("\n해결 방법:")
        print("1. https://www3.kiwoom.com/ 에서 OpenAPI+ 설치")
        print("2. 관리자 권한으로 실행")
        print("3. regsvr32 C:\\OpenAPI\\bin\\khopenapi.ocx")
        
except Exception as e:
    print(f"[ERROR] QAxContainer 오류: {e}")

print()
print("="*60)
print("테스트 완료")
print("="*60)

# 정상 종료
if 'app' in locals():
    sys.exit(0)