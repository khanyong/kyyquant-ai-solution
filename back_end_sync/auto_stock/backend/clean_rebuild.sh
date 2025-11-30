#!/bin/bash
# Synology NAS Complete Rebuild Script
# Run this in Task Scheduler as root

echo "========================================="
echo "Auto Stock Backend - Complete Clean Build"
echo "========================================="

cd /volume1/docker/auto_stock

# 1. Stop and remove existing container
echo "1. Stopping existing container..."
docker-compose down

# 2. Remove the old image
echo "2. Removing old images..."
docker rmi auto-stock-backend:latest -f
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null

# 3. Clean all Docker cache
echo "3. Cleaning Docker cache..."
docker system prune -a --volumes -f

# 4. Create logs directory
echo "4. Creating logs directory..."
mkdir -p /volume1/docker/auto_stock/logs
chmod 755 /volume1/docker/auto_stock/logs

# 5. Build fresh image (no cache)
echo "5. Building fresh image..."
docker-compose build --no-cache --pull

# 6. Start the container
echo "6. Starting container..."
docker-compose up -d

# 7. Wait for startup
sleep 10

# 8. Check status
echo "7. Container status:"
docker ps | grep auto-stock

# 9. Show logs
echo "8. Container logs:"
docker logs --tail 50 auto-stock-backend

echo "========================================="
echo "Rebuild complete!"
echo "========================================="