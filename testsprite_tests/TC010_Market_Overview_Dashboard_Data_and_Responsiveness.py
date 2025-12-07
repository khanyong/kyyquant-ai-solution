import asyncio
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None
    
    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()
        
        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )
        
        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)
        
        # Open a new page in the browser context
        page = await context.new_page()
        
        # Navigate to your target URL and wait until the network request is committed
        await page.goto("http://localhost:3000", wait_until="commit", timeout=10000)
        
        # Wait for the main page to reach DOMContentLoaded state (optional for stability)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except async_api.Error:
            pass
        
        # Iterate through all iframes and wait for them to load as well
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except async_api.Error:
                pass
        
        # Interact with the page elements to simulate user flow
        # -> Click on the link or button to open the Market Overview dashboard.
        frame = context.pages[-1]
        # Click on '전략 마켓플레이스' link to open Market Overview dashboard
        elem = frame.locator('xpath=html/body/div/div/div/div[9]/div/div/div[2]/div/a[2]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Resize viewport to tablet size and verify dashboard layout and usability.
        await page.mouse.wheel(0, 400)
        

        await page.mouse.wheel(0, 400)
        

        # --> Assertions to verify final state
        frame = context.pages[-1]
        await expect(frame.locator('text=전략 마켓플레이스').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=전략 팔로우').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=자동 매매 실행').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=이중 수익 구조').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=전략 보호').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=투자 유니버스 필터링').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=30+ 재무지표와 기술적 지표를 활용하여 우량 종목을 자동으로 선별합니다.').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=재무지표 필터링').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=실시간 스크리닝').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=커스텀 필터 저장').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=백테스트 연동').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=전략 빌더').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=코딩 없이 클릭만으로 복잡한 매매 전략을 만들고 최적화할 수 있습니다.').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=노코드 전략 생성').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=50+ 기술적 지표').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=다중 조건 설정').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=전략 템플릿').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=백테스팅 엔진').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=과거 10년 데이터로 전략을 검증하고 성과를 시뮬레이션합니다.').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=10년+ 과거 데이터').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=실시간 결과 분석').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=리스크 지표').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=최적화 기능').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=실시간 신호').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=밀리초 단위로 시장을 모니터링하고 매매 시그널을 포착합니다.').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=실시간 모니터링').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=즉시 알림').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=신호 필터링').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=WebSocket 연결').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=자동매매').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=검증된 전략을 자동으로 실행하여 기회를 놓치지 않습니다.').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=자동 주문 실행').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=위험 관리').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=포지션 관리').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=실시간 모니터링').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=성과 분석').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=AI가 포트폴리오를 분석하고 개선점을 제안합니다.').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=AI 분석 리포트').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=수익률 추적').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=리스크 분석').first).to_be_visible(timeout=30000)
        await expect(frame.locator('text=개선 제안').first).to_be_visible(timeout=30000)
        await asyncio.sleep(5)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    