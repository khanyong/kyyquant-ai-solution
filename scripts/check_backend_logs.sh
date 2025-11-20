#!/bin/bash
# 백엔드 로그 확인 스크립트

echo "==================================================="
echo "백엔드 Docker 컨테이너 로그 확인"
echo "==================================================="

# 1. 컨테이너 상태 확인
echo ""
echo "1. Docker 컨테이너 상태:"
docker ps | grep backend

# 2. 최근 로그 확인 (포트폴리오 검증 관련)
echo ""
echo "2. 포트폴리오 검증 로그 (SELL 관련):"
docker logs auto_stock_backend --tail 100 | grep -i "SELL\|portfolio"

# 3. 에러 로그 확인
echo ""
echo "3. 에러 로그:"
docker logs auto_stock_backend --tail 100 | grep -i "error\|exception"

# 4. 실시간 로그 모니터링 (10초간)
echo ""
echo "4. 실시간 로그 (10초간):"
timeout 10 docker logs auto_stock_backend -f --tail 20
