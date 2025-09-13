"""
종목 리스트 API 엔드포인트 추가
NAS 서버의 main.py에 이 코드를 추가하세요
"""

from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime

router = APIRouter()

# Mock 종목 데이터 (실제로는 키움 API에서 가져와야 함)
MOCK_STOCKS = {
    # KOSPI 주요 종목
    "005930": {"name": "삼성전자", "market": "KOSPI"},
    "000660": {"name": "SK하이닉스", "market": "KOSPI"},
    "207940": {"name": "삼성바이오로직스", "market": "KOSPI"},
    "005380": {"name": "현대차", "market": "KOSPI"},
    "005935": {"name": "삼성전자우", "market": "KOSPI"},
    "000270": {"name": "기아", "market": "KOSPI"},
    "068270": {"name": "셀트리온", "market": "KOSPI"},
    "035420": {"name": "NAVER", "market": "KOSPI"},
    "051910": {"name": "LG화학", "market": "KOSPI"},
    "006400": {"name": "삼성SDI", "market": "KOSPI"},
    "003670": {"name": "포스코퓨처엠", "market": "KOSPI"},
    "035720": {"name": "카카오", "market": "KOSPI"},
    "012330": {"name": "현대모비스", "market": "KOSPI"},
    "028260": {"name": "삼성물산", "market": "KOSPI"},
    "066570": {"name": "LG전자", "market": "KOSPI"},
    "036570": {"name": "NCsoft", "market": "KOSPI"},
    "033780": {"name": "KT&G", "market": "KOSPI"},
    "003550": {"name": "LG", "market": "KOSPI"},
    "017670": {"name": "SK텔레콤", "market": "KOSPI"},
    "105560": {"name": "KB금융", "market": "KOSPI"},

    # KOSDAQ 주요 종목
    "247540": {"name": "에코프로비엠", "market": "KOSDAQ"},
    "086520": {"name": "에코프로", "market": "KOSDAQ"},
    "328130": {"name": "루닛", "market": "KOSDAQ"},
    "196170": {"name": "알테오젠", "market": "KOSDAQ"},
    "141080": {"name": "레고켐바이오", "market": "KOSDAQ"},
}

@router.get("/api/market/stock-list")
async def get_stock_list(market: str = None):
    """
    전체 종목 리스트 조회

    Parameters:
    - market: "KOSPI", "KOSDAQ", None (전체)

    Returns:
    - 종목 코드, 이름, 시장 정보
    """

    stocks = []

    for code, info in MOCK_STOCKS.items():
        if market is None or info["market"] == market:
            stocks.append({
                "code": code,
                "name": info["name"],
                "market": info["market"]
            })

    return {
        "success": True,
        "data": stocks,
        "count": len(stocks),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/api/market/stock-list-full")
async def get_full_stock_list():
    """
    실제 키움 API를 사용한 전체 종목 리스트 조회
    (키움 API 연결이 필요함)
    """

    try:
        # 실제 구현시 키움 API 사용
        # from pykiwoom import Kiwoom
        # kiwoom = Kiwoom()
        # kospi = kiwoom.GetCodeListByMarket("0")
        # kosdaq = kiwoom.GetCodeListByMarket("10")

        # Mock 응답
        return {
            "success": True,
            "message": "키움 API 연결이 필요합니다",
            "data": list(MOCK_STOCKS.keys()),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# === main.py에 추가할 코드 ===
"""
# main.py 파일에 다음을 추가하세요:

# 1. import 추가
from stock_list_api import router as stock_list_router

# 2. 라우터 등록 (app 생성 후)
app.include_router(stock_list_router)

# 또는 직접 엔드포인트 추가:

@app.get("/api/market/stock-list")
async def get_stock_list():
    # KOSPI + KOSDAQ 전체 종목
    stocks = []

    # Mock 데이터 (실제로는 키움 API 사용)
    kospi_stocks = [
        {"code": "005930", "name": "삼성전자", "market": "KOSPI"},
        {"code": "000660", "name": "SK하이닉스", "market": "KOSPI"},
        # ... 더 많은 종목
    ]

    kosdaq_stocks = [
        {"code": "247540", "name": "에코프로비엠", "market": "KOSDAQ"},
        {"code": "086520", "name": "에코프로", "market": "KOSDAQ"},
        # ... 더 많은 종목
    ]

    stocks.extend(kospi_stocks)
    stocks.extend(kosdaq_stocks)

    return {
        "success": True,
        "data": stocks,
        "count": len(stocks),
        "timestamp": datetime.now().isoformat()
    }
"""