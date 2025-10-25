# NAS로 복사해야 할 파일 목록

백엔드 API 수정사항을 NAS Docker 컨테이너에 반영하기 위해 다음 파일들을 수동으로 복사하세요.

## 📋 복사할 파일

### 1. 새로 생성된 파일

**소스**: `d:\Dev\auto_stock\backend\api\indicators.py`
**대상**: `\\eiNNNieSysNAS\docker\auto_stock\backend\api\indicators.py`

> 🆕 지표 계산 API 엔드포인트

### 2. 수정된 파일

**소스**: `d:\Dev\auto_stock\backend\main.py`
**대상**: `\\eiNNNieSysNAS\docker\auto_stock\backend\main.py`

> ✏️ indicators 라우터 등록 추가 (88-92번 라인)

---

## 🔧 수동 복사 방법

### Windows 파일 탐색기 사용

1. **indicators.py 복사**:
   ```
   소스: d:\Dev\auto_stock\backend\api\indicators.py
   대상: \\eiNNNieSysNAS\docker\auto_stock\backend\api\indicators.py
   ```
   - 파일 탐색기에서 소스 파일 복사 (Ctrl+C)
   - `\\eiNNNieSysNAS\docker\auto_stock\backend\api\` 폴더 열기
   - 붙여넣기 (Ctrl+V)

2. **main.py 복사**:
   ```
   소스: d:\Dev\auto_stock\backend\main.py
   대상: \\eiNNNieSysNAS\docker\auto_stock\backend\main.py
   ```
   - 파일 탐색기에서 소스 파일 복사 (Ctrl+C)
   - `\\eiNNNieSysNAS\docker\auto_stock\backend\` 폴더 열기
   - 붙여넣기 (Ctrl+V)
   - 덮어쓰기 확인

### PowerShell 사용

```powershell
# indicators.py 복사
Copy-Item -Path "d:\Dev\auto_stock\backend\api\indicators.py" `
          -Destination "\\eiNNNieSysNAS\docker\auto_stock\backend\api\indicators.py" `
          -Force

# main.py 복사
Copy-Item -Path "d:\Dev\auto_stock\backend\main.py" `
          -Destination "\\eiNNNieSysNAS\docker\auto_stock\backend\main.py" `
          -Force
```

---

## 🐳 Docker 컨테이너 재시작

파일 복사 후 백엔드 Docker 컨테이너를 재시작하세요:

```bash
# NAS SSH 접속
ssh admin@eiNNNieSysNAS

# Docker 컨테이너 재시작
cd /volume1/docker/auto_stock
docker-compose restart backend

# 또는 전체 재시작
docker-compose down
docker-compose up -d

# 로그 확인
docker-compose logs -f backend
```

**기대 로그**:
```
[OK] Indicators router registered
```

---

## ✅ 확인 방법

### 1. API 엔드포인트 확인

```bash
# NAS 백엔드 서버로 요청
curl http://eiNNNieSysNAS:8000/api/indicators/health
```

**기대 응답**:
```json
{
  "status": "healthy",
  "service": "indicators-api",
  "timestamp": "2025-10-26T15:30:00"
}
```

### 2. 지표 계산 테스트

```bash
curl -X POST http://eiNNNieSysNAS:8000/api/indicators/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "005930",
    "indicators": [
      {"name": "ma", "params": {"period": 20}},
      {"name": "bollinger", "params": {"period": 20}},
      {"name": "rsi", "params": {"period": 14}}
    ],
    "days": 60
  }'
```

**기대 응답**:
```json
{
  "stock_code": "005930",
  "indicators": {
    "ma_20": 75000.5,
    "bollinger_upper": 78000,
    "bollinger_middle": 75000,
    "bollinger_lower": 72000,
    "rsi": 45.5,
    "close": 75500
  },
  "calculated_at": "2025-10-26T15:30:00"
}
```

---

## 📝 주의사항

1. **NAS 경로 접근 권한 확인**
   - Windows 파일 탐색기에서 `\\eiNNNieSysNAS` 접근 가능한지 확인
   - 접근 불가 시 네트워크 드라이브 매핑 필요

2. **Docker 볼륨 마운트 확인**
   - `docker-compose.yml`에서 backend 폴더가 올바르게 마운트되어 있는지 확인
   - 컨테이너 내부 경로: `/app/backend`

3. **환경 변수 확인**
   - `SUPABASE_URL`, `SUPABASE_KEY` 환경 변수 설정 확인
   - `.env` 파일 또는 `docker-compose.yml`에서 설정

---

**작성일**: 2025-10-26
**작성자**: Claude Code
