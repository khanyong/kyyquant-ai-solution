
import subprocess
import os
import time

PEM_FILE = "LightsailDefaultKey-ap-northeast-2.pem"
REMOTE_HOST = "ubuntu@13.209.204.159"
REMOTE_DIR = "/home/ubuntu/auto_stock/backend/api"

FILES_TO_DEPLOY = [
    ("backend/api/account.py", f"{REMOTE_DIR}/account.py"),
    ("backend/api/kiwoom_client.py", f"{REMOTE_DIR}/kiwoom_client.py"),
    ("backend/api/token_manager.py", f"{REMOTE_DIR}/token_manager.py"),
    ("backend/api/kiwoom_websocket.py", f"{REMOTE_DIR}/kiwoom_websocket.py"),
    ("backend/api/strategy.py", f"{REMOTE_DIR}/strategy.py"),
    ("backend/backtest/engine.py", "/home/ubuntu/auto_stock/backend/backtest/engine.py"),
    ("backend/indicators/calculator.py", "/home/ubuntu/auto_stock/backend/indicators/calculator.py")
]

def deploy_file(local_path, remote_path):
    print(f"Deploying {local_path} to {remote_path}...")
    
    if not os.path.exists(local_path):
        print(f"ERROR: Local file not found: {local_path}")
        return False

    # Read local content
    with open(local_path, 'rb') as f:
        content = f.read()

    # Construct SSH command: ssh -i key user@host "cat > remote_path"
    # We pipe content to stdin of this process
    cmd = [
        "ssh", 
        "-i", PEM_FILE, 
        "-o", "StrictHostKeyChecking=no",
        REMOTE_HOST, 
        f"cat > {remote_path}"
    ]

    try:
        # Run subprocess, piping content to stdin
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=content, timeout=30)
        
        if process.returncode != 0:
            print(f"FAILED: {stderr.decode()}")
            return False
            
        print("SUCCESS")
        return True
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def restart_backend():
    print("Restarting backend container...")
    cmd = [
        "ssh", 
        "-i", PEM_FILE, 
        "-o", "StrictHostKeyChecking=no",
        REMOTE_HOST, 
        "cd /home/ubuntu/auto_stock && sudo docker compose up -d --build backend"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(result.stdout)
        print(result.stderr)
        if result.returncode == 0:
            print("Restart Commanded Successfully.")
        else:
            print("Restart Failed.")
    except Exception as e:
        print(f"Restart Exception: {e}")

if __name__ == "__main__":
    success = True
    for local, remote in FILES_TO_DEPLOY:
        if not deploy_file(local, remote):
            success = False
            break
    
    if success:
        restart_backend()
    else:
        print("Deployment failed, skipping restart.")
