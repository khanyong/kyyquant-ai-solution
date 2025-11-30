#!/bin/bash
# 나스 서버 배포 스크립트

NAS_HOST="192.168.50.150"
NAS_EXTERNAL="khanyong.asuscomm.com"
NAS_USER="khanyong"
NAS_PATH="/volume1/docker/auto_stock"

echo "==================================="
echo "Auto Stock Backend NAS Deployment"
echo "==================================="

# 1. 파일 압축
echo "1. Creating archive..."
tar -czf backend_deploy.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env' \
    .

# 2. 나스로 전송
echo "2. Uploading to NAS..."
scp backend_deploy.tar.gz $NAS_USER@$NAS_HOST:$NAS_PATH/

# 3. 나스에서 압축 해제 및 Docker 실행
echo "3. Extracting and running on NAS..."
ssh $NAS_USER@$NAS_HOST << EOF
    cd $NAS_PATH
    tar -xzf backend_deploy.tar.gz
    rm backend_deploy.tar.gz

    # Docker 이미지 빌드
    docker build -t auto_stock_backend .

    # 기존 컨테이너 중지 및 제거
    docker stop auto_stock_backend 2>/dev/null || true
    docker rm auto_stock_backend 2>/dev/null || true

    # 새 컨테이너 실행
    docker run -d \
        --name auto_stock_backend \
        -p 8000:8000 \
        --restart unless-stopped \
        --env-file .env \
        auto_stock_backend

    # 상태 확인
    docker ps | grep auto_stock_backend
EOF

echo "4. Deployment complete!"
echo "======================================"
echo "Local Access:"
echo "  API: http://$NAS_HOST:8080"
echo "  Docs: http://$NAS_HOST:8080/docs"
echo ""
echo "External Access:"
echo "  API: https://api.bll-pro.com"
echo "  Docs: https://api.bll-pro.com/docs"
echo ""
echo "DDNS Access:"
echo "  API: http://$NAS_EXTERNAL:8080"
echo "  Docs: http://$NAS_EXTERNAL:8080/docs"
echo "======================================"