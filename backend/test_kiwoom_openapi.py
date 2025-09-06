"""
키움증권 OpenAPI+ 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.kiwoom_openapi import test_kiwoom_openapi

if __name__ == "__main__":
    print("\n키움증권 OpenAPI+ 연동 테스트 시작\n")
    print("주의사항:")
    print("1. KOA Studio가 실행 중이어야 합니다")
    print("2. 키움증권 계정으로 로그인되어 있어야 합니다")
    print("3. 처음 실행 시 로그인 창이 나타날 수 있습니다\n")
    
    test_kiwoom_openapi()