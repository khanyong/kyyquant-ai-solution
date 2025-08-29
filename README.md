# KyyQuant AI Solution

🚀 **Algorithmic Trading Platform** - 보조지표 기반 자동매매 시스템

## 📌 Overview

KyyQuant AI Solution은 프로그램 매매에 특화된 알고리즘 트레이딩 플랫폼입니다.
보조지표를 활용한 매매 조건 설정, 백테스팅, 실시간 신호 모니터링을 제공합니다.

## ✨ Features

- **📊 전략 빌더**: RSI, MACD, 볼린저밴드 등 다양한 보조지표 조합
- **📈 백테스팅**: 과거 데이터로 전략 검증 및 성과 분석
- **⚡ 실시간 신호**: 매수/매도 신호 실시간 모니터링
- **📉 성과 대시보드**: Sharpe Ratio, MDD, 승률 등 핵심 지표 분석
- **🔒 리스크 관리**: 손절/익절, 포지션 사이징, 트레일링 스탑

## 🛠 Tech Stack

### Backend
- Python 3.10+
- FastAPI
- PyQt5 (키움 OpenAPI+ 연동)
- Pandas, NumPy
- WebSocket

### Frontend
- React 18 + TypeScript
- Material-UI
- Redux Toolkit
- Chart.js
- Socket.io-client

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- 키움 OpenAPI+ (Windows only)

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env file with your configuration
```

### Frontend Setup

```bash
# Install Node dependencies
npm install
```

## 🚀 Quick Start

### Option 1: Run Both Servers

```bash
# Windows
run_servers.bat

# Linux/Mac
./run_servers.sh
```

### Option 2: Run Separately

```bash
# Terminal 1: Backend server
python api_server.py

# Terminal 2: Frontend server
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
kyyquant-ai-solution/
├── src/                    # React frontend source
│   ├── components/         # UI components
│   ├── services/          # API services
│   ├── store/            # Redux store
│   └── types/            # TypeScript types
├── api_server.py         # FastAPI server
├── kiwoom_api.py        # Kiwoom OpenAPI+ wrapper
├── trading_engine.py    # Trading strategies & backtesting
├── models.py           # Pydantic models
└── requirements.txt    # Python dependencies
```

## 📊 Trading Strategies

### Available Indicators
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
- Volume Analysis
- Stochastic Oscillator

### Strategy Examples
```python
# RSI Oversold Strategy
if RSI(14) < 30 and price > SMA(20):
    signal = BUY

# MACD Crossover Strategy
if MACD_line crosses above Signal_line:
    signal = BUY
```

## 🧪 Testing

```bash
# Run API tests
python test_api.py

# Run backtest
python trading_engine.py
```

## 📝 API Documentation

Interactive API documentation available at http://localhost:8000/docs

### Key Endpoints
- `POST /api/login` - User authentication
- `GET /api/accounts` - Get account list
- `POST /api/balance` - Get account balance
- `POST /api/order` - Place order
- `WS /ws` - WebSocket for real-time data

## ⚠️ Important Notes

1. **Windows Only**: 키움 OpenAPI+ requires Windows OS
2. **Market Hours**: Real trading only during KRX market hours
3. **Demo Mode**: Use `DEMO_MODE=true` for testing
4. **Risk Management**: Always set stop-loss and position limits

## 📄 License

Private - All rights reserved

## 🤝 Contributing

This is a private repository. For questions or suggestions, please contact the repository owner.

## 📧 Contact

For support or inquiries, please open an issue in this repository.

---

**Disclaimer**: This software is for educational purposes. Always test thoroughly before using with real money. The authors are not responsible for any financial losses.