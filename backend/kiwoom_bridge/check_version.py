#!/usr/bin/env python
"""
backtest_engine_advanced.py 버전 확인 스크립트
Core 모듈 사용 여부를 체크합니다.
"""

import os
import sys

def check_file_version(filepath="backtest_engine_advanced.py"):
    """파일이 Core 모듈을 사용하는지 확인"""

    if not os.path.exists(filepath):
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 체크 항목
    checks = {
        "Core 임포트": "from core import" in content,
        "USE_CORE 변수": "USE_CORE" in content,
        "compute_indicators 호출": "compute_indicators(" in content,
        "evaluate_conditions 호출": "evaluate_conditions(" in content,
        "자체 TechnicalIndicators 클래스": "class TechnicalIndicators" in content,
        "자체 SignalGenerator 클래스": "class SignalGenerator" in content
    }

    print("="*60)
    print(f"파일 버전 확인: {filepath}")
    print("="*60)

    core_count = 0
    legacy_count = 0

    for check_name, result in checks.items():
        if "Core" in check_name or "USE_CORE" in check_name:
            if result:
                print(f"✅ {check_name}: 있음")
                core_count += 1
            else:
                print(f"❌ {check_name}: 없음")
        elif "자체" in check_name:
            if result:
                print(f"⚠️  {check_name}: 있음 (레거시)")
                legacy_count += 1
            else:
                print(f"✅ {check_name}: 없음 (좋음)")
        else:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'있음' if result else '없음'}")
            if result:
                core_count += 1

    print("\n" + "="*60)

    # 최종 판정
    if core_count >= 3 and legacy_count == 0:
        print("✅ Core 모듈 전용 버전 (최신)")
        return "CORE_ONLY"
    elif core_count >= 2:
        print("⚠️  Core 모듈 부분 사용 버전 (혼합)")
        return "MIXED"
    else:
        print("❌ 레거시 버전 (구버전)")
        return "LEGACY"

    print("="*60)

    # 추가 정보
    if "from core import" in content:
        print("\n[Core 임포트 내용]")
        for line in content.split('\n'):
            if 'from core import' in line:
                print(f"  {line.strip()}")

    return core_count > 0

if __name__ == "__main__":
    # 현재 디렉토리의 파일 확인
    result = check_file_version("backtest_engine_advanced.py")

    print("\n[권장사항]")
    if result == "LEGACY":
        print("➡️  Core 모듈을 사용하는 버전으로 업데이트가 필요합니다.")
        print("➡️  수정된 backtest_engine_advanced.py를 업로드하세요.")
    elif result == "MIXED":
        print("➡️  레거시 코드를 제거하고 Core 모듈만 사용하도록 정리가 필요합니다.")
    else:
        print("➡️  최신 버전입니다. 추가 작업이 필요 없습니다.")