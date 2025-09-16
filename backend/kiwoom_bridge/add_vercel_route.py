"""
Vercel 프론트엔드 호환을 위한 라우트 추가 스크립트
main.py 파일에 /api/backtest-run 라우트를 추가합니다.
"""

import os

# main.py 파일 경로
main_file = "main.py"

# 추가할 코드
additional_code = '''
# Vercel 프론트엔드 호환 라우트
@app.post("/api/backtest-run")
async def backtest_run_vercel(request: BacktestRequest):
    """Vercel에서 사용하는 경로 - /api/backtest/run으로 리다이렉트"""
    print(f"[VERCEL ROUTE] Redirecting to /api/backtest/run")
    # backtest_router의 run_backtest 직접 호출
    from backtest_api import run_backtest
    return await run_backtest(request)

print("[OK] Vercel compatibility route added: /api/backtest-run")
'''

# main.py 읽기
with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 이미 추가되었는지 확인
if "/api/backtest-run" in content:
    print("Route already exists!")
else:
    # BacktestRequest import 찾기
    import_line = "from backtest_api import router as backtest_router"
    if import_line in content:
        # BacktestRequest도 import에 추가
        new_import = "from backtest_api import router as backtest_router, BacktestRequest, run_backtest"
        content = content.replace(import_line, new_import)

    # 파일 끝에 라우트 추가
    content = content + "\n" + additional_code

    # 파일 저장
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Route added successfully!")
    print("Please restart the Docker container:")
    print("  docker-compose restart kiwoom-bridge")