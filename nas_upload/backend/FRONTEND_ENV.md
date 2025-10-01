# Frontend 환경 변수 (Vercel)

## 🌐 Vercel 환경 변수 설정

```bash
# WebSocket URL
VITE_WS_URL=wss://api.bll-pro.com/ws

# API URL (Cloudflared)
VITE_API_URL=https://api.bll-pro.com
NAS_API_URL=https://api.bll-pro.com

# TLS 설정
NODE_TLS_REJECT_UNAUTHORIZED=0

# N8N Workflow
VITE_N8N_URL=https://workflow.bll-pro.com

# Supabase
VITE_SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs
```

## 📌 연결 구조

```
Vercel Frontend (React/Vite)
    ↓
Cloudflared Tunnel (HTTPS)
    - api.bll-pro.com → NAS 8080 포트
    - workflow.bll-pro.com → N8N
    ↓
NAS Server (192.168.50.150)
    - Backend API: 포트 8080 → 8001
    - N8N Workflow: 포트 5678
    ↓
Supabase Cloud Database
```

## 🔧 Backend에서 필요한 설정

Backend의 `.env` 파일에 다음 추가:

```bash
# Supabase (Frontend와 동일)
SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs

# CORS 설정 (Frontend URL)
FRONTEND_URL=https://your-vercel-app.vercel.app
```

## ⚠️ 주의사항

1. **CORS 설정**: Backend에서 Vercel 도메인 허용 필요
2. **WebSocket**: 현재 Backend에 WS 구현 필요시 추가 개발 필요
3. **TLS**: `NODE_TLS_REJECT_UNAUTHORIZED=0`은 개발용, 프로덕션에서는 보안 인증서 사용 권장