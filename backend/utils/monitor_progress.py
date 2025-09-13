"""
다운로드 진행률 모니터링
"""
import os
import json
import time
from datetime import datetime

def monitor():
    """진행률 실시간 모니터링"""
    
    progress_files = [
        'auto_download_progress.json',
        'download_progress.json', 
        'collection_progress.txt',
        'test_progress.json'
    ]
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("="*60)
        print("📊 다운로드 진행률 모니터")
        print("="*60)
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)
        
        found = False
        
        for file in progress_files:
            if os.path.exists(file):
                found = True
                
                if file.endswith('.json'):
                    with open(file, 'r') as f:
                        data = json.load(f)
                        
                    completed = len(data.get('completed', []))
                    updated = data.get('updated', 'N/A')
                    
                    # 전체 종목 수 추정 (KOSPI 800 + KOSDAQ 1400)
                    total_estimate = 2200
                    progress = (completed / total_estimate) * 100
                    
                    # 진행률 바
                    bar_length = 40
                    filled = int(bar_length * completed / total_estimate)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"\n📁 {file}")
                    print(f"   완료: {completed:,}개 종목")
                    print(f"   진행: {bar} {progress:.1f}%")
                    print(f"   갱신: {updated}")
                    
                    # 최근 완료 종목
                    if data.get('completed'):
                        recent = data['completed'][-5:]
                        print(f"   최근: {', '.join(recent)}")
                    
                else:  # .txt 파일
                    with open(file, 'r') as f:
                        last_code = f.read().strip()
                    print(f"\n📁 {file}")
                    print(f"   마지막 종목: {last_code}")
        
        if not found:
            print("\n⚠️  진행 파일이 없습니다.")
            print("다운로드를 먼저 시작하세요:")
            print("  python safe_auto_download.py")
        
        # 예상 시간 계산
        if found and completed > 0:
            # 분당 처리 속도 (약 60개/분)
            speed = 60
            remaining = total_estimate - completed
            eta_minutes = remaining / speed
            eta_hours = eta_minutes / 60
            
            print(f"\n⏱️  예상 시간:")
            print(f"   남은 종목: {remaining:,}개")
            print(f"   처리 속도: 약 {speed}개/분")
            print(f"   예상 완료: {eta_hours:.1f}시간")
        
        print("\n[Ctrl+C로 종료, 5초마다 갱신]")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n종료합니다.")
            break

def check_once():
    """한 번만 확인"""
    print("Download Progress Status")
    print("-"*60)
    
    # 모든 진행 파일 체크
    files_found = []
    
    if os.path.exists('auto_download_progress.json'):
        with open('auto_download_progress.json', 'r') as f:
            data = json.load(f)
        completed = len(data.get('completed', []))
        print(f"[OK] auto_download_progress.json: {completed} completed")
        files_found.append(('auto', completed))
    
    if os.path.exists('download_progress.json'):
        with open('download_progress.json', 'r') as f:
            data = json.load(f)
        completed = len(data.get('completed_stocks', []))
        print(f"[OK] download_progress.json: {completed} completed")
        files_found.append(('batch', completed))
    
    if os.path.exists('collection_progress.txt'):
        with open('collection_progress.txt', 'r') as f:
            last = f.read().strip()
        print(f"[OK] collection_progress.txt: last {last}")
        files_found.append(('collect', 0))
    
    if not files_found:
        print("[X] No progress files found.")
    else:
        # 가장 많이 진행된 것
        best = max(files_found, key=lambda x: x[1])
        total = 2200  # 예상
        percent = (best[1] / total) * 100
        print(f"\nBest Progress: {best[1]:,}/{total:,} ({percent:.1f}%)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        check_once()
    else:
        monitor()