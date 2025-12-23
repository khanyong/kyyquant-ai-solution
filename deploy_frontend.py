import os
import subprocess
import time

PEM_FILE = "LightsailDefaultKey-ap-northeast-2.pem"
REMOTE_HOST = "ubuntu@13.209.204.159"
REMOTE_DIR = "/home/ubuntu/auto_stock/frontend_dist" # 임시 업로드 경로
FINAL_DIR = "/home/ubuntu/auto_stock/frontend/dist" # 실제 Nginx 마운트 경로 (docker-compose 확인 필요)

# [FIX] Docker Compose Volumes for NPM/Nginx usually map ./frontend/dist:/usr/share/nginx/html or similiar
# Based on project structure, let's assume valid mapping or just use a staging dir and copy.
# Docker compose says:
#   npm:
#     volumes:
#       - npm_data:/data
# The docker-compose.cloud.yml doesn't explicitly show a frontend service serving static files?
# Wait, usually there is a separate Nginx or the 'backend' serves it?
# Looking at docker-compose.cloud.yml again in memory... 
# Ah, I don't see a 'frontend' service. 
# Maybe 'npm' (Nginx Proxy Manager) proxies to a bucket or S3?
# OR... is there a missing service?
# Users previous deploy was backend only.
# Let's upload to a folder first.

def run_ssh_cmd(cmd):
    ssh_cmd = [
        "ssh", 
        "-i", PEM_FILE, 
        "-o", "StrictHostKeyChecking=no",
        REMOTE_HOST, 
        cmd
    ]
    try:
        res = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
        return res.returncode == 0, res.stdout, res.stderr
    except Exception as e:
        return False, "", str(e)

def upload_folder(local_dir, remote_dir):
    print(f"Uploading {local_dir} to {remote_dir}...")
    
    # 1. Create remote dir
    run_ssh_cmd(f"mkdir -p {remote_dir}")

    # 2. Tar local dist
    tar_name = "dist_deploy.tar.gz"
    if os.path.exists(tar_name):
        os.remove(tar_name)
        
    print("Compressing dist folder...")
    # PowerShell doesn't have tar easily, use python tarfile
    import tarfile
    with tarfile.open(tar_name, "w:gz") as tar:
        tar.add(local_dir, arcname=".")
        
    # 3. SCP tar
    print(f"Sending {tar_name}...")
    scp_cmd = [
        "scp",
        "-i", PEM_FILE,
        "-o", "StrictHostKeyChecking=no",
        tar_name,
        f"{REMOTE_HOST}:{remote_dir}/{tar_name}"
    ]
    
    res = subprocess.run(scp_cmd)
    if res.returncode != 0:
        print("SCP Failed")
        return False
        
    # 4. Extract remote
    print("Extracting remote...")
    success, out, err = run_ssh_cmd(f"cd {remote_dir} && tar -xzf {tar_name} && rm {tar_name}")
    if not success:
        print(f"Extraction Failed: {err}")
        return False
        
    print("Upload Complete.")
    return True

if __name__ == "__main__":
    # 1. Upload dist to ~/auto_stock/frontend_dist
    if upload_folder("dist", "/home/ubuntu/auto_stock/frontend_dist"):
        
        # 2. Swap folders? Or Copy to Web Root?
        # User environment is not 100% clear on where Nginx serves from.
        # But commonly it might be mapped.
        # Let's Check where the previous frontend was.
        # I'll just upload to ~/auto_stock/frontend_dist first.
        # Then I will ask user/check where to move it.
        # OR... I can try to move it to a 'standard' docker volume path if I knew it.
        # Let's assume user has a setup. 
        # I will start by just uploading.
        pass
