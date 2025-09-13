# Vercel 배포 문제 해결 가이드

## 🚨 현재 문제
- 외부 사용자가 전략 저장 시 에러 발생
- NAS API 서버 외부 접근 불가 (`khanyong.asuscomm.com:8001`)
- 잘못된 Supabase URL이 빌드에 포함됨

## ✅ 즉시 해결 방법

### 1. Vercel 환경 변수 수정

Vercel 대시보드 → Settings → Environment Variables:

```bash
VITE_SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs
```

### 2. API URL 설정 (선택)

**옵션 A**: NAS 포트 포워딩 설정 후
```bash
VITE_API_URL=https://khanyong.asuscomm.com:8001
```

**옵션 B**: 임시로 제거 (Supabase만 사용)
```bash
# VITE_API_URL 주석 처리 또는 삭제
```

### 3. 재배포

환경 변수 수정 후 자동 재배포가 시작됩니다.

## 🔧 NAS 서버 외부 접근 설정 (옵션)

### 공유기 설정:
1. 포트 포워딩: 8001 → NAS IP:8001
2. DDNS 확인: khanyong.asuscomm.com 정상 작동

### NAS 설정:
1. 방화벽: 8001 포트 허용
2. Docker 컨테이너: 포트 바인딩 확인

## 🎯 우선순위

1. **즉시**: Vercel 환경 변수 수정 + 재배포
2. **나중**: NAS 외부 접근 설정 (백테스트용)

전략 저장은 Supabase만으로도 충분히 작동합니다!