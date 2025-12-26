#!/bin/bash

KEY_PATH="LightsailDefaultKey-ap-northeast-2.pem"
HOST_IP="13.209.204.159"
USER="ubuntu"
REMOTE_DIR="~/auto_stock"

echo "Deploying modified files to $HOST_IP..."

# Upload strategy.py
echo "Uploading strategy.py..."
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no backend/api/strategy.py $USER@$HOST_IP:$REMOTE_DIR/backend/api/strategy.py

# Upload manager.py
echo "Uploading manager.py..."
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no backend/strategies/manager.py $USER@$HOST_IP:$REMOTE_DIR/backend/strategies/manager.py

# Upload provider.py
echo "Uploading provider.py..."
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no backend/data/provider.py $USER@$HOST_IP:$REMOTE_DIR/backend/data/provider.py

# Upload calculator.py
echo "Uploading calculator.py..."
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no backend/indicators/calculator.py $USER@$HOST_IP:$REMOTE_DIR/backend/indicators/calculator.py

if [ $? -eq 0 ]; then
    echo "Upload success. Rebuilding backend..."
    
    # Rebuild and restart
    ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no $USER@$HOST_IP "cd $REMOTE_DIR && docker compose build backend && docker compose up -d backend"
    
    if [ $? -eq 0 ]; then
        echo "Deployment complete!"
    else
        echo "Docker restart failed."
    fi
else
    echo "Upload failed."
fi
