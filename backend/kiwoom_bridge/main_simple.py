"""
간단한 테스트용 API 서버
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Kiwoom Bridge Test")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CurrentPriceRequest(BaseModel):
    stock_code: str

@app.get("/")
async def root():
    return {
        "service": "Kiwoom Bridge Test",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/test")
async def test():
    return {"success": True, "message": "Test OK"}

@app.post("/api/market/current-price")
async def get_current_price(request: CurrentPriceRequest):
    """간단한 Mock 데이터 반환"""
    return {
        "success": True,
        "data": {
            "rt_cd": "0",
            "msg1": "정상처리",
            "output": {
                "stck_prpr": "71900",
                "prdy_vrss": "-500",
                "prdy_ctrt": "-0.69",
                "stck_sdpr": "72400"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)