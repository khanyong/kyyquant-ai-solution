"""
인코딩 문제 진단
"""
import sys
import locale

print("="*50)
print("시스템 인코딩 정보")
print("="*50)
print(f"Python 버전: {sys.version}")
print(f"기본 인코딩: {sys.getdefaultencoding()}")
print(f"파일시스템 인코딩: {sys.getfilesystemencoding()}")
print(f"stdout 인코딩: {sys.stdout.encoding}")
print(f"Locale: {locale.getdefaultlocale()}")
print(f"Preferred encoding: {locale.getpreferredencoding()}")

# pykiwoom 테스트
try:
    from PyQt5.QtWidgets import QApplication
    from pykiwoom.kiwoom import Kiwoom
    
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    
    if kiwoom.GetConnectState() == 0:
        print("\n키움 연결 중...")
        kiwoom.CommConnect()
        import time
        time.sleep(2)
    
    # 테스트 종목
    test_codes = ['005930', '000660', '035720']
    
    print("\n" + "="*50)
    print("종목명 인코딩 테스트")
    print("="*50)
    
    for code in test_codes:
        name = kiwoom.GetMasterCodeName(code)
        print(f"\n종목코드: {code}")
        print(f"원본 이름: {name}")
        print(f"타입: {type(name)}")
        print(f"repr: {repr(name)}")
        
        # 다양한 인코딩 시도
        try:
            # UTF-8로 인코딩
            utf8 = name.encode('utf-8')
            print(f"UTF-8 인코딩: {utf8}")
        except Exception as e:
            print(f"UTF-8 인코딩 실패: {e}")
        
        try:
            # CP949로 인코딩
            cp949 = name.encode('cp949')
            print(f"CP949 인코딩: {cp949}")
        except Exception as e:
            print(f"CP949 인코딩 실패: {e}")
            
except Exception as e:
    print(f"\n오류 발생: {e}")