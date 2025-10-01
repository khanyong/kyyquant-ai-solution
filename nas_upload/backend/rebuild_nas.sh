#!/bin/bash

# Rebuild script for Synology NAS deployment
# Usage: ./rebuild_nas.sh

echo "==================================="
echo "Auto Stock Backend Rebuild Script"
echo "==================================="

# Configuration
NAS_IP="192.168.50.150"
NAS_USER="khanyong"
PROJECT_PATH="/volume1/docker/auto_stock"

echo "Target: ${NAS_USER}@${NAS_IP}:${PROJECT_PATH}"
echo ""

# Stop existing container
echo "1. Stopping existing container..."
ssh ${NAS_USER}@${NAS_IP} "cd ${PROJECT_PATH} && sudo docker-compose down"

# Clean Docker cache
echo "2. Cleaning Docker cache..."
ssh ${NAS_USER}@${NAS_IP} "sudo docker system prune -f"

# Create logs directory if not exists
echo "3. Creating logs directory..."
ssh ${NAS_USER}@${NAS_IP} "mkdir -p ${PROJECT_PATH}/logs"

# Rebuild with docker-compose
echo "4. Building new image..."
ssh ${NAS_USER}@${NAS_IP} "cd ${PROJECT_PATH} && sudo docker-compose build --no-cache"

# Start container
echo "5. Starting container..."
ssh ${NAS_USER}@${NAS_IP} "cd ${PROJECT_PATH} && sudo docker-compose up -d"

# Wait for startup
echo "6. Waiting for startup..."
sleep 5

# Check container status
echo "7. Checking container status..."
ssh ${NAS_USER}@${NAS_IP} "sudo docker ps | grep auto-stock"

# Check logs
echo "8. Recent logs:"
ssh ${NAS_USER}@${NAS_IP} "sudo docker logs --tail 20 auto-stock-backend"

# Test health endpoint
echo "9. Testing health endpoint..."
curl -s http://${NAS_IP}:8080/health | python -m json.tool

echo ""
echo "==================================="
echo "Rebuild complete!"
echo "Access points:"
echo "- Local: http://${NAS_IP}:8080"
echo "- Docs: http://${NAS_IP}:8080/docs"
echo "- Cloudflare: https://api.bll-pro.com"
echo "===================================