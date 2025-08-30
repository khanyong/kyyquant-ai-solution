# KyyQuant AI Solution - Project Structure

## 📁 Directory Structure

```
kyyquant-ai-solution/
├── 📁 backend/                 # Backend Python files
│   ├── api_server.py           # FastAPI server
│   ├── backend_api.py          # Backend API endpoints
│   ├── kiwoom_api.py           # Kiwoom Securities API integration
│   ├── main.py                 # Main backend entry point
│   ├── main_dev.py             # Development server
│   ├── models.py               # Data models
│   ├── trading_engine.py       # Trading logic engine
│   ├── test_api.py             # API tests
│   ├── run_servers.bat         # Windows server startup script
│   └── run_servers.sh          # Unix server startup script
│
├── 📁 docs/                    # Documentation
│   ├── README.md               # Main documentation
│   ├── SUPABASE_SETUP.md       # Supabase setup guide
│   ├── architecture.md         # System architecture
│   ├── 키움 REST API 문서.pdf  # Kiwoom API documentation
│   └── PROJECT_STRUCTURE.md    # This file
│
├── 📁 src/                     # Frontend React source code
│   ├── 📁 components/          # React components
│   │   ├── 📁 admin/           # Admin-only components
│   │   │   └── AdminApprovalPanel.tsx
│   │   ├── 📁 common/          # Shared components
│   │   │   ├── Header.tsx
│   │   │   ├── LoginDialog.tsx
│   │   │   └── Notice.tsx
│   │   ├── 📁 trading/         # Trading-related components
│   │   │   ├── AutoTradingPanel.tsx
│   │   │   ├── MarketOverview.tsx
│   │   │   ├── OrderPanel.tsx
│   │   │   ├── PortfolioPanel.tsx
│   │   │   └── StockChart.tsx
│   │   ├── 📁 test/            # Test/Development components
│   │   │   ├── TestEmailVerification.tsx
│   │   │   └── TestSupabase.tsx
│   │   ├── BacktestResults.tsx
│   │   ├── PerformanceDashboard.tsx
│   │   ├── SignalMonitor.tsx
│   │   ├── StrategyBuilder.tsx
│   │   └── TradingSettings.tsx
│   │
│   ├── 📁 hooks/               # Custom React hooks
│   │   └── redux.ts
│   │
│   ├── 📁 lib/                 # External library configurations
│   │   └── supabase.ts
│   │
│   ├── 📁 pages/               # Page components
│   │   ├── AdminDashboard.tsx
│   │   └── Settings.tsx
│   │
│   ├── 📁 services/            # API and service layers
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── kiwoomApi.ts
│   │   ├── kiwoomSupabase.ts
│   │   └── websocket.ts
│   │
│   ├── 📁 store/               # Redux store
│   │   ├── authSlice.ts
│   │   ├── index.ts
│   │   └── marketSlice.ts
│   │
│   ├── 📁 types/               # TypeScript type definitions
│   │   └── index.ts
│   │
│   ├── App.tsx                 # Main app component (old)
│   ├── AppWithRouter.tsx       # Main app with routing
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
│
├── 📁 supabase/                # Supabase database scripts
│   ├── schema.sql              # Main database schema
│   ├── complete-admin-setup.sql
│   ├── make-admin.sql
│   └── [other SQL files]
│
├── 📁 dist/                    # Production build output
├── 📁 node_modules/            # Node.js dependencies
│
├── 📄 Configuration Files
│   ├── .env.local              # Local environment variables
│   ├── .env.production         # Production environment variables
│   ├── .gitignore              # Git ignore rules
│   ├── package.json            # Node.js dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── vite.config.ts          # Vite bundler configuration
│   └── vercel.json             # Vercel deployment config
│
└── 📄 Project Management
    ├── .taskmaster/            # Task management system
    └── CLAUDE.md               # AI assistant instructions
```

## 🗂️ Component Organization

### Admin Components (`/src/components/admin/`)
- **AdminApprovalPanel**: User approval management for administrators

### Common Components (`/src/components/common/`)
- **Header**: Main navigation header
- **LoginDialog**: Authentication modal
- **Notice**: Announcements and notifications

### Trading Components (`/src/components/trading/`)
- **AutoTradingPanel**: Automated trading strategy management
- **MarketOverview**: Market status and indices
- **OrderPanel**: Order placement and management
- **PortfolioPanel**: Portfolio holdings display
- **StockChart**: Stock price visualization

### Test Components (`/src/components/test/`)
- **TestEmailVerification**: Email verification testing
- **TestSupabase**: Supabase connection testing

## 📝 Key Files

### Frontend Entry Points
- `src/main.tsx` - React application bootstrap
- `src/AppWithRouter.tsx` - Main application with routing

### Backend Entry Points
- `backend/main.py` - Production server
- `backend/main_dev.py` - Development server
- `backend/api_server.py` - FastAPI server

### Configuration
- `.env.local` - Local environment variables (Supabase keys)
- `supabase/complete-admin-setup.sql` - Admin system setup
- `supabase/make-admin.sql` - Grant admin privileges

## 🚀 Development Workflow

1. **Frontend Development**
   ```bash
   npm run dev
   ```

2. **Backend Development**
   ```bash
   cd backend
   python main_dev.py
   ```

3. **Database Setup**
   - Run SQL scripts in Supabase SQL Editor
   - Start with `complete-admin-setup.sql`
   - Then run `make-admin.sql` with your email

## 📦 Deployment

- **Frontend**: Deployed to Vercel
- **Backend**: Python FastAPI server (separate deployment)
- **Database**: Supabase (cloud-hosted PostgreSQL)

## 🔑 Environment Variables

Required environment variables in `.env.local`:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

## 🛠️ Technology Stack

- **Frontend**: React + TypeScript + Vite + Material-UI
- **Backend**: Python + FastAPI + Kiwoom API
- **Database**: Supabase (PostgreSQL)
- **State Management**: Redux Toolkit
- **Authentication**: Supabase Auth