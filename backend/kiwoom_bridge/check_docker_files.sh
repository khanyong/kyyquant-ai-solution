#!/bin/bash
# Docker 컨테이너 내 파일 확인 스크립트

echo "========================================"
echo "Docker 컨테이너 파일 확인"
echo "========================================"

echo -e "\n1. Core 모듈 파일 목록:"
docker exec kiwoom-bridge ls -la /app/core/

echo -e "\n2. wrapper.py 존재 확인:"
docker exec kiwoom-bridge ls -la /app/core/wrapper.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ wrapper.py 존재"
else
    echo "❌ wrapper.py 없음"
fi

echo -e "\n3. indicators.py 수정 확인 (MA로 통일):"
docker exec kiwoom-bridge grep -n "MA로 통일" /app/core/indicators.py

echo -e "\n4. __init__.py에서 wrapper import 확인:"
docker exec kiwoom-bridge grep -n "from .wrapper import" /app/core/__init__.py

echo -e "\n5. 컨테이너 로그 확인 (최근 50줄):"
docker logs kiwoom-bridge --tail 50 2>&1 | grep -E "\[Core\]|\[FIX\]|\[DEBUG\]|신호"

echo -e "\n========================================"
echo "완료"
echo "========================================"