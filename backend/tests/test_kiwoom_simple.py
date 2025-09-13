"""
키움 API 간단 테스트
"""
print("1. 임포트 테스트...")

try:
    import sys
    print(f"   Python: {sys.version}")
    print(f"   경로: {sys.executable}")
except Exception as e:
    print(f"   실패: {e}")

try:
    import PyQt5.QtWidgets
    from PyQt5.QtWidgets import QApplication
    print("   PyQt5: OK")
except Exception as e:
    print(f"   PyQt5 실패: {e}")
    try:
        import PyQt5.QtCore
        print("   PyQt5.QtCore: OK")
    except:
        pass

try:
    from pykiwoom.kiwoom import Kiwoom
    print("   pykiwoom: OK")
except Exception as e:
    print(f"   pykiwoom 실패: {e}")

print("\n2. 키움 연결 테스트...")
try:
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    print("   키움 객체 생성: OK")
    
    # 연결
    kiwoom.CommConnect()
    print("   연결 시도 중...")
    
except Exception as e:
    print(f"   실패: {e}")

print("\n테스트 완료")