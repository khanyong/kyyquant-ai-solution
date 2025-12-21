
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
    
    return {
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
