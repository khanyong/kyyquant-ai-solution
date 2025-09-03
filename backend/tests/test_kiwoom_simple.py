"""
키움 OpenAPI 간단한 연결 테스트
pykiwoom 라이브러리 사용
"""

from pykiwoom.kiwoom import Kiwoom
import time

def test_kiwoom():
    print("=" * 50)
    print("키움 OpenAPI 연결 테스트 (pykiwoom)")
    print("=" * 50)
    
    try:
        # Kiwoom 객체 생성
        kiwoom = Kiwoom()
        
        # 로그인
        print("\n로그인 시도 중...")
        kiwoom.CommConnect(block=True)
        
        # 연결 상태 확인
        if kiwoom.GetConnectState() == 1:
            print("[SUCCESS] 키움 OpenAPI 연결 성공!")
            
            # 계좌 정보 가져오기
            accounts = kiwoom.GetLoginInfo("ACCNO")
            if accounts:
                print(f"\n계좌 목록: {accounts}")
                
            # 사용자 정보
            user_id = kiwoom.GetLoginInfo("USER_ID")
            user_name = kiwoom.GetLoginInfo("USER_NAME")
            print(f"사용자 ID: {user_id}")
            print(f"사용자 이름: {user_name}")
            
            # 서버 구분
            server = kiwoom.GetLoginInfo("GetServerGubun")
            if server:
                server_type = "모의투자" if "1" in server else "실거래"
                print(f"접속 서버: {server_type}")
            
            print("\n[SUCCESS] 테스트 완료!")
            return True
        else:
            print("[ERROR] 키움 OpenAPI 연결 실패")
            return False
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        print("\n해결 방법:")
        print("1. 키움 OpenAPI가 설치되어 있는지 확인")
        print("2. 32비트 Python을 사용하고 있는지 확인")
        print("3. 관리자 권한으로 실행")
        return False

if __name__ == "__main__":
    success = test_kiwoom()
    
    if success:
        print("\n키움 API를 사용할 준비가 되었습니다!")
    else:
        print("\n키움 API 연결에 문제가 있습니다.")