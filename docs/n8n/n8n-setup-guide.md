# 📋 NAS N8N 서버 연동 가이드

## 1️⃣ N8N 접속
- NAS IP 주소: `http://[NAS_IP]:5678`
- 예: `http://192.168.1.100:5678`

## 2️⃣ Credentials 설정

### Supabase Credential 생성:
1. N8N → Settings → Credentials → Add Credential
2. "Supabase" 선택
3. 입력:
   ```
   Host: https://hznkyaomtrpzcayayayh.supabase.co
   Service Role Key: [Supabase Dashboard에서 확인]
   ```

### 키움 API 환경변수 설정:
1. N8N → Settings → Environment Variables
2. 추가:
   ```
   KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
   KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
   KIWOOM_ACCOUNT_NO=81101350-01
   KIWOOM_API_URL=https://mockapi.kiwoom.com
   ```

## 3️⃣ 워크플로우 임포트

1. N8N → Workflows → Import
2. 파일 선택: `n8n-workflows/kiwoom-trading-workflow.json`
3. 활성화 (Active 토글 ON)

## 4️⃣ 워크플로우 수정 필요사항

### 토큰 발급 노드:
- Method: POST
- URL: https://mockapi.kiwoom.com/oauth2/token
- Headers:
  ```json
  {
    "Content-Type": "application/json;charset=UTF-8"
  }
  ```
- Body:
  ```json
  {
    "grant_type": "client_credentials",
    "appkey": "{{$env.KIWOOM_APP_KEY}}",
    "secretkey": "{{$env.KIWOOM_APP_SECRET}}"
  }
  ```

## 5️⃣ 테스트
1. 워크플로우에서 "Execute Workflow" 클릭
2. 성공 시 Supabase에 데이터 저장 확인