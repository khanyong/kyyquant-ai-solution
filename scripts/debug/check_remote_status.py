import subprocess
import os
import sys

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

# Same constants as deploy_patch.py
PEM_FILE = "LightsailDefaultKey-ap-northeast-2.pem"
REMOTE_HOST = "ubuntu@13.209.204.159"

def check_remote_status():
    print(f"Connecting to {REMOTE_HOST} using {PEM_FILE}...")
    
    if not os.path.exists(PEM_FILE):
        print(f"Error: PEM file '{PEM_FILE}' not found in current directory.")
        return

    # Command to check container status and file timestamp
    # 1. docker ps for uptime
    # 2. ls -l for strategy.py timestamp verification
    remote_cmds = [
        "echo '=== Docker Container Status ==='",
        "sudo docker ps --filter name=auto-stock-backend --format '{{.Names}}: {{.Status}}'",
        "echo ''",
        "echo '=== File Timestamp Verification ==='",
        "ls -l --time-style=long-iso /home/ubuntu/auto_stock/backend/api/strategy.py"
    ]
    
    full_remote_cmd = "; ".join(remote_cmds)

    ssh_cmd = [
        "ssh",
        "-i", PEM_FILE,
        "-o", "StrictHostKeyChecking=no",
        REMOTE_HOST,
        full_remote_cmd
    ]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("SSH Command Failed:")
            print(result.stderr)
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    check_remote_status()
