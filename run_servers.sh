#!/bin/bash

echo "======================================"
echo "  키움 자동매매 시스템 실행"
echo "======================================"
echo

echo "[1/2] 백엔드 서버 시작..."
python api_server.py &
BACKEND_PID=$!

sleep 3

echo "[2/2] 프론트엔드 서버 시작..."
npm run dev &
FRONTEND_PID=$!

echo
echo "======================================"
echo "  서버 실행 완료!"
echo "======================================"
echo
echo "백엔드: http://localhost:8000"
echo "프론트엔드: http://localhost:3000"
echo "API 문서: http://localhost:8000/docs"
echo
echo "종료하려면 Ctrl+C를 누르세요."
echo

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait