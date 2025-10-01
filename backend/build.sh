#!/bin/bash

# 빌드 스크립트
echo "======================================="
echo "Auto Stock Backend Build Script"
echo "======================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 빌드 모드 선택
MODE=${1:-dev}

echo -e "${YELLOW}Build mode: $MODE${NC}"

# 기존 컨테이너 정리
echo -e "\n${YELLOW}1. Cleaning up existing containers...${NC}"
docker-compose down 2>/dev/null || true

# 캐시 정리 옵션
if [ "$2" == "--no-cache" ]; then
    echo -e "${YELLOW}2. Building without cache...${NC}"
    docker-compose build --no-cache
else
    echo -e "${YELLOW}2. Building with cache...${NC}"
    docker-compose build
fi

# 빌드 확인
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

# 프로덕션 모드일 경우
if [ "$MODE" == "prod" ]; then
    echo -e "\n${YELLOW}3. Using production configuration...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
else
    echo -e "\n${YELLOW}3. Starting development server...${NC}"
    docker-compose up -d
fi

# 상태 확인
echo -e "\n${YELLOW}4. Checking container status...${NC}"
sleep 3
docker ps | grep auto_stock_backend

# 로그 확인
echo -e "\n${YELLOW}5. Recent logs:${NC}"
docker logs --tail 20 auto_stock_backend

echo -e "\n${GREEN}=======================================${NC}"
echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}API URL: http://localhost:8000${NC}"
echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}=======================================${NC}"