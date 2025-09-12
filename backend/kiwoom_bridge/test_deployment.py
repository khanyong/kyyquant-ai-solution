#!/usr/bin/env python3
"""
시놀로지 NAS 배포 테스트 스크립트
키움 API Bridge 서버의 모든 엔드포인트를 테스트합니다.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class KiwoomAPITester:
    def __init__(self, base_url: str = "http://192.168.1.100:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def print_header(self, text: str):
        """헤더 출력"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{text}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
    def print_success(self, text: str):
        """성공 메시지 출력"""
        print(f"{GREEN}✅ {text}{RESET}")
        self.test_results.append(("PASS", text))
        
    def print_error(self, text: str):
        """오류 메시지 출력"""
        print(f"{RED}❌ {text}{RESET}")
        self.test_results.append(("FAIL", text))
        
    def print_warning(self, text: str):
        """경고 메시지 출력"""
        print(f"{YELLOW}⚠️  {text}{RESET}")
        
    def print_info(self, text: str):
        """정보 메시지 출력"""
        print(f"   {text}")
        
    def test_health_check(self) -> bool:
        """헬스체크 테스트"""
        self.print_header("1. 헬스체크 테스트")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"서버 상태: {data.get('status', 'unknown')}")
                self.print_info(f"메시지: {data.get('message', '')}")
                self.print_info(f"시간: {data.get('timestamp', '')}")
                return True
            else:
                self.print_error(f"HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("서버에 연결할 수 없습니다")
            return False
        except Exception as e:
            self.print_error(f"오류: {str(e)}")
            return False
            
    def test_current_price(self, stock_code: str = "005930") -> bool:
        """현재가 조회 테스트"""
        self.print_header("2. 현재가 조회 테스트")
        try:
            response = self.session.post(
                f"{self.base_url}/api/market/current-price",
                json={"stock_code": stock_code}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("rt_cd") == "0":
                    output = data.get("output", {})
                    self.print_success(f"종목 코드: {stock_code}")
                    self.print_info(f"현재가: {output.get('stck_prpr', 'N/A')}원")
                    self.print_info(f"전일 대비: {output.get('prdy_vrss', 'N/A')}원")
                    self.print_info(f"등락률: {output.get('prdy_ctrt', 'N/A')}%")
                    return True
                else:
                    self.print_error(f"API 오류: {data.get('msg1', 'Unknown error')}")
                    return False
            else:
                self.print_error(f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"오류: {str(e)}")
            return False
            
    def test_authentication(self, user_id: str = "test_user") -> bool:
        """인증 테스트 (토큰 발급)"""
        self.print_header("3. 인증 테스트")
        self.print_warning("실제 Supabase 사용자 ID와 API 키가 필요합니다")
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/token",
                json={
                    "user_id": user_id,
                    "is_test_mode": True
                }
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.print_success("액세스 토큰 발급 성공")
                    self.print_info(f"토큰 타입: {data.get('token_type', 'N/A')}")
                    self.print_info(f"만료 시간: {data.get('expires_in', 'N/A')}초")
                    return True
                else:
                    self.print_error("토큰 발급 실패")
                    return False
            elif response.status_code == 404:
                self.print_warning("사용자 API 키를 찾을 수 없습니다")
                self.print_info("MyPage에서 API 키를 먼저 등록하세요")
                return False
            else:
                self.print_error(f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"오류: {str(e)}")
            return False
            
    def test_order_placement(self, user_id: str = "test_user") -> bool:
        """주문 테스트 (모의투자)"""
        self.print_header("4. 주문 테스트 (모의투자)")
        self.print_warning("실제 주문을 실행하지 않고 API 호출만 테스트합니다")
        try:
            response = self.session.post(
                f"{self.base_url}/api/trading/order",
                json={
                    "user_id": user_id,
                    "stock_code": "005930",
                    "order_type": "buy",
                    "quantity": 1,
                    "price": 0,  # 시장가
                    "order_method": "01",  # 지정가
                    "is_test_mode": True
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("rt_cd") == "0":
                    self.print_success("주문 API 호출 성공")
                    output = data.get("output", {})
                    self.print_info(f"주문 번호: {output.get('odno', 'N/A')}")
                    self.print_info(f"주문 시간: {output.get('ord_tmd', 'N/A')}")
                    return True
                else:
                    self.print_error(f"주문 실패: {data.get('msg1', 'Unknown error')}")
                    return False
            elif response.status_code == 404:
                self.print_warning("사용자 API 키를 찾을 수 없습니다")
                return False
            else:
                self.print_error(f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"오류: {str(e)}")
            return False
            
    def test_n8n_connection(self, n8n_url: str = "http://192.168.1.100:5678") -> bool:
        """N8N 연결 테스트"""
        self.print_header("5. N8N 연결 테스트")
        try:
            response = requests.get(n8n_url, timeout=5)
            if response.status_code in [200, 401]:  # 401은 인증이 필요하다는 의미
                self.print_success("N8N 서버가 실행 중입니다")
                self.print_info(f"URL: {n8n_url}")
                if response.status_code == 401:
                    self.print_info("인증이 필요합니다 (정상)")
                return True
            else:
                self.print_error(f"N8N 서버 응답 오류: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("N8N 서버에 연결할 수 없습니다")
            self.print_info("N8N이 설치되어 실행 중인지 확인하세요")
            return False
        except Exception as e:
            self.print_error(f"오류: {str(e)}")
            return False
            
    def print_summary(self):
        """테스트 결과 요약"""
        self.print_header("테스트 결과 요약")
        
        total = len(self.test_results)
        passed = sum(1 for result in self.test_results if result[0] == "PASS")
        failed = total - passed
        
        print(f"\n총 테스트: {total}")
        print(f"{GREEN}통과: {passed}{RESET}")
        print(f"{RED}실패: {failed}{RESET}")
        
        if failed > 0:
            print(f"\n{RED}실패한 테스트:{RESET}")
            for result, text in self.test_results:
                if result == "FAIL":
                    print(f"  - {text}")
                    
        success_rate = (passed / total * 100) if total > 0 else 0
        if success_rate == 100:
            print(f"\n{GREEN}🎉 모든 테스트 통과!{RESET}")
        elif success_rate >= 80:
            print(f"\n{YELLOW}⚠️  일부 테스트 실패 (성공률: {success_rate:.1f}%){RESET}")
        else:
            print(f"\n{RED}❌ 많은 테스트 실패 (성공률: {success_rate:.1f}%){RESET}")
            
    def run_all_tests(self, nas_ip: str = None, user_id: str = None):
        """모든 테스트 실행"""
        if nas_ip:
            self.base_url = f"http://{nas_ip}:8001"
            n8n_url = f"http://{nas_ip}:5678"
        else:
            n8n_url = "http://192.168.1.100:5678"
            
        if not user_id:
            user_id = "test_user"
            
        print(f"{BLUE}키움 API Bridge 배포 테스트{RESET}")
        print(f"서버: {self.base_url}")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 테스트 실행
        self.test_health_check()
        self.test_current_price()
        self.test_authentication(user_id)
        self.test_order_placement(user_id)
        self.test_n8n_connection(n8n_url)
        
        # 결과 요약
        self.print_summary()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="키움 API Bridge 배포 테스트")
    parser.add_argument("--nas-ip", help="NAS IP 주소", default="192.168.1.100")
    parser.add_argument("--user-id", help="Supabase 사용자 ID", default="test_user")
    
    args = parser.parse_args()
    
    tester = KiwoomAPITester()
    tester.run_all_tests(nas_ip=args.nas_ip, user_id=args.user_id)