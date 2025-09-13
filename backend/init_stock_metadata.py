"""
stock_metadata 테이블 초기화
주요 종목들을 데이터베이스에 추가
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def init_stock_metadata():
    """stock_metadata 테이블에 초기 데이터 삽입"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("stock_metadata 테이블 초기화")
    print("=" * 60)

    # 주요 종목 리스트 (확장 가능)
    stocks = [
        # KOSPI 대표 종목
        {"stock_code": "005930", "stock_name": "삼성전자", "market": "KOSPI", "sector": "IT", "industry": "반도체"},
        {"stock_code": "000660", "stock_name": "SK하이닉스", "market": "KOSPI", "sector": "IT", "industry": "반도체"},
        {"stock_code": "207940", "stock_name": "삼성바이오로직스", "market": "KOSPI", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "005380", "stock_name": "현대차", "market": "KOSPI", "sector": "자동차", "industry": "완성차"},
        {"stock_code": "005935", "stock_name": "삼성전자우", "market": "KOSPI", "sector": "IT", "industry": "반도체"},
        {"stock_code": "000270", "stock_name": "기아", "market": "KOSPI", "sector": "자동차", "industry": "완성차"},
        {"stock_code": "068270", "stock_name": "셀트리온", "market": "KOSPI", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "035420", "stock_name": "NAVER", "market": "KOSPI", "sector": "IT", "industry": "인터넷"},
        {"stock_code": "051910", "stock_name": "LG화학", "market": "KOSPI", "sector": "화학", "industry": "석유화학"},
        {"stock_code": "006400", "stock_name": "삼성SDI", "market": "KOSPI", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "003670", "stock_name": "포스코퓨처엠", "market": "KOSPI", "sector": "철강", "industry": "철강"},
        {"stock_code": "035720", "stock_name": "카카오", "market": "KOSPI", "sector": "IT", "industry": "인터넷"},
        {"stock_code": "012330", "stock_name": "현대모비스", "market": "KOSPI", "sector": "자동차", "industry": "자동차부품"},
        {"stock_code": "028260", "stock_name": "삼성물산", "market": "KOSPI", "sector": "유통", "industry": "종합상사"},
        {"stock_code": "066570", "stock_name": "LG전자", "market": "KOSPI", "sector": "전기전자", "industry": "가전"},
        {"stock_code": "036570", "stock_name": "NCsoft", "market": "KOSPI", "sector": "IT", "industry": "게임"},
        {"stock_code": "033780", "stock_name": "KT&G", "market": "KOSPI", "sector": "생활소비재", "industry": "담배"},
        {"stock_code": "003550", "stock_name": "LG", "market": "KOSPI", "sector": "지주", "industry": "지주회사"},
        {"stock_code": "017670", "stock_name": "SK텔레콤", "market": "KOSPI", "sector": "통신", "industry": "무선통신"},
        {"stock_code": "105560", "stock_name": "KB금융", "market": "KOSPI", "sector": "금융", "industry": "은행"},
        {"stock_code": "055550", "stock_name": "신한지주", "market": "KOSPI", "sector": "금융", "industry": "은행"},
        {"stock_code": "086790", "stock_name": "하나금융지주", "market": "KOSPI", "sector": "금융", "industry": "은행"},
        {"stock_code": "316140", "stock_name": "우리금융지주", "market": "KOSPI", "sector": "금융", "industry": "은행"},
        {"stock_code": "024110", "stock_name": "기업은행", "market": "KOSPI", "sector": "금융", "industry": "은행"},
        {"stock_code": "090430", "stock_name": "아모레퍼시픽", "market": "KOSPI", "sector": "화장품", "industry": "화장품"},
        {"stock_code": "000810", "stock_name": "삼성화재", "market": "KOSPI", "sector": "금융", "industry": "보험"},
        {"stock_code": "009150", "stock_name": "삼성전기", "market": "KOSPI", "sector": "IT", "industry": "전자부품"},
        {"stock_code": "096770", "stock_name": "SK이노베이션", "market": "KOSPI", "sector": "에너지", "industry": "정유"},
        {"stock_code": "018260", "stock_name": "삼성에스디에스", "market": "KOSPI", "sector": "IT", "industry": "SI"},
        {"stock_code": "010130", "stock_name": "고려아연", "market": "KOSPI", "sector": "소재", "industry": "비철금속"},
        {"stock_code": "000100", "stock_name": "유한양행", "market": "KOSPI", "sector": "헬스케어", "industry": "제약"},
        {"stock_code": "034730", "stock_name": "SK", "market": "KOSPI", "sector": "지주", "industry": "지주회사"},
        {"stock_code": "032830", "stock_name": "삼성생명", "market": "KOSPI", "sector": "금융", "industry": "보험"},
        {"stock_code": "003490", "stock_name": "대한항공", "market": "KOSPI", "sector": "운송", "industry": "항공"},
        {"stock_code": "015760", "stock_name": "한국전력", "market": "KOSPI", "sector": "전기", "industry": "전력"},
        {"stock_code": "010140", "stock_name": "삼성중공업", "market": "KOSPI", "sector": "조선", "industry": "조선"},
        {"stock_code": "009540", "stock_name": "HD한국조선해양", "market": "KOSPI", "sector": "조선", "industry": "조선"},
        {"stock_code": "011200", "stock_name": "HMM", "market": "KOSPI", "sector": "운송", "industry": "해운"},
        {"stock_code": "034020", "stock_name": "두산에너빌리티", "market": "KOSPI", "sector": "기계", "industry": "중공업"},
        {"stock_code": "010950", "stock_name": "S-Oil", "market": "KOSPI", "sector": "에너지", "industry": "정유"},

        # KOSDAQ 대표 종목
        {"stock_code": "247540", "stock_name": "에코프로비엠", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "086520", "stock_name": "에코프로", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "328130", "stock_name": "루닛", "market": "KOSDAQ", "sector": "헬스케어", "industry": "AI의료"},
        {"stock_code": "196170", "stock_name": "알테오젠", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "141080", "stock_name": "레고켐바이오", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "145020", "stock_name": "휴젤", "market": "KOSDAQ", "sector": "헬스케어", "industry": "의료기기"},
        {"stock_code": "112040", "stock_name": "위메이드", "market": "KOSDAQ", "sector": "IT", "industry": "게임"},
        {"stock_code": "293490", "stock_name": "카카오게임즈", "market": "KOSDAQ", "sector": "IT", "industry": "게임"},
        {"stock_code": "263750", "stock_name": "펄어비스", "market": "KOSDAQ", "sector": "IT", "industry": "게임"},
        {"stock_code": "357780", "stock_name": "솔브레인", "market": "KOSDAQ", "sector": "화학", "industry": "전자재료"},
        {"stock_code": "272210", "stock_name": "한화시스템", "market": "KOSDAQ", "sector": "방산", "industry": "방위산업"},
        {"stock_code": "067160", "stock_name": "아프리카TV", "market": "KOSDAQ", "sector": "IT", "industry": "인터넷방송"},
        {"stock_code": "095340", "stock_name": "ISC", "market": "KOSDAQ", "sector": "철강", "industry": "철강"},
        {"stock_code": "383310", "stock_name": "에코프로에이치엔", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "122870", "stock_name": "와이지엔터테인먼트", "market": "KOSDAQ", "sector": "엔터", "industry": "엔터테인먼트"},
    ]

    success_count = 0
    fail_count = 0

    for stock in stocks:
        try:
            # Upsert (있으면 업데이트, 없으면 삽입)
            result = supabase.table('stock_metadata').upsert(stock).execute()
            print(f"  OK: {stock['stock_code']} - {stock['stock_name']}")
            success_count += 1
        except Exception as e:
            print(f"  ERROR: {stock['stock_code']} - {e}")
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"초기화 완료!")
    print(f"  성공: {success_count}개")
    print(f"  실패: {fail_count}개")
    print("=" * 60)

    # 테이블 확인
    check_result = supabase.table('stock_metadata').select('stock_code', count='exact').execute()
    total_count = len(check_result.data) if check_result.data else 0
    print(f"\n현재 stock_metadata 테이블의 총 종목 수: {total_count}개")

if __name__ == "__main__":
    init_stock_metadata()