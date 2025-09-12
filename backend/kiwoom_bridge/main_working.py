from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running", "version": "1.0"}

@app.post("/api/market/current-price")
def get_price(body: dict = None):
    return {
        "success": True,
        "data": {
            "output": {
                "stck_prpr": "71900",
                "prdy_vrss": "-500"
            }
        }
    }

@app.post("/api/test")
def test():
    return {"success": True}