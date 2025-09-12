from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CurrentPriceRequest(BaseModel):
    stock_code: str

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/api/market/current-price")
def get_price(request: CurrentPriceRequest):
    return {
        "success": True,
        "data": {
            "output": {
                "stck_prpr": "71900",
                "prdy_vrss": "-500"
            }
        }
    }