#!/bin/bash

# 시놀로지 NAS 자동 배포 스크립트
# Usage: ./deploy_to_nas.sh [NAS_IP] [NAS_USER]

NAS_IP=${1:-"192.168.1.100"}
NAS_USER=${2:-"admin"}
REMOTE_PATH="/volume1/docker/kiwoom_bridge"

echo "🚀 시놀로지 NAS 배포 시작..."
echo "📍 대상: ${NAS_USER}@${NAS_IP}"
echo "📂 경로: ${REMOTE_PATH}"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수: 성공/실패 메시지
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: SSH 연결 테스트
echo ""
echo "1️⃣ SSH 연결 테스트..."
ssh -o ConnectTimeout=5 ${NAS_USER}@${NAS_IP} "echo '연결 성공'" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "SSH 연결 성공"
else
    print_error "SSH 연결 실패. NAS IP와 사용자명을 확인하세요."
fi

# Step 2: NAS에 디렉토리 생성
echo ""
echo "2️⃣ NAS에 디렉토리 생성..."
ssh ${NAS_USER}@${NAS_IP} "mkdir -p ${REMOTE_PATH}/logs ${REMOTE_PATH}/n8n_workflows"
if [ $? -eq 0 ]; then
    print_success "디렉토리 생성 완료"
else
    print_error "디렉토리 생성 실패"
fi

# Step 3: 파일 전송
echo ""
echo "3️⃣ 파일 전송 중..."

# 필수 파일 목록
FILES=(
    "main.py"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    ".env.example"
)

# 각 파일 전송
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        scp "$file" ${NAS_USER}@${NAS_IP}:${REMOTE_PATH}/ > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "   📄 $file 전송 완료"
        else
            print_warning "$file 전송 실패"
        fi
    else
        print_warning "$file 파일이 없습니다"
    fi
done

# N8N 워크플로우 파일 전송
if [ -f "n8n_workflows/auto_trading_workflow.json" ]; then
    scp "n8n_workflows/auto_trading_workflow.json" ${NAS_USER}@${NAS_IP}:${REMOTE_PATH}/n8n_workflows/ > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   📄 N8N 워크플로우 전송 완료"
    fi
fi

print_success "파일 전송 완료"

# Step 4: .env 파일 설정
echo ""
echo "4️⃣ 환경 변수 설정..."

# .env.example을 .env로 복사
ssh ${NAS_USER}@${NAS_IP} "cd ${REMOTE_PATH} && cp .env.example .env"

print_warning ".env 파일이 생성되었습니다. 다음 값들을 설정해주세요:"
echo "   - SUPABASE_KEY: 실제 Supabase 키 입력"
echo "   - FRONTEND_URL: Vercel 앱 URL 또는 http://localhost:3000"
echo "   - NAS_IP: 실제 NAS IP (현재: ${NAS_IP})"

# Step 5: Docker 이미지 빌드
echo ""
echo "5️⃣ Docker 이미지 빌드..."
echo "   이 작업은 몇 분 소요될 수 있습니다..."

ssh ${NAS_USER}@${NAS_IP} "cd ${REMOTE_PATH} && sudo docker build -t kiwoom-bridge:latest ." > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Docker 이미지 빌드 완료"
else
    print_error "Docker 이미지 빌드 실패"
fi

# Step 6: 기존 컨테이너 정리
echo ""
echo "6️⃣ 기존 컨테이너 정리..."
ssh ${NAS_USER}@${NAS_IP} "sudo docker stop kiwoom-bridge 2>/dev/null; sudo docker rm kiwoom-bridge 2>/dev/null"

# Step 7: Docker 컨테이너 실행
echo ""
echo "7️⃣ Docker 컨테이너 실행..."
ssh ${NAS_USER}@${NAS_IP} "cd ${REMOTE_PATH} && sudo docker-compose up -d"
if [ $? -eq 0 ]; then
    print_success "Docker 컨테이너 실행 중"
else
    print_error "Docker 컨테이너 실행 실패"
fi

# Step 8: 상태 확인
echo ""
echo "8️⃣ 서비스 상태 확인..."
sleep 5

# API 서버 상태 확인
API_STATUS=$(ssh ${NAS_USER}@${NAS_IP} "curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/" 2>/dev/null)
if [ "$API_STATUS" = "200" ]; then
    print_success "키움 API Bridge 서버 정상 작동 중"
else
    print_warning "API 서버 응답 대기 중... (상태 코드: $API_STATUS)"
fi

# N8N 상태 확인
N8N_STATUS=$(ssh ${NAS_USER}@${NAS_IP} "curl -s -o /dev/null -w '%{http_code}' http://localhost:5678/" 2>/dev/null)
if [ "$N8N_STATUS" = "200" ] || [ "$N8N_STATUS" = "401" ]; then
    print_success "N8N 서버 정상 작동 중"
else
    print_warning "N8N 서버를 확인하세요"
fi

# Step 9: 로그 확인
echo ""
echo "9️⃣ 최근 로그 (마지막 10줄)..."
ssh ${NAS_USER}@${NAS_IP} "sudo docker logs --tail 10 kiwoom-bridge 2>&1"

# 완료 메시지
echo ""
echo "="*50
print_success "배포가 완료되었습니다!"
echo "="*50
echo ""
echo "📌 다음 단계:"
echo "1. SSH로 NAS 접속: ssh ${NAS_USER}@${NAS_IP}"
echo "2. 환경 변수 설정: nano ${REMOTE_PATH}/.env"
echo "3. Docker 재시작: cd ${REMOTE_PATH} && sudo docker-compose restart"
echo "4. API 테스트: http://${NAS_IP}:8001/"
echo "5. N8N 워크플로우 설정: http://${NAS_IP}:5678/"
echo ""
echo "📚 전체 가이드: SYNOLOGY_NAS_DEPLOYMENT_GUIDE.md 참조"