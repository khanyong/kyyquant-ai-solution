"""
모듈 설치 확인 스크립트
"""
import sys
import importlib

def check_module(module_name, import_path=None):
    """모듈 설치 확인"""
    try:
        if import_path:
            module = importlib.import_module(import_path)
        else:
            module = importlib.import_module(module_name)
        print(f"✅ {module_name}: 설치됨")
        if hasattr(module, '__version__'):
            print(f"   버전: {module.__version__}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: 설치 안됨")
        print(f"   오류: {e}")
        return False

print("="*50)
print("필수 모듈 확인")
print("="*50)
print(f"Python 버전: {sys.version}")
print(f"Python 경로: {sys.executable}")
print("-"*50)

# 필수 모듈 확인
modules = [
    ("PyQt5", "PyQt5.QtWidgets"),
    ("pykiwoom", None),
    ("pandas", None),
    ("supabase", None),
    ("dotenv", None),
    ("win32com", "win32com.client"),
]

all_installed = True
for module, import_path in modules:
    if not check_module(module, import_path):
        all_installed = False

print("-"*50)
if all_installed:
    print("✅ 모든 필수 모듈이 설치되어 있습니다!")
else:
    print("⚠️ 일부 모듈이 누락되었습니다.")
    print("\n설치 명령:")
    print("pip install PyQt5 pykiwoom pandas supabase python-dotenv pywin32")