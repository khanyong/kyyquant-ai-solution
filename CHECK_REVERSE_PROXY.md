# 리버스 프록시 확인 및 해결

## 문제 원인
Let's Encrypt는 도메인 확인을 위해 다음 경로에 접근합니다:
- `http://bll-pro.com/.well-known/acme-challenge/[token]`
- `http://api.bll-pro.com/.well-known/acme-challenge/[token]`
- `http://workflow.bll-pro.com/.well-known/acme-challenge/[token]`

리버스 프록시가 이 경로를 다른 곳으로 전달하면 인증 실패!

## 1. 현재 리버스 프록시 규칙 확인

**Control Panel** → **Application Portal** → **Reverse Proxy**

현재 설정된 규칙들 확인:
- workflow.bll-pro.com → 어디로?
- api.bll-pro.com → 설정되어 있나?
- bll-pro.com → 설정되어 있나?

## 2. 인증서 생성 시 리버스 프록시 임시 비활성화

### 방법 A: 규칙 임시 비활성화
1. 각 리버스 프록시 규칙 선택
2. **Disable** 클릭
3. 인증서 생성
4. 생성 완료 후 다시 **Enable**

### 방법 B: acme-challenge 예외 규칙 추가
리버스 프록시 규칙을 유지하면서 Let's Encrypt 경로만 예외 처리

1. **Create** 새 규칙
2. 설정:
   - Description: Let's Encrypt Challenge
   - Source:
     - Protocol: HTTP
     - Hostname: api.bll-pro.com
     - Port: 80
     - **Enable custom header** 체크
     - Path: `/.well-known/acme-challenge`
   - Destination:
     - Protocol: HTTP  
     - Hostname: localhost
     - Port: 80
3. 이 규칙을 **최상단**으로 이동 (우선순위 높임)

## 3. 테스트

```bash
# acme-challenge 경로 접근 테스트
curl http://api.bll-pro.com/.well-known/acme-challenge/test

# 404 Not Found가 나와야 정상 (리버스 프록시 거치지 않음)
# 다른 응답이 나오면 리버스 프록시가 간섭 중
```

## 4. Web Station 확인

Web Station이 실행 중이면:
1. **Control Panel** → **Web Station**
2. **General Settings**
3. HTTP port가 80이 아닌지 확인
4. Virtual Host 설정 확인

## 5. 정확한 순서

1. **리버스 프록시 비활성화** 또는 예외 규칙 추가
2. **Cloudflare 프록시 비활성화** (회색 구름)
3. 5-10분 대기 (DNS 전파)
4. **인증서 생성 시도**
5. 성공 후:
   - 리버스 프록시 재활성화
   - Cloudflare 프록시 재활성화 (오렌지 구름)

## 6. 대안: 기존 workflow 인증서 활용

workflow.bll-pro.com이 이미 작동 중이라면:
1. 동일한 인증서를 api.bll-pro.com에도 사용
2. 또는 workflow 인증서를 교체하여 api도 포함

## 진단 명령어

```bash
# 리버스 프록시 거치는지 확인
curl -I http://api.bll-pro.com
# Server 헤더 확인 (nginx면 직접 연결, 다른 값이면 프록시 경유)

# Let's Encrypt 경로 확인  
curl http://api.bll-pro.com/.well-known/acme-challenge/
# 404면 정상, 다른 응답이면 리버스 프록시 문제
```