#!/bin/bash
# Docker 이미지 완전 재빌드 스크립트

echo "=== Docker 완전 재빌드 시작 ==="
echo ""
echo "⚠️  주의: docker-compose.yml에서 './backend:/app' 볼륨 마운트가 주석 처리되어 있는지 확인하세요!"
echo "   볼륨 마운트가 활성화되어 있으면 Dockerfile 빌드가 무효화됩니다."
echo ""
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 1
fi

# 1. 컨테이너 정지 및 삭제
echo "[1/6] 기존 컨테이너 정지 및 삭제..."
docker compose down

# 2. 이미지 삭제
echo "[2/6] 기존 이미지 삭제..."
docker rmi auto_stock-backend 2>/dev/null || true

# 3. Python 캐시 파일 삭제
echo "[3/6] Python 캐시 파일 삭제..."
find ./backend -type f -name "*.pyc" -delete
find ./backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 4. Docker 빌드 캐시 무효화하여 재빌드
echo "[4/6] 캐시 무시하고 이미지 재빌드..."
CACHEBUST=$(date +%s) docker compose build --no-cache

# 5. 컨테이너 시작
echo "[5/6] 컨테이너 시작..."
docker compose up -d

# 6. 로그 확인
echo "[6/6] 서버 시작 대기 (5초)..."
sleep 5

echo ""
echo "=== 재빌드 완료 ==="
echo ""
echo "컨테이너 상태 확인:"
docker compose ps
echo ""
echo "최근 로그 (Ctrl+C로 종료):"
docker compose logs -f --tail=50 backend
