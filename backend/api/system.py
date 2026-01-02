
from fastapi import APIRouter
import psutil
import os
import time

router = APIRouter()

@router.get("/status")
def get_system_status():
    """
    서버 시스템 리소스 상태 조회 (CPU, Memory, Disk)
    AWS 프리티어 모니터링용
    """
    
    # 1. CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 2. Memory Usage
    mem = psutil.virtual_memory()
    
    # 3. Disk Usage (Root)
    disk = psutil.disk_usage('/')
    
    # 4. Boot Time / Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    # 5. Trading Context (For Frontend Awareness)
    import os
    is_demo = os.getenv("KIWOOM_IS_DEMO", "true").lower() == "true"
    
    # [NEW] Expose BOTH accounts so Frontend can switch
    # Defaults updated to match User Config (Step 3820)
    # [FIX] Normalize: Remove hyphens to match API format often returned by GetLoginInfo
    # AND Append '10' if length is 8 (Stock Account Suffix)
    
    def normalize_acc(acc_str):
        if not acc_str: return acc_str
        clean = acc_str.replace('-', '')
        if len(clean) == 8:
            return clean + '10'
        return clean

    live_account = normalize_acc(os.getenv("KIWOOM_LIVE_ACCOUNT_NO", "5093-6181"))
    test_account = normalize_acc(os.getenv("KIWOOM_TEST_ACCOUNT_NO", "8112610001"))
    
    active_account = test_account if is_demo else live_account
    
    return {
        "trading_context": {
            "mode": "MOCK" if is_demo else "REAL",
            "active_account_no": active_account,
            "accounts": {
                "LIVE": live_account,
                "MOCK": test_account
            },
            "server_ip": "13.209.204.159"
        },
        "cpu": {
            "usage_percent": cpu_percent,
            "count": psutil.cpu_count(),
            "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
        },
        "memory": {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        },
        "uptime_seconds": uptime_seconds,
        "timestamp": time.time()
    }
