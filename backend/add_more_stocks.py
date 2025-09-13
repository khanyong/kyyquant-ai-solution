"""
stock_metadata 테이블에 추가 종목 삽입
KOSPI와 KOSDAQ 주요 종목 확대
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def add_more_stocks():
    """추가 종목 데이터 삽입"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("추가 종목 데이터 삽입")
    print("=" * 60)

    # 추가할 종목 리스트
    additional_stocks = [
        # KOSPI 추가 종목 (시가총액 상위)
        {"stock_code": "005490", "stock_name": "POSCO홀딩스", "market": "KOSPI", "sector": "철강", "industry": "철강"},
        {"stock_code": "030200", "stock_name": "KT", "market": "KOSPI", "sector": "통신", "industry": "통신"},
        {"stock_code": "259960", "stock_name": "크래프톤", "market": "KOSPI", "sector": "IT", "industry": "게임"},
        {"stock_code": "034220", "stock_name": "LG디스플레이", "market": "KOSPI", "sector": "IT", "industry": "디스플레이"},
        {"stock_code": "011170", "stock_name": "롯데케미칼", "market": "KOSPI", "sector": "화학", "industry": "석유화학"},
        {"stock_code": "010120", "stock_name": "LS ELECTRIC", "market": "KOSPI", "sector": "전기전자", "industry": "중전기"},
        {"stock_code": "011070", "stock_name": "LG이노텍", "market": "KOSPI", "sector": "IT", "industry": "전자부품"},
        {"stock_code": "009830", "stock_name": "한화솔루션", "market": "KOSPI", "sector": "화학", "industry": "태양광"},
        {"stock_code": "161390", "stock_name": "한국타이어앤테크놀로지", "market": "KOSPI", "sector": "자동차", "industry": "타이어"},
        {"stock_code": "251270", "stock_name": "넷마블", "market": "KOSPI", "sector": "IT", "industry": "게임"},
        {"stock_code": "271560", "stock_name": "오리온", "market": "KOSPI", "sector": "식품", "industry": "제과"},
        {"stock_code": "000120", "stock_name": "CJ대한통운", "market": "KOSPI", "sector": "운송", "industry": "물류"},
        {"stock_code": "001040", "stock_name": "CJ", "market": "KOSPI", "sector": "지주", "industry": "지주회사"},
        {"stock_code": "004020", "stock_name": "현대제철", "market": "KOSPI", "sector": "철강", "industry": "철강"},
        {"stock_code": "011790", "stock_name": "SKC", "market": "KOSPI", "sector": "화학", "industry": "화학"},
        {"stock_code": "005830", "stock_name": "DB손해보험", "market": "KOSPI", "sector": "금융", "industry": "보험"},
        {"stock_code": "001570", "stock_name": "금양", "market": "KOSPI", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "078930", "stock_name": "GS", "market": "KOSPI", "sector": "지주", "industry": "지주회사"},
        {"stock_code": "006360", "stock_name": "GS건설", "market": "KOSPI", "sector": "건설", "industry": "건설"},
        {"stock_code": "011780", "stock_name": "금호석유", "market": "KOSPI", "sector": "화학", "industry": "석유화학"},
        {"stock_code": "000720", "stock_name": "현대건설", "market": "KOSPI", "sector": "건설", "industry": "건설"},
        {"stock_code": "028050", "stock_name": "삼성엔지니어링", "market": "KOSPI", "sector": "건설", "industry": "엔지니어링"},
        {"stock_code": "002790", "stock_name": "아모레G", "market": "KOSPI", "sector": "화장품", "industry": "화장품"},
        {"stock_code": "021240", "stock_name": "코웨이", "market": "KOSPI", "sector": "가전", "industry": "생활가전"},
        {"stock_code": "241560", "stock_name": "두산밥캣", "market": "KOSPI", "sector": "기계", "industry": "건설기계"},
        {"stock_code": "042660", "stock_name": "한화오션", "market": "KOSPI", "sector": "조선", "industry": "조선"},
        {"stock_code": "005070", "stock_name": "코스모신소재", "market": "KOSPI", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "047050", "stock_name": "포스코인터내셔널", "market": "KOSPI", "sector": "유통", "industry": "종합상사"},
        {"stock_code": "326030", "stock_name": "SK바이오팜", "market": "KOSPI", "sector": "헬스케어", "industry": "제약"},
        {"stock_code": "361610", "stock_name": "SK아이이테크놀로지", "market": "KOSPI", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "302440", "stock_name": "SK바이오사이언스", "market": "KOSPI", "sector": "헬스케어", "industry": "백신"},
        {"stock_code": "377300", "stock_name": "카카오페이", "market": "KOSPI", "sector": "IT", "industry": "핀테크"},
        {"stock_code": "138040", "stock_name": "메리츠금융지주", "market": "KOSPI", "sector": "금융", "industry": "금융"},
        {"stock_code": "029780", "stock_name": "삼성카드", "market": "KOSPI", "sector": "금융", "industry": "카드"},
        {"stock_code": "071050", "stock_name": "한국금융지주", "market": "KOSPI", "sector": "금융", "industry": "금융"},
        {"stock_code": "032640", "stock_name": "LG유플러스", "market": "KOSPI", "sector": "통신", "industry": "통신"},
        {"stock_code": "003410", "stock_name": "쌍용C&E", "market": "KOSPI", "sector": "건설", "industry": "시멘트"},
        {"stock_code": "267250", "stock_name": "HD현대", "market": "KOSPI", "sector": "지주", "industry": "지주회사"},
        {"stock_code": "000880", "stock_name": "한화", "market": "KOSPI", "sector": "화학", "industry": "화약"},
        {"stock_code": "088350", "stock_name": "한화생명", "market": "KOSPI", "sector": "금융", "industry": "보험"},

        # KOSDAQ 추가 종목 (시가총액 상위 및 주요 성장주)
        {"stock_code": "373220", "stock_name": "LG에너지솔루션", "market": "KOSPI", "sector": "IT", "industry": "2차전지"},  # 실제로는 KOSPI
        {"stock_code": "091990", "stock_name": "셀트리온헬스케어", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "036930", "stock_name": "주성엔지니어링", "market": "KOSDAQ", "sector": "IT", "industry": "반도체장비"},
        {"stock_code": "121600", "stock_name": "나노신소재", "market": "KOSDAQ", "sector": "소재", "industry": "2차전지소재"},
        {"stock_code": "222800", "stock_name": "심텍", "market": "KOSDAQ", "sector": "IT", "industry": "PCB"},
        {"stock_code": "214450", "stock_name": "파마리서치", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "214150", "stock_name": "클래시스", "market": "KOSDAQ", "sector": "헬스케어", "industry": "의료기기"},
        {"stock_code": "195870", "stock_name": "해성디에스", "market": "KOSDAQ", "sector": "IT", "industry": "휴대폰부품"},
        {"stock_code": "192820", "stock_name": "코스맥스", "market": "KOSDAQ", "sector": "화장품", "industry": "화장품OEM"},
        {"stock_code": "140860", "stock_name": "파크시스템스", "market": "KOSDAQ", "sector": "IT", "industry": "측정장비"},
        {"stock_code": "403870", "stock_name": "HPSP", "market": "KOSDAQ", "sector": "IT", "industry": "반도체"},
        {"stock_code": "399720", "stock_name": "가온칩스", "market": "KOSDAQ", "sector": "IT", "industry": "반도체"},
        {"stock_code": "394280", "stock_name": "오픈엣지테크놀로지", "market": "KOSDAQ", "sector": "IT", "industry": "AI반도체"},
        {"stock_code": "393890", "stock_name": "더블유씨피", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지"},
        {"stock_code": "348370", "stock_name": "엔켐", "market": "KOSDAQ", "sector": "화학", "industry": "2차전지소재"},
        {"stock_code": "336570", "stock_name": "원텍", "market": "KOSDAQ", "sector": "IT", "industry": "반도체장비"},
        {"stock_code": "319660", "stock_name": "피에스케이", "market": "KOSDAQ", "sector": "IT", "industry": "반도체장비"},
        {"stock_code": "317690", "stock_name": "퀄리타스반도체", "market": "KOSDAQ", "sector": "IT", "industry": "반도체"},
        {"stock_code": "298380", "stock_name": "에이비엘바이오", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "290650", "stock_name": "엘앤씨바이오", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "278280", "stock_name": "천보", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지소재"},
        {"stock_code": "253450", "stock_name": "스튜디오드래곤", "market": "KOSDAQ", "sector": "엔터", "industry": "콘텐츠"},
        {"stock_code": "240810", "stock_name": "원익IPS", "market": "KOSDAQ", "sector": "IT", "industry": "반도체장비"},
        {"stock_code": "237690", "stock_name": "에스티팜", "market": "KOSDAQ", "sector": "헬스케어", "industry": "제약"},
        {"stock_code": "236810", "stock_name": "엔비티", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "228760", "stock_name": "지노믹트리", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "222080", "stock_name": "씨아이에스", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지장비"},
        {"stock_code": "214370", "stock_name": "케어젠", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "200670", "stock_name": "휴메딕스", "market": "KOSDAQ", "sector": "헬스케어", "industry": "의료기기"},
        {"stock_code": "194480", "stock_name": "데브시스터즈", "market": "KOSDAQ", "sector": "IT", "industry": "게임"},
        {"stock_code": "183300", "stock_name": "코미코", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지소재"},
        {"stock_code": "178320", "stock_name": "서진시스템", "market": "KOSDAQ", "sector": "IT", "industry": "2차전지장비"},
        {"stock_code": "166090", "stock_name": "하나머티리얼즈", "market": "KOSDAQ", "sector": "IT", "industry": "반도체소재"},
        {"stock_code": "160980", "stock_name": "싸이맥스", "market": "KOSDAQ", "sector": "IT", "industry": "반도체장비"},
        {"stock_code": "137400", "stock_name": "피엔티", "market": "KOSDAQ", "sector": "IT", "industry": "반도체장비"},
        {"stock_code": "131970", "stock_name": "테스나", "market": "KOSDAQ", "sector": "IT", "industry": "반도체검사"},
        {"stock_code": "123860", "stock_name": "아나패스", "market": "KOSDAQ", "sector": "IT", "industry": "반도체설계"},
        {"stock_code": "098460", "stock_name": "고영", "market": "KOSDAQ", "sector": "IT", "industry": "검사장비"},
        {"stock_code": "095700", "stock_name": "제넥신", "market": "KOSDAQ", "sector": "헬스케어", "industry": "바이오"},
        {"stock_code": "094360", "stock_name": "칩스앤미디어", "market": "KOSDAQ", "sector": "IT", "industry": "반도체설계"},
    ]

    success_count = 0
    fail_count = 0
    skip_count = 0

    for stock in additional_stocks:
        try:
            # 이미 있는지 확인
            existing = supabase.table('stock_metadata').select('stock_code').eq('stock_code', stock['stock_code']).execute()

            if existing.data:
                print(f"  SKIP: {stock['stock_code']} - {stock['stock_name']} (이미 존재)")
                skip_count += 1
            else:
                # 새로운 종목 추가
                result = supabase.table('stock_metadata').insert(stock).execute()
                print(f"  OK: {stock['stock_code']} - {stock['stock_name']}")
                success_count += 1

        except Exception as e:
            print(f"  ERROR: {stock['stock_code']} - {e}")
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"추가 완료!")
    print(f"  성공: {success_count}개")
    print(f"  건너뜀: {skip_count}개")
    print(f"  실패: {fail_count}개")
    print("=" * 60)

    # 전체 종목 수 확인
    total_result = supabase.table('stock_metadata').select('stock_code', count='exact').execute()
    total_count = len(total_result.data) if total_result.data else 0
    print(f"\n현재 stock_metadata 테이블의 총 종목 수: {total_count}개")

    # 시장별 분류
    kospi = supabase.table('stock_metadata').select('stock_code').eq('market', 'KOSPI').execute()
    kosdaq = supabase.table('stock_metadata').select('stock_code').eq('market', 'KOSDAQ').execute()

    print(f"  - KOSPI: {len(kospi.data) if kospi.data else 0}개")
    print(f"  - KOSDAQ: {len(kosdaq.data) if kosdaq.data else 0}개")

if __name__ == "__main__":
    add_more_stocks()