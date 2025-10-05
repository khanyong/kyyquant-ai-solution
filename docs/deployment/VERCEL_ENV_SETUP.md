# Vercel 환경변수 설정 가이드

## 🎯 데모 영상 URL 설정

### Vercel Dashboard에서 설정

1. **Vercel 프로젝트 접속**
   - https://vercel.com/dashboard
   - 해당 프로젝트 선택

2. **Settings → Environment Variables**
   - 상단 메뉴에서 **Settings** 클릭
   - 왼쪽 메뉴에서 **Environment Variables** 클릭

3. **환경변수 추가**

   | Key | Value | Environment |
   |-----|-------|-------------|
   | `VITE_DEMO_VIDEO_URL` | `https://hznkyaomtrpzcayayayh.supabase.co/storage/v1/object/public/public-assets/video-1759676192502.mp4` | Production, Preview, Development |

4. **Save** 클릭

5. **재배포 (Re-deploy)**
   - Deployments 탭으로 이동
   - 가장 최근 배포 → 오른쪽 점 3개 클릭 → **Redeploy**
   - 또는 새로운 커밋 푸시 시 자동 재배포

---

## 📋 전체 Vercel 환경변수 목록

### 필수 환경변수

```bash
# Supabase
VITE_SUPABASE_URL=https://hznkyaomtrpzcayayayh.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs

# 백테스트 서버 (프로덕션용 - 별도 설정 필요)
VITE_API_URL=https://api.kyyquant.com

# 데모 영상
VITE_DEMO_VIDEO_URL=https://hznkyaomtrpzcayayayh.supabase.co/storage/v1/object/public/public-assets/video-1759676192502.mp4
```

### 선택 환경변수 (나중에 추가)

```bash
# N8N Webhook
N8N_WEBHOOK_URL=https://n8n.kyyquant.com/webhook/...

# 키움증권 (프로덕션에서는 불필요 - 백엔드에서 처리)
# KIWOOM_* 변수들은 Vercel에 설정 안 함
```

---

## 🔒 보안 주의사항

### ✅ Vercel에 추가해도 안전한 변수
- `VITE_*` 접두사 변수 (클라이언트 노출)
- Supabase ANON KEY (공개용 키)
- 데모 영상 URL (공개 버킷)

### ❌ Vercel에 추가하면 안 되는 변수
- `SUPABASE_SERVICE_KEY` (서버용 키)
- `KIWOOM_APP_SECRET` (비밀 키)
- `GITHUB_PERSONAL_ACCESS_TOKEN` (개인 토큰)

> 위 비밀 변수들은 백엔드 서버 또는 Vercel Edge Functions에서만 사용

---

## 📺 데모 영상 작동 원리

### 로컬 개발 환경
```typescript
// .env 파일에서 로드
VITE_DEMO_VIDEO_URL=https://...supabase.co/storage/.../demo-video.mp4

// 코드에서 사용
videoSrc={import.meta.env.VITE_DEMO_VIDEO_URL || '/Company_CI/video-1759676192502.mp4'}
```

### Vercel 배포 환경
```typescript
// Vercel 환경변수에서 로드
VITE_DEMO_VIDEO_URL=https://...supabase.co/storage/.../demo-video.mp4

// 빌드 시 자동으로 주입됨
```

### Fallback (환경변수 없을 때)
```typescript
// 로컬 파일 경로로 폴백
videoSrc='/Company_CI/video-1759676192502.mp4'
```

---

## 🚀 배포 체크리스트

### 배포 전 확인사항

- [ ] Supabase Storage에 동영상 업로드 완료
- [ ] Vercel 환경변수 `VITE_DEMO_VIDEO_URL` 설정 완료
- [ ] 로컬에서 `.env` 파일 업데이트 완료
- [ ] 코드 커밋 & 푸시 완료

### 배포 후 확인사항

- [ ] Vercel 배포 성공 확인
- [ ] 배포된 사이트에서 "데모 영상 보기" 버튼 클릭
- [ ] 동영상 정상 재생 확인
- [ ] 컨트롤 동작 확인 (재생/일시정지/볼륨/전체화면)
- [ ] 모바일에서도 재생 확인

---

## 🐛 문제 해결

### 동영상이 재생되지 않을 때

1. **Supabase Storage 확인**
   ```
   URL: https://hznkyaomtrpzcayayayh.supabase.co/storage/v1/object/public/public-assets/demo-video.mp4
   → 브라우저에서 직접 접속해서 동영상 다운로드되는지 확인
   ```

2. **버킷이 Public인지 확인**
   ```
   Supabase Dashboard → Storage → public-assets
   → "Public" 표시 확인
   ```

3. **CORS 에러 발생 시**
   ```
   Supabase Dashboard → Storage → Policies
   → "Allow public access to public-assets bucket" 정책 추가
   ```

4. **Vercel 환경변수 확인**
   ```
   Vercel Dashboard → Settings → Environment Variables
   → VITE_DEMO_VIDEO_URL 값 확인
   → 오타 없는지 체크
   ```

5. **재배포**
   ```
   환경변수 변경 후에는 반드시 재배포 필요!
   Deployments → Redeploy
   ```

---

## 📊 대안: Vercel Blob Storage (선택사항)

Supabase Storage 대신 Vercel Blob을 사용할 수도 있습니다:

### Vercel Blob 사용법

1. **Vercel Dashboard → Storage → Create Database**
   - Blob 선택

2. **동영상 업로드**
   ```bash
   npm install @vercel/blob

   # 업로드 스크립트
   import { put } from '@vercel/blob'
   const blob = await put('demo-video.mp4', file, { access: 'public' })
   console.log(blob.url)
   ```

3. **환경변수 업데이트**
   ```bash
   VITE_DEMO_VIDEO_URL=https://[random].public.blob.vercel-storage.com/demo-video.mp4
   ```

### 비교

| 항목 | Supabase Storage | Vercel Blob |
|------|------------------|-------------|
| 무료 용량 | 1GB | 500MB |
| CDN | ✅ | ✅ |
| 설정 난이도 | 쉬움 | 중간 |
| 추가 비용 | 없음 | 없음 (무료 플랜) |
| 추천 | ⭐⭐⭐ (이미 사용 중) | ⭐⭐ |

---

**작성일**: 2024-10-06
**작성자**: Claude Code Assistant
