# 🚀 Backend 배포 가이드

## 배포 옵션별 실행 방식

### 1. **Vercel/Netlify (프론트엔드) + Railway/Render (백엔드)**

```yaml
# railway.toml 또는 render.yaml
services:
  - type: web
    name: auto-stock-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        value: your-supabase-url
      - key: SUPABASE_KEY
        value: your-supabase-key
```

**실행 과정:**
1. Git push → Railway/Render 자동 배포
2. Python 서버가 클라우드에서 24/7 실행
3. 프론트엔드가 `https://your-api.railway.app`로 요청

### 2. **AWS EC2 / Google Cloud VM**

```bash
# 서버 설정 스크립트
#!/bin/bash

# 1. Python 환경 설정
sudo apt update
sudo apt install python3.11 python3-pip nginx

# 2. 프로젝트 클론
git clone https://github.com/your/auto_stock.git
cd auto_stock/backend

# 3. 의존성 설치
pip install -r requirements.txt

# 4. systemd 서비스 생성
sudo tee /etc/systemd/system/auto-stock.service > /dev/null <<EOF
[Unit]
Description=Auto Stock Trading Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/auto_stock/backend
ExecStart=/usr/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 5. 서비스 시작
sudo systemctl enable auto-stock
sudo systemctl start auto-stock
```

### 3. **Docker 컨테이너 배포**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENAPI_KEY=${OPENAPI_KEY}
      - OPENAPI_SECRET=${OPENAPI_SECRET}
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - backend
```

### 4. **Serverless (AWS Lambda / Vercel Functions)**

```python
# vercel_function.py
from fastapi import FastAPI
from mangum import Mangum
from api_server import app

# Vercel serverless adapter
handler = Mangum(app)
```

```json
// vercel.json
{
  "functions": {
    "api/*.py": {
      "runtime": "python3.9"
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/vercel_function"
    }
  ]
}
```

## 🔄 실시간 전략 실행 방식

### **Option 1: 크론잡 스케줄러**
```python
# scheduler.py
import schedule
import time
from datetime import datetime
from trading_engine import TradingEngine

def run_trading_strategy():
    """매일 9시에 실행"""
    if is_market_open():
        engine = TradingEngine()
        engine.execute_all_active_strategies()

# 스케줄 설정
schedule.every().day.at("09:00").do(run_trading_strategy)
schedule.every(1).minutes.do(check_signals)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### **Option 2: Celery + Redis (비동기 작업)**
```python
# celery_tasks.py
from celery import Celery
from celery.schedules import crontab

app = Celery('auto_stock', broker='redis://localhost:6379')

@app.task
def execute_strategy(strategy_id):
    """전략 실행 태스크"""
    from strategy_manager import CloudStrategyManager
    manager = CloudStrategyManager()
    strategy = manager.load_strategy(strategy_id)
    # 전략 실행...

# 주기적 실행 설정
app.conf.beat_schedule = {
    'execute-strategies': {
        'task': 'celery_tasks.execute_strategy',
        'schedule': crontab(hour=9, minute=0),  # 매일 9시
    },
}
```

### **Option 3: GitHub Actions (무료 자동화)**
```yaml
# .github/workflows/trading.yml
name: Auto Trading

on:
  schedule:
    - cron: '0 0 * * 1-5'  # 평일 9시 (UTC+9)
  workflow_dispatch:  # 수동 실행

jobs:
  trade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run trading strategy
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          python backend/run_strategy.py
```

## 📊 모니터링 대시보드

```python
# monitoring.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """실시간 모니터링 대시보드"""
    # Supabase에서 데이터 조회
    strategies = db.get_active_strategies()
    performance = db.get_performance_metrics()
    
    # Plotly 차트 생성
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=performance['dates'],
        y=performance['returns'],
        name='Strategy Returns'
    ))
    
    html = f"""
    <html>
        <head>
            <title>Trading Dashboard</title>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <h1>실시간 트레이딩 대시보드</h1>
            <div>{fig.to_html()}</div>
            <h2>활성 전략: {len(strategies)}</h2>
            <ul>
                {"".join([f"<li>{s['name']}: {s['status']}</li>" for s in strategies])}
            </ul>
        </body>
    </html>
    """
    return html
```

## 🔑 환경 변수 설정

```bash
# .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
OPENAPI_APP_KEY=your-korea-investment-key
OPENAPI_APP_SECRET=your-korea-investment-secret
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/db
```

## 📝 배포 체크리스트

- [ ] 환경 변수 설정 완료
- [ ] Supabase 테이블 생성 완료
- [ ] API 서버 실행 테스트
- [ ] 프론트엔드 API URL 설정
- [ ] SSL 인증서 설정 (프로덕션)
- [ ] 로그 수집 설정
- [ ] 에러 모니터링 (Sentry 등)
- [ ] 백업 스케줄 설정
- [ ] 보안 점검 (API Key 숨김)