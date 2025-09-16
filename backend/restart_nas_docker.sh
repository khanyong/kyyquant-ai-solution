#!/bin/bash
# NAS Docker 컨테이너 재시작 스크립트

echo "NAS Docker 컨테이너 재시작 스크립트"
echo "===================================="

# 1. 실행 중인 컨테이너 확인
echo "1. 실행 중인 컨테이너 확인:"
docker ps | grep kiwoom

# 2. kiwoom 관련 컨테이너 모두 중지
echo ""
echo "2. kiwoom 관련 컨테이너 중지:"
docker stop $(docker ps -q --filter "name=kiwoom")

# 3. 잠시 대기
echo ""
echo "3. 5초 대기..."
sleep 5

# 4. 새 컨테이너 시작
echo ""
echo "4. 새 컨테이너 시작:"
cd /volume1/docker/kiwoom_bridge
docker-compose up -d --force-recreate

# 5. 상태 확인
echo ""
echo "5. 컨테이너 상태 확인:"
sleep 3
docker ps | grep kiwoom

echo ""
echo "완료!"
echo "===================================="