#!/bin/bash
# Docker 로그를 파일로 저장하는 스크립트

echo "Getting Docker logs..."
docker logs kiwoom-bridge --tail 200 > /docker/kiwoom-bridge/docker_logs.txt 2>&1

echo "Logs saved to /docker/kiwoom-bridge/docker_logs.txt"
echo "Last 50 lines:"
tail -50 /docker/kiwoom-bridge/docker_logs.txt