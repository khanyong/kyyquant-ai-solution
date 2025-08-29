"""
API 테스트 스크립트
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """API 엔드포인트 테스트"""
    print(f"\n{'='*50}")
    print(f"테스트: {description or endpoint}")
    print(f"{'='*50}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"Unsupported method: {method}")
            return
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[SUCCESS]")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print("[FAILED]")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[CONNECTION ERROR] 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    """메인 테스트 실행"""
    print(f"\n{'#'*50}")
    print("  키움 자동매매 시스템 API 테스트")
    print(f"  시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*50}")
    
    # 1. Health Check
    test_endpoint("GET", "/health", description="헬스체크")
    
    # 2. Root
    test_endpoint("GET", "/", description="루트 엔드포인트")
    
    # 3. Login
    test_endpoint("POST", "/api/login", 
                 data={"demo_mode": True},
                 description="로그인")
    
    # 4. Get Accounts
    test_endpoint("GET", "/api/accounts", description="계좌 목록 조회")
    
    # 5. Get Balance
    test_endpoint("POST", "/api/balance",
                 data={"account_no": "12345678"},
                 description="계좌 잔고 조회")
    
    # 6. Get Stock Info
    test_endpoint("POST", "/api/stock-info",
                 data={"stock_code": "005930"},
                 description="삼성전자 정보 조회")
    
    # 7. Place Order
    test_endpoint("POST", "/api/order",
                 data={
                     "account_no": "12345678",
                     "stock_code": "005930",
                     "order_type": "buy",
                     "quantity": 10,
                     "price": 70000,
                     "order_method": "limit"
                 },
                 description="매수 주문")
    
    # 8. Get Market Stocks
    test_endpoint("GET", "/api/markets/KOSPI/stocks?limit=5",
                 description="KOSPI 종목 조회")
    
    print(f"\n{'#'*50}")
    print("  테스트 완료!")
    print(f"{'#'*50}\n")

if __name__ == "__main__":
    main()