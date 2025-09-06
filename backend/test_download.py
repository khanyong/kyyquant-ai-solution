"""
간단한 다운로드 테스트 (진행률 표시)
"""
import os
import json
import time
from datetime import datetime

def test_download():
    """다운로드 시뮬레이션 (실제 API 없이)"""
    
    # 테스트 종목 리스트
    test_stocks = [
        ('005930', '삼성전자'),
        ('000660', 'SK하이닉스'),
        ('035720', '카카오'),
        ('035420', '네이버'),
        ('005380', '현대차'),
        ('051910', 'LG화학'),
        ('006400', '삼성SDI'),
        ('003550', 'LG'),
        ('105560', 'KB금융'),
        ('055550', '신한지주'),
    ]
    
    progress_file = "test_progress.json"
    
    # 이전 진행 상황 로드
    completed = []
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            data = json.load(f)
            completed = data.get('completed', [])
    
    print("="*60)
    print("📊 다운로드 테스트 (진행률 표시)")
    print("="*60)
    
    total = len(test_stocks)
    done = len(completed)
    
    print(f"전체: {total}개 종목")
    print(f"완료: {done}개")
    print(f"남은: {total - done}개")
    print("-"*60)
    
    for code, name in test_stocks:
        if code in completed:
            continue
            
        done += 1
        progress = (done / total) * 100
        
        # 진행률 바
        bar_length = 30
        filled = int(bar_length * done / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n[{done}/{total}] {bar} {progress:.1f}%")
        print(f"다운로드 중: {name} ({code})")
        
        # 다운로드 시뮬레이션
        time.sleep(1)  # 실제로는 여기서 API 호출
        
        print(f"  ✓ 일봉: 2,500일")
        print(f"  ✓ 주봉: 520주")
        print(f"  ✓ 월봉: 120개월")
        
        # 완료 목록에 추가
        completed.append(code)
        
        # 진행 상황 저장
        with open(progress_file, 'w') as f:
            json.dump({
                'completed': completed,
                'updated': datetime.now().isoformat(),
                'progress': f"{done}/{total}"
            }, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ 다운로드 완료!")
    print(f"총 {total}개 종목 처리")
    print("="*60)

if __name__ == "__main__":
    test_download()