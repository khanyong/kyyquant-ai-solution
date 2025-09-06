"""
키움 OpenAPI+ 연결 테스트
"""
import sys
from PyQt5.QWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom

def test_connection():
    """키움 API 연결 테스트"""
    print("🔌 키움 OpenAPI+ 연결 테스트 시작...")
    
    # PyQt 앱 생성
    app = QApplication(sys.argv)
    
    # 키움 객체 생성
    kiwoom = Kiwoom()
    
    # 로그인
    kiwoom.CommConnect()
    
    # 연결 상태 확인
    if kiwoom.GetConnectState() == 1:
        print("✅ 연결 성공!")
        
        # 계좌 정보
        accounts = kiwoom.GetLoginInfo("ACCNO")
        print(f"📌 계좌번호: {accounts}")
        
        # 사용자 정보
        user_id = kiwoom.GetLoginInfo("USER_ID")
        user_name = kiwoom.GetLoginInfo("USER_NAME")
        print(f"📌 사용자: {user_name} ({user_id})")
        
        # 종목 테스트 (삼성전자)
        name = kiwoom.GetMasterCodeName("005930")
        print(f"📌 종목명 조회 테스트: 005930 = {name}")
        
    else:
        print("❌ 연결 실패")
    
    return kiwoom

if __name__ == "__main__":
    try:
        kiwoom = test_connection()
        print("\n테스트 완료! 창을 닫아주세요.")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print("\n키움 OpenAPI+가 설치되어 있는지 확인하세요.")
        print("설치 방법:")
        print("1. 키움증권 홈페이지에서 OpenAPI+ 다운로드")
        print("2. 모듈 설치 후 키움 로그인")
        print("3. pip install pykiwoom")