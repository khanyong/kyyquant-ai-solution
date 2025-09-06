"""
모의 키움증권 데이터 생성기 (테스트용)
실제 API 키가 없을 때 사용
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_mock_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    모의 주가 데이터 생성
    
    Args:
        stock_code: 종목코드
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
    
    Returns:
        주가 데이터 DataFrame
    """
    
    # 날짜 범위 생성
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    dates = pd.date_range(start=start, end=end, freq='B')  # Business days only
    
    # 초기 가격 설정 (종목별로 다른 가격대)
    price_map = {
        "005930": 70000,   # 삼성전자
        "000660": 120000,  # SK하이닉스
        "035720": 50000,   # 카카오
        "005380": 200000,  # 현대차
        "051910": 800000,  # LG화학
    }
    
    base_price = price_map.get(stock_code, 100000)
    
    # 가격 데이터 생성
    num_days = len(dates)
    prices = []
    
    current_price = base_price
    for i in range(num_days):
        # 일일 변동률 (-3% ~ +3%)
        daily_return = np.random.normal(0.001, 0.02)  # 평균 0.1%, 표준편차 2%
        current_price = current_price * (1 + daily_return)
        
        # OHLC 데이터 생성
        open_price = current_price * np.random.uniform(0.995, 1.005)
        high_price = max(open_price, current_price) * np.random.uniform(1.0, 1.02)
        low_price = min(open_price, current_price) * np.random.uniform(0.98, 1.0)
        close_price = current_price
        
        # 거래량 (기본 100만주 전후)
        volume = int(np.random.normal(1000000, 300000))
        volume = max(100000, volume)  # 최소 10만주
        
        prices.append({
            'date': dates[i],
            'open': round(open_price),
            'high': round(high_price),
            'low': round(low_price),
            'close': round(close_price),
            'volume': volume,
            'trading_value': int(close_price * volume)
        })
    
    # DataFrame 생성
    df = pd.DataFrame(prices)
    df.set_index('date', inplace=True)
    
    return df

def get_mock_realtime_price(stock_code: str) -> dict:
    """
    모의 실시간 가격 데이터
    
    Args:
        stock_code: 종목코드
    
    Returns:
        실시간 가격 정보
    """
    price_map = {
        "005930": 70000,
        "000660": 120000,
        "035720": 50000,
        "005380": 200000,
        "051910": 800000,
    }
    
    base_price = price_map.get(stock_code, 100000)
    current_price = base_price * np.random.uniform(0.98, 1.02)
    
    return {
        'stock_code': stock_code,
        'current_price': round(current_price),
        'change': round(current_price - base_price),
        'change_rate': round((current_price - base_price) / base_price * 100, 2),
        'volume': random.randint(100000, 2000000),
        'timestamp': datetime.now().isoformat()
    }

# 백테스트용 데이터 생성 함수
def generate_backtest_data(stock_codes: list, start_date: str, end_date: str) -> dict:
    """
    여러 종목의 백테스트 데이터 생성
    
    Args:
        stock_codes: 종목코드 리스트
        start_date: 시작일
        end_date: 종료일
    
    Returns:
        종목별 데이터 딕셔너리
    """
    all_data = {}
    
    for code in stock_codes:
        data = generate_mock_stock_data(code, start_date, end_date)
        if not data.empty:
            all_data[code] = data
            print(f"Generated mock data for {code}: {len(data)} days")
    
    return all_data