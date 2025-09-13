# NAS REST API 엔드포인트 예시

## 현재 구현된 엔드포인트
- `/api/market/current-price` - 개별 종목 현재가 조회
- `/api/backtest/run` - 백테스트 실행

## 추가 필요한 엔드포인트

### 1. 전체 종목 리스트 조회
```python
@app.get("/api/market/stock-list")
def get_stock_list():
    """전체 종목 리스트 반환"""
    # 키움 API의 GetCodeListByMarket 사용
    kospi = kiwoom.GetCodeListByMarket("0")   # KOSPI
    kosdaq = kiwoom.GetCodeListByMarket("10")  # KOSDAQ

    stocks = []
    for code in kospi:
        name = kiwoom.GetMasterCodeName(code)
        stocks.append({"code": code, "name": name, "market": "KOSPI"})

    for code in kosdaq:
        name = kiwoom.GetMasterCodeName(code)
        stocks.append({"code": code, "name": name, "market": "KOSDAQ"})

    return {"success": True, "data": stocks}
```

### 2. 주식 기본정보 조회 (opt10001)
```python
@app.post("/api/stock/basic-info")
def get_stock_info(request):
    """시가총액, 발행주식수 등 기본정보"""
    stock_code = request.get("stock_code")

    # opt10001 TR 호출
    data = kiwoom.request("opt10001", {"종목코드": stock_code})

    return {
        "success": True,
        "data": {
            "시가총액": data.get("시가총액"),
            "유통주식수": data.get("유통주식수"),
            "PER": data.get("PER"),
            "PBR": data.get("PBR")
        }
    }
```

### 3. 외국인 보유 정보 조회
```python
@app.post("/api/stock/foreign-holding")
def get_foreign_holding(request):
    """외국인 지분율 조회"""
    stock_code = request.get("stock_code")

    # opt10040 TR 호출
    data = kiwoom.request("opt10040", {"종목코드": stock_code})

    return {
        "success": True,
        "data": {
            "foreign_ratio": data.get("외국인비율")
        }
    }
```

## NAS 서버 구현 위치
NAS 서버의 FastAPI 또는 Flask 앱에 위 엔드포인트들을 추가하면 됩니다.