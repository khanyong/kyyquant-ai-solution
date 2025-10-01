#!/bin/bash

# NAS 서버 배포 스크립트
# 현재 backend 폴더를 NAS 서버에 배포합니다

echo "========================================"
echo "Auto Stock Backend NAS 배포"
echo "========================================"

# 1. backend 폴더를 압축
echo "1. backend 폴더 압축 중..."
cd /d/Dev/auto_stock
tar -czf backend_deploy.tar.gz backend/

echo "2. 압축 완료: backend_deploy.tar.gz"
echo ""
echo "다음 단계를 수동으로 진행하세요:"
echo ""
echo "1) NAS 웹 인터페이스로 접속 (http://192.168.50.150)"
echo ""
echo "2) File Station에서 /docker/auto-stock 폴더로 이동"
echo ""
echo "3) backend_deploy.tar.gz 파일 업로드"
echo ""
echo "4) SSH 또는 Container Manager에서 다음 명령 실행:"
echo "   cd /volume1/docker/auto-stock"
echo "   # 백업 생성"
echo "   mv backend backend_backup_$(date +%Y%m%d)"
echo "   # 압축 해제"
echo "   tar -xzf backend_deploy.tar.gz"
echo "   # Docker 컨테이너 재시작"
echo "   docker restart auto-stock-backend"
echo ""
echo "5) 로그 확인:"
echo "   docker logs auto-stock-backend --tail 50"
echo ""
echo "========================================"