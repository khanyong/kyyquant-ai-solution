"""
전체 종목 다운로드 테스트
NAS REST API를 통해 전체 종목 리스트를 가져와서 샘플 다운로드 테스트
"""

import requests
import time
from datetime import datetime

def test_download():
    """전체 종목 다운로드 테스트"""

    nas_url = "http://192.168.50.150:8080"

    print("=" * 60)
    print("전체 종목 다운로드 테스트")
    print("=" * 60)

    # 1. 종목 리스트 가져오기
    print("\n1. NAS에서 종목 리스트 가져오기...")
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list")
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('data', [])
            print(f"   성공! {len(stocks)}개 종목 수신")
            print(f"   데이터 소스: {data.get('source', 'unknown')}")

            # 시장별 분류
            kospi_stocks = [s for s in stocks if s['market'] == 'KOSPI']
            kosdaq_stocks = [s for s in stocks if s['market'] == 'KOSDAQ']
            konex_stocks = [s for s in stocks if s['market'] == 'KONEX']

            print(f"\n   시장별 종목 수:")
            print(f"     - KOSPI: {len(kospi_stocks)}개")
            print(f"     - KOSDAQ: {len(kosdaq_stocks)}개")
            print(f"     - KONEX: {len(konex_stocks)}개")

            # 2. 샘플 종목 현재가 조회 테스트
            print("\n2. 샘플 종목 현재가 조회 테스트...")

            # 각 시장에서 3개씩 샘플 추출
            test_stocks = []
            if kospi_stocks:
                test_stocks.extend(kospi_stocks[:3])
            if kosdaq_stocks:
                test_stocks.extend(kosdaq_stocks[:3])

            for stock in test_stocks:
                try:
                    # 현재가 조회
                    price_response = requests.post(
                        f"{nas_url}/api/market/current-price",
                        json={"stock_code": stock['code']}
                    )

                    if price_response.status_code == 200:
                        price_data = price_response.json()
                        if price_data.get('success'):
                            output = price_data['data']['output']
                            print(f"   OK [{stock['market']}] {stock['code']} - {stock['name']}")
                            print(f"      현재가: {output['stck_prpr']}원")
                        else:
                            print(f"   FAIL {stock['code']} - 조회 실패")
                    else:
                        print(f"   FAIL {stock['code']} - HTTP {price_response.status_code}")

                    time.sleep(0.5)  # API 제한 방지

                except Exception as e:
                    print(f"   FAIL {stock['code']} - 오류: {e}")

            # 3. 전체 다운로드 예상 시간 계산
            print("\n3. 전체 다운로드 예상 시간 계산")
            total_stocks = len(stocks)
            seconds_per_stock = 0.5  # API 제한 고려
            total_seconds = total_stocks * seconds_per_stock
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            print(f"   전체 종목 수: {total_stocks}개")
            print(f"   종목당 소요시간: {seconds_per_stock}초")
            print(f"   예상 총 소요시간: 약 {int(hours)}시간 {int(minutes)}분")

            # 4. 배치 다운로드 시뮬레이션
            print("\n4. 배치 다운로드 권장 설정")
            batch_size = 100
            batch_count = (total_stocks + batch_size - 1) // batch_size
            print(f"   권장 배치 크기: {batch_size}개")
            print(f"   총 배치 수: {batch_count}개")
            print(f"   배치당 소요시간: 약 {batch_size * seconds_per_stock / 60:.1f}분")

        else:
            print(f"   실패: HTTP {response.status_code}")

    except Exception as e:
        print(f"   오류: {e}")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_download()